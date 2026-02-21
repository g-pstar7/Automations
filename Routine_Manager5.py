import datetime
import random
import asyncio
import telegram
import sqlite3
import pytz
from contextlib import contextmanager
from typing import List, Tuple, Dict

routines = {
    "Monday": {
        "vibe": "Clean slate — motivated but steady, sharp focus, grounded in faith",
        "blocks": [
            ("4:00 AM – 4:30 AM", "Wake & Prime", "Hydrate, stretch; light prayer & visualization. Mindset: Clean slate, sharp focus, nearness to God. Play 'LoFi Morning Boost' playlist"),
            ("4:30 AM – 5:30 AM", "Workout", "Bands + calisthenics or gym/run/functional training. Play 'Beast Mode' Spotify playlist"),
            ("5:30 AM – 6:00 AM", "Shower & Reset", "Cold rinse, gratitude practice"),
            ("6:00 AM – 8:30 AM", "Morning Trading", "Execute strategy, monitor setups, record key notes"),
            ("8:30 AM – 9:00 AM", "Breakfast", "Eggs, toast, avocado"),
            ("9:00 AM – 10:30 AM", "Learning Block", "Deep dive: Blockchain/AI fundamentals & coding practice"),
            ("10:30 AM – 1:00 PM", "Research & Swing Plays", "Study patterns, test volatility setups, journal insights"),
            ("1:00 PM – 1:30 PM", "Lunch", "Chicken, rice, veggies"),
            ("1:30 PM – 3:00 PM", "Strategic Work", "Funding pitch, project milestones, refining North Star"),
            ("3:00 PM – 4:30 PM", "Leverage Expansion", "Explore partnerships, scale opportunities, network outreach"),
            ("4:30 PM – 6:00 PM", "Volatility Plays", "Short bursts of tactical trades"),
            ("6:00 PM – 7:00 PM", "Dinner & Social Connection", "Cottage cheese, nuts, berries; connect with family or friends"),
            ("7:00 PM – 8:00 PM", "Evening Wind-Down", "Light reading, Tom Bilyeu mindset video (or similar), or quiet reflection"),
            ("8:00 PM – 8:30 PM", "Journaling", "Wins, lessons, adjustments; gratitude to God"),
            ("8:30 PM – 9:00 PM", "Final Prep & Lights Out", "Dim lights, no screens, short prayer"),
            ("9:00 PM", "Sleep", "")
        ]
    },
    "Tuesday": {
        "vibe": "High intensity — crush it day, full throttle, adrenaline + faith",
        "blocks": [
            ("4:00 AM – 4:30 AM", "Wake & Prime", "Hydrate, stretch; light prayer & visualization. Mindset: Crush it, beast mode activated, nearness to God. Play 'LoFi Morning Boost' playlist"),
            ("4:30 AM – 5:30 AM", "Workout", "High-intensity: gym, sprints, or max reps. Bands + calisthenics if home. Play 'Beast Mode' Spotify playlist"),
            ("5:30 AM – 6:00 AM", "Shower & Reset", "Cold rinse, gratitude practice"),
            ("6:00 AM – 8:30 AM", "Live Trading", "Execute strategy, monitor setups, record key notes"),
            ("8:30 AM – 9:00 AM", "Breakfast", "Scrambled eggs with hot sauce or spicy twist"),
            ("9:00 AM – 10:30 AM", "Bots/Code", "Adjust parameters, test ideas, optimize execution"),
            ("10:30 AM – 12:00 PM", "Blockchain/AI", "Tackle hardest coding problem first — ride the post-workout adrenaline"),
            ("12:00 PM – 2:30 PM", "Bullradar Development", "Signal-sharing platform, backtesting enhancements"),
            ("2:30 PM – 3:00 PM", "Lunch", "Spicy chicken tacos or curry rice"),
            ("3:00 PM – 4:30 PM", "Interstellarswaphub", "dApp development, smart contract tweaks"),
            ("4:30 PM – 6:00 PM", "Volatility Plays", "Short bursts of tactical trades"),
            ("6:00 PM – 6:30 PM", "Meta Skill Building", "Quick hit: leadership/communication/resilience reading or application"),
            ("6:30 PM – 7:30 PM", "Dinner & Social Connection", "Greek yogurt with zesty fruit (e.g., mango + chili flakes); connect with family or friends"),
            ("7:30 PM – 8:00 PM", "Evening Wind-Down", "Light stretch, calm music, or short high-impact read"),
            ("8:00 PM – 8:30 PM", "Journaling", "Wins, lessons, adjustments; gratitude to God"),
            ("8:30 PM – 9:00 PM", "Final Prep & Lights Out", "Dim lights, no screens, short prayer"),
            ("9:00 PM", "Sleep", "")
        ]
    },
    "Wednesday": {
        "vibe": "Midweek breather — steady and calm, sustainable pace, grounded in faith",
        "blocks": [
            ("4:00 AM – 4:30 AM", "Wake & Prime", "Hydrate, stretch; light prayer & visualization. Mindset: Steady focus, calm energy, nearness to God. Play 'LoFi Morning Boost' playlist"),
            ("4:30 AM – 5:30 AM", "Workout", "Moderate resistance, yoga, or restorative movement. Play chill beats or silence for calm"),
            ("5:30 AM – 6:00 AM", "Shower & Reset", "Cold rinse (or warm for calm), gratitude practice"),
            ("6:00 AM – 8:30 AM", "Live Trading", "Execute strategy, monitor setups, record key notes"),
            ("8:30 AM – 9:00 AM", "Breakfast", "Smoothie (banana, spinach, protein — easy and calm)"),
            ("9:00 AM – 10:30 AM", "Bots/Code", "Light adjustments, test stability, optimize gently"),
            ("10:30 AM – 1:30 PM", "Deep Learning Block", "Advanced Blockchain/AI concepts + AI model training/smart contract design. Include a 10-min walk break midway"),
            ("1:30 PM – 2:00 PM", "Lunch", "Simple fish + rice + greens"),
            ("2:00 PM – 3:30 PM", "Swing Trading", "Study patterns, test volatility setups, journal insights"),
            ("3:30 PM – 5:00 PM", "AI & Automation Integration", "Integrate AI tools into workflows, automate routine tasks"),
            ("5:00 PM – 6:00 PM", "Evening Dev", "Fun blockchain side project — keep it light and enjoyable"),
            ("6:00 PM – 7:00 PM", "Dinner & Social Connection", "Cottage cheese + almonds; connect with family or friends"),
            ("7:00 PM – 7:30 PM", "Evening Wind-Down", "Calm music, light stretch, or breathing"),
            ("7:30 PM – 8:00 PM", "Journaling", "Wins, lessons, adjustments; gratitude to God"),
            ("8:00 PM – 8:30 PM", "Meditation & Final Prep", "Short meditation, prayer, dim lights, no screens"),
            ("8:30 PM – 9:00 PM", "Buffer / Lights Out", "Extra calm time if needed"),
            ("9:00 PM", "Sleep", "")
        ]
    },
    "Thursday": {
        "vibe": "Intellectual flex — deep focus day, big-picture thinking, sustained concentration, grounded in faith",
        "blocks": [
            ("4:00 AM – 4:30 AM", "Wake & Prime", "Hydrate, stretch; light prayer & visualization. Mindset: Deep focus, intellectual sharpness, nearness to God. Play 'LoFi Morning Boost' playlist"),
            ("4:30 AM – 5:30 AM", "Workout", "Gym, running, or functional training. Bands + calisthenics if home. Play 'Beast Mode' Spotify playlist"),
            ("5:30 AM – 6:00 AM", "Shower & Reset", "Cold rinse, gratitude practice"),
            ("6:00 AM – 8:30 AM", "Live Trading", "Execute strategy, monitor setups, record key notes"),
            ("8:30 AM – 9:00 AM", "Breakfast", "Omelette with mushrooms or savory twist"),
            ("9:00 AM – 10:30 AM", "Bots/Code", "Adjust parameters, test ideas, optimize execution"),
            ("10:30 AM – 12:00 PM", "Blockchain/AI", "Watch complex Fireship tutorial and code along — deep immersion"),
            ("12:00 PM – 2:30 PM", "Bullradar Development", "Signal-sharing platform, backtesting enhancements"),
            ("2:30 PM – 3:00 PM", "Lunch", "Salmon + quinoa + roasted veggies (rich and satisfying)"),
            ("3:00 PM – 4:30 PM", "Interstellarswaphub", "dApp development, smart contract tweaks"),
            ("4:30 PM – 6:00 PM", "Second Order Research", "Deep analysis of implications, trend forecasting, scenario planning"),
            ("6:00 PM – 7:30 PM", "Volatility Plays", "Short bursts of tactical trades"),
            ("7:30 PM – 8:30 PM", "Dinner & Social Connection", "Greek yogurt + walnuts + drizzle of honey; connect with family or friends"),
            ("8:30 PM – 9:00 PM", "Evening Wind-Down & Journaling", "Slow jazz playlist, sketch big ideas; wins, lessons, adjustments; gratitude to God"),
            ("9:00 PM", "Lights Out", "Final prayer, no screens, sleep")
        ]
    },
    "Friday": {
        "vibe": "Celebration — pre-weekend hype, wrap the week strong, energy high, gratitude flowing",
        "blocks": [
            ("4:00 AM – 4:30 AM", "Wake & Prime", "Hydrate, stretch; light prayer & visualization. Mindset: Wrap strong, celebrate progress, nearness to God. Play 'LoFi Morning Boost' playlist"),
            ("4:30 AM – 5:30 AM", "Workout", "High-energy gym, sprints, or functional training. Play 'Beast Mode' Spotify playlist"),
            ("5:30 AM – 6:00 AM", "Shower & Reset", "Cold rinse, gratitude practice"),
            ("6:00 AM – 8:30 AM", "Live Trading", "Execute strategy, monitor setups, record key notes"),
            ("8:30 AM – 9:00 AM", "Breakfast", "Pancakes or protein waffle (small indulgence)"),
            ("9:00 AM – 10:30 AM", "Bots/Code", "Finalize tweaks and optimizations for the week"),
            ("10:30 AM – 1:00 PM", "Financial Strategy", "Capital management, pitch work, review allocations"),
            ("1:00 PM – 1:30 PM", "Lunch", "Burger (lean beef or chicken) + sweet potato fries"),
            ("1:30 PM – 3:00 PM", "Network & Influence", "Collaborations, outreach, or community engagement"),
            ("3:00 PM – 4:30 PM", "Strategic Reflection & Recalibration", "Review week, adjust goals, align with vision & faith"),
            ("4:30 PM – 6:00 PM", "Trading Volatility", "Short bursts of tactical trades — blast EDM for hype"),
            ("6:00 PM – 7:00 PM", "Dinner & Social Connection", "Cottage cheese + dark chocolate (mini reward); connect with family or friends"),
            ("7:00 PM – 8:30 PM", "Evening Celebration Relaxation", "Watch Matt D’Avella (or similar) video, play quick game, light music — enjoy the wins"),
            ("8:30 PM – 9:00 PM", "Journaling", "Wins, lessons, adjustments; big gratitude to God"),
            ("9:00 PM – 10:00 PM", "Final Wind-Down", "Dim lights, calm music or reading, short prayer, no screens after 9:30"),
            ("10:00 PM", "Sleep", "")
        ]
    },
    "Saturday": {
        "vibe": "Full-on weekend — freedom & feast, recovery, fun, indulgence, gratitude",
        "blocks": [
            ("6:30 AM – 7:00 AM", "Wake & Prime", "Sleep in if needed, then hydrate, light stretch; optional prayer & visualization. Mindset: Freedom, gratitude, nearness to God. Play chill LoFi or nature sounds"),
            ("7:00 AM – 8:00 AM", "Bots/Code (Optional)", "Quick parameter check or light tweaks — skip if you want full disconnect"),
            ("8:00 AM – 9:00 AM", "Big Breakfast", "Eggs, bacon, toast — go big, enjoy slowly"),
            ("9:00 AM – 12:00 PM", "Chores & Errands", "Laundry, grocery shopping, house tasks, bill pay, etc. Batch them efficiently — play upbeat playlist"),
            ("12:00 PM – 1:00 PM", "Lunch", "BBQ chicken, beachside sandwich, or whatever sounds good"),
            ("1:00 PM – 4:00 PM", "Free Time / Light Activity", "Chill, read, nap, walk, or optional light trading/research if markets call you"),
            ("4:00 PM – 7:00 PM", "Outdoor/Recharge Activity", "Hike, beach, swim, sport, park hangout — get sun and movement"),
            ("7:00 PM – 8:00 PM", "Dinner", "Whatever you crave — pizza, takeout, grill, feast mode"),
            ("8:00 PM – 9:30 PM", "Movie Night / Gaming / Social", "Big screen movie, gaming session, or hang with friends/family"),
            ("9:30 PM – 10:00 PM", "Journaling & Wind-Down", "Quick wins/reflections or skip; gratitude to God, short prayer"),
            ("10:00 PM", "Sleep", "")
        ]
    },
    "Sunday": {
        "vibe": "Wind down and prep — reflective calm, Sabbath rest, spiritual renewal, gratitude",
        "blocks": [
            ("6:30 AM – 7:00 AM", "Wake & Prime", "Sleep in if body needs it, then hydrate, gentle stretch; prayer for rest and renewal. Mindset: Sabbath peace, nearness to God. Play soft worship or silence"),
            ("7:00 AM – 11:00 AM", "Morning Reflection & Reading", "Extended journaling, read Scripture, devotional, or inspirational books. Slow and contemplative"),
            ("11:00 AM – 12:00 PM", "Breakfast", "Smoothie or light eggs + fruit — eat mindfully"),
            ("12:00 PM – 2:00 PM", "Chores & Light Errands", "Laundry, quick grocery top-up if needed, light house tasks — keep it low-energy and efficient"),
            ("2:00 PM – 2:30 PM", "Lunch", "Fish + salad (clean and simple)"),
            ("2:30 PM – 4:30 PM", "Weekly Review & Spiritual Alignment", "Career & Wealth reflection, Quarterly Horizons check; spiritual alignment, prayer over the week ahead"),
            ("4:30 PM – 5:30 PM", "Rest & Recharge", "Nap, quiet walk in nature, or silent reflection"),
            ("5:30 PM – 6:30 PM", "Optional Moderate Workout", "Light walk, yoga, stretching, or full rest — listen to your body"),
            ("6:30 PM – 7:30 PM", "Dinner & Social Connection", "Cottage cheese + berries; fellowship with family/friends/church community"),
            ("7:30 PM – 8:00 PM", "Evening Planning", "Lightly plan the coming week with calm music (rain sounds); short prayer for guidance"),
            ("8:00 PM – 8:30 PM", "Journaling & Gratitude", "Final reflections, wins of the week, deep gratitude to God"),
            ("8:30 PM – 9:00 PM", "Meditation & Lights Out", "Breathing, short prayer, dim lights, no screens"),
            ("9:00 PM", "Sleep", "")
        ]
    }
}

