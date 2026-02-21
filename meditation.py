import json
import time
import threading
import random
import asyncio
import pyttsx3
import pygame
from telegram import Bot
from datetime import datetime, timedelta

# Meditation styles
STYLES = {
    1: {"name": "Mindfulness Flow", "desc": "Focus on breath, present-moment clarity.", "prompts": ["Notice your breath like a steady market ticker, flowing in and out.", "Let thoughts pass like clouds, return to your breath."], "breathing": (4, 4, 6)},
    2: {"name": "Cosmic Drift", "desc": "Visualize drifting through a starry galaxy.", "prompts": ["Float among the stars, each breath a pulse of light.", "Your mind is a nebula, vast and calm."], "breathing": (4, 4, 6)},
    3: {"name": "Gratitude Pulse", "desc": "Reflect on three things you’re grateful for.", "prompts": ["Think of one thing today that sparks joy, let it fill your chest.", "What moment today felt like a win?"], "breathing": (4, 7, 8)},
    4: {"name": "Body Scan Circuit", "desc": "Scan body to release tension like debugging code.", "prompts": ["Scan your shoulders, release any stored tension like clearing a cache.", "Move to your chest, let it soften."], "breathing": (5, 5, 5)},
    5: {"name": "Zen Minimal", "desc": "Minimalist breath counting, pure focus.", "prompts": ["Count each exhale up to 10, then start again.", "If you lose count, gently restart at one."], "breathing": (4, 0, 4)},
    6: {"name": "Energy Surge", "desc": "Dynamic breathing to boost energy.", "prompts": ["Breathe in sharply for 3, out for 3, feel the surge.", "Charge your focus like a rising trend."], "breathing": (3, 0, 3)},
    7: {"name": "Lunar Reflection", "desc": "Introspective emotional clarity under moonlight.", "prompts": ["What emotion glows softly in you now, like moonlight?", "What can you release to feel lighter?"], "breathing": (4, 7, 8)},
    8: {"name": "Quantum Focus", "desc": "Align thoughts like a quantum processor.", "prompts": ["Align your thoughts like qubits in a quantum array.", "Your focus is a laser, precise and clear."], "breathing": (4, 4, 4)},
    9: {"name": "Nature Sync", "desc": "Sync with nature’s rhythms, forest or ocean.", "prompts": ["Breathe with the tide, in and out, one with the ocean.", "Feel the earth’s pulse in your breath."], "breathing": (5, 5, 5)},
    10: {"name": "Trader’s Calm", "desc": "Calm the mind for trading, no volatility.", "prompts": ["Your mind is a calm market, no volatility, just flow.", "Steady your focus like a perfect trade."], "breathing": (4, 7, 8)}
}

SOUNDSCAPES = {1: "ocean.wav", 2: "forest.wav", 3: "cosmic.wav"}

# Load or create config
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        config = {
            "default_style": 10,
            "default_duration": 10,
            "default_soundscape": 3,
            "telegram_token": "",
            "telegram_chat_id": ""
        }
        print("🌌 First-time setup: Enter Telegram Bot Token:")
        config["telegram_token"] = input("> ")
        print("Enter Telegram Chat ID:")
        config["telegram_chat_id"] = input("> ")
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        return config

# Save session to ledger
def save_session(style, duration, notes):
    try:
        with open("ledger.json", "r") as f:
            ledger = json.load(f)
    except FileNotFoundError:
        ledger = {"sessions": [], "total_minutes": 0, "streak": 0}
    
    today = datetime.now().strftime("%Y-%m-%d")
    last_session = ledger["sessions"][-1]["date"] if ledger["sessions"] else today
    last_date = datetime.strptime(last_session, "%Y-%m-%d")
    today_date = datetime.strptime(today, "%Y-%m-%d")
    
    # Update streak
    if today_date == last_date:
        ledger["streak"] = ledger["streak"]
    elif today_date == last_date + timedelta(days=1):
        ledger["streak"] += 1
    else:
        ledger["streak"] = 1
    
    ledger["sessions"].append({
        "date": today,
        "style": STYLES[style]["name"],
        "duration": duration,
        "notes": notes
    })
    ledger["total_minutes"] += duration
    
    with open("ledger.json", "w") as f:
        json.dump(ledger, f, indent=4)
    return ledger["streak"], ledger["total_minutes"]

