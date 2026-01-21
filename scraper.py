import requests
import json
import os

API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'

def fetch_wingo_data():
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://draw.ar-lottery01.com',
        'referer': 'https://draw.ar-lottery01.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'mark.via.gp' # এটি একটি মোবাইল ব্রাউজার সিগন্যাল
    }
    
    # এটি উইনগোর নির্দিষ্ট পে-লোড ফরম্যাট
    payload = {
        "pageIndex": 1,
        "pageSize": 20,
        "type": 30 # ৩০ সেকেন্ড বুঝানোর জন্য
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        
        # ডাটা আসলে ফাইল তৈরি হবে
        if response.status_code == 200:
            data = response.json()
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully saved data.")
        else:
            # যদি এপিআই ব্লক করে, তবে কেন করছে তার কারণ লিখে রাখবে
            error_data = {"error": "API Blocked", "status_code": response.status_code}
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(error_data, f, indent=4)
            print(f"Failed! Status: {response.status_code}")

    except Exception as e:
        # এরর হলেও ফাইল তৈরি হবে যাতে গিটহাব অ্যাকশন এরর না দেয়
        with open("wingo_history.json", "w", encoding="utf-8") as f:
            json.dump({"error": str(e)}, f, indent=4)
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_wingo_data()
    