# Motivational content
tweaks = [
    "Add a 5-min podcast (Jocko Willink)",
    "Switch up the music—try trap beats!",
    "Take a 10-min walk to reset.",
    "Review one trade with a critical eye.",
    "Sip a green tea for focus.",
    "Do a 1-min plank for energy.",
    "Sketch a quick algo flowchart.",
    "Listen to a 5-min crypto news update.",
    "Check one Web3 trend on X.",
    "Write a 10-word trading mantra.",
    "Pause for a quick prayer of thanks."
]

motivational_quotes = [
    "Crush the day—chaos is your canvas!",
    "One block down, a legend rises.",
    "Flow with the grind, own the vibe.",
    "You’re not just doing—you’re becoming.",
    "Trade smart, live bold—own the market!",
    "Every tick is a chance to win big.",
    "Code, trade, conquer—build your empire!",
    "Seek first the Kingdom—align your work with purpose.",
    "In His strength, you rise above the storm."
]

vibe_tweaks = {
    "energized": ["Crank the tempo—EDM time!", "Add a quick 10-pushup burst.", "Blast some hip-hop for momentum."],
    "tired": ["Switch to chill beats—lo-fi it.", "Shorten this block by 15 min.", "Take 5 deep breaths to recharge."],
    "in between": ["Try a funky playlist twist.", "Sip some tea and vibe.", "Do a quick stretch for clarity."]
}

