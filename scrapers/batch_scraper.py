import requests
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://www.gsmarena.com/"
CHECKPOINT_FILE = "data/last_scraped_id.txt"

def get_last_id():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return int(f.read().strip())
    return 100  # Start from 100 as requested

def save_last_id(current_id):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(current_id))

def scrape_by_id(mobile_id):
    # Note: GSMArena URLs usually follow a slug-id.php format. 
    # Since we don't have the slug, we first hit a generic link or search
    # to find the correct redirect URL for that ID.
    test_url = f"{BASE_URL}phone-recorder.php3?idPhone={mobile_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(test_url, headers=headers, allow_redirects=True, timeout=10)
        if response.status_code != 200 or "res.php" in response.url:
            return False # ID doesn't exist yet

        soup = BeautifulSoup(response.text, 'html.parser')
        model_name = soup.find('h1', class_='specs-phone-name-title').text.replace(" ", "_").lower()
        folder_path = f"data/{model_name}-{mobile_id}"
        
        os.makedirs(folder_path, exist_ok=True)
        
        # Extract Specs
        specs = {}
        for table in soup.find_all('table'):
            section = table.find('th').text if table.find('th') else "General"
            specs[section] = {tr.find('td', class_='ttl').text: tr.find('td', class_='nfo').text 
                              for tr in table.find_all('tr') if tr.find('td', class_='ttl')}
        
        with open(f"{folder_path}/specs.json", "w") as f:
            json.dump(specs, f, indent=4)
        return True
    except:
        return False

if __name__ == "__main__":
    start_id = get_last_id()
    count = 0
    current_id = start_id + 1
    
    print(f"Starting batch from ID: {current_id}")
    
    # Process exactly 100 successful models
    while count < 100:
        success = scrape_by_id(current_id)
        if success:
            print(f"Successfully scraped ID: {current_id}")
            count += 1
        else:
            print(f"ID {current_id} not found, skipping...")
        
        current_id += 1
        time.sleep(1) # Ethical delay to avoid bans
        
        # Safety break if we hit a massive gap in IDs
        if current_id > start_id + 500: 
            break

    save_last_id(current_id - 1)
