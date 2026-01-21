import json
import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # ব্রাউজার এমনভাবে লঞ্চ করা যাতে বট ডিটেকশন ফেইল করে
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox'
            ]
        )
        
        # আপনার ফোনের মতো একটি এনভায়রনমেন্ট তৈরি
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            viewport={'width': 360, 'height': 800},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            locale="en-US",
            timezone_id="Asia/Dhaka"
        )

        # অ্যান্টি-ডিটেকশন স্ক্রিপ্ট ইনজেক্ট করা
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)

        page = await context.new_page()
        
        try:
            print("গুগলের মাধ্যমে রিডাইরেক্ট হচ্ছে...")
            await page.goto("https://www.google.com")
            await asyncio.sleep(2)
            
            print("উইনগো গেমে প্রবেশ করা হচ্ছে...")
            # আপনার মেইন ড্র পেজ ইউআরএল
            target_url = "https://draw.ar-lottery01.com/"
            await page.goto(target_url, wait_until="networkidle", timeout=90000)
            
            # মানুষের মতো আচরণ করতে স্ক্রল করা
            await page.mouse.wheel(0, 500)
            await asyncio.sleep(random.uniform(10, 15))

            # API থেকে ডাটা সংগ্রহের চ্যালেঞ্জ নেওয়া
            API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
            payload = {"pageIndex": 1, "pageSize": 50, "type": 30}

            # ব্রাউজারের ভেতর থেকে রিকোয়েস্ট পাঠানো
            response_data = await page.evaluate(f"""
                async () => {{
                    try {{
                        const res = await fetch('{API_URL}', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json;charset=UTF-8' }},
                            body: JSON.stringify({json.dumps(payload)})
                        }});
                        return await res.json();
                    }} catch (e) {{
                        return {{ error: e.message }};
                    }}
                }}
            """)

            # ডাটা প্রসেসিং এবং সেভ করা
            if response_data and 'data' in response_data:
                history_file = "wingo_history.json"
                # ডাটা রিড এবং অ্যাপেন্ড করার লজিক
                current_records = []
                if os.path.exists(history_file):
                    try:
                        with open(history_file, 'r') as f:
                            current_records = json.load(f)
                    except: pass
                
                # নতুন ডাটা মার্জ করা
                new_list = response_data['data']['list']
                existing_ids = {r['issueNumber'] for r in current_records}
                for item in new_list:
                    if item['issueNumber'] not in existing_ids:
                        current_records.append(item)
                
                # সর্বোচ্চ ১০০০টি ডাটা সেভ রাখা
                current_records = sorted(current_records, key=lambda x: x['issueNumber'], reverse=True)[:1000]

                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(current_records, f, indent=4, ensure_ascii=False)
                
                print(f"সফল! বর্তমানে মোট {len(current_records)}টি ডাটা জমা আছে।")
            else:
                print("ডাটা পাওয়া যায়নি, সিকিউরিটি চ্যালেঞ্জ সামনে এসেছে।")

        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
    
