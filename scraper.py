import requests
import json
import os
from datetime import datetime

# উইনগো ডাটা সোর্স (আপনার API বা URL এখানে দিন)
URL = "YOUR_WINGO_API_ENDPOINT" 

def fetch_data():
    response = requests.get(URL)
    data = response.json()
    
    # বর্তমান সময় অনুযায়ী ফাইল সেভ করা
    filename = "data.json"
    with open(filename, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    fetch_data()
  
