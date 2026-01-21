import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def fetch_data():
    async with async_playwright() as p:
        # ব্রাউজার লঞ্চ করা
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        # স্টেলথ মোড অ্যাপ্লাই করা যাতে বট ধরা না পড়ে
        await stealth_async(page)

        try:
            # সরাসরি সাইটে না গিয়ে প্রথমে গুগলের মাধ্যমে রেফারার হিসেবে যাওয়া (বাইপাস ট্রিক)
            await page.goto("https://www.google.com", wait_until="networkidle")
            
            # এবার আসল সাইটে যাওয়া
            await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle", timeout=60000)
            
            # ক্লাউডফেয়ার চ্যালেঞ্জ সমাধানের জন্য কিছু সময় অপেক্ষা
            await asyncio.sleep(10)

            # এবার ব্রাউজারের ভেতর থেকে API কল করা
            API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
            payload = {"pageIndex": 1, "pageSize": 20, "type": 30}
            
            response_json = await page.evaluate(f"""
                async () => {{
                    const response = await fetch('{API_URL}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({json.dumps(payload)})
                    }});
                    return await response.json();
                }}
            """)

            if response_json:
                with open("wingo_history.json", "w", encoding="utf-8") as f:
                    json.dump(response_json, f, indent=4, ensure_ascii=False)
                print("Data Bypass Success!")

        except Exception as e:
            # যদি ফেইল করে তবে স্ক্রিনশট বা এরর সেভ করা (মোবাইলে দেখার জন্য সুবিধা হবে)
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({"status": "Failed", "error": str(e)}, f, indent=4)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
