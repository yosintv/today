import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

def generate_sitemap(all_days):
    """Generates a proper sitemap.xml for all date pages."""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    domain = "https://today.singhyogendra.com.np"
    
    # Add Home
    u_home = ET.SubElement(urlset, "url")
    ET.SubElement(u_home, "loc").text = f"{domain}/"
    ET.SubElement(u_home, "changefreq").text = "daily"
    
    # Add each Day
    for day in all_days:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = f"{domain}/{day['bs']}.html"
        ET.SubElement(u, "changefreq").text = "monthly"
        
    tree = ET.ElementTree(urlset)
    tree.write("sitemap.xml", encoding='utf-8', xml_declaration=True)

def get_html_layout(target_day, data, today_ad, bs_month_name, bs_year):
    """Generates the full HTML for a specific day, populating its unique data."""
    
    # Dynamic Meta Info based on the day clicked
    title = f"Nepali Date: {target_day['bs']} | {target_day['ad']} - {target_day['event'] if target_day.get('event') else 'Nepali Patro'}"
    description = f"Today's date details: BS {target_day['bs']} and AD {target_day['ad']}. Day: {target_day['day']}. Event: {target_day['event'] if target_day.get('event') else 'No specific event'}."

    # Build Calendar Days (The Grid)
    calendar_html = ""
    for day in data['days']:
        # Highlight the day currently being viewed
        is_viewing = "ring-4 ring-red-500 shadow-lg" if day['bs'] == target_day['bs'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        calendar_html += f"""
        <a href="{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_viewing} transition-all block text-inherit no-underline">
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
        <meta name="keywords" content="Nepali date today, {target_day['bs']}, {target_day['ad']}, Aaja ko gate, Nepali calendar {bs_month_name}">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 text-slate-900 antialiased">
        <header class="max-w-4xl mx-auto px-4 py-10 text-center">
            <h1 class="text-4xl font-extrabold text-slate-800 tracking-tight mb-2"><a href="/">Nepali Patro</a></h1>
            <p class="text-slate-500">Your daily digital calendar for Nepal</p>
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
                    <h3 class="text-2xl font-bold text-slate-800">{bs_month_name} {bs_year} / {data['month_info']['ad_month']}</h3>
                    <div class="flex items-center bg-slate-100 p-1 rounded-full">
                        <button id="toggleBS" class="px-6 py-2 rounded-full bg-white shadow-sm text-sm font-bold transition-all">BS</button>
                        <button id="toggleAD" class="px-6 py-2 rounded-full text-sm font-medium transition-all">AD</button>
                    </div>
                </div>
                <div class="grid grid-cols-7 gap-2">
                    {calendar_html}
                </div>
            </section>

            <section class="prose prose-slate max-w-none mb-10 bg-white p-6 rounded-3xl border border-slate-100">
                <h2 class="text-xl font-bold mb-4">Date Information</h2>
                <p>The Nepali date (BS) for this day is <strong>{target_day['bs']}</strong>. On the English calendar (AD), it is <strong>{target_day['ad']}</strong>. The day of the week is <strong>{target_day['day']}</strong>.</p>
            </section>
        </main>

        <footer class="text-center py-10 text-slate-400 text-sm">
            <p>© 2026 today.singhyogendra.com.np</p>
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
    
    file_path = f"date/{file_key}.json"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        raw_data = json.load(f)
        data = raw_data[0] if isinstance(raw_data, list) else raw_data

    bs_month_name = data['month_info']['bs_months'][0].split()[0]
    bs_year = data['month_info']['bs_months'][0].split()[1]

    # Generate sitemap.xml
    generate_sitemap(data['days'])

    # Create ALL individual day pages and index.html
    for day in data['days']:
        content = get_html_layout(day, data, today_ad, bs_month_name, bs_year)
        
        # This creates 2082-08-15.html, etc.
        with open(f"{day['bs']}.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        # This creates the homepage
        if day['ad'] == today_ad:
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(content)

    print(f"Generated index.html + {len(data['days'])} pages.")

if __name__ == "__main__":
    generate_html()
