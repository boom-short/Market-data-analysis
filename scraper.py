import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from datetime import datetime

# প্রজেক্ট ডিরেক্টরি সেটআপ
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class WingoEnterpriseBot:
    def __init__(self):
        self.api_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.history_file = "data/wingo_master_history.json"
        self.report_file = "reports/live_analysis.md"
        # শক্তিশালী ব্রাউজার ফিঙ্গারপ্রিন্ট লিস্ট
        self.impersonate_list = ["chrome110", "chrome120", "edge101", "safari_ios_16_0"]

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/"
        }

        try:
            print(f"[{datetime.now()}] Initializing request...")
            # সেশন ব্যবহার করে TLS Fingerprint সিমুলেট করা
            with requests.Session() as s:
                response = s.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    impersonate=random.choice(self.impersonate_list),
                    timeout=30
                )

            if response.status_code == 200:
                json_data = response.json()
                if 'data' in json_data and 'list' in json_data['data']:
                    return json_data['data']['list']
                print("API Error: Data structure unexpected.")
            else:
                print(f"Failed to bypass. Status Code: {response.status_code}")
            return None
        except Exception as e:
            print(f"System Error: {e}")
            return None

    def process_and_report(self, new_items):
        if not new_items: return

        # পুরনো ডাটা লোড করা
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except: history = []

        # নতুন ডাটা মার্জ করা (ডুপ্লিকেট চেক করে)
        existing_ids = {str(item['issueNumber']) for item in history if 'issueNumber' in item}
        added = 0
        for item in new_items:
            if str(item['issueNumber']) not in existing_ids:
                history.append(item)
                added += 1

        if added == 0:
            print("Database is already up to date.")
            return

        # সর্টিং (লেটেস্ট ডাটা আগে) এবং ১০,০০০ ডাটা সেভ রাখা
        history = sorted(history, key=lambda x: str(x['issueNumber']), reverse=True)[:10000]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"Successfully added {added} records.")
        self.generate_markdown_report(history)

    def generate_markdown_report(self, history):
        df = pd.DataFrame(history)
        
        # ১. টেবিল ফরম্যাটে লেটেস্ট ১০টি ড্র
        latest_draws = df.head(10)[['issueNumber', 'number', 'colour']].to_markdown(index=False)
        
        # ২. স্ট্যাটিস্টিকস (গত ১০০ ড্র-এর উপর ভিত্তি করে)
        stats_data = df.head(100)
        color_dist = stats_data['colour'].value_counts(normalize=True) * 100
        
        report = f"""
# 🚀 Wingo Enterprise Intelligence Report
**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 Latest Market Activity (Top 10)
{latest_draws}

### 📈 Probability Trends (Last 100 Games)
- **🔴 Red:** {color_dist.get('red', 0):.1f}%
- **🟢 Green:** {color_dist.get('green', 0):.1f}%
- **🟣 Violet:** {color_dist.get('violet', 0):.1f}%

---
*Powered by AI Market Scraper 2026*
"""
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report)

if __name__ == "__main__":
    # অ্যান্টি-বট ডিলে (৩-১০ সেকেন্ড)
    time.sleep(random.randint(3, 10))
    bot = WingoEnterpriseBot()
    data = bot.fetch_data()
    bot.process_and_report(data)
    
