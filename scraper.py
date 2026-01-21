import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def fetch_data():
    async with async_playwright() as p:
        # ব্রাউজার লঞ্চ
        browser = await p.chromium.launch(headless=True)
        # মোবাইল বা বড় স্ক্রিন যেকোনো একটি ইমুলেট করা
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # স্টেলথ মোড চালু করা (বট ডিটেকশন এড়াতে)
        await stealth_async(page)

        try:
            # সরাসরি এপিআই লিঙ্কে যাওয়ার বদলে আগে মেইন সাইটে যাওয়া
            await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle", timeout=60000)
            
            # ক্লাউডফেয়ার যেন আমাদের আসল ইউজার মনে করে তাই একটু সময় দেওয়া
            await asyncio.sleep(15)

            # এবার জাভাস্ক্রিপ্ট ব্যবহার করে ডাটা রিকোয়েস্ট করা
            API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
            payload = {"pageIndex": 1, "pageSize": 20, "type": 30}
            
            # ব্রাউজারের ভেতর থেকে fetch অপারেশন চালানো
            script = f"""
                async () => {{
                    const res = await fetch('{API_URL}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({json.dumps(payload)})
                    }});
                    return await res.json();
                }}
            """
            
            response_json = await page.evaluate(script)

            if response_json:
                with open("wingo_history.json", "w", encoding="utf-8") as f:
                    json.dump(response_json, f, indent=4, ensure_ascii=False)
                print("সফলভাবে ডাটা সংগ্রহ করা হয়েছে!")
            else:
                print("কোনো ডাটা পাওয়া যায়নি।")

        except Exception as e:
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({
                    "status": "Error",
                    "message": str(e),
                    "hint": "Cloudflare challenge still active"
                }, f, indent=4)
            print(f"Error occurred: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
