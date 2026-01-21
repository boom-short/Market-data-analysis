import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from datetime import datetime

# ১. অটোমেটিক ফোল্ডার তৈরি (আপনার ডাটা এখানে জমা হবে)
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class WingoEnterpriseBot:
    def __init__(self):
        self.api_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.history_file = "data/wing_history.json"
        self.report_file = "reports/market_analysis.md"
        # উন্নত সিকিউরিটি ফিঙ্গারপ্রিন্ট
        self.browsers = ["chrome110", "chrome120", "edge101", "safari_ios_16_0"]

    def get_secure_headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        try:
            print(f"[{datetime.now()}] Attempting to fetch data with TLS bypass...")
            # সেশন ব্যবহার করে কুকি হ্যান্ডেল করা
            with requests.Session() as s:
                # প্রথমে হোমপেজ হিট করে কুকি সেট করা (সিকিউরিটি বাইপাস)
                s.get("https://draw.ar-lottery01.com/", impersonate=random.choice(self.browsers))
                time.sleep(2)
                
                response = s.post(
                    self.api_url,
                    json=payload,
                    headers=self.get_secure_headers(),
                    impersonate=random.choice(self.browsers),
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'list' in data['data']:
                    return data['data']['list']
            
            print(f"Error: Server responded with status {response.status_code}")
            return None
        except Exception as e:
            print(f"Connection Error: {e}")
            return None

    def process_and_save(self, new_items):
        if not new_items:
            print("No data received from API. It might be blocked.")
            return

        # পুরনো ডাটা পড়া
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except: history = []

        # ডুপ্লিকেট চেক ও নতুন ডাটা যোগ
        existing_ids = {str(item.get('issueNumber')) for item in history}
        added_count = 0
        for item in new_items:
            if str(item.get('issueNumber')) not in existing_ids:
                history.append(item)
                added_count += 1

        if added_count == 0:
            print("Database is already up to date. No new records.")
            return

        # সর্টিং (লেটেস্ট ডাটা আগে)
        history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:10000]

        # ডাটাবেজে সেভ (JSON ফাইল)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"Successfully saved {added_count} new entries.")
        self.generate_report(history)

    def generate_report(self, history):
        """ডাটা থেকে রিপোর্ট তৈরি করা"""
        df = pd.DataFrame(history)
        latest = df.head(10)[['issueNumber', 'number', 'colour']].to_markdown(index=False)
        
        report = f"""
# 📊 Wingo Enterprise Live Report
**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🕒 Recent Draws
{latest}

---
*Data stored in: data/wing_history.json*
"""
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report)

if __name__ == "__main__":
    # হিউম্যান সিমুলেশন ডিলে
    time.sleep(random.randint(5, 12))
    bot = WingoEnterpriseBot()
    raw_data = bot.fetch_data()
    bot.process_and_save(raw_data)
            
