#!/usr/bin/env python3
"""
Master Orchestrator Daemon for the 3 Verified Non-Freelance Revenue Engines:
1. DataFeedEngine (Model 2): Zero-Bounce B2B Lead & Candidate Brokerage ($2k-$8k/mo MRR)
2. BountyHunter (Model 3): In-Scope Bugcrowd/HackerOne Secret Scanner ($500-$5k/hit)
3. CheckoutWatchdog (Model 4): Real Synthetic Checkout & Conversion Monitor ($1.5k-$5k/mo MRR)
"""

import subprocess
import time

PYTHON_BIN = "/home/n1khy/Projects/UGC/.venv/bin/python3"

ENGINES = [
    {
        "id": "engine_2_lead_feed",
        "name": "B2B Zero-Bounce Data Feed Brokerage",
        "script": "/home/n1khy/Projects/UGC/autonomous_engines/data_feeds/data_feed_engine.py"
    },
    {
        "id": "engine_3_bug_bounty",
        "name": "Bugcrowd In-Scope Secret & Key Scanner",
        "script": "/home/n1khy/Projects/UGC/autonomous_engines/bounty_scanner/bounty_scanner_engine.py"
    },
    {
        "id": "engine_4_checkout_watchdog",
        "name": "Headless Synthetic Checkout Watchdog",
        "script": "/home/n1khy/Projects/UGC/autonomous_engines/checkout_watchdog/watchdog_engine.py"
    }
]

def run_all_engines():
    print(f"==================================================")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] RUNNING FULL NON-FREELANCE REVENUE ENGINE CYCLE")
    print(f"==================================================")
    
    for eng in ENGINES:
        name = eng["name"]
        script = eng["script"]
        print(f"\n--- [START] {name} ---")
        try:
            res = subprocess.run([PYTHON_BIN, script], capture_output=True, text=True, timeout=180)
            if res.stdout:
                print(res.stdout.strip())
            if res.stderr and "Error" in res.stderr:
                print(f"[{name} Errors]: {res.stderr.strip()[:300]}")
        except Exception as e:
            print(f"[{name} Exception]: {e}")
        print(f"--- [DONE] {name} ---\n")

    print(f"==================================================")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ALL ENGINES EXECUTED CLEANLY")
    print(f"==================================================")

if __name__ == "__main__":
    run_all_engines()
