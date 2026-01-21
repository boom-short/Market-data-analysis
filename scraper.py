import json
import asyncio
import random
from playwright.async_api import async_playwright

# ফ্রি প্রক্সি লিস্ট (এগুলো কাজ না করলে নতুন প্রক্সি যোগ করতে হবে)
PROXIES = [
    "http://50.174.7.155:80",
    "http://154.236.177.121:1981",
    "http://38.45.106.18:8080"
]

async def fetch_data():
    async with async_playwright() as p:
        # রেন্ডম একটি প্রক্সি সিলেক্ট করা
        proxy = random.choice(PROXIES)
        print(f"Using Proxy: {proxy}")
        
        try:
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": proxy}
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # সরাসরি এপিআই ইউআরএল
            API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
            payload = {"pageIndex": 1, "pageSize": 20, "type": 30}

            # সাইটে প্রবেশ
            await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(15)

            # জাভাস্ক্রিপ্ট দিয়ে ডাটা আনা
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
                print("Data Fetched via Proxy!")

        except Exception as e:
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({"status": "Failed", "proxy": proxy, "error": str(e)}, f, indent=4)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