micro_challenges = [
    "Do 10 squats now!",
    "Hum a tune for 30 sec.",
    "Take 5 deep breaths and roar!",
    "Jot down a wild idea in 10 words.",
    "Visualize a winning trade for 30 sec.",
    "Write one line of code for fun.",
    "Check a crypto price spike on X.",
    "Whisper a quick prayer for focus."
]

sleep_tips = [
    "Dim lights 30 min before bed.",
    "No screens—try a book!",
    "Deep breaths to wind down.",
    "Set a cozy vibe—rain sounds.",
    "Review one trade lesson before sleep.",
    "End with a bedtime prayer for peace."
]

# Configuration
TELEGRAM_BOT_TOKEN = "7397010047:AAEnGgvsUuGdXY9sMiQkw54BC2zlH6Yip5E"
TELEGRAM_CHAT_ID = "5932647180"
EAT_TZ = pytz.timezone("Africa/Nairobi")

# Priorities (Eisenhower Matrix)
TASK_PRIORITIES = {
    "Wake & Prime": ("Important, Not Urgent", 2),
    "Workout": ("Important, Not Urgent", 2),
    "Shower & Reset": ("Important, Not Urgent", 2),
    "Morning Trading": ("Urgent & Important", 1),
    "Live Trading": ("Urgent & Important", 1),
    "Breakfast": ("Important, Not Urgent", 2),
    "Learning Block": ("Important, Not Urgent", 2),
    "Bots/Code": ("Important, Not Urgent", 2),
    "Blockchain/AI": ("Important, Not Urgent", 2),
    "Deep Learning Block": ("Important, Not Urgent", 2),
    "Research & Swing Plays": ("Urgent & Important", 1),
    "Swing Trading": ("Urgent & Important", 1),
    "Bullradar Development": ("Important, Not Urgent", 2),
    "Interstellarswaphub": ("Important, Not Urgent", 2),
    "Financial Strategy": ("Important, Not Urgent", 2),
    "Network & Influence": ("Important, Not Urgent", 2),
    "Strategic Work": ("Important, Not Urgent", 2),
    "Leverage Expansion": ("Important, Not Urgent", 2),
    "Second Order Research": ("Important, Not Urgent", 2),
    "AI & Automation Integration": ("Important, Not Urgent", 2),
    "Strategic Reflection & Recalibration": ("Important, Not Urgent", 2),
    "Volatility Plays": ("Urgent & Important", 1),
    "Trading Volatility": ("Urgent & Important", 1),
    "Meta Skill Building": ("Important, Not Urgent", 2),
    "Evening Dev": ("Important, Not Urgent", 2),
    "Lunch": ("Important, Not Urgent", 2),
    "Dinner & Social Connection": ("Important, Not Urgent", 2),
    "Dinner": ("Important, Not Urgent", 2),
    "Big Breakfast": ("Important, Not Urgent", 2),
    "Evening Wind-Down": ("Not Urgent, Not Important", 4),
    "Evening Celebration Relaxation": ("Not Urgent, Not Important", 4),
    "Evening Wind-Down & Journaling": ("Not Urgent, Not Important", 4),
    "Journaling": ("Important, Not Urgent", 2),
    "Journaling & Gratitude": ("Important, Not Urgent", 2),
    "Journaling & Wind-Down": ("Important, Not Urgent", 2),
    "Final Prep & Lights Out": ("Not Urgent, Not Important", 4),
    "Meditation & Final Prep": ("Not Urgent, Not Important", 4),
    "Meditation & Lights Out": ("Not Urgent, Not Important", 4),
    "Final Wind-Down": ("Not Urgent, Not Important", 4),
    "Buffer / Lights Out": ("Not Urgent, Not Important", 4),
    "Lights Out": ("Not Urgent, Not Important", 4),
    "Sleep": ("Important, Not Urgent", 2),
    "Weekly Review & Spiritual Alignment": ("Important, Not Urgent", 2),
    "Morning Reflection & Reading": ("Important, Not Urgent", 2),
    "Rest & Recharge": ("Not Urgent, Not Important", 4),
    "Optional Moderate Workout": ("Important, Not Urgent", 2),
    "Chores & Errands": ("Important, Not Urgent", 2),
    "Chores & Light Errands": ("Important, Not Urgent", 2),
    "Free Time / Light Activity": ("Not Urgent, Not Important", 4),
    "Outdoor/Recharge Activity": ("Important, Not Urgent", 2),
    "Movie Night / Gaming / Social": ("Not Urgent, Not Important", 4),
    "Evening Planning": ("Important, Not Urgent", 2),
    "Bots/Code (Optional)": ("Important, Not Urgent", 2)
}

