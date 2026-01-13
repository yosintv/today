import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

DOMAIN = "https://today.singhyogendra.com.np"
JSON_SOURCE = "date/2026.json"

def get_html_layout(target_day, month_days, today_ad, month_label):
    """The exact same CSS design you requested."""
    title = f"Nepali Date: {target_day['bs']} | {target_day['ad']} - {target_day.get('event') or 'Nepali Patro'}"
    description = f"View details for {target_day['bs']}. English date: {target_day['ad']}. Event: {target_day.get('event') or 'Regular Day'}."

    # Build Calendar Grid
    calendar_html = ""
    for day in month_days:
        is_active = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['bs'] == target_day['bs'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        calendar_html += f"""
        <a href="{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_active} transition-all block text-inherit no-underline">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
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
            {f'<div class="p-5 bg-yellow-50 text-center text-yellow-900 font-bold border-b border-yellow-100 text-xl italic">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
        </div>
        <section class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-10">
            <div class="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
                <h3 class="text-2xl font-black text-slate-800 uppercase tracking-tight">{month_label}</h3>
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

def generate():
    # Setup Nepal Time
    npt_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=45)
    today_ad = npt_now.strftime('%Y-%m-%d')
    
    if not os.path.exists(JSON_SOURCE):
        print(f"Error: {JSON_SOURCE} not found.")
        return

    with open(JSON_SOURCE, 'r') as f:
        data = json.load(f)
        if isinstance(data, list): data = data[0]

    all_days = []
    
    for month_data in data['calendar_data']:
        month_label = " / ".join(month_data['bs_months'])
        
        for day in month_data['days']:
            all_days.append(day)
            html_content = get_html_layout(day, month_data['days'], today_ad, month_label)
            
            # Save the file (e.g., 2082-09-28.html) in the root directory
            # This ensures https://today.singhyogendra.com.np/2082-09-28.html works
            with open(f"{day['bs']}.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Create/Update index.html if this matches today's AD date
            if day['ad'] == today_ad:
                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(html_content)

    # Generate Sitemap
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    u_home = ET.SubElement(urlset, "url")
    ET.SubElement(u_home, "loc").text = f"{DOMAIN}/"
    
    for day in all_days:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = f"{DOMAIN}/{day['bs']}.html"
    
    tree = ET.ElementTree(urlset)
    tree.write("sitemap.xml", encoding='utf-8', xml_declaration=True)
    
    print(f"Success! Generated {len(all_days)} pages and sitemap.xml")

if __name__ == "__main__":
    generate()
