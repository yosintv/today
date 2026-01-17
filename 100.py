import json 
import os 
from datetime import datetime, timedelta, timezone 

# --- CONFIGURATION ---
DOMAIN = "https://today.singhyogendra.com.np"
SUB_FOLDER = "nepali-date"  # Folder where date files will reside
JSON_FILE = "date/2026.json"
LOCAL_OFFSET = timezone(timedelta(hours=5, minutes=45))

# Logic to fetch current Nepal Time
NOW = datetime.now(LOCAL_OFFSET)
TODAY_AD_STR = NOW.strftime('%Y-%m-%d')

# Ensure the subfolder exists before writing files
if not os.path.exists(SUB_FOLDER):
    os.makedirs(SUB_FOLDER)

def get_html_template(target_day, full_year_days, month_label, ad_month):
    # Calculations for "Days Left" and Event Navigation
    # FIX: We now use full_year_days so past/future pages always show global upcoming events
    today_dt = datetime.strptime(TODAY_AD_STR, '%Y-%m-%d')
    upcoming_events = []
    for d in full_year_days:
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
    
    # Sort and pick top 10 for the UI
    ui_upcoming_events = sorted(upcoming_events, key=lambda x: x['days_left'])[:10]

    # --- DYNAMIC FAQ GENERATION ---
    faqs = [
        {"q": "Aaja k gate ho? (What is the Nepali date today?)", "a": f"Aaja ko gate {target_day['bs']} ho. It is {target_day['day']}."},
        {"q": "Aaja ko tarikh k ho? (What is the English date today?)", "a": f"Today's English date (tarikh) is {target_day['ad']}."},
    ]

    for ev in upcoming_events:
        event_name = ev['event']
        days_rem = ev['days_left']
        bs_date = ev['bs']
        year_bs = bs_date.split('-')[0]
        
        q_text = f"How many days remaining for {event_name} in {year_bs}?"
        if days_rem == 0:
            a_text = f"Today is {event_name}! It falls on {bs_date} BS."
        else:
            a_text = f"There are {days_rem} days remaining for {event_name} {year_bs}. It will be celebrated on {bs_date} BS ({ev['ad']} AD)."
        
        faqs.append({"q": q_text, "a": a_text})

    faqs.append({"q": "What is Nepali Patro?", "a": "Nepali Patro is the traditional solar calendar used in Nepal. You can find Aaja ko gate and Aaja ko tarikh here daily."})

    faq_json_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]
    }

    # Month View Grid (This remains month-specific for the UI)
    # We filter the full_year_days to only show days belonging to this specific month_label
    # (Using the global target_day_context_days defined in build_site)
    
    calendar_html = ""
    for day in target_day_context_days:
        is_viewing = "ring-4 ring-red-500 shadow-lg bg-red-50" if day['ad'] == TODAY_AD_STR else "hover:bg-gray-50"
        event_dot = '<span class="block w-1 h-1 bg-red-500 rounded-full mx-auto mt-1"></span>' if day.get('event') else ''
        # UPDATED: Links now point inside the /nepali-date/ folder
        calendar_html += f'''
        <a href="{DOMAIN}/{SUB_FOLDER}/{day['bs']}.html" class="p-2 sm:p-4 border border-gray-100 rounded-xl text-center {is_viewing} transition-all block">
            <div class="text-[10px] text-gray-400 font-bold uppercase">{day['day'][:3]}</div>
            <div class="text-lg sm:text-xl font-bold text-slate-800">{day['bs'].split("-")[-1]}</div>
            {event_dot}
        </a>'''

    return f"""<!DOCTYPE html>
<html lang="ne">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nepali Date Today: {target_day['bs']} | {target_day['ad']} - Nepali Patro</title>
    <meta name="description" content="Find Nepali date today: {target_day['bs']}. Today Nepali date, Nepali calendar {month_label}, Aaja ko tarikh, and upcoming festivals.">
    <meta name="keywords" content="Nepali date today, Today Nepali date, Nepali calendar {month_label}, Aaja ko gate, Aaja ko tarikh, Aaja k gate ho?, Nepali patro">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{DOMAIN}/{SUB_FOLDER}/{target_day['bs']}.html">
    <link rel="icon" type="image/png" href="/favicon.ico">
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
                {f'<div class="p-6 bg-yellow-50 text-center text-yellow-800 font-bold text-lg sm:text-xl border-b border-yellow-100">✨ {target_day["event"]}</div>' if target_day.get('event') else ''}
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
                <a href="{DOMAIN}/{SUB_FOLDER}/{e['bs']}.html" class="bg-white p-4 rounded-2xl border border-slate-100 flex flex-wrap justify-between items-center shadow-sm hover:border-red-300 transition-colors">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-800">{e['event']}</span>
                        <span class="text-xs text-slate-400 font-medium">{e['bs']} ({e['ad']})</span>
                    </div>
                    <div class="bg-red-50 text-red-600 px-3 py-1 rounded-full text-xs font-black mt-2 sm:mt-0">
                        {f'Today' if e['days_left'] == 0 else f'In {e["days_left"]} Days'}
                    </div>
                </a>''' for e in ui_upcoming_events]) if ui_upcoming_events else '<p class="text-slate-400 p-4 italic">No more festivals remaining this year.</p>'}
            </div>
        </section>

        <section class="mb-12">
            <h3 class="text-xl font-black text-slate-800 mb-6 uppercase tracking-tight px-2">Commonly Asked Questions</h3>
            <div class="grid gap-4 px-1">
                {"".join([f'<div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm"><h4 class="font-bold text-slate-800 mb-2">Q: {f["q"]}</h4><p class="text-slate-600">A: {f["a"]}</p></div>' for f in faqs])}
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
            // Local Clock
            document.getElementById('local-clock').innerText = now.toLocaleTimeString();
            
            // Fixed Nepal Clock & Date logic
            const nptFormatter = new Intl.DateTimeFormat('en-CA', {{
                timeZone: 'Asia/Kathmandu',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            }});
            
            const nptParts = nptFormatter.formatToParts(now);
            const nptDateMap = {{}};
            nptParts.forEach(p => nptDateMap[p.type] = p.value);
            
            const nptDateStr = `${{nptDateMap.year}}-${{nptDateMap.month}}-${{nptDateMap.day}}`;
            document.getElementById('npt-clock').innerText = `${{nptDateMap.hour}}:${{nptDateMap.minute}}:${{nptDateMap.second}}`;

            const renderedDate = "{target_day['ad']}";
            
            // Only show the button if the current Nepal date is truly different from the page date
            if (nptDateStr !== renderedDate) {{
                document.getElementById('goto-today-btn').style.display = 'flex';
            }} else {{
                document.getElementById('goto-today-btn').style.display = 'none';
            }}
        }}
        setInterval(updateClocks, 1000); 
        updateClocks();
    </script>

<!-- Supercounters (optional) -->
<div style="position:fixed;top:0;left:0;width:100%;height:1px;overflow:hidden;visibility:hidden;z-index:9999;">
    <script type="text/javascript" src="//widget.supercounters.com/ssl/online_i.js"></script>
    <script type="text/javascript">sc_online_i(1727928,"ffffff","ffffff");</script>
    <noscript><a href="https://www.supercounters.com/" style="visibility:hidden;">free online counter</a></noscript>
</div>

</body>
</html>"""

