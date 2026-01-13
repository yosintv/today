import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

DOMAIN = "https://today.singhyogendra.com.np"
JSON_FILE = "date/2026.json"

def get_html_layout(target_day, month_days, today_ad, month_label, ad_month_label):
    """Generates the full HTML for a specific day with the original CSS and grid."""
    
    title = f"Nepali Date Today: {target_day['bs']} | {target_day['ad']} - Nepali Patro"
    description = f"Check today's Nepali date (Aaja ko gate): {target_day['bs']}. Get full Nepali calendar for {month_label} with events."

    # Build Calendar Grid for the specific month
    calendar_html = ""
    for day in month_days:
        # Highlight the specific page date
        is_active = "ring-4 ring-red-500 shadow-lg" if day['bs'] == target_day['bs'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        calendar_html += f"""
        <a href="{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_active} transition-all block text-inherit no-underline">
            <div class="text-xs text-gray-400 font-medium">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-gray-800 bs-date-val">{day['bs'].split('-')[-1]}</div>
            <div class="text-xs text-gray-500 ad-date-val hidden">{day['ad'].split('-')[-1]}</div>
            {event_dot}
        </a>"""

    return f"""
    <!DOCTYPE html>
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
            <p class="text-slate-500">Your daily digital calendar for Nepal</p>
        </header>

        <main class="max-w-4xl mx-auto px-4">
            <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-10 border border-slate-100">
                <div class="bg-red-600 p-6 text-white text-center">
                    <h2 class="text-lg font-medium opacity-90">Aaja ko Gate (Today's Date)</h2>
                    <div class="text-6xl font-black my-2">{target_day['bs']}</div>
                    <p class="text-xl opacity-90">{target_day['ad']} | {target_day['day']}</p>
                </div>
                {f'<div class="p-4 bg-yellow-50 text-center text-yellow-800 font-bold border-b border-yellow-100">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
            </div>

            <section class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-10">
                <div class="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
                    <h3 class="text-2xl font-bold text-slate-800 uppercase tracking-tight">{month_label} / {ad_month_label}</h3>
                    <div class="flex items-center bg-slate-100 p-1 rounded-full">
                        <button id="toggleBS" class="px-6 py-2 rounded-full bg-white shadow-sm text-sm font-bold transition-all">BS</button>
                        <button id="toggleAD" class="px-6 py-2 rounded-full text-sm font-medium transition-all">AD</button>
                    </div>
                </div>
                <div class="grid grid-cols-7 gap-2">{calendar_html}</div>
            </section>
        </main>

        <footer class="text-center py-10 text-slate-400 text-sm">
            <p>© 2026 Today Singh Yogendra. All Rights Reserved.</p>
        </footer>

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

def run():
    npt_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=45)
    today_ad = npt_now.strftime('%Y-%m-%d')
    
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return

    with open(JSON_FILE, 'r') as f:
        full_data = json.load(f)
        if isinstance(full_data, list): full_data = full_data[0]

    all_days = []
    
    # Process each month in the 2026.json
    for month_block in full_data['calendar_data']:
        month_label = " / ".join(month_block['bs_months'])
        ad_month_label = month_block['month']
        
        for day in month_block['days']:
            all_days.append(day)
            html_content = get_html_layout(day, month_block['days'], today_ad, month_label, ad_month_label)
            
            # Create individual file (e.g., 2082-09-28.html)
            with open(f"{day['bs']}.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Update index.html if it matches today's date
            if day['ad'] == today_ad:
                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(html_content)

    # Generate sitemap.xml
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    # Home link
    u_home = ET.SubElement(urlset, "url")
    ET.SubElement(u_home, "loc").text = f"{DOMAIN}/"
    
    for day in all_days:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = f"{DOMAIN}/{day['bs']}.html"
    
    tree = ET.ElementTree(urlset)
    tree.write("sitemap.xml", encoding='utf-8', xml_declaration=True)
    print(f"Successfully generated sitemap and {len(all_days)} date pages.")

if __name__ == "__main__":
    run()
