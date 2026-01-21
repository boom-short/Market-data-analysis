import json
import asyncio
import os
from playwright.async_api import async_playwright

async def fetch_data():
    async with async_playwright() as p:
        # ব্রাউজার লঞ্চ করা
        browser = await p.chromium.launch(headless=True)
        
        # আসল ব্রাউজারের মতো এনভায়রনমেন্ট তৈরি
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()

        try:
            # মেইন সাইটে যাওয়া যাতে কুকি সেটআপ হয়
            print("Connecting to Wingo site...")
            await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle", timeout=60000)
            
            # ক্লাউডফেয়ার চ্যালেঞ্জের জন্য ১০ সেকেন্ড অপেক্ষা
            await asyncio.sleep(10)

            # ব্রাউজার থেকে এপিআই কল করা
            API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
            payload = {"pageIndex": 1, "pageSize": 20, "type": 30}
            
            # সরাসরি ব্রাউজার কনসোল থেকে ডাটা রিকোয়েস্ট
            script = f"""
                async () => {{
                    const response = await fetch('{API_URL}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json;charset=UTF-8' }},
                        body: JSON.stringify({json.dumps(payload)})
                    }});
                    return await response.json();
                }}
            """
            
            response_json = await page.evaluate(script)

            if response_json:
                with open("wingo_history.json", "w", encoding="utf-8") as f:
                    json.dump(response_json, f, indent=4, ensure_ascii=False)
                print("সফলভাবে ডাটা সংগ্রহ করা হয়েছে!")
            else:
                raise Exception("Empty response from API")

        except Exception as e:
            # এরর হলেও ফাইল আপডেট করবে যাতে আপনি বুঝতে পারেন কি সমস্যা হচ্ছে
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({"status": "Failed", "error": str(e)}, f, indent=4)
            print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
