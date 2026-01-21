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
        # আসল ব্রাউজারের বিভিন্ন ফিঙ্গারপ্রিন্ট প্রোফাইল
        self.profiles = ["chrome110", "chrome120", "edge101", "safari_ios_16_0", "safari_17_0"]

    def get_dynamic_headers(self):
        # প্রতিবার নতুন নতুন ডিভাইস থেকে রিকোয়েস্ট যাচ্ছে এমনটা বোঝাবে
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(118, 124)}.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        
        for attempt in range(3): # ৩ বার চেষ্টা করবে
            try:
                print(f"[{datetime.now()}] Attempt {attempt+1}: Accessing API...")
                
                with requests.Session() as s:
                    # ১. প্রথমে সাইটের মেইন লিঙ্কে গিয়ে কুকি সংগ্রহ
                    s.get("https://draw.ar-lottery01.com/", impersonate=random.choice(self.profiles))
                    time.sleep(random.uniform(3, 6))
                    
                    # ২. ডাটার জন্য আসল রিকোয়েস্ট
                    response = s.post(
                        self.target_url,
                        json=payload,
                        headers=self.get_dynamic_headers(),
                        impersonate=random.choice(self.profiles),
                        timeout=30
                    )

                if response.status_code == 200:
                    raw_res = response.json()
                    if 'data' in raw_res and 'list' in raw_res['data']:
                        return raw_res['data']['list']
                    else:
                        print("API responded but structure is empty (Anti-Bot Triggered).")
                else:
                    print(f"Server Refused Connection: Status {response.status_code}")
                
                time.sleep(random.randint(5, 10)) # ফেইল করলে একটু বিরতি দিয়ে আবার চেষ্টা
            except Exception as e:
                print(f"Request Error: {e}")
        return None

    def save_and_process(self, new_data):
        if not new_data:
            print("❌ Critical: No data found. Anti-bot systems are still blocking the bot.")
            return

        # আগের জমানো ডাটা লোড করা
        history = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except: history = []

        # নতুন ডাটা চেক এবং মার্জ করা
        existing_issues = {str(item.get('issueNumber')) for item in history}
        added = 0
        for item in new_data:
            if str(item.get('issueNumber')) not in existing_issues:
                history.append(item)
                added += 1

        if added == 0:
            print("ℹ️ Status: Everything is up-to-date. No new draws yet.")
            return

        # লেটেস্ট ১০,০০০ ডাটা সেভ রাখা (সর্টিং করে)
        history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:10000]

        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"✅ Success: Saved {added} new draw results.")
        self.generate_market_report(history)

    def generate_market_report(self, history):
        df = pd.DataFrame(history)
        latest_results = df.head(15)[['issueNumber', 'number', 'colour']].to_markdown(index=False)
        
        report = f"""
# 🚀 Wingo Enterprise Analytics 2026
**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🕒 Latest Market History (Top 15)
{latest_results}

---
*Generated by Enterprise Scraper Engine.*
"""
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report)

if __name__ == "__main__":
    # হিউম্যান লাইক ওয়েট
    time.sleep(random.uniform(5, 10))
    bot = EnterpriseScraper()
    data = bot.fetch_data()
    bot.save_and_process(data)
            
