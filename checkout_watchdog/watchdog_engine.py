#!/usr/bin/env python3
"""
Agent 3: Headless Checkout Watchdog Micro-SaaS
Performs synthetic, end-to-end checkout health audits on live e-commerce stores:
- Emulates mobile viewports.
- Ingests verified live flagship product pages (HTTP 200).
- Verifies 'Add to Cart' mechanics and cart drawer progression.
- Logs full diagnostic metrics (latency, console errors, 4xx/5xx network failures).
"""

import asyncio
import time
import json
import os
from playwright.async_api import async_playwright

LOG_PATH = "/home/n1khy/Projects/UGC/autonomous_engines/checkout_watchdog/watchdog_health_reports.json"
INPUT_PATH = "/home/n1khy/Projects/UGC/autonomous_engines/checkout_watchdog/verified_live_stores.json"

async def audit_checkout_flow(page, store):
    name = store["name"]
    url = store["url"]
    print(f"\n[Watchdog] Initiating synthetic checkout flow on {name} ({url})...")
    
    report = {
        "store": name,
        "url": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "http_status": 0,
        "pdp_load_time_ms": 0,
        "atc_button_detected": False,
        "atc_clickable": False,
        "cart_flow_passed": False,
        "console_errors": [],
        "network_errors": []
    }
    
    page.on("console", lambda msg: report["console_errors"].append(msg.text) if msg.type == "error" else None)
    page.on("response", lambda resp: report["network_errors"].append(f"{resp.status}: {resp.url[:60]}") if resp.status >= 400 else None)
    
    try:
        t0 = time.time()
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        report["http_status"] = resp.status if resp else 0
        report["pdp_load_time_ms"] = int((time.time() - t0) * 1000)
        
        await asyncio.sleep(2.0)
        
        # Check Add to Cart button presence
        atc_btn = await page.query_selector('button[name="add"], form[action*="/cart/add"] button, button:has-text("Add to"), a:has-text("Add to")')
        if atc_btn:
            report["atc_button_detected"] = True
            is_visible = await atc_btn.is_visible()
            if is_visible:
                report["atc_clickable"] = True
                print(f"[Watchdog] Verified Add to Cart button is visible and active on {name}.")
                try:
                    await atc_btn.click(timeout=5000)
                    await asyncio.sleep(2.0)
                    cart_open = await page.evaluate("""() => {
                        return document.querySelector('[class*="cart-drawer"], [id*="cart-drawer"], [class*="mini-cart"], [class*="side-cart"]') !== null || window.location.href.includes('/cart');
                    }""")
                    report["cart_flow_passed"] = bool(cart_open)
                    print(f"[Watchdog] Cart flow response: {cart_open}")
                except Exception as click_err:
                    print(f"[Watchdog] Click simulation error: {click_err}")
        else:
            print(f"[Watchdog] Warning: No standard Add to Cart selector found on {name}.")
            
        screenshot_path = f"/home/n1khy/Projects/UGC/autonomous_engines/checkout_watchdog/watchdog_{name.lower().replace(' ', '_')}.png"
        await page.screenshot(path=screenshot_path)
        report["screenshot"] = screenshot_path
        
    except Exception as e:
        print(f"[Watchdog] Critical audit failure on {name}: {e}")
        report["error"] = str(e)
        
    return report

async def run():
    print("[Watchdog] Starting Headless Checkout Health Watchdog...")
    if not os.path.exists(INPUT_PATH):
        print(f"[Watchdog] Missing input stores file: {INPUT_PATH}")
        return
        
    with open(INPUT_PATH) as f:
        stores = json.load(f)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = await browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        
        reports = []
        for s in stores:
            r = await audit_checkout_flow(page, s)
            reports.append(r)
            
        await browser.close()
        
    with open(LOG_PATH, "w") as f:
        json.dump(reports, f, indent=2)
    print(f"\n[Watchdog] Audit cycle completed. Reports recorded to {LOG_PATH}.")

if __name__ == "__main__":
    asyncio.run(run())
