import json
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ================= CONFIG =================
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TZ = ZoneInfo(config.get("timezone", "Asia/Kathmandu"))
DATA_FOLDER = Path(config.get("data_folder", "date"))
SITE_TITLE = config.get("site_title", "Nepali Calendar Today")

# ================= TIME =================
now = datetime.now(TZ)
year_month = now.strftime("%Y%m")
today_ad = now.strftime("%Y-%m-%d")

json_file = DATA_FOLDER / f"{year_month}.json"

print("NPT:", now)
print("JSON:", json_file)

# ================= LOAD JSON (SAFE) =================
with open(json_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

data = raw[0] if isinstance(raw, list) else raw
days = data["days"]
month = data["month_info"]

# ================= FIND TODAY =================
today = next((d for d in days if d["ad"] == today_ad), None)

if not today:
    raise ValueError("Today's date not found in JSON")

# ================= NEPALI NUMERALS =================
NEP_NUM = str.maketrans("0123456789", "०१२३४५६७८९")

def nep(s):
    return s.translate(NEP_NUM)

# ================= EVENT BADGE =================
def badge(event):
    if not event:
        return ""
    e = event.lower()
    if any(x in e for x in ["puja", "lhosar", "ekadashi", "shivaratri"]):
        c = "festival"
    elif any(x in e for x in ["world", "international", "day"]):
        c = "international"
    else:
        c = "national"
    return f'<span class="badge {c}">{event}</span>'

# ================= BS PAGE NAME =================
bs_page = today["bs"].replace(" ", "-") + ".html"   # 2082-10-18.html

# ================= HTML =================
html = f"""<!DOCTYPE html>
<html lang="ne">
<head>
<meta charset="UTF-8">
<title>{SITE_TITLE} | {today['bs']}</title>

<meta name="description"
content="Nepali calendar today {today['bs']} ({today['ad']}) with festivals and events.">

<link rel="canonical" href="/{bs_page}">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Nepali Calendar Today",
  "startDate": "{today['ad']}",
  "eventStatus": "https://schema.org/EventScheduled"
}}
</script>

<style>
body{{font-family:Arial;background:#f4f4f4}}
.container{{max-width:900px;margin:auto;background:#fff;padding:20px}}
.today{{background:#fff3cd;padding:15px;border-radius:6px}}
.badge{{padding:4px 8px;border-radius:4px;font-size:13px}}
.festival{{background:#ff9800;color:#fff}}
.international{{background:#2196f3;color:#fff}}
.national{{background:#4caf50;color:#fff}}
</style>
</head>

<body>
<div class="container">

<h1>{SITE_TITLE}</h1>

<div class="today">
<h2>आजको मिति</h2>
<p>
<strong>{nep(today['bs'])}</strong><br>
{today['day']}<br>
AD: {today['ad']}
</p>
{badge(today['event'])}
</div>

<p style="color:#777;margin-top:10px">
Updated {now.strftime('%Y-%m-%d %H:%M')} (NPT)
</p>

</div>
</body>
</html>
"""

# ================= WRITE BS PAGE =================
Path(bs_page).write_text(html, encoding="utf-8")

# ================= INDEX REDIRECT =================
index_html = f"""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="0; url=/{bs_page}">
<link rel="canonical" href="/{bs_page}">
<title>{SITE_TITLE}</title>
</head>
<body>
Redirecting to today’s Nepali date…
</body>
</html>
"""

Path("index.html").write_text(index_html, encoding="utf-8")

print("✅ Generated:", bs_page)