# Work blocks for hour tracking (Mon–Fri only)
WORK_BLOCKS = {
    "Morning Trading", "Live Trading", "Learning Block", "Bots/Code", "Blockchain/AI", "Deep Learning Block",
    "Research & Swing Plays", "Swing Trading", "Bullradar Development", "Interstellarswaphub",
    "Financial Strategy", "Network & Influence", "Strategic Work", "Leverage Expansion",
    "Second Order Research", "AI & Automation Integration", "Strategic Reflection & Recalibration",
    "Volatility Plays", "Trading Volatility", "Meta Skill Building", "Evening Dev"
}

@contextmanager
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("routine_tracker.db", check_same_thread=False)
        yield conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        asyncio.create_task(send_telegram_message(f"Database error: {e}"))
    finally:
        if conn:
            conn.close()

def init_db():
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS routine_tracker
                         (date TEXT, time_str TEXT, task TEXT, completed TEXT,
                          on_time INTEGER, adjustment TEXT, energy_level INTEGER,
                          details TEXT, PRIMARY KEY (date, time_str, task))''')
            c.execute('''CREATE TABLE IF NOT EXISTS todo_list
                         (date TEXT, task TEXT, completed INTEGER,
                          PRIMARY KEY (date, task))''')
            c.execute('''CREATE TABLE IF NOT EXISTS weekly_summary
                         (week_start TEXT PRIMARY KEY, total_hours REAL, completion_rate REAL,
                          avg_energy REAL, spiritual_reflections TEXT)''')
            c.execute("PRAGMA table_info(routine_tracker)")
            columns = [col[1] for col in c.fetchall()]
            if "details" not in columns:
                c.execute("ALTER TABLE routine_tracker ADD COLUMN details TEXT")
            conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to initialize database: {e}")
        asyncio.create_task(send_telegram_message(f"Failed to initialize database: {e}"))

def save_block_to_db(date: str, time_str: str, task: str, completed: str, on_time: bool, adjustment: str, energy_level: int, details: str):
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO routine_tracker
                         (date, time_str, task, completed, on_time, adjustment, energy_level, details)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (date, time_str, task, completed, int(on_time), adjustment, energy_level, details))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to save block: {e}")
        asyncio.create_task(send_telegram_message(f"Failed to save block: {e}"))

def save_todo_to_db(date: str, task: str, completed: bool = False):
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO todo_list
                         (date, task, completed)
                         VALUES (?, ?, ?)''',
                      (date, task, int(completed)))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to save todo: {e}")
        asyncio.create_task(send_telegram_message(f"Failed to save todo: {e}"))

