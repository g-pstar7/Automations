import random
import datetime
import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7397010047:AAEnGgvsUuGdXY9sMiQkw54BC2zlH6Yip5E"
TELEGRAM_CHAT_ID = "5932647180"

def send_to_telegram(message):
    """Send a message to your Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram Error:", e)

# Workout plan dictionary with all days
WORKOUT_PLAN = {
    "Monday": {
        "name": "Upper Body (Push: Chest, Shoulders, Triceps)",
        "exercises": [
            {"name": "Resistance Band Push-ups", "sets": 4, "reps": 12},
            {"name": "Pike Push-ups", "sets": 3, "reps": "10-12"},
            {"name": "Dips (Weighted Backpack)", "sets": 3, "reps": "10-12"},
            {"name": "Triceps Extensions", "sets": 3, "reps": "12-15"},
            {"name": "Plank Hold (Backpack)", "sets": 3, "reps": "30 sec"}
        ],
        "variations": {
            "Pike Push-ups": ["Overhead Band Press", "Handstand Hold"],
            "Triceps Extensions": ["Band Overhead Extensions", "Close-Grip Push-ups"]
        },
        "music": [
            "The Weeknd - Blinding Lights",
            "Drake - One Dance",
            "Post Malone - Circles"
        ]
    },
    "Tuesday": {
        "name": "Lower Body (Legs & Glutes)",
        "exercises": [
            {"name": "Bulgarian Split Squats", "sets": 4, "reps": "10-12"},
            {"name": "Wall Sit (Backpack)", "sets": 3, "reps": "45 sec"},
            {"name": "Step-ups (Backpack)", "sets": 3, "reps": "12"},
            {"name": "Glute Bridges (Band & Backpack)", "sets": 4, "reps": "12-15"},
            {"name": "Calf Raises (Backpack)", "sets": 3, "reps": "15"}
        ],
        "variations": {
            "Bulgarian Split Squats": ["Lunges (Backpack)", "Single-Leg Glute Bridges"],
            "Step-ups": ["Box Jumps", "Lateral Step-ups"]
        },
        "music": [
            "Dua Lipa - Don't Start Now",
            "Calvin Harris - Feel So Close",
            "Tame Impala - The Less I Know The Better"
        ]
    },
    "Wednesday": {
        "name": "Back & Biceps",
        "exercises": [
            {"name": "Pull-ups (Weighted Backpack)", "sets": 3, "reps": "8-12"},
            {"name": "Backpack Rows", "sets": 3, "reps": "12-15"},
            {"name": "Biceps Curls (Band or Backpack)", "sets": 3, "reps": "12-15"},
            {"name": "Superman Holds (Backpack)", "sets": 3, "reps": "30 sec"}
        ],
        "variations": {
            "Backpack Rows": ["Bent-Over Band Rows", "Single-Arm Backpack Rows"],
            "Biceps Curls": ["Hammer Curls (Band)", "Isometric Bicep Hold"]
        },
        "music": [
            "Kanye West - Stronger",
            "Eminem - Lose Yourself",
            "J. Cole - No Role Modelz"
        ]
    },
    "Thursday": {
        "name": "Core & Stability",
        "exercises": [
            {"name": "Hanging Leg Raises", "sets": 3, "reps": "12"},
            {"name": "Bicycle Crunches", "sets": 3, "reps": "20"},
            {"name": "Planks (Weighted Backpack)", "sets": 3, "reps": "1 min"},
            {"name": "Russian Twists (Band or Backpack)", "sets": 3, "reps": "20"}
        ],
        "variations": {
            "Hanging Leg Raises": ["Lying Leg Raises (Backpack)", "Knee Tucks"],
            "Russian Twists": ["Side Planks", "Band Woodchoppers"]
        },
        "music": [
            "Chillhop - Lo-Fi Beats",
            "ODESZA - A Moment Apart",
            "Bon Iver - Holocene"
        ]
    },
    "Friday": {
        "name": "Full Body (Power & Explosiveness)",
        "exercises": [
            {"name": "Jump Squats (Backpack or Band)", "sets": 3, "reps": "12"},
            {"name": "Burpees", "sets": 3, "reps": "10"},
            {"name": "Resistance Band Push-ups", "sets": 3, "reps": "15-20"},
            {"name": "Backpack Thrusters", "sets": 3, "reps": "12"}
        ],
        "variations": {
            "Jump Squats": ["Explosive Lunges", "Band Squat Jumps"],
            "Burpees": ["Mountain Climbers", "High Knees"]
        },
        "music": [
            "Skrillex - Bangarang",
            "The Chainsmokers - Closer",
            "Imagine Dragons - Thunder"
        ]
    },
    "Saturday": {
        "name": "Beach Day & Active Recovery",
        "exercises": [
            {"name": "Mobility & Stretching (Yoga)", "sets": 1, "reps": "20 min"},
            {"name": "Beach Activity", "sets": 1, "reps": "2 hours"}
        ],
        "variations": {
            "Beach Activity": ["Beach Yoga", "Sand Sprints", "Bodyweight Circuit"]
        },
        "music": [
            "Marconi Union - Weightless",
            "Jack Johnson - Better Together",
            "Yiruma - River Flows in You"
        ]
    },
    "Sunday": {
        "name": "Weak Points Focus + Beach Time",
        "exercises": [
            {"name": "Weak Point Exercise (User Choice)", "sets": 3, "reps": "10-12"},
            {"name": "Beach Activity", "sets": 1, "reps": "2 hours"}
        ],
        "variations": {
            "Weak Point Exercise": ["Band Flyes (Chest)", "Extra Pull-ups (Back)", "Single-Leg Squats (Legs)"],
            "Beach Activity": ["Light Swim", "Beach Meditation", "Sand Burpees"]
        },
        "music": [
            "Debussy - Clair de Lune",
            "Bob Marley - Three Little Birds",
            "Tycho - Awake"
        ]
    }
}

MOTIVATIONAL_QUOTES = [
    "Push through the resistance, you're stronger than you think!",
    "Every rep is a step toward your beach-ready self!",
    "Your backpack is heavy, but your will is heavier!",
    "Sweat today, shine on the beach tomorrow!",
    "Crush the workout, own the shore!"
]

BEACH_ACTIVITIES = [
    "20-min Beach Yoga Session",
    "10 Sand Sprints (30 sec each)",
    "Light Swim for 30 min",
    "Bodyweight Circuit (10 Push-ups, 10 Squats, 10 Sit-ups)",
    "Build a sandcastle for Grip Strength",
    "Sunset Beach Walk with Deep Breaths"
]

REWARD_QUOTES = [
    "You're carving strength like waves shape the shore!",
    "Each rep is a star in your fitness constellation!",
    "Your grit shines brighter than the beach at noon!"
]

REWARD_SONGS = [
    "Tycho - Awake",
    "Petit Biscuit - Sunset Lover",
    "Flume - Never Be Like You"
]

BADGE_CHALLENGES = [
    "Add 5 extra reps to one exercise tomorrow!",
    "Hold your plank 10 seconds longer next time!",
    "Try a new variation for one exercise!"
]

LOG_FILE = "workout_log.txt"
BADGE_FILE = "badge_progress.json"
ENERGY_LOG_FILE = "energy_log.json"

def create_badge_image(badge_name):
    """Create a simple badge image with Pillow."""
    img = Image.new('RGB', (200, 200), color=(0, 105, 148))  # Blue background
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.text((10, 80), badge_name, fill=(255, 255, 255), font=font)
    draw.text((10, 120), "🌴🦡", fill=(255, 255, 255), font=font)
    img.save(f"{badge_name.lower().replace(' ', '_')}.png")

def display_ascii_badge(badge_name):
    """Display an ASCII-art badge."""
    ascii_art = """
    🌴🦡🌴
   /  ***  \\
  /_________\\
  |  {}  |
  |  Earned!  |
  \\_________/
    """.format(badge_name.center(10))
    print(ascii_art)
    return ascii_art

def update_badge_progress(points_earned, badge_name, feedback, energy):
    """Update badge progress in JSON file."""
    badge_data = {"total_points": 0, "badges_earned": [], "energy_logs": []}
    if os.path.exists(BADGE_FILE):
        with open(BADGE_FILE, "r") as f:
            badge_data = json.load(f)
    
    badge_data["total_points"] += points_earned
    if badge_name and badge_name not in badge_data["badges_earned"]:
        badge_data["badges_earned"].append(badge_name)
    
    badge_data["energy_logs"].append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "energy": energy,
        "feedback": feedback,
        "points_earned": points_earned
    })
    
    with open(BADGE_FILE, "w") as f:
        json.dump(badge_data, f, indent=2)
    
    return badge_data["total_points"]

def check_badge_milestone(total_points):
    """Check if a badge milestone is reached."""
    badges = [
        {"name": "Beach Badger", "points": 50},
        {"name": "Coastal Conqueror", "points": 100},
        {"name": "Starlit Spartan", "points": 200}
    ]
    for badge in badges:
        if total_points >= badge["points"]:
            return badge["name"]
    return None

def get_next_badge_points(total_points):
    """Get points needed for the next badge."""
    badges = [
        {"name": "Beach Badger", "points": 50},
        {"name": "Coastal Conqueror", "points": 100},
        {"name": "Starlit Spartan", "points": 200}
    ]
    for badge in badges:
        if total_points < badge["points"]:
            return badge["name"], badge["points"]
    return "Legend of the Shore", 300  # Default next milestone

def analyze_energy_correlation():
    """Analyze energy and feedback correlation."""
    if not os.path.exists(BADGE_FILE):
        return "No energy data yet!"
    
    with open(BADGE_FILE, "r") as f:
        badge_data = json.load(f)
    
    energy_counts = {"low": 0, "medium": 0, "high": 0}
    feedback_counts = {"tough": 0, "great": 0, "easy": 0}
    tough_high_energy = 0
    total_logs = len(badge_data["energy_logs"])
    
    for log in badge_data["energy_logs"]:
        energy_counts[log["energy"]] += 1
        feedback_counts[log["feedback"]] += 1
        if log["feedback"] == "tough" and log["energy"] == "high":
            tough_high_energy += 1
    
    if total_logs == 0:
        return "No energy data yet!"
    
    summary = f"Energy Trends ({total_logs} workouts):\n"
    summary += f"- Low Energy: {energy_counts['low']} ({energy_counts['low']/total_logs*100:.1f}%)\n"
    summary += f"- Medium Energy: {energy_counts['medium']} ({energy_counts['medium']/total_logs*100:.1f}%)\n"
    summary += f"- High Energy: {energy_counts['high']} ({energy_counts['high']/total_logs*100:.1f}%)\n"
    if energy_counts['high'] > 0:
        summary += f"- Tough Workouts with High Energy: {tough_high_energy} ({tough_high_energy/energy_counts['high']*100:.1f}% of high-energy days)\n"
    else:
        summary += f"- Tough Workouts with High Energy: {tough_high_energy} (No high-energy days yet)\n"
    
    if tough_high_energy / total_logs > 0.3:
        summary += "💡 Tip: You often push through tough workouts with high energy—keep fueling up!"
    elif energy_counts["low"] / total_logs > 0.4:
        summary += "💡 Tip: Low energy is common—try a lighter variation or extra rest!"
    
    return summary

def get_user_input():
    print("\n🌊 Welcome to Your BeachFit Workout Bot! 🌴")
    energy = input("Energy level (low/medium/high): ").lower()
    soreness = input("Any sore areas (e.g., arms, legs, none)? ").lower()
    focus = input("Focus area (e.g., chest, legs, weak point, none)? ").lower()
    if focus == "weak point":
        focus = input("Specify weak point (e.g., chest, back, legs): ").lower()
    return energy, soreness, focus

def adjust_workout(day_plan, energy, soreness, focus):
    adjusted_plan = day_plan.copy()
    if energy == "low":
        for exercise in adjusted_plan["exercises"]:
            exercise["sets"] = max(2, exercise["sets"] - 1)
    if soreness == "arms" and "Upper Body" in day_plan["name"]:
        adjusted_plan["exercises"] = [
            ex for ex in adjusted_plan["exercises"] if "Triceps" not in ex["name"] and "Biceps" not in ex["name"]
        ]
    if soreness == "legs" and "Lower Body" in day_plan["name"]:
        adjusted_plan["exercises"] = [
            ex for ex in adjusted_plan["exercises"] if "Squats" not in ex["name"] and "Step-ups" not in ex["name"]
        ]
    if focus not in ["none", "weak point"]:
        adjusted_plan["exercises"].append(
            {"name": f"Extra {focus.capitalize()} Exercise", "sets": 2, "reps": "10-12"}
        )
    return adjusted_plan

def add_variation(day_plan):
    for exercise in day_plan["exercises"]:
        if exercise["name"] in day_plan.get("variations", {}):
            variations = day_plan["variations"][exercise["name"]]
            if random.random() < 0.3:
                exercise["name"] = random.choice(variations)
        if exercise["name"] == "Beach Activity":
            exercise["name"] = random.choice(BEACH_ACTIVITIES)
    return day_plan

def log_workout(day, plan, feedback, beach_points, energy):
    with open(LOG_FILE, "a") as f:
        f.write(f"\n{datetime.datetime.now()}\n")
        f.write(f"Day: {day} ({plan['name']})\n")
        for ex in plan["exercises"]:
            f.write(f"- {ex['name']}: {ex['sets']}x{ex['reps']}\n")
        f.write(f"Feedback: {feedback}\n")
        f.write(f"Energy: {energy}\n")
        f.write(f"Beach Points Earned: {beach_points}\n")

def display_workout(day, plan):
    print(f"\n🏋️‍♂️ {day}: {plan['name']} 🏋️‍♂️")
    workout_summary = f"{day} Workout - {plan['name']}\n"
    for ex in plan["exercises"]:
        line = f"- {ex['name']}: {ex['sets']} sets x {ex['reps']}"
        print(line)
        workout_summary += line + "\n"
    print("\n🎵 Playlist:")
    for song in plan["music"]:
        print(f"- {song}")
        workout_summary += f"♪ {song}\n"
    motivation = random.choice(MOTIVATIONAL_QUOTES)
    print(f"\n💪 {motivation}")
    workout_summary += f"\n💪 {motivation}"
    return workout_summary

def main():
    today = datetime.datetime.now().strftime("%A")
    if today not in WORKOUT_PLAN:
        print("No workout scheduled today!")
        return

    energy, soreness, focus = get_user_input()
    day_plan = adjust_workout(WORKOUT_PLAN[today], energy, soreness, focus)
    day_plan = add_variation(day_plan)
    summary = display_workout(today, day_plan)

    feedback = input("\nHow did the workout feel (e.g., tough, great, easy)? ")
    beach_points = 10 if feedback else 5
    log_workout(today, day_plan, feedback, beach_points, energy)
    print(f"\n🌟 Workout logged! Earned {beach_points} Beach Points! 🌴")

    # Update badge progress
    total_points = update_badge_progress(beach_points, None, feedback, energy)
    badge_name = check_badge_milestone(total_points)
    
    telegram_message = f"🏋️‍♂️ {summary}\nFeedback: {feedback}\nEnergy: {energy}\nBeach Points: {beach_points}"
    
    if badge_name:
        ascii_badge = display_ascii_badge(badge_name)
        create_badge_image(badge_name)
        print(f"🎉 Milestone! Unlocked '{badge_name}' Badge!")
        reward = random.choice(REWARD_QUOTES + REWARD_SONGS)
        challenge = random.choice(BADGE_CHALLENGES)
        print(f"🏆 Reward Unlocked: {reward}")
        print(f"🌟 Next Challenge: {challenge}")
        update_badge_progress(0, badge_name, feedback, energy)  # Log badge
        telegram_message += f"\n🎉 Unlocked '{badge_name}' Badge!\n{ascii_badge}\nReward: {reward}\nChallenge: {challenge}"
    
    # Energy correlation feedback
    energy_summary = analyze_energy_correlation()
    print(f"\n📊 {energy_summary}")
    telegram_message += f"\n📊 {energy_summary}"
    
    # Send to Telegram
    send_to_telegram(telegram_message)
    
    # Display progress
    print(f"\n🏖️ Total Beach Points: {total_points}")
    next_badge, next_points = get_next_badge_points(total_points)
    print(f"📈 Next Badge: '{next_badge}' ({next_points - total_points} points away)")

if __name__ == "__main__":
    main()