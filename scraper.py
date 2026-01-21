import json
import asyncio
from playwright.async_api import async_playwright

async def fetch_data():
    async with async_playwright() as p:
        # মোবাইল ব্রাউজার হিসেবে লঞ্চ করা
        browser = await p.chromium.launch(headless=True)
        device = p.devices['Pixel 5']
        context = await browser.new_context(**device)
        page = await context.new_page()

        try:
            # সরাসরি উইনগো গেমিং পেজে যাওয়া
            # দ্রষ্টব্য: আপনার দেওয়া ড্র লিঙ্কটি যদি সরাসরি পেজ হয়, তবে সেটি দিন
            url = "https://draw.ar-lottery01.com/" 
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # সাইটটি লোড হওয়ার জন্য ৫ সেকেন্ড অপেক্ষা
            await asyncio.sleep(5)

            # রেজাল্ট টেবিল বা এলিমেন্ট থেকে ডাটা নেওয়া
            # এখানে আমরা পুরো পেজের বডি টেক্সট বা নির্দিষ্ট এলিমেন্ট নিচ্ছি
            # যেহেতু আমি জানি না ভিতরের HTML কেমন, তাই আমরা বডি টেক্সট সেভ করছি
            content = await page.content()
            
            # ডাটা সেভ করা (এটি চেক করার জন্য যে পেজে কি আছে)
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                data = {
                    "status": "Captured",
                    "html_preview": content[:2000] # প্রথম ২০০০ ক্যারেক্টার
                }
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print("Page content captured successfully.")

        except Exception as e:
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({"error": str(e)}, f, indent=4)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
