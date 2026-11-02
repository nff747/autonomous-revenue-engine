#!/usr/bin/env python3
"""
Agent 1: DTC / E-commerce Leak Hunter
Scans DTC e-commerce PDPs on mobile viewports.
Strict adherence to GEMINI.md:
- Zero synthetic evidence.
- Physical DOM inspection only.
- Measuring sticky ATC presence, layout shifts, or broken selectors.
- Verifying 200 OK before logging.
"""

import asyncio
import os
import time
import urllib.request
import json
from playwright.async_api import async_playwright

REGISTRY_PATH = "/home/n1khy/Projects/UGC/outreach_registry.tsv"

TARGET_BRANDS = [
    {"brand": "Gymshark", "domain": "gymshark.com", "pdp": "https://www.gymshark.com/products/gymshark-everyday-seamless-leggings-black"},
    {"brand": "Chubbies", "domain": "chubbiesshorts.com", "pdp": "https://www.chubbiesshorts.com/products/the-originals-5-5-stretch"},
    {"brand": "Ridge", "domain": "ridge.com", "pdp": "https://ridge.com/products/aluminum-gunmetal"},
    {"brand": "Cuts Clothing", "domain": "cutsclothing.com", "pdp": "https://www.cutsclothing.com/products/ao-curve-hem-black"},
    {"brand": "True Classic", "domain": "trueclassictees.com", "pdp": "https://www.trueclassictees.com/products/black-crew-neck"},
    {"brand": "Ten Thousand", "domain": "tenthousand.cc", "pdp": "https://www.tenthousand.cc/products/interval-short"},
    {"brand": "Vuori", "domain": "vuoriclothing.com", "pdp": "https://vuoriclothing.com/products/kore-short-black"},
    {"brand": "Allbirds", "domain": "allbirds.com", "pdp": "https://www.allbirds.com/products/mens-wool-runners"},
    {"brand": "Alo Yoga", "domain": "aloyoga.com", "pdp": "https://www.aloyoga.com/products/m4038r-warrior-mat"},
    {"brand": "Bombas", "domain": "bombas.com", "pdp": "https://bombas.com/products/mens-ankle-sock-4-pack"}
]

async def audit_brand(page, brand_info):
    brand = brand_info["brand"]
    url = brand_info["pdp"]
    domain = brand_info["domain"]
    
    print(f"[LeakHunter] Inspecting {brand} ({url})...")
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        status = response.status if response else 0
        if status != 200:
            print(f"[LeakHunter] {brand} returned status {status}. Aborting per Rule 1.2.")
            return None
        
        await asyncio.sleep(2.0)
        
        scroll_height = await page.evaluate("() => document.body.scrollHeight")
        has_sticky_atc = await page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button, a, form[action*="/cart/add"] input[type="submit"]'));
            const atcButtons = buttons.filter(b => {
                const txt = (b.innerText || b.value || '').toLowerCase();
                return txt.includes('add to cart') || txt.includes('bag') || txt.includes('buy');
            });
            if (atcButtons.length === 0) return false;
            
            for (let b of atcButtons) {
                let el = b;
                while (el && el !== document.body) {
                    const style = window.getComputedStyle(el);
                    if (style.position === 'fixed' || style.position === 'sticky') {
                        return true;
                    }
                    el = el.parentElement;
                }
            }
            return false;
        }""")
        
        await page.evaluate("() => window.scrollBy(0, 1500)")
        await asyncio.sleep(1.0)
        
        observation = {
            "brand": brand,
            "domain": domain,
            "url": url,
            "status": status,
            "scrollHeight": scroll_height,
            "hasStickyATC": has_sticky_atc
        }
        
        screenshot_path = f"/home/n1khy/Projects/UGC/autonomous_engines/leak_hunter/proof_{brand.lower().replace(' ', '_')}.png"
        await page.screenshot(path=screenshot_path)
        observation["screenshot"] = screenshot_path
        
        print(f"[LeakHunter] Factually observed {brand}: ScrollHeight={scroll_height}px, StickyATC={has_sticky_atc}")
        return observation
        
    except Exception as e:
        print(f"[LeakHunter] Error auditing {brand}: {e}")
        return None

async def run():
    print("[LeakHunter] Initializing Playwright Mobile Viewport Auditor...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = await browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        
        audits = []
        for b in TARGET_BRANDS:
            obs = await audit_brand(page, b)
            if obs:
                audits.append(obs)
            await asyncio.sleep(2.0)
            
        await browser.close()
        
    out_file = "/home/n1khy/Projects/UGC/autonomous_engines/leak_hunter/verified_audits.json"
    with open(out_file, "w") as f:
        json.dump(audits, f, indent=2)
    print(f"[LeakHunter] Completed audit cycle. Saved {len(audits)} verified observations to {out_file}.")

if __name__ == "__main__":
    asyncio.run(run())
