import tweepy
import os
import openai
import json
import re
import logging
import argparse
from typing import Dict, Optional, List, Tuple
import time
import requests  # For API polling
import sys  # For UTF-8 fix
from datetime import datetime, timedelta  # For news recency
import random  # For diversity randomness
import feedparser  # For RSS (pip install feedparser)
from PIL import Image  # For image handling (pip install pillow)
import io  # For in-mem image
from gtts import gTTS  # For TTS (pip install gtts)
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, AudioFileClip  # For video (pip install moviepy)
from googleapiclient.discovery import build  # For YouTube API (pip install google-api-python-client google-auth-oauthlib)
from googleapiclient.http import MediaFileUpload  # For video upload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle  # For token save
import moviepy.config as mpconf
mpconf.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe"})

# Windows UTF-8 fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('diverse_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Env vars
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')  # Required for upload
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDS_FILE = 'client_secrets.json'
TOKEN_FILE = 'token.pickle'
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Configs
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=1h"
NEWS_URL = "https://newsdata.io/api/1/crypto?apikey={key}&language=en&size=5"
RSS_SOURCES = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://cryptonews.com/news/feed/",
    "https://www.ambcrypto.com/feed/",
    "https://www.coinbureau.com/feed/"
]
SIGNAL_THRESHOLD = 5.0
COOLDOWN_HOURS = 1
NEWS_COOLDOWN_HOURS = 4
EVERGREEN_TEMPLATES = [
    "Top 3 beginner mistakes in crypto trading",
    "Poll: Will BTC hit $100K by end of 2025?",
    "Quick tip: How to spot a rug pull early",
    "Fun fact: Satoshi's estimated net worth today",
    "Why diversify beyond BTC/ETH?",
    "Wallet security checklist for 2025",
    "DeFi yield farming basics",
    "NFTs in 2025: Hype or value?"
]
posted_coins = {}
posted_news_sources = set()
posted_rss_sources = {}
NEWS_LAST_CLEAR = time.time()

def clear_old_sources():
    global NEWS_LAST_CLEAR, posted_news_sources, posted_rss_sources
    now = time.time()
    if now - NEWS_LAST_CLEAR > 86400:
        posted_news_sources.clear()
        posted_rss_sources.clear()
        NEWS_LAST_CLEAR = now
        logger.info("Cleared old news sources cache.")