# Show stats
def show_stats():
    try:
        with open("ledger.json", "r") as f:
            ledger = json.load(f)
        print("🌌 Meditation Stats:")
        print(f"Total Sessions: {len(ledger['sessions'])}")
        print(f"Total Minutes: {ledger['total_minutes']}")
        print(f"Current Streak: {ledger['streak']} days")
        style_counts = {}
        for session in ledger["sessions"]:
            style = session["style"]
            style_counts[style] = style_counts.get(style, 0) + 1
        print("Sessions by Style:")
        for style, count in style_counts.items():
            print(f"{style}: {count}")
    except FileNotFoundError:
        print("No sessions yet!")

# Cosmic animation
def cosmic_animation(stop_event):
    stars = ["🌟", "✨", "⭐"]
    while not stop_event.is_set():
        print(" " * random.randint(0, 50) + random.choice(stars), flush=True)
        time.sleep(0.5)

# Send Telegram message
async def send_telegram_message(token, chat_id, message):
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Telegram error: {e}")

# Main session
async def run_session(style, duration, soundscape, config):
    engine = pyttsx3.init()
    engine.setProperty("rate", 120)  # Calm voice speed
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(SOUNDSCAPES[soundscape])
        pygame.mixer.music.play(-1)  # Loop sound
    except Exception as e:
        print(f"Sound error: {e}, continuing without sound.")
    
    stop_event = threading.Event()
    anim_thread = threading.Thread(target=cosmic_animation, args=(stop_event,))
    anim_thread.start()
    
    print(f"🌌 Starting {STYLES[style]['name']} session...")
    engine.say(f"Starting your {STYLES[style]['name']} session.")
    engine.runAndWait()
    
    # Warm-up (1 min)
    print("🌟 Warm-up: Inhale deeply... Exhale slowly...")
    engine.say("Warm-up. Inhale deeply. Exhale slowly.")
    engine.runAndWait()
    await asyncio.sleep(60)
    
    # Main session
    inhale, hold, exhale = STYLES[style]["breathing"]
    prompt = random.choice(STYLES[style]["prompts"])
    print(f"🌟 Main: Breathe in for {inhale}, hold for {hold}, exhale for {exhale}...")
    print(f"Prompt: {prompt}")
    engine.say(f"Breathe in for {inhale}, hold for {hold}, exhale for {exhale}. {prompt}")
    engine.runAndWait()
    await asyncio.sleep((duration - 2) * 60)  # Main session minus warm-up and cooldown
    
    # Cooldown (1 min)
    print("🌟 Cooldown: Reflect on your session...")
    engine.say("Cooldown. Reflect on your session.")
    engine.runAndWait()
    await asyncio.sleep(60)
    
    stop_event.set()
    anim_thread.join()
    pygame.mixer.music.stop()
    
    # Collect notes
    print("Enter any reflections (or press Enter to skip):")
    notes = input("> ")
    
    # Save session
    streak, total_minutes = save_session(style, duration, notes)
    
    # Send Telegram summary
    message = f"🌌 Completed {duration}-min {STYLES[style]['name']}. Streak: {streak} days, Total: {total_minutes} min."
    ifjmml = asyncio.create_task(send_telegram_message(config["telegram_token"], config["telegram_chat_id"], message))

# Main CLI
async def main():
    config = load_config()
    while True:
        print("\n🌌 ZenBot 🌌")
        print("1. Start Meditation")
        print("2. View Stats")
        print("3. Exit")
        choice = input("> ")
        
        if choice == "1":
            print("\nSelect Meditation Style:")
            for i in range(1, 11):
                print(f"{i}. {STYLES[i]['name']} - {STYLES[i]['desc']}")
            style = int(input("> "))
            
            print("Duration (minutes, 5-30):")
            duration = max(5, min(30, int(input("> "))))
            
            print("Soundscape: [1] Ocean [2] Forest [3] Cosmic")
            soundscape = int(input("> "))
            
            await run_session(style, duration, soundscape, config)
        elif choice == "2":
            show_stats()
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())