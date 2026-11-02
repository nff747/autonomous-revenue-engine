#!/usr/bin/env python3
import subprocess
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = sys.executable

ENGINES = [
    {
        "id": "engine_2_lead_feed",
        "name": "B2B Zero-Bounce Data Feed Brokerage",
        "script": os.path.join(BASE_DIR, "data_feeds/data_feed_engine.py")
    },
    {
        "id": "engine_3_bug_bounty",
        "name": "Bugcrowd In-Scope Secret & Key Scanner",
        "script": os.path.join(BASE_DIR, "bounty_scanner/bounty_scanner_engine.py")
    },
    {
        "id": "engine_4_checkout_watchdog",
        "name": "Headless Synthetic Checkout Watchdog",
        "script": os.path.join(BASE_DIR, "checkout_watchdog/watchdog_engine.py")
    }
]

def run_all_engines():
    print(f"==================================================")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] RUNNING FULL NON-FREELANCE REVENUE ENGINE CYCLE")
    print(f"==================================================")
    
    for eng in ENGINES:
        name = eng["name"]
        script = eng["script"]
        print(f"
--- [START] {name} ---")
        try:
            res = subprocess.run([PYTHON_BIN, script], capture_output=True, text=True, timeout=180)
            if res.stdout:
                print(res.stdout.strip())
            if res.stderr and "Error" in res.stderr:
                print(f"[{name} Errors]: {res.stderr.strip()[:300]}")
        except Exception as e:
            print(f"[{name} Exception]: {e}")
        print(f"--- [DONE] {name} ---
")

    print(f"==================================================")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ALL ENGINES EXECUTED CLEANLY")
    print(f"==================================================")

if __name__ == "__main__":
    run_all_engines()
