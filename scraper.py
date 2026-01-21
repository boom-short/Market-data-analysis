import json
import asyncio
import os
from playwright.async_api import async_playwright

async def fetch_data():
    async with async_playwright() as p:
        # স্টেলথ ব্রাউজার লঞ্চ
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("উইনগো সাইটে প্রবেশ করা হচ্ছে...")
            # আপনার ড্র-এর মেইন ইউআরএল এখানে দিন যদি এটি আলাদা হয়
            await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle", timeout=60000)
            
            # ক্লাউডফেয়ার বাইপাস করার জন্য ১৫ সেকেন্ড অপেক্ষা
            await asyncio.sleep(15)

            # আমরা এখন ড্র হিস্ট্রি টেবিল থেকে ডাটা সরাসরি এক্সট্রাক্ট করব
            # এটি সাইটটির এইচটিএমএল স্ট্রাকচার অনুযায়ী কাজ করবে
            history_data = await page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('tr'); // টেবিল রো খুঁজছে
                    const results = [];
                    rows.forEach(row => {
                        const cols = row.querySelectorAll('td');
                        if(cols.length >= 2) {
                            results.append({
                                issue: cols[0].innerText.trim(),
                                number: cols[1].innerText.trim()
                            });
                        }
                    });
                    return results;
                }
            """)

            if not history_data:
                # যদি টেবিল না পায়, তবে ফুল পেজ টেক্সট সেভ করবে চেক করার জন্য
                content = await page.inner_text("body")
                history_data = {"status": "Table not found", "preview": content[:500]}

            # ফাইল সেভ করা
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=4, ensure_ascii=False)
            
            print("ডাটা সেভ হয়েছে।")

        except Exception as e:
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({"status": "Failed", "error": str(e)}, f, indent=4)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
