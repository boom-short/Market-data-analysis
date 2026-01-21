import cloudscraper
import json
import os

API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'

def fetch_wingo_data():
    # cloudscraper ব্রাউজারের কুকি এবং চ্যালেঞ্জ বাইপাস করতে সাহায্য করে
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )
    
    payload = {
        "pageIndex": 1,
        "pageSize": 20,
        "type": 30
    }

    try:
        response = scraper.post(API_URL, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            # ডাটা সফলভাবে আসলে সেভ করবে
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully saved data.")
        else:
            # যদি এখনো ব্লক থাকে তবে রেসপন্স টেক্সট সেভ করবে চেক করার জন্য
            error_info = {
                "error": "Still Blocked",
                "status_code": response.status_code,
                "response_text": response.text[:500] # প্রথম ৫০০ ক্যারেক্টার
            }
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump(error_info, f, indent=4)
            print(f"Failed! Status: {response.status_code}")

    except Exception as e:
        with open("wingo_history.json", "w", encoding="utf-8") as f:
            json.dump({"error": str(e)}, f, indent=4)

if __name__ == "__main__":
    fetch_wingo_data()
    
