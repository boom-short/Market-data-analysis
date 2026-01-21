import json
import os
import time
import random
from curl_cffi import requests

def fetch_wingo_data():
    # উইনগো অফিশিয়াল এপিআই লিঙ্ক
    url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
    
    # হুবহু ব্রাউজারের হেডার নকল করা
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://draw.ar-lottery01.com",
        "Referer": "https://draw.ar-lottery01.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # ড্র ডাটার জন্য দরকারি প্যারামিটার
    payload = {"pageIndex": 1, "pageSize": 50, "type": 30}

    try:
        # impersonate="chrome120" হলো এই প্রজেক্টের আসল শক্তি
        # এটি TLS Fingerprint পরিবর্তন করে ক্লাউডফেয়ারকে বোকা বানায়
        print("Fetching data from API...")
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            impersonate="chrome120", 
            timeout=30
        )
        
        if response.status_code == 200:
            new_data = response.json()
            if 'data' in new_data:
                update_history_file(new_data['data']['list'])
                print("Successfully updated history.")
            else:
                print("API responded but no data found.")
        else:
            print(f"Failed! Status Code: {response.status_code}")
            # যদি এখনও ৪০৩ আসে, তবে স্ক্রিপ্ট ফাইলটিতে এরর সেভ করবে
            with open("wingo_history.json", "w") as f:
                json.dump({"status": "error", "code": response.status_code}, f)

    except Exception as e:
        print(f"System Error: {e}")

def update_history_file(new_items):
    file_path = "wingo_history.json"
    history = []

    # আগের জমানো ডাটা পড়া
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list): history = []
        except:
            history = []

    # ডুপ্লিকেট চেক করে নতুন ডাটা যোগ করা
    existing_issues = {str(item['issueNumber']) for item in history if 'issueNumber' in item}
    
    added_count = 0
    for item in new_items:
        if str(item['issueNumber']) not in existing_issues:
            history.append(item)
            added_count += 1
    
    # সর্টিং এবং লেটেস্ট ১০০০০ ডাটা লিমিট (ভবিষ্যতের অ্যানালাইসিসের জন্য বড় ডাটাবেজ)
    history = sorted(history, key=lambda x: str(x.get('issueNumber', '')), reverse=True)[:10000]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    print(f"Added {added_count} new entries.")

if __name__ == "__main__":
    # বট ডিটেকশন এড়াতে ১-১০ সেকেন্ডের রেন্ডম ওয়েট
    time.sleep(random.randint(1, 10))
    fetch_wingo_data()
    
