import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from datetime import datetime

# ফোল্ডার তৈরি
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class WingoEnterprise:
    def __init__(self):
        # অফিশিয়াল ড্র এপিআই
        self.url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.db_path = "data/wingo_master_history.json"
        self.report_path = "reports/market_summary.md"
        # ব্রাউজার ইম্পার্সোনেশন লিস্ট (বট ডিটেকশন এড়াতে)
        self.browsers = ["chrome110", "chrome120", "edge101", "safari_ios_16_0"]

    def get_headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": f"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        
        try:
            print(f"[{datetime.now()}] Attempting to fetch data...")
            # সেশন ব্যবহার করা হচ্ছে যাতে কুকি এবং কানেকশন বজায় থাকে
            with requests.Session() as s:
                response = s.post(
                    self.url,
                    json=payload,
                    headers=self.get_headers(),
                    impersonate=random.choice(self.browsers),
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'list' in data['data']:
                    return data['data']['list']
            
            print(f"Error: Received Status Code {response.status_code}")
            return None
        except Exception as e:
            print(f"Connection Failed: {e}")
            return None

    def process_data(self, new_items):
        if not new_items:
            return

        # আগের ডাটা লোড করা
        history = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                history = []

        # ডুপ্লিকেট চেক (Issue Number দিয়ে)
        existing_ids = {str(x.get('issueNumber')) for x in history}
        new_entries = 0
        
        for item in new_items:
            if str(item.get('issueNumber')) not in existing_ids:
                history.append(item)
                new_entries += 1

        if new_entries == 0:
            print("No new draw data to save.")
            return

        # সর্টিং এবং লিমিটিং (লেটেস্ট ২০,০০০ ডাটা রাখা হবে)
        history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:20000]

        # ডাটাবেজ আপডেট
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

        print(f"Success! Added {new_entries} new entries.")
        self.generate_ai_report(history)

    def generate_ai_report(self, history):
        """ডাটা থেকে মার্কেট ইনসাইট তৈরি করা"""
        df = pd.DataFrame(history)
        
        # লেটেস্ট ১০টি ড্র রেজাল্ট
        latest_table = df.head(10)[['issueNumber', 'number', 'colour']].to_markdown(index=False)
        
        # পরিসংখ্যান (গত ১০০ ড্র)
        last_100 = df.head(100)
        color_stats = last_100['colour'].value_counts(normalize=True) * 100
        
        report_content = f"""
# 📊 Wingo Market Intelligence (Enterprise)
**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🕒 Latest 10 Draws
{latest_table}

### 📈 Probability Analysis (Last 100 Games)
- **Green:** {color_stats.get('green', 0):.2f}%
- **Red:** {color_stats.get('red', 0):.2f}%
- **Violet:** {color_stats.get('violet', 0):.2f}%

---
*Status: Advanced Scraper active with TLS Fingerprinting.*
"""
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

if __name__ == "__main__":
    # বট ডিটেকশন এড়াতে র‍্যান্ডম বিরতি
    time.sleep(random.uniform(3, 8))
    bot = WingoEnterprise()
    raw_data = bot.fetch_data()
    bot.process_data(raw_data)
        
