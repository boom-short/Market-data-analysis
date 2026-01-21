import requests
import json
import os

# উইনগো ৩০ সেকেন্ডের অফিসিয়াল এপিআই
API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'

def fetch_wingo_data():
    try:
        # পে-লোড (সাধারণত এই ধরনের এপিআই-তে কিছু প্যারামিটার লাগে)
        payload = {
            "pageIndex": 1,
            "pageSize": 10
        }
        
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # ডাটা গিটহাবে সেভ করার জন্য ফরম্যাট করা
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("ডাটা সফলভাবে সংগ্রহ করা হয়েছে।")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_wingo_data()
    
