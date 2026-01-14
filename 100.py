import json 
import os
from datetime import datetime, timedelta, timezone 

# --- CONFIGURATION ---
DOMAIN = "https://today.singhyogendra.com.np"
JSON_FILE = "date/2026.json"
LOCAL_OFFSET = timezone(timedelta(hours=5, minutes=45))
NOW = datetime.now(LOCAL_OFFSET)
TODAY_AD_STR = NOW.strftime('%Y-%m-%d')

def get_html_template(target_day, all_days, month_label, ad_month):
    # Calculations for "Days Left" and Event Navigation
    today_dt = datetime.strptime(TODAY_AD_STR, '%Y-%m-%d')
    upcoming_events = []
    for d in all_days:
        if d.get('event'):
            event_dt = datetime.strptime(d['ad'], '%Y-%m-%d')
            days_left = (event_dt - today_dt).days
            if days_left >= 0:
                upcoming_events.append({
                    "event": d['event'],
                    "bs": d['bs'],
                    "ad": d['ad'],
                    "days_left": days_left
                })
    
    # Sort and pick top 10
    upcoming_events = sorted(upcoming_events, key=lambda x: x['days_left'])[:10]

    # Dynamic SEO Keywords & Title
    event_suffix = f" | {target_day['event']}" if target_day.get('event') else ""
    page_title = f"Nepali Date Today: {target_day['bs']} | {target_day['ad']}{event_suffix} - Nepali Patro"
    meta_desc = f"Find Nepali date today (Aaja ko gate): {target_day['bs']}. Today Nepali date, Nepali calendar {month_label}, Aaja ko tarikh, and upcoming festivals."
    
    # FAQ Generation for Schema and HTML
    faqs = [
        {"q": "Aaja k gate ho? (What is the Nepali date today?)", "a": f"Aaja ko gate {target_day['bs']} ho. It is {target_day['day']}."},
        {"q": "Aaja ko tarikh k ho? (What is the English date today?)", "a": f"Today's English date (tarikh) is {target_day['ad']}."},
        {"q": f"Nepali calendar {month_label} events?", "a": f"The calendar for {month_label} includes events like {', '.join([e['event'] for e in upcoming_events[:3]]) if upcoming_events else 'upcoming festivals'}."},
        {"q": "How many days left for the next festival?", "a": f"The next major event is {upcoming_events[0]['event']} which is in {upcoming_events[0]['days_left']} days." if upcoming_events else "No major festivals upcoming this month."},
        {"q": "What is Nepali Patro?", "a": "Nepali Patro is the traditional solar calendar used in Nepal. You can find Aaja ko gate and Aaja ko tarikh here daily."},
    ]

    # JSON-LD Schema Construction
    faq_json_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]
    }

    # Calendar Grid Construction
    calendar_html = ""
    for day in all_days:
        is_viewing = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['ad'] == TODAY_AD_STR else "hover:bg-gray-50"
        event_dot = '<span class="block w-1 h-1 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        calendar_html += f'''
        <a href="{DOMAIN}/{day['bs']}.html" class="p-2 sm:p-4 border border-gray-100 rounded-xl text-center {is_viewing} transition-all block">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
            <div class="text-lg sm:text-xl font-bold text-slate-800">{day['bs'].split("-")[-1]}</div>
            {event_dot}
        </a>'''

    # Final HTML Template
    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="Nepali date today, Today Nepali date, Nepali calendar {month_label}, Aaja ko gate, Aaja ko tarikh, Aaja k gate ho?, Nepali patro">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{DOMAIN}/{target_day['bs']}.html">
    
    <link rel="icon" type="image/png" href="/favicon.ico">

    <meta property="og:type" content="website">
    <meta property="og:url" content="{DOMAIN}/{target_day['bs']}.html">
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="https://today.singhyogendra.com.np/og-image.jpg">

    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{DOMAIN}/{target_day['bs']}.html">
    <meta property="twitter:title" content="{page_title}">
    <meta property="twitter:description" content="{meta_desc}">
    <meta property="twitter:image" content="https://today.singhyogendra.com.np/og-image.jpg">

    <script type="application/ld+json">{json.dumps(faq_json_ld)}</script>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        body {{ font-family: 'Inter', sans-serif; scroll-behavior: smooth; }}
        #goto-today-btn {{
            position: fixed; bottom: 2rem; right: 1.5rem; z-index: 100;
            display: none; animation: floatBounce 2s infinite;
        }}
        @keyframes floatBounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 antialiased">
    <a id="goto-today-btn" href="{DOMAIN}" class="bg-red-600 text-white px-6 py-4 rounded-full font-black shadow-2xl flex items-center gap-2 hover:bg-red-700 transition-all">
        <span>📅</span> <span>GO TO TODAY</span>
    </a>

    <header class="max-w-4xl mx-auto px-4 py-6 text-center">
        <h1 class="text-2xl font-black text-slate-800 tracking-tighter"><a href="{DOMAIN}">TODAY NEPALI DATE</a></h1>
    </header>

    <main class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-[2rem] shadow-xl overflow-hidden mb-8 border border-slate-100">
            <div class="bg-red-600 p-6 sm:p-10 text-white text-center">
                <p class="text-xs font-bold uppercase tracking-widest opacity-80 mb-2">Aaja ko Nepali Date</p>
                <div id="dynamic-bs" class="text-5xl sm:text-8xl font-black mb-4 tracking-tighter">{target_day['bs']}</div>
                <div class="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-6 text-lg sm:text-2xl opacity-95 font-medium">
                    <span id="dynamic-ad">{target_day['ad']}</span>
                    <span class="hidden sm:block text-red-400">|</span>
                    <span id="dynamic-day">{target_day['day']}</span>
                </div>
            </div>
            
            <div class="grid grid-cols-2 divide-x divide-slate-100 border-b border-slate-100">
                <div class="p-4 text-center">
                    <p class="text-[10px] font-bold text-slate-400 uppercase">Nepal Time</p>
                    <div id="npt-clock" class="text-lg sm:text-xl font-mono font-bold text-red-600">--:--:--</div>
                </div>
                <div class="p-4 text-center">
                    <p class="text-[10px] font-bold text-slate-400 uppercase">Your Time</p>
                    <div id="local-clock" class="text-lg sm:text-xl font-mono font-bold text-slate-800">--:--:--</div>
                </div>
            </div>
            <div id="dynamic-event-container">
                {f'<div class="p-6 bg-yellow-50 text-center text-yellow-800 font-bold text-lg sm:text-xl italic border-b border-yellow-100">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
            </div>
        </div>

        <section class="bg-white p-4 sm:p-8 rounded-[2rem] shadow-sm border border-slate-100 mb-8">
            <h3 class="text-xl font-black text-slate-800 mb-6 uppercase text-center sm:text-left px-2 tracking-tight">{month_label}</h3>
            <div class="grid grid-cols-7 gap-1 sm:gap-3">{calendar_html}</div>
        </section>

        <section class="mb-8" id="upcoming-events-section">
            <h3 class="text-xl font-black text-slate-800 mb-4 flex items-center gap-2 uppercase tracking-tight px-2">
                <span class="w-2 h-6 bg-red-600 rounded-full"></span> Upcoming Events
            </h3>
            <div class="space-y-3 px-1" id="events-list">
                {"".join([f'''
                <a href="{DOMAIN}/{e['bs']}.html" class="bg-white p-4 rounded-2xl border border-slate-100 flex flex-wrap justify-between items-center shadow-sm hover:border-red-300 transition-colors">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-800">{e['event']}</span>
                        <span class="text-xs text-slate-400 font-medium">{e['bs']} ({e['ad']})</span>
                    </div>
                    <div class="bg-red-50 text-red-600 px-3 py-1 rounded-full text-xs font-black mt-2 sm:mt-0">
                        {f'Today' if e['days_left'] == 0 else f'In {e["days_left"]} Days'}
                    </div>
                </a>''' for e in upcoming_events])}
            </div>
        </section>

        <section class="mb-12">
            <h3 class="text-xl font-black text-slate-800 mb-6 uppercase tracking-tight px-2">Commonly Asked Questions</h3>
            <div class="grid gap-4 px-1">
                {"".join([f'<div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm"><h4 class="font-bold text-slate-800 mb-2">Q: {f["q"]}</h4><p class="text-slate-600 italic">A: {f["a"]}</p></div>' for f in faqs])}
            </div>
        </section>
    </main>

    <footer class="text-center py-10 border-t border-slate-200 text-slate-400 text-[10px] sm:text-xs">
        <p class="font-bold text-slate-500 mb-2 uppercase tracking-widest">Nepali date today | Today Nepali date | Nepali Patro</p>
        <p>© 2026 Today Singh Yogendra. All Rights Reserved.</p>
    </footer>

    <script>
        function updateClocks() {{
            const now = new Date();
            document.getElementById('local-clock').innerText = now.toLocaleTimeString();
            const npt = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (5.75 * 3600000));
            document.getElementById('npt-clock').innerText = npt.toLocaleTimeString();
            const nptDateStr = npt.toISOString().split('T')[0];
            const renderedDate = "{target_day['ad']}";
            if (nptDateStr !== renderedDate) {{
                document.getElementById('goto-today-btn').style.display = 'flex';
            }}
        }}
        setInterval(updateClocks, 1000); 
        updateClocks();
    </script>
</body>
</html>"""

def build_site():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        content = json.load(f)
        data = content[0] if isinstance(content, list) else content
    
    files_count = 0
    
    # Process each month
    for m_data in data['calendar_data']:
        label = f"{' / '.join(m_data['bs_months'])} {data.get('year', '')}" 
        
        for day in m_data['days']:
            html = get_html_template(day, m_data['days'], label, m_data['month'])
            filename = f"{day['bs']}.html"
            
            with open(filename, "w", encoding='utf-8') as f_out: 
                f_out.write(html)
            
            files_count += 1
            
            if day['ad'] == TODAY_AD_STR:
                with open("index.html", "w", encoding='utf-8') as f_idx: 
                    f_idx.write(html)
        
    print(f"Success! Generated {files_count} HTML files. index.html updated for {TODAY_AD_STR}.")

if __name__ == "__main__": 
    build_site()
