import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

def get_target_months():
    """Returns strings for current and previous month to filter releases."""
    now = datetime.now()
    current = now.strftime("%Y, %B") # e.g., "2026, January"
    
    first_day_current = now.replace(day=1)
    last_month = (first_day_current - timedelta(days=1)).strftime("%Y, %B")
    
    return [current, last_month]

def scrape_latest():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    base_url = "https://www.gsmarena.com/"
    targets = get_target_months()
    
    print(f"Searching for phones announced in: {targets}")
    
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Target links from the 'Latest' sidebar and main 'Makers' list
    latest_links = [a['href'] for a in soup.select('.module-phones-link, .makers a')]
    
    for link in latest_links:
        full_url = base_url + link if not link.startswith('http') else link
        try:
            device_res = requests.get(full_url, headers=headers, timeout=10)
            dev_soup = BeautifulSoup(device_res.text, 'html.parser')
            
            # Find the 'Announced' field
            announced_tag = dev_soup.find('td', {'data-spec': 'year'})
            announced_date = announced_tag.text if announced_tag else ""
            
            if any(m in announced_date for m in targets):
                model_name = dev_soup.find('h1', class_='specs-phone-name-title').text.replace(" ", "_").lower()
                mobile_id = link.split('-')[-1].replace('.php', '')
                
                # FORCE SAVE TO 'latest/' FOLDER
                folder_path = f"latest/{model_name}-{mobile_id}"
                os.makedirs(folder_path, exist_ok=True)
                
                specs = {}
                for table in dev_soup.find_all('table'):
                    section = table.find('th').text if table.find('th') else "General"
                    specs[section] = {tr.find('td', class_='ttl').text: tr.find('td', class_='nfo').text 
                                      for tr in table.find_all('tr') if tr.find('td', class_='ttl')}
                
                with open(f"{folder_path}/specs.json", "w") as f:
                    json.dump(specs, f, indent=4)
                print(f"Successfully saved: {folder_path}")
        except Exception as e:
            print(f"Error scraping {link}: {e}")

if __name__ == "__main__":
    scrape_latest()
