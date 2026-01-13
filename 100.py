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

def get_html_template(target_day, all_days, month_label, ad_month):
    # Prepare Events List (Next 10 upcoming)
    upcoming_events = [d for d in all_days if d.get('event') and d['ad'] >= target_day['ad']][:10]
    
    # Prepare FAQ Data
    faqs = [
        {"q": f"Aaja k gate ho? (What is the Nepali date today?)", "a": f"Aaja ko gate {target_day['bs']} ho ({target_day['day']})."},
        {"q": f"What is today's English date?", "a": f"Today is {target_day['ad']} (AD)."},
        {"q": f"Is there any event today ({target_day['bs']})?", "a": f"{target_day.get('event') if target_day.get('event') else 'There are no major public events today.'}"},
        {"q": f"Which Nepali month is it now?", "a": f"It is currently {month_label.split('/')[0]}."},
        {"q": f"What is the next big festival?", "a": f"The next event is {upcoming_events[0]['event']} on {upcoming_events[0]['bs']}." if upcoming_events else "Please check our monthly calendar for details."},
        {"q": "How to convert BS to AD?", "a": "You can use our daily updated calendar to find accurate conversion for any date in 2082/2083."},
        {"q": f"How many days in {ad_month} 2026?", "a": f"There are {len(all_days)} days in this calendar block."},
        {"q": "Is today a public holiday in Nepal?", "a": "Public holidays usually coincide with major events. Check the red dots on our calendar grid."},
        {"q": "Where can I find tomorrow's Nepali date?", "a": "You can click on the next box in our grid to see details for tomorrow."},
        {"q": "Who provides this Nepali Patro?", "a": "This service is provided by Singh Yogendra to help users track Nepali dates and festivals."}
    ]

    # Build Grid
    calendar_html = ""
    for day in all_days:
        is_viewing = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['ad'] == target_day['ad'] else "hover:bg-gray-50"
        event_dot = '<span class="block w-1.5 h-1.5 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        calendar_html += f'''
        <a href="{DOMAIN}/{day['bs']}.html" class="p-4 border border-gray-100 rounded-xl text-center {is_viewing} transition-all block no-underline">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
            <div class="text-xl font-bold text-slate-800 bs-date-val">{day['bs'].split("-")[-1]}</div>
            <div class="text-xs text-gray-500 ad-date-val hidden">{day['ad'].split("-")[-1]}</div>
            {event_dot}
        </a>'''

    # Build FAQ HTML and Schema
    faq_html = ""
    faq_schema = []
    for f in faqs:
        faq_html += f'<div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm"><h4 class="font-bold text-slate-800 mb-2">Q: {f["q"]}</h4><p class="text-slate-600">A: {f["a"]}</p></div>'
        faq_schema.append({"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}})

    # Template
    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nepali Date Today: {target_day['bs']} | {target_day['ad']} - Nepali Patro</title>
    <meta name="description" content="Aaja ko gate: {target_day['bs']}. English Date: {target_day['ad']}. Full Nepali calendar for {month_label} with festivals and holidays.">
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": {json.dumps(faq_schema)}
    }}
    </script>
</head>
<body class="bg-slate-50 text-slate-900 antialiased">
    <header class="max-w-4xl mx-auto px-4 py-8 text-center">
        <h1 class="text-3xl font-black text-slate-800 tracking-tight"><a href="{DOMAIN}">NEPALI PATRO</a></h1>
    </header>

    <main class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-[2rem] shadow-2xl overflow-hidden mb-8 border border-slate-100">
            <div class="bg-red-600 p-8 text-white text-center">
                <p class="text-sm font-bold uppercase tracking-widest opacity-80 mb-2">Aaja ko Nepali Date</p>
                <div class="text-7xl font-black mb-4 tracking-tighter">{target_day['bs']}</div>
                <div class="flex flex-wrap justify-center gap-4 text-lg opacity-90 font-medium">
                    <span>{target_day['ad']}</span> | <span>{target_day['day']}</span>
                </div>
            </div>
            
            <div class="grid grid-cols-2 divide-x divide-slate-100 border-b border-slate-100">
                <div class="p-4 text-center">
                    <p class="text-[10px] font-bold text-slate-400 uppercase">Nepal Time (NPT)</p>
                    <div id="npt-clock" class="text-xl font-mono font-bold text-red-600">--:--:--</div>
                </div>
                <div class="p-4 text-center">
                    <p class="text-[10px] font-bold text-slate-400 uppercase">Your Local Time</p>
                    <div id="local-clock" class="text-xl font-mono font-bold text-slate-800">--:--:--</div>
                </div>
            </div>
            {f'<div class="p-6 bg-yellow-50 text-center text-yellow-800 font-bold text-xl italic">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
        </div>

        <section class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 mb-8">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-black text-slate-800 uppercase tracking-tight">{month_label}</h3>
                <div class="flex bg-slate-100 p-1 rounded-full">
                    <button id="toggleBS" class="px-4 py-1.5 rounded-full bg-white shadow-sm text-xs font-bold">BS</button>
                    <button id="toggleAD" class="px-4 py-1.5 rounded-full text-xs font-medium">AD</button>
                </div>
            </div>
            <div class="grid grid-cols-7 gap-2">{calendar_html}</div>
        </section>

        <section class="mb-8">
            <h3 class="text-xl font-black text-slate-800 mb-4 px-2 uppercase tracking-tight">Upcoming Events</h3>
            <div class="grid gap-3">
                {"".join([f'<div class="bg-white p-4 rounded-2xl border border-slate-100 flex justify-between items-center shadow-sm"><span class="font-bold">{e["event"]}</span><span class="text-sm text-slate-500 font-medium">{e["bs"]}</span></div>' for e in upcoming_events])}
            </div>
        </section>

        <section class="mb-12">
            <h3 class="text-xl font-black text-slate-800 mb-6 px-2 uppercase tracking-tight">Frequently Asked Questions</h3>
            <div class="grid gap-4">{faq_html}</div>
        </section>
    </main>

    <footer class="text-center py-12 border-t border-slate-200 text-slate-400 text-sm">
        <p class="font-bold text-slate-500 mb-2">Nepali Patro © 2026 Today Singh Yogendra</p>
        <p>Providing accurate Aaja ko Gate and English to Nepali date conversion.</p>
    </footer>

    <script>
        // Clock Logic
        function updateClocks() {{
            const now = new Date();
            document.getElementById('local-clock').innerText = now.toLocaleTimeString();
            
            const npt = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (5.75 * 3600000));
            document.getElementById('npt-clock').innerText = npt.toLocaleTimeString();
        }}
        setInterval(updateClocks, 1000); updateClocks();

        // Toggle Logic
        const tBS = document.getElementById('toggleBS'), tAD = document.getElementById('toggleAD');
        const bsV = document.querySelectorAll('.bs-date-val'), adV = document.querySelectorAll('.ad-date-val');
        tAD.addEventListener('click', () => {{
            tAD.classList.add('bg-white','shadow-sm','font-bold'); tBS.classList.remove('bg-white','shadow-sm','font-bold');
            bsV.forEach(el => el.classList.add('hidden')); adV.forEach(el => el.classList.remove('hidden'));
        }});
        tBS.addEventListener('click', () => {{
            tBS.classList.add('bg-white','shadow-sm','font-bold'); tAD.classList.remove('bg-white','shadow-sm','font-bold');
            adV.forEach(el => el.classList.add('hidden')); bsV.forEach(el => bsV.forEach(el => el.classList.remove('hidden')));
            adV.forEach(el => el.classList.add('hidden'));
        }});
    </script>
</body>
</html>"""

def build_site():
    with open(JSON_FILE, 'r') as f:
        content = json.load(f)
        data = content[0] if isinstance(content, list) else content

    sitemap_urls = [f"{DOMAIN}/"]
    for m_data in data['calendar_data']:
        label = f"{' / '.join(m_data['bs_months'])} / {m_data['month']}"
        for day in m_data['days']:
            html = get_html_template(day, m_data['days'], label, m_data['month'])
            # Save file at root for short URL
            filename = f"{day['bs']}.html"
            with open(filename, "w", encoding='utf-8') as f_out: f_out.write(html)
            sitemap_urls.append(f"{DOMAIN}/{filename}")
            if day['ad'] == TODAY_AD:
                with open("index.html", "w", encoding='utf-8') as f_idx: f_idx.write(html)

    # Simple Sitemap
    sm = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for u in sorted(list(set(sitemap_urls))): sm += f'<url><loc>{u}</loc><changefreq>daily</changefreq></url>'
    with open("sitemap.xml", "w") as f: f.write(sm + '</urlset>')

if __name__ == "__main__": build_site()
