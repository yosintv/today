import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
DOMAIN = "https://today.singhyogendra.com.np"
JSON_SOURCE = "date/2026.json"
LOCAL_OFFSET = timezone(timedelta(hours=5, minutes=45)) # Nepal Time
NOW = datetime.now(LOCAL_OFFSET)
TODAY_AD = NOW.strftime('%Y-%m-%d')

def get_html_layout(target_day, month_days, month_label):
    """Template logic similar to your Cricfoot script"""
    title = f"Nepali Date: {target_day['bs']} | {target_day['ad']} - {target_day.get('event') or 'Nepali Patro'}"
    
    # Build Calendar Grid for the UI
    calendar_html = ""
    for day in month_days:
        # Link logic: Points to the folder-based URL
        is_active = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['bs'] == target_day['bs'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        # We assume the URL structure will be /year/month/day/ but for simplicity 
        # let's keep it root-level file based like your previous request:
        calendar_html += f'''
        <a href="{DOMAIN}/{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_active} transition-all block no-underline">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-slate-800">{day['bs'].split("-")[-1]}</div>
            {event_dot}
        </a>'''

    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900">
    <header class="max-w-4xl mx-auto px-4 py-8 text-center">
        <h1 class="text-3xl font-black text-slate-800"><a href="{DOMAIN}">NEPALI PATRO</a></h1>
    </header>
    <main class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-8 border border-slate-100">
            <div class="bg-red-600 p-8 text-white text-center">
                <div class="text-7xl font-black mb-2">{target_day['bs']}</div>
                <p class="text-2xl opacity-90">{target_day['ad']} | {target_day['day']}</p>
            </div>
            {f'<div class="p-5 bg-yellow-50 text-center text-yellow-900 font-bold text-xl">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
        </div>
        
        <section class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-8">
            <h3 class="text-xl font-bold mb-6 text-slate-800 uppercase tracking-wider">{month_label}</h3>
            <div class="grid grid-cols-7 gap-2">{calendar_html}</div>
        </section>
    </main>
</body>
</html>"""

def run_generator():
    if not os.path.exists(JSON_SOURCE):
        print("JSON source missing.")
        return

    with open(JSON_SOURCE, 'r') as f:
        full_data = json.load(f)
        if isinstance(full_data, list): full_data = full_data[0]

    sitemap_urls = []

    for month_block in full_data['calendar_data']:
        month_label = " / ".join(month_block['bs_months'])
        
        for day in month_block['days']:
            html_content = get_html_layout(day, month_block['days'], month_label)
            
            # 1. Create specific day file (e.g., 2082-09-28.html)
            filename = f"{day['bs']}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            sitemap_urls.append(f"{DOMAIN}/{filename}")

            # 2. If it's today's AD date, generate index.html
            if day['ad'] == TODAY_AD:
                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                sitemap_urls.append(f"{DOMAIN}/")

    # 3. Generate Sitemap (Cricfoot logic)
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for url in list(set(sitemap_urls)):
        sitemap_content += f'<url><loc>{url}</loc><lastmod>{NOW.strftime("%Y-%m-%d")}</lastmod></url>'
    sitemap_content += '</urlset>'
    
    with open("sitemap.xml", "w", encoding='utf-8') as sm: 
        sm.write(sitemap_content)

    print(f"Patro Generated: {len(sitemap_urls)} pages created.")

if __name__ == "__main__":
    run_generator()
