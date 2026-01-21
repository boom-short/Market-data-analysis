import requests
import json
import os

# আপনার এপিআই লিঙ্ক
API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'

def fetch_wingo_data():
    # ব্রাউজারের মতো লুক দিতে হেডার যোগ করা হয়েছে
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://draw.ar-lottery01.com',
        'Referer': 'https://draw.ar-lottery01.com/'
    }
    
    # এপিআই-এর জন্য প্রয়োজনীয় পে-লোড
    payload = {
        "pageIndex": 1,
        "pageSize": 10
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        
        # ডাটা সফলভাবে আসলে সেভ করবে
        if response.status_code == 200:
            data = response.json()
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully saved data.")
        else:
            print(f"Failed! Status Code: {response.status_code}")
            # যদি এরর আসে তবে সেটিও লগ করবে যাতে আপনি বুঝতে পারেন
            with open("error_log.txt", "a") as f:
                f.write(f"Time: {response.headers.get('Date')} - Status: {response.status_code}\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_wingo_data()
    
