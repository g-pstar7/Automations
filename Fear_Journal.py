import json
import os
from datetime import datetime
import random
import colorama
from colorama import Fore, Style
import telegram
import asyncio
from statistics import mean

colorama.init()

# Configuration
JOURNAL_FILE = "fear_journal.json"
CONFIG_FILE = "fear_journal_config.json"
TELEGRAM_TOKEN = "7397010047:AAEnGgvsUuGdXY9sMiQkw54BC2zlH6Yip5E"  # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = "5932647180"  # Replace with your chat ID
DAILY_VIBES = {
    "Monday": "Fresh start—build momentum",
    "Tuesday": "High intensity—crush it",
    "Wednesday": "Deep focus—dig in",
    "Thursday": "Creative spark—innovate",
    "Friday": "Wrap strong—reflect",
    "Saturday": "Balance—recharge",
    "Sunday": "Plan ahead—set tone"
}

# Motivational quotes
QUOTES = [
    "Fear is a compass—follow it to growth.",
    "Every fear faced is a step toward strength.",
    "What scares you is what shapes you.",
    "Fear whispers warnings; courage answers.",
    "Embrace fear—it’s just a guide in disguise.",
    "Fear is fuel—use it to soar.",
    "The only way out is through—face it.",
    "Fear signals opportunity—seize it."
]

# Guided prompts for each section
GUIDED_PROMPTS = {
    "description": ["What does this fear feel like?", "What situation brought it up?"],
    "root": ["What past event shaped this fear?", "Is there a belief driving it?"],
    "worst_case": ["What’s the absolute worst outcome?", "How likely is it?"],
    "protection": ["What loss is this fear preventing?", "What’s at stake?"],
    "reframe": ["How could this fear be a teacher?", "What strength can it build?"],
    "action_step": ["What’s one small step to face this?", "How can you start today?"]
}

# ASCII art
FEAR_COMPASS = """
{Fore.CYAN}
   ^^^ Fear Compass ^^^
   Face it, grow from it!
   ---------------------
{Style.RESET_ALL}
"""

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"nickname": "Fearless"}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"nickname": "Fearless"}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def load_journal():
    if not os.path.exists(JOURNAL_FILE):
        return []
    try:
        with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_journal(entries):
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)

def get_intensity(nickname):
    while True:
        try:
            rating = input(f"{Fore.YELLOW}{nickname}, rate fear intensity (1-5, or Enter to skip):{Style.RESET_ALL} ").strip()
            if rating == "":
                return None
            rating = int(rating)
            if 1 <= rating <= 5:
                return rating
            print(f"{Fore.RED}Please enter a number between 1 and 5.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Enter a number or leave blank.{Style.RESET_ALL}")

def get_reflection_score(nickname):
    while True:
        try:
            score = input(f"{Fore.YELLOW}{nickname}, how helpful was this session? (1-5, or Enter to skip):{Style.RESET_ALL} ").strip()
            if score == "":
                return None
            score = int(score)
            if 1 <= score <= 5:
                return score
            print(f"{Fore.RED}Please enter a number between 1 and 5.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Enter a number or leave blank.{Style.RESET_ALL}")

async def send_telegram_message(nickname, message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"{nickname}, {message}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Telegram notification failed: {e}{Style.RESET_ALL}")
        return False

def display_entry(entry):
    stars = "★" * (entry.get('intensity') or 0) + "☆" * (5 - (entry.get('intensity') or 0))
    refl_stars = "★" * (entry.get('reflection_score') or 0) + "☆" * (5 - (entry.get('reflection_score') or 0))
    print(f"\n{Fore.CYAN}--- Journal Entry ({entry['timestamp']}) ---{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Fear:{Style.RESET_ALL} {entry['description']}")
    if entry.get('intensity'):
        print(f"{Fore.YELLOW}Intensity:{Style.RESET_ALL} {stars} ({entry['intensity']}/5)")
    if entry.get('triggers'):
        print(f"{Fore.YELLOW}Triggers:{Style.RESET_ALL} {entry['triggers']}")
    if entry.get('physical_sensations'):
        print(f"{Fore.YELLOW}Physical Sensations:{Style.RESET_ALL} {entry['physical_sensations']}")
    print(f"{Fore.YELLOW}Root:{Style.RESET_ALL} {entry['root']}")
    print(f"{Fore.YELLOW}Worst Case:{Style.RESET_ALL} {entry['worst_case']}")
    print(f"{Fore.YELLOW}Protection:{Style.RESET_ALL} {entry['protection']}")
    print(f"{Fore.YELLOW}Reframe:{Style.RESET_ALL} {entry['reframe']}")
    print(f"{Fore.GREEN}Action Step:{Style.RESET_ALL} {entry['action_step']}")
    if entry.get('tags'):
        print(f"{Fore.YELLOW}Tags:{Style.RESET_ALL} {', '.join(entry['tags'])}")
    if entry.get('custom_prompt'):
        print(f"{Fore.YELLOW}Custom Prompt Answer:{Style.RESET_ALL} {entry['custom_prompt']['answer']}")
    if entry.get('reflection_score'):
        print(f"{Fore.YELLOW}Reflection Score:{Style.RESET_ALL} {refl_stars} ({entry['reflection_score']}/5)")
    if entry.get('goal'):
        print(f"{Fore.YELLOW}Goal Progress:{Style.RESET_ALL} {entry['goal']['progress']}")

