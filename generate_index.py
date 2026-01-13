import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
DOMAIN = "https://today.singhyogendra.com.np"
JSON_FILE = "date/2026.json"
# Nepal Time Offset (UTC+5:45)
LOCAL_OFFSET = timezone(timedelta(hours=5, minutes=45))
NOW = datetime.now(LOCAL_OFFSET)
TODAY_AD = NOW.strftime('%Y-%m-%d')

def get_html_template(target_day, month_days, month_label, ad_month):
    """
    Combines the SEO-optimized design with dynamic pathing.
    """
    title = f"Nepali Date Today: {target_day['bs']} | {target_day['ad']} - Nepali Patro"
    description = f"Check Nepali date {target_day['bs']} ({target_day['day']}). Event: {target_day.get('event') or 'Regular Day'}. View {month_label} calendar."

    # Build Calendar Grid (The "Weekly Menu" logic from Cricfoot)
    calendar_html = ""
    for day in month_days:
        is_viewing = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['ad'] == target_day['ad'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        # Every date links to its own unique .html page
        calendar_html += f'''
        <a href="{DOMAIN}/{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_viewing} transition-all block no-underline">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-slate-800 bs-date-val">{day['bs'].split("-")[-1]}</div>
            <div class="text-xs text-gray-500 ad-date-val hidden">{day['ad'].split("-")[-1]}</div>
            {event_dot}
        </a>'''

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
        <h1 class="text-4xl font-extrabold text-slate-800 tracking-tight mb-2"><a href="{DOMAIN}">Nepali Patro</a></h1>
        <p class="text-slate-500">Digital Calendar & Aaja ko Gate</p>
    </header>
    <main class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-10 border border-slate-100">
            <div class="bg-red-600 p-8 text-white text-center">
                <h2 class="text-lg font-medium opacity-90 uppercase tracking-widest">Selected Date</h2>
                <div class="text-7xl font-black my-2 tracking-tighter">{target_day['bs']}</div>
                <p class="text-2xl opacity-90">{target_day['ad']} | {target_day['day']}</p>
            </div>
            {f'<div class="p-5 bg-yellow-50 text-center text-yellow-900 font-bold border-b border-yellow-100 text-xl italic">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
        </div>
        <section class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-10">
            <div class="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
                <h3 class="text-2xl font-black text-slate-800 uppercase tracking-tight">{month_label} / {ad_month}</h3>
                <div class="flex items-center bg-slate-100 p-1 rounded-full">
                    <button id="toggleBS" class="px-6 py-2 rounded-full bg-white shadow-sm text-sm font-bold transition-all">BS</button>
                    <button id="toggleAD" class="px-6 py-2 rounded-full text-sm font-medium transition-all">AD</button>
                </div>
            </div>
            <div class="grid grid-cols-7 gap-2">{calendar_html}</div>
        </section>
    </main>
    <footer class="text-center py-10 text-slate-400 text-sm">
        <p>© {NOW.year} Today Singh Yogendra. All Rights Reserved.</p>
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

def build_site():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return

    with open(JSON_FILE, 'r') as f:
        raw_data = json.load(f)
        data = raw_data[0] if isinstance(raw_data, list) else raw_data

    sitemap_urls = [f"{DOMAIN}/"]
    
    # Iterate through each month block
    for month_data in data['calendar_data']:
        month_label = " / ".join(month_data['bs_months'])
        ad_month = month_data['month']
        
        # Iterate through each day in the month
        for day in month_data['days']:
            # Generate the specific day HTML
            html_content = get_html_template(day, month_data['days'], month_label, ad_month)
            
            # Save individual date page
            filename = f"{day['bs']}.html"
            with open(filename, "w", encoding='utf-8') as f_out:
                f_out.write(html_content)
            
            sitemap_urls.append(f"{DOMAIN}/{filename}")

            # If this is today's real date, set as index.html
            if day['ad'] == TODAY_AD:
                with open("index.html", "w", encoding='utf-8') as f_idx:
                    f_idx.write(html_content)

    # --- SITEMAP GENERATION (Cricfoot Logic) ---
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for url in sorted(list(set(sitemap_urls))):
        sitemap_content += f'<url><loc>{url}</loc><lastmod>{NOW.strftime("%Y-%m-%d")}</lastmod><changefreq>daily</changefreq></url>'
    sitemap_content += '</urlset>'
    
    with open("sitemap.xml", "w", encoding='utf-8') as sm:
        sm.write(sitemap_content)

    print(f"Done! {len(sitemap_urls)} pages generated in sitemap.")

if __name__ == "__main__":
    build_site()
