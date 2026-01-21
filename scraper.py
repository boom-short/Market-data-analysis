import json
import asyncio
from playwright.async_api import async_playwright

async def fetch_data():
    async with async_playwright() as p:
        # ব্রাউজার ওপেন করা
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        page = await context.new_page()

        API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
        
        # প্রথমে মেইন সাইটে যাওয়া যাতে সিকিউরিটি চেক পাস হয়
        await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle")
        
        # এপিআই রিকোয়েস্ট পাঠানো
        payload = {"pageIndex": 1, "pageSize": 20, "type": 30}
        
        response = await page.evaluate(f"""
            fetch('{API_URL}', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({json.dumps(payload)})
            }}).then(res => res.json())
        """)

        if response:
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(response, f, indent=4, ensure_ascii=False)
            print("Successfully fetched data using browser.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