def load_todo_list(date: str) -> List[Dict[str, any]]:
    todos = []
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT task, completed FROM todo_list WHERE date = ?", (date,))
            todos = [{"task": task, "completed": bool(completed)} for task, completed in c.fetchall()]
    except sqlite3.Error as e:
        print(f"Failed to load todos: {e}")
        asyncio.create_task(send_telegram_message(f"Failed to load todos: {e}"))
    return todos

def load_today_state(date: str, blocks: List[Tuple[str, str, str]]) -> Tuple[List[str], List[bool], List[str], List[Tuple[str, int]], List[str]]:
    completions = [None] * len(blocks)
    on_time = [False] * len(blocks)
    adjustments = ["None"] * len(blocks)
    energy_log = []
    details = [""] * len(blocks)
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT time_str, task, completed, on_time, adjustment, energy_level, details FROM routine_tracker WHERE date = ?", (date,))
            rows = c.fetchall()
            stored = {(row[0], row[1]): row for row in rows}
            for idx, (time_str, task, _) in enumerate(blocks):
                key = (time_str, task)
                if key in stored:
                    row = stored[key]
                    completions[idx] = row[2]
                    on_time[idx] = bool(row[3])
                    adjustments[idx] = row[4] or "None"
                    details[idx] = row[6] or ""
                    time_key = time_str.split(" – ")[0] if " – " in time_str else time_str
                    energy_log.append((time_key, row[5]))
    except sqlite3.Error as e:
        print(f"Failed to load state: {e}")
        asyncio.create_task(send_telegram_message(f"Failed to load state: {e}"))
    if energy_log:
        energy_log.sort(key=lambda x: datetime.datetime.strptime(x[0], "%I:%M %p").time() if "M" in x[0] else datetime.datetime.min.time())
    return completions, on_time, adjustments, energy_log, details

# In display_today_status – small improvement to avoid double "(Skipped)"
def display_today_status(completions: List[str], blocks: List[Tuple[str, str, str]], on_time: List[bool], adjustments: List[str], details: List[str]) -> str:
    msg = "Today's Routine Status:\n"
    now_time = datetime.datetime.now(EAT_TZ).time()
    for idx, (time_str, task, _) in enumerate(blocks):
        start, end = parse_block_time(time_str)
        is_past = end < now_time
        if completions[idx] is None:
            status = "Missed" if is_past else "Pending"
        elif completions[idx] == "Y":
            status = "Completed"
            if on_time[idx]:
                status += " (On Time)"
            elif adjustments[idx] != "None":
                status += f" ({adjustments[idx]})"
        else:
            adj = adjustments[idx]
            if adj == "None":
                adj = "Skipped"
            status = f"Skipped ({adj})"
        msg += f"{time_str} → {task}: {status}"
        if details[idx]:
            msg += f" | Details: {details[idx]}"
        msg += "\n"
    msg += "=" * 26
    return msg

def display_past_summary(blocks: List[Tuple[str, str, str]], completions: List[str], on_time: List[bool], adjustments: List[str], details: List[str], past_idx: int) -> str:
    if past_idx == 0:
        return ""
    msg = "\nPast Blocks Summary:\n"
    now_time = datetime.datetime.now(EAT_TZ).time()
    for idx in range(past_idx):
        time_str, task, _ = blocks[idx]
        if completions[idx] is None:
            status = "Missed"
        elif completions[idx] == "Y":
            status = "Completed (On Time)" if on_time[idx] else f"Completed ({adjustments[idx]})"
        else:
            status = f"Skipped ({adjustments[idx]})"
        msg += f"{time_str} → {task}: {status}"
        if details[idx]:
            msg += f" | Details: {details[idx]}"
        msg += "\n"
    msg += "=" * 26
    return msg

def display_todo_list(todos: List[Dict[str, any]]) -> str:
    if not todos:
        return "No to-do tasks today."
    msg = "Today's To-Do List:\n"
    for todo in todos:
        status = "✓" if todo.get("completed", False) else "⬜"
        msg += f"{status} {todo.get('task', 'Unknown task')}\n"
    return msg

