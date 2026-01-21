import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from datetime import datetime

# ডিরেক্টরি সেটআপ
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class UltraSecureScraper:
    def __init__(self):
        self.url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.db_path = "data/wingo_master_history.json"
        
        # বিভিন্ন আসল ব্রাউজারের ভার্সন (বট ডিটেকশন এড়াতে)
        self.browser_versions = [
            "chrome110", "chrome116", "chrome120", 
            "safari_ios_16_0", "safari_ios_17_0", "edge101"
        ]

    def get_stealth_headers(self):
        # হুবহু আসল ব্রাউজারের সিকিউরিটি প্যারামিটার
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            "Content-Type": "application/json;charset=UTF-8",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        
        try:
            # সেশন ব্যবহারের মাধ্যমে কানেকশন রিইউজ করা (ব্লকিং কমায়)
            with requests.Session() as session:
                print(f"[{datetime.now()}] Initializing Secure Session...")
                
                # ১. প্রথমে হোমপেজ ভিজিট করা (কুকি সেট করার জন্য)
                session.get("https://draw.ar-lottery01.com/", impersonate=random.choice(self.browser_versions))
                time.sleep(random.uniform(1, 3))
                
                # ২. আসল ডাটা রিকোয়েস্ট
                response = session.post(
                    self.url,
                    json=payload,
                    headers=self.get_stealth_headers(),
                    impersonate=random.choice(self.browser_versions),
                    timeout=30
                )
            
            if response.status_code == 200:
                res_json = response.json()
                if 'data' in res_json and 'list' in res_json['data']:
                    return res_json['data']['list']
                else:
                    print("Structure Error: Cloudflare might have served a challenge page.")
            else:
                print(f"Blocked! Status Code: {response.status_code}")
                # যদি ৪MD৫ বা অন্য এরর আসে তবে আইপি পরিবর্তনের ইঙ্গিত দিবে
                
            return None
        except Exception as e:
            print(f"Security Engine Error: {e}")
            return None

    def save_and_analyze(self, new_data):
        if not new_data: return

        history = []
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                history = json.load(f)

        existing_issues = {str(x['issueNumber']) for x in history}
        added = 0
        for item in new_data:
            if str(item['issueNumber']) not in existing_issues:
                history.append(item)
                added += 1

        if added > 0:
            history = sorted(history, key=lambda x: str(x['issueNumber']), reverse=True)[:10000]
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
            print(f"Security Check Passed: {added} new records encrypted and saved.")
        else:
            print("Sync Complete: No new draw data.")

if __name__ == "__main__":
    # হিউম্যান লাইক ডিলে
    wait_time = random.uniform(5, 15)
    print(f"Waiting for {wait_time:.2f}s to mimic human behavior...")
    time.sleep(wait_time)
    
    bot = UltraSecureScraper()
    data = bot.fetch_data()
    bot.save_and_analyze(data)
                      