def show_progress_summary(entries):
    if not entries:
        print(f"{Fore.YELLOW}No entries yet.{Style.RESET_ALL}")
        return
    intensities = [e['intensity'] for e in entries if e.get('intensity')]
    triggers = [e['triggers'] for e in entries if e.get('triggers')]
    tags = [tag for e in entries for tag in e.get('tags', []) if e.get('tags')]
    print(f"\n{Fore.CYAN}--- Progress Summary ---{Style.RESET_ALL}")
    if intensities:
        print(f"{Fore.YELLOW}Average Fear Intensity:{Style.RESET_ALL} {mean(intensities):.1f}/5")
    if triggers:
        common_trigger = max(set(triggers), key=triggers.count, default="None")
        print(f"{Fore.YELLOW}Most Common Trigger:{Style.RESET_ALL} {common_trigger}")
    if tags:
        common_tag = max(set(tags), key=tags.count, default="None")
        print(f"{Fore.YELLOW}Most Common Tag:{Style.RESET_ALL} {common_tag}")
    print(f"{Fore.YELLOW}Total Entries:{Style.RESET_ALL} {len(entries)}")

def export_to_text(entries):
    filename = f"fear_journal_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"Entry ({entry['timestamp']}):\n")
            for key, value in entry.items():
                if value and key != 'tags' and key != 'custom_prompt' and key != 'goal':
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                elif key == 'tags' and value:
                    f.write(f"Tags: {', '.join(value)}\n")
                elif key == 'custom_prompt' and value:
                    f.write(f"Custom Prompt ({value['question']}): {value['answer']}\n")
                elif key == 'goal' and value:
                    f.write(f"Goal ({value['description']}): {value['progress']}\n")
            f.write("\n")
    print(f"{Fore.GREEN}Exported to {filename}{Style.RESET_ALL}")

def view_past_entries(entries):
    if not entries:
        print(f"{Fore.YELLOW}No entries to display.{Style.RESET_ALL}")
        return
    filter_type = input(f"{Fore.YELLOW}Filter by (date/tag/intensity/none):{Style.RESET_ALL} ").strip().lower()
    if filter_type == "date":
        date = input(f"{Fore.YELLOW}Enter date (YYYY-MM-DD):{Style.RESET_ALL} ").strip()
        filtered = [e for e in entries if e['timestamp'].startswith(date)]
    elif filter_type == "tag":
        tag = input(f"{Fore.YELLOW}Enter tag:{Style.RESET_ALL} ").strip()
        filtered = [e for e in entries if tag in e.get('tags', [])]
    elif filter_type == "intensity":
        intensity = int(input(f"{Fore.YELLOW}Enter intensity (1-5):{Style.RESET_ALL} ").strip())
        filtered = [e for e in entries if e.get('intensity') == intensity]
    else:
        filtered = entries
    for entry in filtered:
        display_entry(entry)

