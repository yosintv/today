import requests
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://www.gsmarena.com/"

def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return BeautifulSoup(response.text, 'html.parser') if response.status_code == 200 else None
    except: return None

def scrape_device_details(device_url, folder_name):
    soup = get_soup(device_url)
    if not soup: return
    
    specs = {}
    for table in soup.find_all('table'):
        section = table.find('th').text if table.find('th') else "General"
        specs[section] = {tr.find('td', class_='ttl').text: tr.find('td', class_='nfo').text 
                          for tr in table.find_all('tr') if tr.find('td', class_='ttl')}
    
    # Save Specs
    os.makedirs(f"data/{folder_name}", exist_ok=True)
    with open(f"data/{folder_name}/specs.json", "w") as f:
        json.dump(specs, f, indent=4)
        
    # Download Image
    img_tag = soup.find('div', class_='specs-photo-main').find('img') if soup.find('div', class_='specs-photo-main') else None
    if img_tag:
        img_data = requests.get(img_tag['src']).content
        with open(f"data/{folder_name}/device_image.jpg", "wb") as f:
            f.write(img_data)

def discover_all_devices():
    """Finds all devices from brands and upcoming lists."""
    makers_soup = get_soup(f"{BASE_URL}makers.php3")
    brand_links = [BASE_URL + a['href'] for a in makers_soup.find('table').find_all('a')]
    
    for brand_url in brand_links:
        brand_soup = get_soup(brand_url)
        if not brand_soup: continue
        
        # Extract device slugs (e.g., samsung_galaxy_a07_5g-14409)
        devices = brand_soup.find('div', class_='makers').find_all('a')
        for dev in devices:
            slug = dev['href'].replace(".php", "")
            print(f"Scraping: {slug}")
            scrape_device_details(BASE_URL + dev['href'], slug)
            time.sleep(1) # Ethical delay

if __name__ == "__main__":
    discover_all_devices()
