import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from datetime import datetime

# ফোল্ডার নিশ্চিত করা
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

class WingoFinalScraper:
    def __init__(self):
        self.api_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.db_path = "data/wing_history.json"
        self.report_path = "reports/market_analysis.md"

    def get_headers(self):
        # আধুনিক ব্রাউজারগুলোর হুবহু নকল
        chrome_ver = random.randint(120, 125)
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/",
            "Sec-Ch-Ua": f'"Google Chrome";v="{chrome_ver}", "Not(A:Brand";v="8", "Chromium";v="{chrome_ver}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        
        # প্রক্সি ছাড়া কিন্তু শক্তিশালী TLS Fingerprint দিয়ে ৫ বার চেষ্টা
        for attempt in range(5):
            try:
                print(f"[{datetime.now()}] Secure Attempt {attempt+1}...")
                
                # impersonate="chrome" ব্যবহার করা হয়েছে যা TLS 1.3 সিমুলেট করে
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=self.get_headers(),
                    impersonate="chrome120",
                    timeout=30,
                    verify=False # SSL এরর এড়াতে
                )

                if response.status_code == 200:
                    res_json = response.json()
                    if 'data' in res_json and res_json['data']['list']:
                        return res_json['data']['list']
                
                print(f"Failed with Status: {response.status_code}")
                time.sleep(random.randint(10, 20))
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        return None

    def save_and_report(self, new_data):
        if not new_data:
            print("❌ Data fetch failed. Cloudflare is extremely strict.")
            return

        history = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except: history = []

        # ইউনিক ডাটা ফিল্টার
        existing_ids = {str(item.get('issueNumber')) for item in history}
        added = 0
        for item in new_data:
            if str(item.get('issueNumber')) not in existing_ids:
                history.append(item)
                added += 1

        if added > 0:
            history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:10000]
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
            
            # রিপোর্ট তৈরি
            df = pd.DataFrame(history)
            report = f"# 📊 Wingo Analysis\nUpdate: {datetime.now()}\n\n{df.head(10)[['issueNumber', 'number', 'colour']].to_markdown(index=False)}"
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"✅ Success: {added} new entries.")
        else:
            print("ℹ️ Everything up-to-date.")

if __name__ == "__main__":
    bot = WingoFinalScraper()
    data = bot.fetch_data()
    bot.save_and_report(data)
    
