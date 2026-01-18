import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

BASE_URL = "https://www.gsmarena.com/"

def get_target_months():
    """Returns a list of month-year strings for current and previous month."""
    now = datetime.now()
    # Current month: "2026, January"
    current = now.strftime("%Y, %B")
    
    # Previous month
    first_day_current = now.replace(day=1)
    last_month = (first_day_current - timedelta(days=1)).strftime("%Y, %B")
    
    return [current, last_month]

def is_recent_release(announced_str):
    """Checks if the 'Announced' string contains target month/year."""
    targets = get_target_months()
    return any(month_year in announced_str for month_year in targets)

def scrape_recent_phones():
    # 1. Start from the 'Latest Devices' or 'News' pages to find recent slugs
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find links in the "Latest devices" sidebar or section
    latest_links = [a['href'] for a in soup.select('.sidebar .module-phones-link, .makers a')]

    for link in latest_links:
        full_url = BASE_URL + link if not link.startswith('http') else link
        res = requests.get(full_url, headers=headers)
        device_soup = BeautifulSoup(res.text, 'html.parser')
        
        # Extract Announced Date from the table
        announced_tag = device_soup.find('td', {'data-spec': 'year'})
        announced_date = announced_tag.text if announced_tag else ""

        if is_recent_release(announced_date):
            mobile_id = link.split('-')[-1].replace('.php', '')
            model_name = device_soup.find('h1', class_='specs-phone-name-title').text.replace(" ", "_").lower()
            folder_name = f"{model_name}-{mobile_id}"
            
            # Extract Specs
            specs = {}
            for table in device_soup.find_all('table'):
                section = table.find('th').text if table.find('th') else "General"
                specs[section] = {tr.find('td', class_='ttl').text: tr.find('td', class_='nfo').text 
                                  for tr in table.find_all('tr') if tr.find('td', class_='ttl')}
            
            # Export to the required folder
            path = f"data/{folder_name}"
            os.makedirs(path, exist_ok=True)
            with open(f"{path}/specs.json", "w") as f:
                json.dump(specs, f, indent=4)
            print(f"Saved recent device: {folder_name}")

if __name__ == "__main__":
    scrape_recent_phones()
