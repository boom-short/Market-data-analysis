import json
import os
import time
import random
from curl_cffi import requests

# এই ফাংশনটি একদম আসল ব্রাউজারের মতো করে ডাটা আনবে
def fetch_wingo_live():
    url = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
    
    # ব্রাউজারের হুবহু নকল (Impersonate Chrome 120)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Origin": "https://draw.ar-lottery01.com",
        "Referer": "https://draw.ar-lottery01.com/"
    }
    
    payload = {"pageIndex": 1, "pageSize": 50, "type": 30}

    try:
        # এখানে impersonate="chrome120" ব্যবহার করা হয়েছে যা TLS Fingerprint পাল্টে দেয়
        response = requests.post(url, json=payload, headers=headers, impersonate="chrome120", timeout=30)
        
        if response.status_code == 200:
            new_data = response.json()
            process_and_save(new_data)
        else:
            print(f"Failed with Status: {response.status_code}")
            # যদি এখনো ৪০৩ আসে, তবে বুঝবেন আইপি ব্লক
    except Exception as e:
        print(f"Error occurred: {e}")

def process_and_save(new_json):
    file_name = "wingo_history.json"
    if 'data' not in new_json: return

    # পুরানো ডাটা লোড করা
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except: history = []
    else:
        history = []

    # নতুন ডাটা মার্জ করা
    existing_issues = {str(item.get('issueNumber')) for item in history}
    new_items = new_json['data']['list']
    
    count = 0
    for item in new_items:
        if str(item.get('issueNumber')) not in existing_issues:
            history.append(item)
            count += 1
    
    # লেটেস্ট ১০০০টি ডাটা সেভ রাখা
    history = sorted(history, key=lambda x: str(x.get('issueNumber')), reverse=True)[:1000]

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    print(f"Added {count} new records. Total: {len(history)}")

if __name__ == "__main__":
    # মানুষের মতো আচরণ করতে রেন্ডম ওয়েট
    time.sleep(random.randint(5, 15))
    fetch_wingo_live()
    
