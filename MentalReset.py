import time
import os

def clear_screen():
    """Clear the console screen for a fresh display."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause_and_step_away():
    """Step 1: Pause and Step Away (2-5 minutes)."""
    clear_screen()
    print("Step 1: Pause and Step Away")
    print("Close your trading platform or step away from your screen.")
    print("Move to a different space (another room or outside) to break the stress cycle.")
    duration = 2 * 60  # 2 minutes
    print(f"Pausing for {duration//60} minutes. Take this time to step away.")
    time.sleep(duration)
    print("Time's up! Ready for the next step.")

def breathe_deeply():
    """Step 2: Breathe Deeply with Intention (1-2 minutes)."""
    clear_screen()
    print("Step 2: Breathe Deeply with Intention")
    print("Follow this breathing exercise: Inhale for 4s, hold for 4s, exhale for 6s. Repeat 5-10 times.")
    for i in range(5):  # 5 cycles
        print(f"Cycle {i+1}: Inhale (4s)...")
        time.sleep(4)
        print("Hold (4s)...")
        time.sleep(4)
        print("Exhale (6s)...")
        time.sleep(6)
    print("Breathing exercise complete! Feel calmer? Let's move on.")

def acknowledge_emotions():
    """Step 3: Acknowledge and Release Emotions (1-2 minutes)."""
    clear_screen()
    print("Step 3: Acknowledge and Release Emotions")
    print("Write down or type what you're feeling (e.g., frustration, doubt). No judgment.")
    emotions = input("Type your emotions here (or type 'skip' to move on): ")
    if emotions.lower() != 'skip':
        print(f"You wrote: {emotions}")
        print("Now, release these emotions. Say 'I let this go' or visualize them dissolving.")
        time.sleep(10)  # Brief pause to reflect
    else:
        print("Skipping emotion input.")
    print("Emotions acknowledged. Ready for the next step.")

def reframe_streak():
    """Step 4: Reframe the Streak (2-3 minutes)."""
    clear_screen()
    print("Step 4: Reframe the Streak")
    print("Reflect on the losing streak as data, not failure.")
    print("Ask yourself: 'What can I learn from this?'")
    insight = input("Type one actionable insight (e.g., 'I overtraded during volatility'): ")
    if insight.strip():
        print(f"Insight noted: {insight}")
    else:
        print("No insight provided. That's okay, let's continue.")
    time.sleep(10)  # Brief pause to reflect
    print("Mindset shifted. On to the next step!")

def physical_reset():
    """Step 5: Physical Reset (1-2 minutes)."""
    clear_screen()
    print("Step 5: Physical Reset")
    print("Do a quick physical activity: stretch, shake out your arms/legs, or do 10 jumping jacks.")
    print("Starting 1-minute timer for your activity...")
    time.sleep(60)
    print("Physical reset complete! Feeling energized? Let's move forward.")

def affirm_strategy():
    """Step 6: Affirm Your Strategy (1-2 minutes)."""
    clear_screen()
    print("Step 6: Affirm Your Strategy")
    print("Revisit your core strategy or principles (e.g., trading plan, risk management rules).")
    affirmation = input("Type a short affirmation (e.g., 'I stick to my plan, and losses are part of the process') or 'skip': ")
    if affirmation.lower() != 'skip':
        print(f"Affirmation: {affirmation}")
    else:
        print("Using default affirmation: 'I stick to my plan, and losses are part of the process.'")
    time.sleep(10)  # Brief pause to reflect
    print("Confidence reinforced. Almost done!")

def reengage():
    """Step 7: Re-engage with a Clear Signal (1 minute)."""
    clear_screen()
    print("Step 7: Re-engage with a Clear Signal")
    print("Choose a deliberate action (e.g., drink water, set a timer).")
    print("Only resume trading when you feel calm and focused.")
    action = input("Type your chosen action (e.g., 'drink water') or 'skip': ")
    if action.lower() != 'skip':
        print(f"Action chosen: {action}")
    else:
        print("No action specified. That's okay.")
    print("Take a moment to ensure you're calm and focused.")
    time.sleep(30)  # 30-second pause
    print("You're ready to re-engage. Good luck!")

def main():
    """Run the reset bot process."""
    print("Welcome to the Losing Streak Reset Bot")
    print("Follow the steps to reset your mindset and approach.")
    input("Press Enter to start the reset process...")
    
    steps = [
        pause_and_step_away,
        breathe_deeply,
        acknowledge_emotions,
        reframe_streak,
        physical_reset,
        affirm_strategy,
        reengage
    ]
    
    for step in steps:
        step()
        input("Press Enter to continue to the next step...")
    
    clear_screen()
    print("Reset process complete! You're now ready to proceed with a clear mind.")

if __name__ == "__main__":
    main()