#!/usr/bin/env python3
"""
Agent 2: Bug Bounty Secret Scanner Engine
Scans authorized, in-scope public web targets from official Bugcrowd paid bounty programs.
Targets live production JavaScript bundles, manifest files, and public endpoints for exposed secrets:
- Stripe Live Keys (sk_live_)
- AWS Access Keys (AKIA...)
- GitHub Personal Access Tokens (ghp_)
- Slack Webhook URLs
- OpenAI API Keys (sk-...)
- Google Cloud API Keys (AIza...)
"""

import json
import re
import urllib.request
import os
import time

SCOPES_PATH = "/home/n1khy/Projects/UGC/autonomous_engines/bounty_scanner/bugcrowd_programs.json"
RESULTS_PATH = "/home/n1khy/Projects/UGC/autonomous_engines/bounty_scanner/bounty_findings.json"

PATTERNS = {
    "Stripe Live Secret Key": r"sk_live_[0-9a-zA-Z]{24,}",
    "AWS Access Key ID": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{32,}",
    "GitHub Personal Access Token": r"ghp_[a-zA-Z0-9]{36}",
    "Slack Webhook URL": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
    "Google API / Cloud Token": r"AIza[0-9A-Za-z\\-_]{35}"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SecurityAudit/1.0"
}

def load_in_scope_targets():
    if not os.path.exists(SCOPES_PATH):
        return []
    with open(SCOPES_PATH) as f:
        data = json.load(f)
    
    valid_targets = []
    for prog in data:
        name = prog.get("name", "Unknown Program")
        max_payout = prog.get("max_payout", 0)
        in_scope = prog.get("targets", {}).get("in_scope", [])
        for t in in_scope:
            target_str = t.get("target", "")
            if t.get("type") == "website" and target_str.startswith("http"):
                valid_targets.append({
                    "program": name,
                    "max_payout": max_payout,
                    "url": target_str
                })
    return valid_targets

def scan_content(text, source_url, program_name):
    findings = []
    for name, regex in PATTERNS.items():
        matches = re.findall(regex, text)
        if matches:
            for m in set(matches):
                redacted = m[:6] + "..." + m[-4:] if len(m) > 10 else "[REDACTED]"
                findings.append({
                    "program": program_name,
                    "secret_type": name,
                    "redacted_token": redacted,
                    "source_url": source_url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
    return findings

def run():
    print("[BountyHunter] Loading verified in-scope Bugcrowd targets...")
    targets = load_in_scope_targets()
    print(f"[BountyHunter] Total verified website targets in scope: {len(targets)}")
    
    # Process batch of target URLs
    findings = []
    scanned_count = 0
    for t in targets[:15]:
        url = t["url"]
        prog = t["program"]
        print(f"[BountyHunter] Auditing [{prog}] -> {url}...")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode(errors="ignore")
                matches = scan_content(content, url, prog)
                if matches:
                    print(f"[BountyHunter] 🚨 ALERT! Potential secret found in {url}!")
                    findings.extend(matches)
                else:
                    print(f"[BountyHunter] Clean. No exposed patterns in {url}.")
                scanned_count += 1
        except Exception as e:
            print(f"[BountyHunter] Could not fetch {url}: {e}")
        time.sleep(1.0)
        
    print(f"[BountyHunter] Audit completed for {scanned_count} in-scope targets. Findings: {len(findings)}")
    with open(RESULTS_PATH, "w") as f:
        json.dump(findings, f, indent=2)

if __name__ == "__main__":
    run()
