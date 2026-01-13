import json
import os
from datetime import datetime, timedelta, timezone

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

    today_data = next((d for d in data['days'] if d['ad'] == today_ad), data['days'][0])
    bs_month_name = data['month_info']['bs_months'][0].split()[0]
    bs_year = data['month_info']['bs_months'][0].split()[1]

    # Meta Info
    title = f"Nepali Date Today: {today_data['bs']} | {today_data['ad']} - Nepali Patro"
    description = f"Check today's Nepali date (Aaja ko gate): {today_data['bs']}. Get full Nepali calendar for {bs_month_name} {bs_year} with events and holidays."

    # Build Calendar Days for HTML
    calendar_html = ""
    for day in data['days']:
        is_today = "ring-4 ring-red-500 shadow-lg" if day['ad'] == today_ad else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        
        calendar_html += f"""
        <div class="p-4 border border-gray-100 rounded-xl text-center {is_today} transition-all">
            <div class="text-xs text-gray-400 font-medium">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-gray-800 bs-date-val">{day['bs'].split('-')[-1]}</div>
            <div class="text-xs text-gray-500 ad-date-val hidden">{day['ad'].split('-')[-1]}</div>
            {event_dot}
        </div>
        """

    html_content = f"""
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
        <meta property="og:url" content="https://today.singhyogendra.com.np">
        <meta property="og:type" content="website">

        <script type="application/ld+json">
        {{
          "@context": "https://schema.org",
          "@type": "Event",
          "name": "Today's Nepali Date",
          "startDate": "{today_ad}",
          "description": "{today_data['event'] if today_data.get('event') else 'Regular Day'}"
        }}
        </script>
    </head>
    <body class="bg-slate-50 text-slate-900 antialiased">

        <header class="max-w-4xl mx-auto px-4 py-10 text-center">
            <h1 class="text-4xl font-extrabold text-slate-800 tracking-tight mb-2">Nepali Patro</h1>
            <p class="text-slate-500">Your daily digital calendar for Nepal</p>
        </header>

        <main class="max-w-4xl mx-auto px-4">
            <div class="bg-white rounded-3xl shadow-xl overflow-hidden mb-10 border border-slate-100">
                <div class="bg-red-600 p-6 text-white text-center">
                    <h2 class="text-lg font-medium opacity-90">Aaja ko Gate (Today's Date)</h2>
                    <div class="text-6xl font-black my-2">{today_data['bs']}</div>
                    <p class="text-xl opacity-90">{today_data['ad']} | {today_data['day']}</p>
                </div>
                {f'<div class="p-4 bg-yellow-50 text-center text-yellow-800 font-bold border-b border-yellow-100">✨ {today_data["event"]}</div>' if today_data.get('event') else ''}
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

            <section class="prose prose-slate max-w-none mb-10">
                <h2 class="text-2xl font-bold mb-4">Frequently Asked Questions (FAQ)</h2>
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl shadow-sm border">
                        <p class="font-bold">Aaja k gate ho? (What is the Nepali date today?)</p>
                        <p class="text-slate-600">Aaja ko gate {today_data['bs']} ho.</p>
                    </div>
                    <div class="bg-white p-4 rounded-xl shadow-sm border">
                        <p class="font-bold">Aaja ko tarikh k ho? (What is the English date today?)</p>
                        <p class="text-slate-600">Today's English date (tarikh) is {today_data['ad']}.</p>
                    </div>
                    <div class="bg-white p-4 rounded-xl shadow-sm border">
                        <p class="font-bold">What are the upcoming festivals in {bs_month_name}?</p>
                        <p class="text-slate-600">This month marks several events including {", ".join([d['event'] for d in data['days'] if d.get('event')][:3])}.</p>
                    </div>
                </div>
            </section>
        </main>

        <footer class="text-center py-10 text-slate-400 text-sm">
            <p>© 2026 Today Singh Yogendra. All Rights Reserved.</p>
            <p>Nepali Date Today | Today Nepali Date | Nepali Patro</p>
        </footer>

        <script>
            const toggleBS = document.getElementById('toggleBS');
            const toggleAD = document.getElementById('toggleAD');
            const bsVals = document.querySelectorAll('.bs-date-val');
            const adVals = document.querySelectorAll('.ad-date-val');

            toggleAD.addEventListener('click', () => {{
                toggleAD.classList.add('bg-white', 'shadow-sm', 'font-bold');
                toggleBS.classList.remove('bg-white', 'shadow-sm', 'font-bold');
                bsVals.forEach(el => el.classList.add('hidden'));
                adVals.forEach(el => el.classList.remove('hidden'));
            }});

            toggleBS.addEventListener('click', () => {{
                toggleBS.classList.add('bg-white', 'shadow-sm', 'font-bold');
                toggleAD.classList.remove('bg-white', 'shadow-sm', 'font-bold');
                adVals.forEach(el => el.classList.add('hidden'));
                bsVals.forEach(el => el.classList.remove('hidden'));
            }});
        </script>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("SEO-Optimized index.html generated.")

if __name__ == "__main__":
    generate_html()