async def prompt_todo_completion(date: str, todos: List[Dict[str, any]]) -> List[Dict[str, any]]:
    if not todos:
        return todos
    print("\n=== Mark To-Do Completion ===")
    await send_telegram_message("Mark To-Do Completion:")
    for todo in todos:
        if not todo.get("completed", False):
            while True:
                done = input(f"Completed '{todo.get('task', 'Unknown')}'? (Y/N): ").upper()
                if done in ["Y", "N"]:
                    break
                print("Enter Y or N")
            if done == "Y":
                save_todo_to_db(date, todo.get('task', 'Unknown'), True)
                todo["completed"] = True
                await send_telegram_message(f"✓ {todo.get('task', 'Unknown')}")
    return todos

async def prompt_todo_input(date: str) -> List[Dict[str, any]]:
    print(f"\n=== Add To-Do Tasks for {date} ===")
    await send_telegram_message(f"Add To-Do Tasks for {date}:")
    todos = []
    while True:
        task = input("Task (or Enter to finish): ").strip()
        if not task:
            break
        save_todo_to_db(date, task)
        todos.append({"task": task, "completed": False})
        await send_telegram_message(f"Added: {task}")
    return todos

def parse_time(time_str: str) -> datetime.time:
    try:
        return datetime.datetime.strptime(time_str.strip(), "%I:%M %p").time()
    except ValueError:
        try:
            return datetime.datetime.strptime(time_str.strip(), "%I:%M").time()
        except:
            return datetime.datetime.now(EAT_TZ).time()

def parse_block_time(block_time: str) -> Tuple[datetime.time, datetime.time]:
    block_time = block_time.strip()
    if " – " in block_time:
        start_str, end_str = block_time.split(" – ")
        return parse_time(start_str), parse_time(end_str)
    start = parse_time(block_time)
    end = (datetime.datetime.combine(datetime.date.today(), start) + datetime.timedelta(hours=1)).time()
    return start, end

def calculate_block_duration(start_time: datetime.time, end_time: datetime.time) -> float:
    start_dt = datetime.datetime.combine(datetime.date.today(), start_time)
    end_dt = datetime.datetime.combine(datetime.date.today(), end_time)
    if end_dt < start_dt:
        end_dt += datetime.timedelta(days=1)
    return (end_dt - start_dt).total_seconds() / 3600

def get_current_day_and_time() -> Tuple[str, datetime.datetime]:
    now = datetime.datetime.now(EAT_TZ)
    return now.strftime("%A"), now

async def send_telegram_message(message: str):
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
    except Exception as e:
        with open("routine_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now(EAT_TZ)}: Telegram error: {e}\n")

def log_block(day: str, block: Tuple[str, str, str], priority: str, energy_level: int, completed: str, adjustment: str, details: str):
    with open("routine_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now(EAT_TZ)} | {day} | {block[1]} | Priority: {priority} | Energy: {energy_level}/5 | Completed: {completed} | Adjustment: {adjustment} | Details: {details} | Notes: {block[2]}\n")

