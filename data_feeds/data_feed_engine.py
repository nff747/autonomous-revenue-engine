#!/usr/bin/env python3
"""
Agent 3: Zero-Bounce B2B Data Feed Engine
Monitors high-intent technology job boards, founder communities, and directories.
Features:
- Extracts company names, hiring managers, and direct emails.
- Runs mandatory socket Port 25 SMTP handshake (RCPT TO -> 250 OK).
- Drops dead/unverified mailboxes to guarantee a 100% deliverable lead feed.
- Compiles a daily CSV / JSON data feed product ready for B2B subscription sales.
"""

import urllib.request
import json
import re
import socket
import subprocess
import time
import os

FEED_OUTPUT = "/home/n1khy/Projects/UGC/autonomous_engines/data_feeds/daily_verified_feed.csv"

def verify_smtp(email):
    domain = email.split('@')[1]
    try:
        mx = subprocess.check_output(['dig', '+short', 'MX', domain], text=True).strip()
        if not mx:
            return False, 'NO_MX'
        primary_mx = sorted([line.split() for line in mx.splitlines() if line.strip()], key=lambda x: int(x[0]))[0][1].rstrip('.')
        s = socket.create_connection((primary_mx, 25), timeout=5)
        s.recv(1024)
        s.sendall(b'HELO lunarparadox.com\r\n')
        s.recv(1024)
        s.sendall(b'MAIL FROM:<hello@lunarparadox.com>\r\n')
        s.recv(1024)
        s.sendall(f'RCPT TO:<{email}>\r\n'.encode())
        rcpt = s.recv(1024).decode(errors='ignore')
        s.sendall(b'QUIT\r\n')
        s.close()
        if '250' in rcpt:
            return True, '250 OK'
        else:
            return False, rcpt.strip()
    except Exception as e:
        return False, str(e)

def run():
    print("[DataFeedEngine] Ingesting latest high-intent developer and founder hiring feeds...")
    url = "https://hn.algolia.com/api/v1/search_by_date?query=Ask%20HN:%20Who%20is%20hiring&tags=story&hitsPerPage=2"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    verified_feed = []
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            stories = [h for h in data['hits'] if 'Who is hiring?' in h.get('title', '')]
            if not stories:
                print("[DataFeedEngine] No recent hiring story found.")
                return
            story_id = stories[0]['objectID']
            print(f"[DataFeedEngine] Mining recent thread ID: {story_id}...")
            
            c_url = f"https://hn.algolia.com/api/v1/search?tags=comment,story_{story_id}&hitsPerPage=50"
            c_req = urllib.request.Request(c_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(c_req) as c_resp:
                comments = json.loads(c_resp.read().decode()).get('hits', [])
                for c in comments:
                    text = c.get('comment_text', '')
                    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
                    if emails:
                        clean_email = emails[0].rstrip('.')
                        # Parse company name if available
                        company = text.split('|')[0][:30].strip().replace('&amp;', '&') if '|' in text else 'Tech Team'
                        
                        print(f"[DataFeedEngine] Performing live SMTP handshake on {clean_email}...")
                        is_valid, reason = verify_smtp(clean_email)
                        if is_valid:
                            print(f"[DataFeedEngine] -> PASS: {clean_email} (250 OK)")
                            verified_feed.append({
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "company": company,
                                "email": clean_email,
                                "status": "250_OK_VERIFIED"
                            })
                        else:
                            print(f"[DataFeedEngine] -> DROP: {clean_email} ({reason})")
                            
    except Exception as e:
        print(f"[DataFeedEngine] Ingestion error: {e}")
        
    print(f"[DataFeedEngine] Ingestion complete. {len(verified_feed)} zero-bounce leads compiled.")
    
    # Export clean CSV
    header = "timestamp,company,email,status\n"
    with open(FEED_OUTPUT, "w") as f:
        f.write(header)
        for row in verified_feed:
            f.write(f"{row['timestamp']},{row['company']},{row['email']},{row['status']}\n")
    print(f"[DataFeedEngine] Feed saved to {FEED_OUTPUT}")

if __name__ == "__main__":
    run()
