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

class UltraStealthScraper:
    def __init__(self):
        self.target_url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
        self.db_path = "data/wing_history.json"
        self.report_path = "reports/market_analysis.md"
        # শুধুমাত্র স্থিতিশীল প্রোফাইল
        self.profiles = ["chrome110", "chrome120", "edge101"]

    def get_free_proxies(self):
        """ইন্টারনেট থেকে কিছু ফ্রি প্রক্সি লিস্ট সংগ্রহ করার চেষ্টা করে"""
        try:
            # এটি একটি পাবলিক প্রক্সি লিস্ট এপিআই
            res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
            if res.status_code == 200:
                return res.text.strip().split('\r\n')
        except:
            return []
        return []

    def get_headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://draw.ar-lottery01.com",
            "Referer": "https://draw.ar-lottery01.com/",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120, 125)}.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def fetch_data(self):
        payload = {"pageIndex": 1, "pageSize": 50, "type": 30}
        proxies_list = self.get_free_proxies()
        
        print(f"Found {len(proxies_list)} potential proxies. Starting bypass...")

        for attempt in range(10):  # ১০ বার আলাদা আলাদা প্রক্সি দিয়ে চেষ্টা করবে
            proxy = random.choice(proxies_list) if proxies_list else None
            proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
            
            try:
                print(f"[{datetime.now()}] Attempt {attempt+1} using Proxy: {proxy if proxy else 'Direct'}")
                
                with requests.Session() as s:
                    # ১. হোমপেজে হিট করে নিজেকে মানুষ প্রমাণ করা
                    s.get("https://draw.ar-lottery01.com/", 
                          impersonate=random.choice(self.profiles),
                          proxies=proxy_dict,
                          timeout=15)
                    
                    time.sleep(random.uniform(3, 7))
                    
                    # ২. আসল ডাটা রিকোয়েস্ট
                    response = s.post(
                        self.target_url,
                        json=payload,
                        headers=self.get_headers(),
                        impersonate=random.choice(self.profiles),
                        proxies=proxy_dict,
                        timeout=20
                    )

                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']['list']:
                        return data['data']['list']
                
                print(f"Failed with Status {response.status_code}. Trying next proxy...")
            except Exception as e:
                print(f"Proxy error: {e}")
                continue
        return None

    def save_and_process(self, new_data):
        if not new_data:
            print("❌ All attempts failed. Cloudflare is blocking GitHub IPs heavily.")
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

        if added > 0:
            history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:10000]
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
            print(f"✅ Success! {added} new records added.")
            self.generate_report(history)
        else:
            print("ℹ️ No new data found.")

    def generate_report(self, history):
        df = pd.DataFrame(history)
        latest_draws = df.head(15)[['issueNumber', 'number', 'colour']].to_markdown(index=False)
        report = f"# 🚀 Wingo Enterprise Live Report\n**Update:** {datetime.now()}\n\n{latest_draws}"
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report)

if __name__ == "__main__":
    bot = UltraStealthScraper()
    data = bot.fetch_data()
    bot.save_and_process(data)
                    
