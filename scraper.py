import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from datetime import datetime

# ফোল্ডার অটো-জেনারেশন
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class EnterpriseScraper:
    def __init__(self):
        self.target_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.db_path = "data/wing_history.json"
        self.report_path = "reports/market_analysis.md"
        # শুধুমাত্র সাপোর্টেড প্রোফাইলগুলো রাখা হয়েছে
        self.profiles = ["chrome110", "chrome120", "edge101", "safari_ios_16_0"]

    def get_dynamic_headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120, 124)}.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        
        # ব্লকিং এড়াতে ৫ বার ভিন্ন ভিন্ন কৌশলে চেষ্টা করবে
        for attempt in range(5):
            try:
                print(f"[{datetime.now()}] Attempt {attempt+1}: Accessing API...")
                
                # সেশন এবং প্রক্সি হ্যান্ডলিং
                with requests.Session() as s:
                    # মেইন সাইট ভিজিট করে কুকি নেওয়া
                    s.get("https://draw.ar-lottery01.com/", 
                          impersonate=random.choice(self.profiles), 
                          timeout=20)
                    
                    time.sleep(random.uniform(5, 10)) # মানুষের মতো বিরতি
                    
                    response = s.post(
                        self.target_url,
                        json=payload,
                        headers=self.get_dynamic_headers(),
                        impersonate=random.choice(self.profiles),
                        timeout=30
                    )

                if response.status_code == 200:
                    res_json = response.json()
                    if 'data' in res_json and res_json['data']['list']:
                        return res_json['data']['list']
                
                elif response.status_code == 403:
                    print("⚠️ 403 Forbidden: IP is blocked by Cloudflare. Trying to wait longer...")
                
                time.sleep(random.randint(10, 20)) 
            except Exception as e:
                print(f"Request Error on attempt {attempt+1}: {e}")
        return None

    def save_and_process(self, new_data):
        if not new_data:
            print("❌ Failure: Could not bypass security. Check if the site is under high protection.")
            return

        history = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except: history = []

        existing_ids = {str(item.get('issueNumber')) for item in history}
        added = 0
        for item in new_data:
            if str(item.get('issueNumber')) not in existing_ids:
                history.append(item)
                added += 1

        if added == 0:
            print("ℹ️ Status: No new draws found.")
            return

        history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:10000]
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"✅ Success: Added {added} new records.")
        self.generate_report(history)

    def generate_report(self, history):
        df = pd.DataFrame(history)
        latest_results = df.head(15)[['issueNumber', 'number', 'colour']].to_markdown(index=False)
        
        report = f"# 🚀 Wingo Live Market Report\n**Update:** {datetime.now()}\n\n{latest_results}"
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report)

if __name__ == "__main__":
    bot = EnterpriseScraper()
    data = bot.fetch_data()
    bot.save_and_process(data)
    
