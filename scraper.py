import json
import asyncio
import requests
from playwright.async_api import async_playwright

# ফ্রি প্রক্সি সোর্স থেকে আইপি সংগ্রহের ফাংশন
def get_proxies():
    try:
        response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        if response.status_code == 200:
            return response.text.splitlines()
    except:
        return ["http://38.154.227.167:5868", "http://154.236.177.121:1981"]

async def fetch_data():
    proxies = get_proxies()
    print(f"Found {len(proxies)} proxies. Trying to bypass...")
    
    async with async_playwright() as p:
        success = False
        for i in range(min(5, len(proxies))): # প্রথম ৫টি প্রক্সি ট্রাই করবে
            proxy = proxies[i]
            if not proxy.startswith("http"):
                proxy = f"http://{proxy}"
            
            print(f"Attempt {i+1} using: {proxy}")
            
            try:
                browser = await p.chromium.launch(headless=True, proxy={"server": proxy})
                context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                page = await context.new_page()

                # সাইটে যাওয়া
                await page.goto("https://draw.ar-lottery01.com/", wait_until="networkidle", timeout=30000)
                await asyncio.sleep(5)

                API_URL = 'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json'
                payload = {"pageIndex": 1, "pageSize": 20, "type": 30}
                
                script = f"async () => {{ const res = await fetch('{API_URL}', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({json.dumps(payload)}) }}); return await res.json(); }}"
                
                response_json = await page.evaluate(script)

                if response_json:
                    with open("wingo_history.json", "w", encoding="utf-8") as f:
                        json.dump(response_json, f, indent=4, ensure_ascii=False)
                    print("Bingo! Data fetched successfully.")
                    success = True
                    await browser.close()
                    break
                
                await browser.close()
            except Exception as e:
                print(f"Proxy {proxy} failed. Error: {e}")
                continue
        
        if not success:
            with open("wingo_history.json", "w", encoding="utf-8") as f:
                json.dump({"status": "All Proxies Failed", "time": "2026-01-21"}, f, indent=4)

if __name__ == "__main__":
    asyncio.run(fetch_data())
    