# fetch_signals, fetch_news, fetch_rss_news unchanged from v2.7
def fetch_signals(threshold: float = SIGNAL_THRESHOLD) -> List[Tuple[str, str]]:
    try:
        response = requests.get(COINGECKO_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        signals = []
        now = time.time()
        for coin in data:
            change = abs(coin['price_change_percentage_1h_in_currency'])
            if change > threshold:
                coin_id = coin['id']
                last_post = posted_coins.get(coin_id, 0)
                if now - last_post > COOLDOWN_HOURS * 3600:
                    direction = "up" if coin['price_change_percentage_1h_in_currency'] > 0 else "down"
                    signal = f"{coin['symbol'].upper()} {direction} {change:.1f}%"
                    signals.append((signal, coin_id))
                    logger.info(f"Signal detected: {signal}")
        return signals
    except Exception as e:
        logger.error(f"Signal fetch error: {e}")
        return []

def fetch_news(query: Optional[str] = None, source: str = 'newsdata') -> List[Tuple[str, str]]:
    clear_old_sources()
    
    if source == 'rss' or not NEWS_API_KEY:
        logger.info("Using multi-RSS fallback.")
        return fetch_rss_news(query)
    
    try:
        url_params = f"&q={query}" if query else ""
        url = NEWS_URL.format(key=NEWS_API_KEY) + url_params
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cutoff = datetime.now() - timedelta(hours=24)
        news_items = []
        for article in data.get('results', []):
            pub_date_str = article['pubDate'].replace('Z', '+00:00') if article['pubDate'] else None
            if pub_date_str:
                pub_date = datetime.fromisoformat(pub_date_str)
                if pub_date > cutoff and article['source_id'] not in posted_news_sources:
                    headline = article['title']
                    source_id = article['source_id']
                    news_items.append((headline, source_id))
                    posted_news_sources.add(source_id)
                    if len(news_items) >= 5:
                        break
        
        if news_items:
            logger.info(f"Fetched {len(news_items)} fresh NewsData items.")
            return news_items
        else:
            logger.warning("No fresh NewsData; falling back to RSS.")
            return fetch_rss_news(query)
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.warning("401 Unauthorized on NewsData; need registered key. Falling back to RSS.")
        else:
            logger.error(f"NewsData HTTP error: {e}")
        return fetch_rss_news(query)
    except Exception as e:
        logger.error(f"News fetch error: {e}")
        return fetch_rss_news(query)

def fetch_rss_news(query: Optional[str] = None) -> List[Tuple[str, str]]:
    now = time.time()
    available_sources = []
    for rss_url in RSS_SOURCES:
        last_used = posted_rss_sources.get(rss_url, 0)
        if now - last_used > NEWS_COOLDOWN_HOURS * 3600:
            available_sources.append(rss_url)
    
    if not available_sources:
        logger.info("All RSS sources on cooldown; skipping.")
        return []
    
    random.shuffle(available_sources)
    news_items = []
    cutoff = datetime.now() - timedelta(hours=24)
    for rss_url in available_sources[:2]:
        try:
            feed = feedparser.parse(rss_url)
            source = rss_url.split('//')[-1].split('/')[0]
            for entry in feed.entries[:3]:
                if 'published_parsed' in entry:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date > cutoff:
                        headline = entry.title
                        if not query or query.lower() in headline.lower():
                            news_items.append((headline, source))
                            posted_rss_sources[rss_url] = now
                            logger.info(f"Fetched from {source}: {headline[:50]}...")
                            if len(news_items) >= 3:
                                break
            if len(news_items) >= 3:
                break
        except Exception as e:
            logger.warning(f"RSS error on {rss_url}: {e}")
    
    if news_items:
        logger.info(f"Fetched {len(news_items)} fresh RSS items across sources.")
    else:
        logger.info("No fresh RSS items available.")
    return news_items

def generate_image_description(input_str: str, content_type: str) -> str:
    if content_type == "signal":
        return f"A vibrant crypto chart showing {input_str}, with bullish rocket emojis and green arrows, in a modern trading dashboard style."
    elif content_type == "news":
        return f"Illustrative meme for crypto news: {input_str[:50]}..., cartoon style with money bags and question marks."
    else:  # Evergreen
        return f"Engaging infographic for crypto tip: {input_str}, clean design with icons and bullet points."

def generate_content(input_str: str, content_type: str = "signal", model: str = "gpt-4o-mini", temperature: float = 0.7, image_model: Optional[str] = "dall-e-3") -> Dict[str, str]:
    if content_type == "evergreen":
        prompt = f"""
        Based on this evergreen crypto topic: {input_str}
        Generate:
        1. An engaging X post (under 280 chars) with poll idea or question + hashtags.
        2. A 60-sec YouTube Shorts script: Hook, key points, CTA.
        3. A short video title.
        4. 5-10 relevant tags for YouTube.
        5. A description (100-150 chars) with X link placeholder.
        Respond **only** with JSON: {{"tweet": "...", "script": "...", "title": "...", "tags": ["tag1", "tag2"], "desc": "..."}}
        """
    elif content_type == "news":
        prompt = f"""
        Based on this crypto news headline: {input_str}
        Generate a reactive X post: Share quick insights, questions, or takes (under 280 chars) with hashtags.
        Also: 60-sec YouTube Shorts script (hook on headline, analysis, CTA).
        Short video title.
        5-10 relevant tags for YouTube.
        Description (100-150 chars) with X link placeholder.
        Respond **only** with JSON: {{"tweet": "...", "script": "...", "title": "...", "tags": ["tag1", "tag2"], "desc": "..."}}
        """
    else:  # signal
        prompt = f"""
        Based on this trading signal: {input_str}
        Generate:
        1. A punchy X post (under 280 chars) with hashtags.
        2. A 60-sec YouTube Shorts script: Intro hook, explanation, call-to-action.
        3. A short video title.
        4. 5-10 relevant tags for YouTube.
        5. A description (100-150 chars) with X link placeholder.
        Respond **only** with JSON: {{"tweet": "...", "script": "...", "title": "...", "tags": ["tag1", "tag2"], "desc": "..."}}
        """
    
    max_retries = 3
    raw_content = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content.strip()
            logger.info(f"Raw OpenAI response ({content_type}): {raw_content}")
            
            content = json.loads(raw_content)
            if len(content["tweet"]) > 280:
                raise ValueError(f"Tweet exceeds 280 chars: {len(content['tweet'])}")
            
            # Optional image gen
            image_url = None
            if image_model:
                try:
                    img_prompt = generate_image_description(input_str, content_type)
                    img_response = client.images.generate(
                        model=image_model,
                        prompt=img_prompt,
                        n=1,
                        size="1024x1024"
                    )
                    image_url = img_response.data[0].url
                    logger.info(f"Generated image URL: {image_url}")
                except Exception as img_e:
                    logger.warning(f"Image gen failed: {img_e}")
            
            content["image_url"] = image_url
            logger.info(f"Content generated successfully ({content_type})!")
            return content
            
        except json.JSONDecodeError as e:
            logger.warning(f"Parse failed (attempt {attempt+1}): {e}")
            cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_content, flags=re.MULTILINE).strip()
            if cleaned != raw_content:
                try:
                    content = json.loads(cleaned)
                    if len(content["tweet"]) <= 280:
                        logger.info("Parsed after stripping wrapper!")
                        return content
                except json.JSONDecodeError:
                    pass
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Generation error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    raise ValueError(f"Failed after {max_retries} retries. Last raw: {raw_content}")