async def main():
    config = load_config()
    nickname = config.get("nickname", "Fearless")

    if nickname == "Fearless":
        nickname = input(f"{Fore.YELLOW}What’s your journal nickname? (e.g., Cosmos, or Enter for Fearless):{Style.RESET_ALL} ").strip() or "Fearless"
        config["nickname"] = nickname
        save_config(config)

    print(FEAR_COMPASS.replace("Fear Compass", f"Fear Compass, {nickname}"))
    entries = load_journal()

    # Daily vibe
    today = datetime.now().strftime("%A")
    vibe = DAILY_VIBES.get(today, "Seize the day")
    print(f"{Fore.MAGENTA}{nickname}, Today's Vibe: {vibe}{Style.RESET_ALL}")

    # Goal setting
    goal = None
    if not entries or not any(e.get('goal') for e in entries):
        set_goal = input(f"{Fore.YELLOW}{nickname}, set a fear-facing goal? (y/n):{Style.RESET_ALL} ").strip().lower()
        if set_goal == 'y':
            goal_desc = input(f"{Fore.YELLOW}What’s your goal? (e.g., Overcome work fear):{Style.RESET_ALL} ").strip()
            goal = {"description": goal_desc, "progress": "Started"}
    else:
        goal_input = input(f"{Fore.YELLOW}{nickname}, update goal progress? (or Enter to skip):{Style.RESET_ALL} ").strip()
        if goal_input:
            goal = {"description": entries[-1].get('goal', {}).get('description', ''), "progress": goal_input}

    # Collect journal entry
    entry = {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    for field, label in [
        ('description', f'What’s the fear, {nickname}?'),
        ('triggers', 'What triggered this fear? (or Enter to skip)'),
        ('physical_sensations', 'Any physical sensations? (e.g., racing heart, or Enter to skip)'),
        ('root', 'What’s the root of this fear?'),
        ('worst_case', 'What’s the worst that could happen?'),
        ('protection', 'What is this fear protecting you from?'),
        ('reframe', 'How can you reframe this fear?'),
        ('action_step', f'What’s one action step to face this fear? (Vibe: {vibe})')
    ]:
        print(f"\n{Fore.YELLOW}{label}:{Style.RESET_ALL}")
        for prompt in GUIDED_PROMPTS.get(field, []):
            print(f"{Fore.CYAN}  - {prompt}{Style.RESET_ALL}")
        entry[field] = input().strip() or None

    entry['intensity'] = get_intensity(nickname)
    entry['tags'] = [tag.strip() for tag in input(f"{Fore.YELLOW}{nickname}, add tags (comma-separated, or Enter to skip):{Style.RESET_ALL} ").split(',') if tag.strip()] or None
    entry['custom_prompt'] = {
        'question': 'How does this fear impact my trading decisions?',
        'answer': input(f"{Fore.YELLOW}{nickname}, how does this fear impact your trading decisions? (or Enter to skip):{Style.RESET_ALL} ").strip() or None
    } if input(f"{Fore.YELLOW}{nickname}, answer custom prompt? (y/n):{Style.RESET_ALL} ").strip().lower() == 'y' else None
    entry['reflection_score'] = get_reflection_score(nickname)
    if goal:
        entry['goal'] = goal

    # Save entry
    entries.append(entry)
    save_journal(entries)

    # Display entry
    display_entry(entry)
    print(f"\n{Fore.MAGENTA}{random.choice(QUOTES)}{Style.RESET_ALL}")

    # Telegram notification
    if TELEGRAM_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN" and entry['action_step']:
        send_notif = input(f"{Fore.YELLOW}{nickname}, send action step to Telegram? (y/n):{Style.RESET_ALL} ").strip().lower()
        if send_notif == 'y':
            message = f"your action step ({entry['timestamp']}): {entry['action_step']}"
            await send_telegram_message(nickname, message)

    # Additional options
    while True:
        action = input(f"\n{Fore.YELLOW}{nickname}, next? (view/export/summary/change_nickname/done):{Style.RESET_ALL} ").strip().lower()
        if action == 'view':
            view_past_entries(entries)
        elif action == 'export':
            export_to_text(entries)
        elif action == 'summary':
            show_progress_summary(entries)
        elif action == 'change_nickname':
            new_nickname = input(f"{Fore.YELLOW}Enter new nickname (or Enter for Fearless):{Style.RESET_ALL} ").strip() or "Fearless"
            config["nickname"] = new_nickname
            save_config(config)
            nickname = new_nickname
            print(f"{Fore.GREEN}Nickname updated to {nickname}!{Style.RESET_ALL}")
        elif action == 'done':
            break
        else:
            print(f"{Fore.RED}Invalid option. Try view, export, summary, change_nickname, or done.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Done, {nickname}! Run again to journal more.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Journaling interrupted. No entry saved.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")