import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_gsm_specs(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    specs = {}
    
    # Iterate through specification tables
    for table in soup.find_all('table'):
        section = table.find('th').get_text(strip=True) if table.find('th') else "General"
        specs[section] = {}
        for tr in table.find_all('tr'):
            ttl = tr.find('td', class_='ttl')
            nfo = tr.find('td', class_='nfo')
            if ttl and nfo:
                specs[section][ttl.get_text(strip=True)] = nfo.get_text(strip=True)
    
    return specs

if __name__ == "__main__":
    target_url = "https://www.gsmarena.com/samsung_galaxy_a07_5g-14409.php"
    data = scrape_gsm_specs(target_url)
    
    # Ensure folder exists
    os.makedirs("data/samsung_galaxy_a07", exist_ok=True)
    
    with open("data/samsung_galaxy_a07/specs.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Data successfully scraped and saved to the folder.")