def get_youtube_service():
    """Auth and return YouTube API client."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def create_youtube_short(content: Dict[str, str], image_url: Optional[str] = None, bg_path: Optional[str] = None, public: bool = False, x_post_url: Optional[str] = None):
    """Build 60s Short MP4 from content, upload to YouTube."""
    if not YOUTUBE_CHANNEL_ID:
        raise ValueError("YOUTUBE_CHANNEL_ID env var required for upload.")
    
    try:
        # TTS Audio
        tts = gTTS(text=content["script"], lang='en', slow=False)
        audio_path = f"temp_audio_{int(time.time())}.mp3"
        tts.save(audio_path)
        audio = AudioFileClip(audio_path)
        duration = audio.duration  # ~60s
        
        # Video: Simple color bg or image/video
        if image_url:
            img_resp = requests.get(image_url)
            img = Image.open(io.BytesIO(img_resp.content))
            img_clip = ImageClip(io.BytesIO(img_resp.content), duration=duration).set_audio(audio)
        elif bg_path and os.path.exists(bg_path):
            bg_clip = VideoFileClip(bg_path).subclip(0, duration).set_audio(audio)
            # Add text overlays
            txt_clip = TextClip(content["title"], fontsize=70, color='white', font='Arial-Bold').set_position('center').set_duration(duration)
            video = CompositeVideoClip([bg_clip, txt_clip])
        else:
            # Default color bg with text
            bg_clip = ColorClip(size=(1080, 1920), color=(0,0,0), duration=duration).set_audio(audio)
            txt_clip = TextClip(content["script"], fontsize=50, color='white', font='Arial', size=(900, None)).set_position(('center', 'center')).set_duration(duration)
            video = CompositeVideoClip([bg_clip, txt_clip])
        
        video_path = f"temp_short_{int(time.time())}.mp4"
        video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
        
        # Upload
        youtube = get_youtube_service()
        body = {
            'snippet': {
                'title': content["title"],
                'description': content["desc"].replace("[X_LINK]", x_post_url or "") + f"\n\n#Crypto #Shorts",
                'tags': content["tags"],
                'categoryId': '28'  # Science & Technology
            },
            'status': {
                'privacyStatus': 'public' if public else 'private'
            }
        }
        insert_request = youtube.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(video_path))
        response = insert_request.execute()
        video_id = response['id']
        logger.info(f"Uploaded YouTube Short: https://youtu.be/{video_id}")
        
        # Cleanup
        os.remove(audio_path)
        os.remove(video_path)
        return video_id
        
    except Exception as e:
        logger.error(f"YouTube creation/upload error: {e}")
        # Cleanup on fail
        for temp in [f for f in os.listdir('.') if f.startswith('temp_')]:
            os.remove(temp)
        return None

def post_to_x(content: Dict[str, str], input_str: str, content_type: str, dry_run: bool = False, youtube: bool = False, public_yt: bool = False) -> Optional[str]:
    logger.info(f"Posting {content_type} for: {input_str[:50]}...")
    if not all([TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        raise ValueError("Missing Twitter env vars")
    
    tweepy_client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
        wait_on_rate_limit=True
    )
    
    media_ids = None
    x_post_url = None
    if content.get("image_url") and not dry_run:
        try:
            img_response = requests.get(content["image_url"])
            img = Image.open(io.BytesIO(img_response.content))
            temp_path = f"temp_{int(time.time())}.png"
            img.save(temp_path)
            media = tweepy_client.media_upload(temp_path)
            media_ids = [media.media_id_string]
            os.remove(temp_path)
            logger.info(f"Uploaded media ID: {media_ids[0]}")
        except Exception as media_e:
            logger.warning(f"Media upload failed: {media_e}")
    
    try:
        if dry_run:
            logger.info(f"DRY RUN: Would post: {content['tweet']}")
            if content.get("image_url"):
                logger.info(f"With image: {content['image_url']}")
            return "dry_run_success"
        
        response = tweepy_client.create_tweet(text=content["tweet"], media_ids=media_ids)
        post_id = response.data['id']
        x_post_url = f"https://x.com/i/web/status/{post_id}"
        logger.info(f"Posted {content_type}! ID: {post_id}")
        
        # YouTube integration
        if youtube:
            yt_id = create_youtube_short(content, content.get("image_url"), public=public_yt, x_post_url=x_post_url)
            if yt_id:
                logger.info(f"Added YouTube link to tweet? (Manual: Edit with https://youtu.be/{yt_id})")
        
        return str(post_id)
    except Exception as e:
        logger.error(f"Posting error: {e}")
        return None

def save_extras(content: Dict[str, str], output_prefix: Optional[str] = None, item_id: Optional[str] = None, timestamp: Optional[str] = None, content_type: str = "signal"):
    if not (content.get("script") and content.get("title")):
        return
    ts = timestamp or time.strftime("%Y-%m-%d_%H%M")
    filename = f"{output_prefix or ''}{item_id or 'generic'}_{content_type}_{ts}.json".strip('_')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {content_type} extras to {filename}")

def get_evergreen_topic() -> str:
    return random.choice(EVERGREEN_TEMPLATES)

def autonomous_loop(interval_minutes: int = 30, max_iterations: Optional[int] = None, dry_run: bool = False, output_prefix: Optional[str] = None, diversity: float = 0.3, news_query: Optional[str] = None, news_source: str = 'newsdata', evergreen_ratio: float = 0.2, image_model: Optional[str] = "dall-e-3", youtube: bool = False, public_yt: bool = False, video_bg: Optional[str] = None):
    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        signals = fetch_signals()
        items_to_process = []
        
        if signals:
            items_to_process.extend([(s, "signal", cid) for s, cid in signals])
            logger.info(f"Processing {len(signals)} signals.")
        else:
            news = fetch_news(news_query, news_source)
            if news:
                items_to_process.append((news[0][0], "news", news[0][1]))
                logger.info("No signals; falling back to news.")
        
        if not items_to_process and random.random() < diversity:
            news = fetch_news(news_query, news_source)
            if news:
                items_to_process.append((news[0][0], "news", news[0][1]))
                logger.info("Diversity pull: Generating news content.")
        
        if not items_to_process and random.random() < evergreen_ratio:
            topic = get_evergreen_topic()
            items_to_process.append((topic, "evergreen", "evergreen"))
            logger.info(f"Evergreen pull: {topic}")
        
        for input_str, ctype, item_id in items_to_process:
            try:
                content = generate_content(input_str, ctype, image_model=image_model)
                tweet = content["tweet"]
                logger.info(f"Generated {ctype} Tweet for '{input_str[:50]}...': {tweet}")
                
                post_id = post_to_x(content, input_str, ctype, dry_run, youtube, public_yt)
                if post_id and not dry_run:
                    if ctype == "signal":
                        posted_coins[item_id] = time.time()
                    logger.info(f"Live on X: https://x.com/i/web/status/{post_id}")
                
                save_extras(content, output_prefix, item_id.replace('-', '_'), time.strftime("%Y-%m-%d_%H%M"), ctype)
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error processing {ctype} '{input_str[:50]}...': {e}")
        
        iteration += 1
        logger.info(f"Loop complete ({iteration}). Sleeping {interval_minutes}min...")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diverse autonomous content bot with YouTube.")
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument("--signal", help="Manual signal")
    parser_group.add_argument("--autonomous", action="store_true", help="Run loop")
    
    parser.add_argument("--interval", type=int, default=30, help="Poll interval (min)")
    parser.add_argument("--max-iters", type=int, help="Max iterations")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model")
    parser.add_argument("--temp", type=float, default=0.7, help="Temperature")
    parser.add_argument("--dry-run", action="store_true", help="Don't post/upload")
    parser.add_argument("--output", help="Extras prefix")
    parser.add_argument("--threshold", type=float, default=5.0, help="Signal threshold")
    parser.add_argument("--diversity", type=float, default=0.3, help="News fraction")
    parser.add_argument("--evergreen-ratio", type=float, default=0.2, help="Evergreen fraction")
    parser.add_argument("--news-query", help="News keyword")
    parser.add_argument("--news-source", choices=['newsdata', 'rss'], default='newsdata', help="News source")
    parser.add_argument("--image-model", default="dall-e-3", help="Image model (or None)")
    parser.add_argument("--no-image", action="store_true", help="Skip images")
    parser.add_argument("--youtube", action="store_true", help="Generate & upload YouTube Short")
    parser.add_argument("--public-yt", action="store_true", help="Public YouTube upload (default private)")
    parser.add_argument("--video-bg", help="Path to background video/image for Shorts")
    
    args = parser.parse_args()
    
    image_model = None if args.no_image else args.image_model
    
    if args.signal:
        content = generate_content(args.signal, "signal", args.model, args.temp, image_model)
        tweet = content["tweet"]
        logger.info(f"Generated Tweet: {tweet}")
        post_id = post_to_x(content, args.signal, "signal", args.dry_run, args.youtube, args.public_yt)
        if post_id and not args.dry_run:
            logger.info(f"Live on X: https://x.com/i/web/status/{post_id}")
        save_extras(content, args.output, "manual")
    else:
        SIGNAL_THRESHOLD = args.threshold
        autonomous_loop(args.interval, args.max_iters, args.dry_run, args.output, args.diversity, args.news_query, args.news_source, args.evergreen_ratio, image_model, args.youtube, args.public_yt, args.video_bg)