def save_weekly_summary(week_start: str, total_hours: float, completion_rate: float, avg_energy: float, spiritual_reflections: str):
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO weekly_summary
                         (week_start, total_hours, completion_rate, avg_energy, spiritual_reflections)
                         VALUES (?, ?, ?, ?, ?)''',
                      (week_start, total_hours, completion_rate, avg_energy, spiritual_reflections))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Weekly summary save error: {e}")

def get_weekly_stats(week_start: str) -> Tuple[float, float, float, str]:
    try:
        with db_connection() as conn:
            c = conn.cursor()
            end_date = (datetime.datetime.strptime(week_start, "%Y-%m-%d") + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            c.execute('''SELECT task, completed, time_str, date, energy_level, details 
                         FROM routine_tracker WHERE date >= ? AND date < ?''', (week_start, end_date))
            rows = c.fetchall()
            total_hours = completed_blocks = total_blocks = energy_sum = energy_count = 0
            reflections = ""
            for task, completed, time_str, date, energy, details in rows:
                total_blocks += 1
                if completed == "Y":
                    completed_blocks += 1
                    if task in WORK_BLOCKS and datetime.datetime.strptime(date, "%Y-%m-%d").weekday() < 5:
                        if " – " in time_str:
                            start_str, end_str = time_str.split(" – ")
                        else:
                            start_str = end_str = time_str
                        duration = calculate_block_duration(parse_time(start_str), parse_time(end_str))
                        total_hours += duration
                if energy:
                    energy_sum += energy
                    energy_count += 1
                if any(k in task for k in ["Journaling", "Reflection", "Gratitude"]) or "gratitude" in details.lower():
                    reflections += f"{date}: {details}\n"
            completion_rate = completed_blocks / total_blocks if total_blocks else 0
            avg_energy = energy_sum / energy_count if energy_count else 0
            return total_hours, completion_rate, avg_energy, reflections
    except sqlite3.Error as e:
        print(f"Weekly stats error: {e}")
        return 0.0, 0.0, 0.0, ""

def get_stats(completions: List[str], on_time: List[bool], adjustments: List[str], energy_levels: List[int], todos: List[Dict], details: List[str], blocks: List[Tuple[str, str, str]]) -> str:
    total_blocks = len(completions)
    completed = sum(1 for c in completions if c == "Y")
    on_time_count = sum(on_time)
    work_hours = 0.0
    for idx, (time_str, task, _) in enumerate(blocks):
        if task in WORK_BLOCKS and completions[idx] == "Y":
            if " – " in time_str:
                start_str, end_str = time_str.split(" – ")
            else:
                start_str = end_str = time_str
            duration = calculate_block_duration(parse_time(start_str), parse_time(end_str))
            work_hours += duration
    todo_completed = sum(1 for t in todos if t["completed"])
    todo_total = len(todos)
    avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 0
    stats = (
        f"Daily Wrap:\n"
        f"• Blocks: {completed}/{total_blocks} ({completed/total_blocks*100:.0f}%)\n"
        f"• On Time: {on_time_count}/{completed}\n"
        f"• Work Hours: {work_hours:.1f}h\n"
        f"• To-Dos: {todo_completed}/{todo_total}\n"
        f"• Avg Energy: {avg_energy:.1f}/5\n"
    )
    return stats

def show_energy_graph(energy_log: List[Tuple[str, int]]) -> str:
    if not energy_log:
        return ""
    msg = "Energy Flow Today:\n"
    for time, level in energy_log:
        stars = "★" * level + "☆" * (5 - level)
        msg += f"{time}: {stars} ({level}/5)\n"
    return msg

def suggest_bedtime(wake_time: str, hours: float = 7.5) -> str:
    try:
        wake_dt = datetime.datetime.strptime(wake_time.strip(), "%I:%M %p")
        bed_dt = wake_dt - datetime.timedelta(hours=hours)
        return bed_dt.strftime("%I:%M %p")
    except:
        return "9:00 PM"

def is_end_of_week(day: str) -> bool:
    return day == "Sunday"

def is_end_of_month() -> bool:
    today = datetime.datetime.now(EAT_TZ)
    tomorrow = today + datetime.timedelta(days=1)
    return today.month != tomorrow.month

async def manage_routine():
    init_db()
    last_block = None
    day, now = get_current_day_and_time()
    today = now.strftime("%Y-%m-%d")
    next_day = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # Starting energy
    while True:
        try:
            energy_input = input("Starting energy (1-5, Enter for 3): ") or "3"
            start_energy = int(energy_input)
            if 1 <= start_energy <= 5:
                break
            print("Enter 1–5")
        except ValueError:
            print("Enter 1–5")
    energy_level = "energized" if start_energy >= 4 else "tired" if start_energy <= 2 else "in between"
    await send_telegram_message(f"Starting Energy: {start_energy}/5 ({energy_level})")

    # Sleep tracking
    while True:
        try:
            sleep_hours = float(input("Hours slept last night? (e.g. 7): ") or "7")
            target_sleep = float(input("Target sleep tonight? (e.g. 7.5): ") or "7.5")
            break
        except ValueError:
            print("Enter a number")

    wake_time = routines[day]["blocks"][0][0].split(" – ")[0] if day in routines and routines[day]["blocks"] and " – " in routines[day]["blocks"][0][0] else "6:00 AM"
    bedtime = suggest_bedtime(wake_time, target_sleep)
    await send_telegram_message(f"Slept: {sleep_hours}h\nBedtime suggestion: {bedtime}")

    # To-do list – always load from DB first
    todos = load_todo_list(today)
    if not todos:
        todos = await prompt_todo_input(today)
        todos = load_todo_list(today)  # Reload to ensure consistency
    await send_telegram_message(display_todo_list(todos))
    print(display_todo_list(todos))

    # Load state and show today's status + past summary at startup
    if day in routines:
        blocks = routines[day]["blocks"]
        completions, on_time, adjustments, energy_log, details = load_today_state(today, blocks)
        if not energy_log and blocks:
            first_time = blocks[0][0].split(" – ")[0] if " – " in blocks[0][0] else blocks[0][0]
            energy_log = [(first_time, start_energy)]

        status_msg = display_today_status(completions, blocks, on_time, adjustments, details)
        print("\n" + status_msg)
        await send_telegram_message(status_msg)

        # Past summary at startup
        now_time = datetime.datetime.now(EAT_TZ).time()
        past_idx = 0
        for i, block in enumerate(blocks):
            _, end = parse_block_time(block[0])
            if end >= now_time:
                break
            past_idx = i + 1
        past_summary = display_past_summary(blocks, completions, on_time, adjustments, details, past_idx)
        if past_summary:
            print(past_summary)
            await send_telegram_message(past_summary)

    while True:
        day, now = get_current_day_and_time()
        today = now.strftime("%Y-%m-%d")
        if day not in routines:
            await asyncio.sleep(60)
            continue
        vibe = routines[day]["vibe"]
        blocks = routines[day]["blocks"]

        # Initialize if new day
        if not completions:
            completions = [None] * len(blocks)
            on_time = [False] * len(blocks)
            adjustments = ["None"] * len(blocks)
            details = [""] * len(blocks)
            first_time = blocks[0][0].split(" – ")[0] if " – " in blocks[0][0] else blocks[0][0]
            energy_log = [(first_time, start_energy)]

        for idx, block in enumerate(blocks):
            block_time, task, notes = block
            start_time, end_time = parse_block_time(block_time)
            now_time = now.time()

            # Allow up to 30 min grace period for marking
            grace_end = (datetime.datetime.combine(datetime.date.today(), end_time) + datetime.timedelta(minutes=30)).time()
            if start_time <= now_time <= grace_end and block != last_block and completions[idx] is None:
                # Send updated past summary at natural milestones (Lunch, Dinner, Journaling)
                if any(k in task for k in ["Lunch", "Dinner", "Journaling"]):
                    # Recalculate how many blocks are fully past
                    current_past_idx = 0
                    for i in range(len(blocks)):
                        _, block_end = parse_block_time(blocks[i][0])
                        if block_end < now_time:
                            current_past_idx = i + 1
                        else:
                            break
                    past_msg = display_past_summary(blocks, completions, on_time, adjustments, details, current_past_idx)
                    if past_msg:
                        print("\n" + past_msg)
                        await send_telegram_message(past_msg)

                # Block notification (unchanged)
                priority, _ = TASK_PRIORITIES.get(task, ("Unknown", 3))
                tweak = random.choice(vibe_tweaks[energy_level])
                challenge = random.choice(micro_challenges) if random.random() < 0.4 else ""
                quote = random.choice(motivational_quotes)
                msg = (
                    f"*{day} {block_time}*\n"
                    f"**Task**: {task} (Priority: {priority})\n"
                    f"**Vibe**: {vibe}\n"
                    f"**Notes**: {notes}\n"
                    f"**Energy**: {energy_level} → {tweak}\n"
                    f"**Quote**: {quote}"
                )
                if challenge:
                    msg += f"\n**Challenge**: {challenge}"
                if any(k in task for k in ["Journaling", "Meditation", "Prime", "Gratitude", "Prayer"]):
                    msg += "\n🙏 **Spiritual**: Reflect on God's guidance."
                await send_telegram_message(msg)
                print(msg.replace("**", "").replace("*", ""))

                # Completion prompt
                while True:
                    done = input(f"\nDone with '{task}'? (Y/N): ").upper()
                    if done in ["Y", "N"]:
                        break
                    print("Enter Y or N")

                completions[idx] = done

                # Adjustment prompt
                delay_min = 0
                completion_time = datetime.datetime.now(EAT_TZ)
                end_dt = datetime.datetime.combine(completion_time.date(), end_time, tzinfo=EAT_TZ)
                if completion_time > end_dt:
                    delay_min = int((completion_time - end_dt).total_seconds() / 60)

                if done == "Y":
                    default_adj = "On Time" if delay_min == 0 else f"Delayed {delay_min} min"
                    adj_input = input(f"Adjustment? (on_time/delayed/extended/shortened, default: {default_adj}): ").strip().lower() or default_adj.lower()
                else:
                    adj_input = input("Adjustment? (skipped/postponed/shortened/delayed): ").strip().lower() or "skipped"
                adjustment = adj_input.capitalize()
                adjustments[idx] = adjustment
                on_time[idx] = adj_input in ["on_time", "extended", "shortened"]

                # Energy prompt
                while True:
                    try:
                        energy_int = int(input("Energy now (1-5): "))
                        if 1 <= energy_int <= 5:
                            break
                        print("Enter 1–5")
                    except ValueError:
                        print("Enter 1–5")
                energy_level = "energized" if energy_int >= 4 else "tired" if energy_int <= 2 else "in between"

                time_key = block_time.split(" – ")[0] if " – " in block_time else block_time
                energy_log = [e for e in energy_log if e[0] != time_key]
                energy_log.append((time_key, energy_int))

                # Details prompts
                block_details = input(f"Details for '{task}' (optional): ").strip() or "No details"
                if any(k in task for k in ["Journaling", "Meditation", "Prime", "Gratitude"]):
                    spiritual = input("Spiritual note? (optional): ").strip()
                    if spiritual:
                        block_details += f" | Spiritual: {spiritual}"
                if done == "N" or "delay" in adj_input or "postpon" in adj_input:
                    reason = input("Reason/alternative activity? (optional): ").strip() or "No reason"
                    block_details += f" | Reason: {reason}"
                details[idx] = block_details

                # Save to DB and log
                save_block_to_db(today, block_time, task, done, on_time[idx], adjustment, energy_int, block_details)
                log_block(day, block, priority, energy_int, done, adjustment, block_details)

                # Journaling-specific actions
                if "Journaling" in task:
                    await send_telegram_message(display_todo_list(todos))
                    todos = await prompt_todo_completion(today, todos)
                    await prompt_todo_input(next_day)
                    todos = load_todo_list(today)

                    if is_end_of_week(day) and is_end_of_month():
                        reflection = input("Quarterly Horizons reflection? (optional): ").strip() or "None"
                        await send_telegram_message(f"Quarterly Horizons: {reflection}")

                # Sleep tip
                if any(k in task for k in ["Wind-Down", "Lights Out", "Meditation", "Final Prep", "Planning"]):
                    await send_telegram_message(f"Sleep Tip: {random.choice(sleep_tips)}")

                last_block = block

        # End-of-day wrap
        if now.hour >= 20 and all(c is not None for c in completions):
            energy_levels = [e[1] for e in energy_log]
            stats = get_stats(completions, on_time, adjustments, energy_levels, todos, details, blocks)
            energy_graph = show_energy_graph(energy_log)
            wrap_msg = f"{random.choice(tweaks)}\n\n{stats}\n{energy_graph}\n{random.choice(motivational_quotes)}"
            print("\n" + wrap_msg)
            await send_telegram_message(wrap_msg)

            if is_end_of_week(day):
                week_start = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")
                hours, rate, energy, reflections = get_weekly_stats(week_start)
                note = "On target" if 40 <= hours <= 45 else f"Aim 40–45h (current {hours:.1f}h)"
                weekly = (
                    f"*Weekly Summary ({week_start})*\n"
                    f"• Work Hours: {hours:.1f}h — {note}\n"
                    f"• Completion: {rate*100:.0f}%\n"
                    f"• Avg Energy: {energy:.1f}/5\n"
                    f"• Reflections:\n{reflections or 'None'}"
                )
                print("\n" + weekly)
                await send_telegram_message(weekly)
                save_weekly_summary(week_start, hours, rate, energy, reflections)

            # Reset for next day
            completions = on_time = adjustments = energy_log = details = []
            last_block = None

        await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(manage_routine())
    except KeyboardInterrupt:
        print("\nRoutine stopped. All data saved.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        with open("routine_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now(EAT_TZ)}: Unexpected error: {e}\n")