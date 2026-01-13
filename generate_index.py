import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

DOMAIN = "https://today.singhyogendra.com.np"
DATE_FOLDER = "date"

def get_html_layout(target_day, data, today_ad, bs_month_name, bs_year):
    """Generates the full HTML for a specific day."""
    title = f"Nepali Date: {target_day['bs']} | {target_day['ad']} - {target_day.get('event') or 'Nepali Patro'}"
    description = f"Details for {target_day['bs']}: {target_day['ad']}, {target_day['day']}. Event: {target_day.get('event') or 'Regular Day'}."

    calendar_html = ""
    for day in data['days']:
        is_active = "ring-4 ring-red-500 shadow-lg" if day['bs'] == target_day['bs'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        calendar_html += f"""
        <a href="{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_active} transition-all block text-inherit no-underline">
            <div class="text-xs text-gray-400 font-medium">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-gray-800 bs-date-val">{day['bs'].split('-')[-1]}</div>
            <div class="text-xs text-gray-500 ad-date-val hidden">{day['ad'].split('-')[-1]}</div>
            {event_dot}
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 antialiased">
    <header class="max-w-4xl mx-auto px-4 py-10 text-center">
        <h1 class="text-4xl font-extrabold text-slate-800 tracking-tight mb-2"><a href="/">Nepali Patro</a></h1>
    </header>
    <main class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-10 border border-slate-100">
            <div class="bg-red-600 p-8 text-white text-center">
                <h2 class="text-lg font-medium opacity-90 uppercase tracking-widest">Selected Date</h2>
                <div class="text-7xl font-black my-2">{target_day['bs']}</div>
                <p class="text-2xl opacity-90">{target_day['ad']} | {target_day['day']}</p>
            </div>
            {f'<div class="p-5 bg-yellow-50 text-center text-yellow-900 font-bold border-b border-yellow-100 text-xl tracking-tight">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
        </div>
        <section class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-10">
            <div class="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
                <h3 class="text-2xl font-bold text-slate-800">{bs_month_name} {bs_year}</h3>
                <div class="flex items-center bg-slate-100 p-1 rounded-full">
                    <button id="toggleBS" class="px-6 py-2 rounded-full bg-white shadow-sm text-sm font-bold transition-all">BS</button>
                    <button id="toggleAD" class="px-6 py-2 rounded-full text-sm font-medium transition-all">AD</button>
                </div>
            </div>
            <div class="grid grid-cols-7 gap-2">{calendar_html}</div>
        </section>
    </main>
    <script>
        const tBS = document.getElementById('toggleBS'), tAD = document.getElementById('toggleAD');
        const bsV = document.querySelectorAll('.bs-date-val'), adV = document.querySelectorAll('.ad-date-val');
        tAD.addEventListener('click', () => {{
            tAD.classList.add('bg-white', 'shadow-sm', 'font-bold'); tBS.classList.remove('bg-white', 'shadow-sm', 'font-bold');
            bsV.forEach(el => el.classList.add('hidden')); adV.forEach(el => el.classList.remove('hidden'));
        }});
        tBS.addEventListener('click', () => {{
            tBS.classList.add('bg-white', 'shadow-sm', 'font-bold'); tAD.classList.remove('bg-white', 'shadow-sm', 'font-bold');
            adV.forEach(el => el.classList.add('hidden')); bsV.forEach(el => el.classList.remove('hidden'));
        }});
    </script>
</body>
</html>"""

def generate_site():
    npt_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=45)
    today_ad = npt_now.strftime('%Y-%m-%d')
    all_processed_days = []

    # 1. Loop through ALL json files in the date folder
    if not os.path.exists(DATE_FOLDER):
        print(f"Error: Folder '{DATE_FOLDER}' not found.")
        return

    json_files = [f for f in os.listdir(DATE_FOLDER) if f.endswith('.json')]
    
    for json_file in json_files:
        with open(os.path.join(DATE_FOLDER, json_file), 'r') as f:
            raw_data = json.load(f)
            data = raw_data[0] if isinstance(raw_data, list) else raw_data
            
            bs_month_name = data['month_info']['bs_months'][0].split()[0]
            bs_year = data['month_info']['bs_months'][0].split()[1]
            
            for day in data['days']:
                all_processed_days.append(day)
                content = get_html_layout(day, data, today_ad, bs_month_name, bs_year)
                
                # Create the individual page (e.g., 2082-08-15.html)
                with open(f"{day['bs']}.html", "w", encoding="utf-8") as out:
                    out.write(content)
                
                # Set index.html if it's today
                if day['ad'] == today_ad:
                    with open("index.html", "w", encoding="utf-8") as out:
                        out.write(content)

    # 2. Generate Sitemap
    if all_processed_days:
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        # Add Home
        u_home = ET.SubElement(urlset, "url")
        ET.SubElement(u_home, "loc").text = f"{DOMAIN}/"
        ET.SubElement(u_home, "changefreq").text = "daily"
        
        for day in all_processed_days:
            u = ET.SubElement(urlset, "url")
            ET.SubElement(u, "loc").text = f"{DOMAIN}/{day['bs']}.html"
            ET.SubElement(u, "changefreq").text = "monthly"
        
        tree = ET.ElementTree(urlset)
        tree.write("sitemap.xml", encoding='utf-8', xml_declaration=True)
        print(f"Successfully generated sitemap.xml and {len(all_processed_days)} pages.")
    else:
        print("No days found in JSON files to process.")

if __name__ == "__main__":
    generate_site()
