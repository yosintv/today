import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

DOMAIN = "https://today.singhyogendra.com.np"

def generate_sitemap(all_days):
    """Generates sitemap.xml for all created pages."""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Home
    url_home = ET.SubElement(urlset, "url")
    ET.SubElement(url_home, "loc").text = f"{DOMAIN}/"
    ET.SubElement(url_home, "changefreq").text = "daily"
    ET.SubElement(url_home, "priority").text = "1.0"
    
    # Individual Days
    for day in all_days:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{DOMAIN}/{day['bs']}.html"
        ET.SubElement(url, "changefreq").text = "monthly"
        ET.SubElement(url, "priority").text = "0.7"
        
    tree = ET.ElementTree(urlset)
    tree.write("sitemap.xml", encoding='utf-8', xml_declaration=True)

def get_html_content(target_day, data, today_ad, prev_month_label, next_month_label):
    """Returns the full HTML string for a specific day's page."""
    bs_month_name = data['month_info']['bs_months'][0].split()[0]
    bs_year = data['month_info']['bs_months'][0].split()[1]
    
    title = f"Nepali Date Today: {target_day['bs']} | {target_day['ad']} - Nepali Patro"
    description = f"Check today's Nepali date (Aaja ko gate): {target_day['bs']}. Full calendar for {bs_month_name} {bs_year} with events."

    # Build Calendar Grid
    calendar_html = ""
    for day in data['days']:
        # Highlight target day for this specific page
        is_target = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['bs'] == target_day['bs'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        calendar_html += f"""
        <a href="{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_target} transition-all block">
            <div class="text-xs text-gray-400 font-medium">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-gray-800 bs-date-val">{day['bs'].split('-')[-1]}</div>
            <div class="text-xs text-gray-500 ad-date-val hidden">{day['ad'].split('-')[-1]}</div>
            {event_dot}
        </a>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ne">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="description" content="{description}">
        <meta name="keywords" content="Nepali date today, Today Nepali date, Nepali calendar {bs_month_name} {bs_year}, Aaja ko gate, Aaja ko tarikh, Aaja k gate ho?, Nepali patro">
        <script src="https://cdn.tailwindcss.com"></script>
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:url" content="{DOMAIN}/{target_day['bs']}.html">
        <meta property="og:type" content="website">
    </head>
    <body class="bg-slate-50 text-slate-900 antialiased">
        <header class="max-w-4xl mx-auto px-4 py-8 text-center">
            <a href="/" class="text-4xl font-extrabold text-slate-800 tracking-tight block">Nepali Patro</a>
        </header>

        <main class="max-w-4xl mx-auto px-4">
            <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-10 border border-slate-100">
                <div class="bg-red-600 p-8 text-white text-center">
                    <h2 class="text-lg font-medium opacity-90 uppercase tracking-widest">Aaja ko Gate</h2>
                    <div class="text-7xl font-black my-2 tracking-tighter">{target_day['bs']}</div>
                    <p class="text-xl opacity-90 font-semibold">{target_day['ad']} | {target_day['day']}</p>
                </div>
                {f'<div class="p-4 bg-yellow-50 text-center text-yellow-800 font-bold border-b border-yellow-100 italic">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
            </div>

            <section class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-10">
                <div class="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4 border-b pb-4">
                    <div class="flex items-center gap-4">
                        <span class="text-gray-300 font-bold">&larr; {prev_month_label}</span>
                        <h3 class="text-2xl font-black text-slate-800 uppercase">{bs_month_name} {bs_year}</h3>
                        <span class="text-gray-300 font-bold">{next_month_label} &rarr;</span>
                    </div>
                    
                    <div class="flex items-center bg-slate-100 p-1 rounded-full">
                        <button id="toggleBS" class="px-6 py-2 rounded-full bg-white shadow-sm text-sm font-bold transition-all">BS</button>
                        <button id="toggleAD" class="px-6 py-2 rounded-full text-sm font-medium transition-all">AD</button>
                    </div>
                </div>

                <div class="grid grid-cols-7 gap-2">
                    {calendar_html}
                </div>
            </section>

            <section class="prose prose-slate max-w-none mb-10 bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
                <h2 class="text-2xl font-bold mb-4">FAQ: Aaja ko Gate (Nepali Date Today)</h2>
                <div class="space-y-6">
                    <div>
                        <p class="font-bold text-red-600 mb-1">Aaja k gate ho? (What is the Nepali date today?)</p>
                        <p class="text-slate-600">Aaja ko gate <strong>{target_day['bs']}</strong> ho. This is the date in the Bikram Sambat calendar.</p>
                    </div>
                    <div>
                        <p class="font-bold text-red-600 mb-1">Aaja ko tarikh k ho? (What is the English date today?)</p>
                        <p class="text-slate-600">The English date (tarikh) is <strong>{target_day['ad']}</strong> ({target_day['day']}).</p>
                    </div>
                </div>
            </section>
        </main>

        <footer class="text-center py-10 text-slate-400 text-sm">
            <p>© 2026 today.singhyogendra.com.np | Nepali Patro Daily</p>
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
    </html>
    """

def generate_html():
    npt_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=45)
    today_ad = npt_now.strftime('%Y-%m-%d')
    file_key = npt_now.strftime('%Y%m')
    
    # Calculate Labels
    prev_month_label = (npt_now.replace(day=1) - timedelta(days=1)).strftime('%B')
    next_month_label = (npt_now.replace(day=28) + timedelta(days=5)).strftime('%B')
    
    file_path = f"date/{file_key}.json"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        raw_data = json.load(f)
        data = raw_data[0] if isinstance(raw_data, list) else raw_data

    # 1. Create Sitemap
    generate_sitemap(data['days'])

    # 2. Create individual .html files for every day in the JSON
    for day in data['days']:
        page_content = get_html_content(day, data, today_ad, prev_month_label, next_month_label)
        
        # Save each day as its own slug
        with open(f"{day['bs']}.html", "w", encoding="utf-8") as f:
            f.write(page_content)
        
        # If the day being processed is actually TODAY, also save it as index.html
        if day['ad'] == today_ad:
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(page_content)

    print(f"Success: Generated index.html and {len(data['days'])} day pages.")

if __name__ == "__main__":
    generate_html()
