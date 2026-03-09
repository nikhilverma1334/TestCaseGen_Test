import time
import schedule
import subprocess
import os
import sys
from datetime import datetime
import pytz

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

def job():
    print(f"\n--- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Triggering Daily Automation ---")
    try:
        # Run the master orchestrator
        result = subprocess.run(["python", "tools/pilot_orchestrator.py"], capture_output=True, text=True, encoding="utf-8")
        print(result.stdout.encode('ascii', errors='ignore').decode('ascii'))
        if result.returncode != 0:
            print("ERROR: Automation failed.")
            print(result.stderr.encode('ascii', errors='ignore').decode('ascii'))
    except Exception as e:
        print(f"EXCEPTION: {e}")

def run_scheduler():
    # Set timezone to IST
    ist = pytz.timezone('Asia/Kolkata')
    
    # Schedule daily at 09:00 IST
    # Note: schedule library uses local system time. If your PC is already in IST, this works directly.
    schedule.every().day.at("09:00").do(job)
    
    print("--------------------------------------------------")
    print("      🚀 QA PILOT LOCAL SCHEDULER ARMED 🚀        ")
    print(f" Target: Daily at 09:00 AM IST")
    print(f" Current Local Time: {datetime.now().strftime('%H:%M:%S')}")
    print(" Status: WAITING... (Keep this window open)")
    print("--------------------------------------------------")

    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute

if __name__ == "__main__":
    # Ensure dependencies are installed
    try:
        import schedule
        import pytz
    except ImportError:
        print("Installing required scheduling libraries...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule", "pytz"])
    
    run_scheduler()