def build_site():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        content = json.load(f)
        data = content[0] if isinstance(content, list) else content
    
    # Pre-collect all days from all months to ensure we have the full year's data for countdowns
    all_year_days = []
    for m in data['calendar_data']:
        all_year_days.extend(m['days'])

    files_count = 0
    for m_data in data['calendar_data']:
        label = f"{' / '.join(m_data['bs_months'])} {data.get('year', '')}"
        
        # We need to tell the template which days belong to the current month view
        global target_day_context_days
        target_day_context_days = m_data['days']

        for day in m_data['days']:
            # Pass all_year_days so the FAQ and Upcoming section are never empty
            html = get_html_template(day, all_year_days, label, m_data['month'])
            
            # UPDATED: Filename now includes the subdirectory path
            filename = os.path.join(SUB_FOLDER, f"{day['bs']}.html")
            
            with open(filename, "w", encoding='utf-8') as f_out: 
                f_out.write(html)
            files_count += 1
            
            if day['ad'] == TODAY_AD_STR:
                with open("index.html", "w", encoding='utf-8') as f_idx: 
                    f_idx.write(html)
        
    print(f"Success! Generated {files_count} HTML files in /{SUB_FOLDER}/. index.html updated for {TODAY_AD_STR}.")

if __name__ == "__main__": 
    build_site()
