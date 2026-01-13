import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
DOMAIN = "https://today.singhyogendra.com.np"
JSON_FILE = "date/2026.json"
LOCAL_OFFSET = timezone(timedelta(hours=5, minutes=45))
NOW = datetime.now(LOCAL_OFFSET)
TODAY_AD = NOW.strftime('%Y-%m-%d')

def get_html_template(target_day, month_days, month_label, ad_month):
    title = f"Nepali Date: {target_day['bs']} | {target_day['ad']}"
    
    calendar_html = ""
    for day in month_days:
        is_viewing = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['ad'] == target_day['ad'] else "hover:bg-gray-50"
        
        # This creates the short URL you want: domain.com/2082-09-17.html
        page_url = f"{DOMAIN}/{day['bs']}.html"
        
        calendar_html += f'''
        <a href="{page_url}" class="p-4 border border-gray-100 rounded-xl text-center {is_viewing} transition-all block no-underline">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-slate-800">{day['bs'].split("-")[-1]}</div>
        </a>'''

    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 antialiased">
    <header class="max-w-4xl mx-auto px-4 py-10 text-center">
        <h1 class="text-4xl font-black text-slate-800 tracking-tight"><a href="{DOMAIN}">Nepali Patro</a></h1>
    </header>
    <main class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-10 border border-slate-100 text-center">
            <div class="bg-red-600 p-10 text-white">
                <div class="text-8xl font-black tracking-tighter">{target_day['bs']}</div>
                <p class="text-2xl mt-4 font-medium">{target_day['ad']} | {target_day['day']}</p>
            </div>
            {f'<div class="p-6 bg-yellow-50 text-yellow-900 font-bold text-xl border-b border-yellow-100">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
        </div>
        <section class="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 mb-10">
            <h3 class="text-2xl font-black text-slate-800 mb-8 uppercase tracking-tight">{month_label}</h3>
            <div class="grid grid-cols-7 gap-3">{calendar_html}</div>
        </section>
    </main>
</body>
</html>"""

def build_site():
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)[0]

    sitemap_urls = [f"{DOMAIN}/"]
    
    for month_data in data['calendar_data']:
        for day in month_data['days']:
            # Generate the HTML content
            html_content = get_html_template(day, month_data['days'], " / ".join(month_data['bs_months']), month_data['month'])
            
            # SAVE AT ROOT to ensure URL is domain.com/2082-09-17.html
            file_name = f"{day['bs']}.html"
            
            with open(file_name, "w", encoding='utf-8') as f_out:
                f_out.write(html_content)
            
            sitemap_urls.append(f"{DOMAIN}/{file_name}")

            # Update index.html for the current day
            if day['ad'] == TODAY_AD:
                with open("index.html", "w", encoding='utf-8') as f_idx:
                    f_idx.write(html_content)

    # Generate Sitemap
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in sorted(list(set(sitemap_urls))):
        u = ET.SubElement(root, "url")
        ET.SubElement(u, "loc").text = url
    ET.ElementTree(root).write("sitemap.xml", encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    build_site()
