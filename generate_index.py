import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ================= CONFIG =================
SITE_URL = "https://today.singhyogendra.com.np/"
SITE_TITLE = "Nepali Calendar Today"
TIMEZONE = ZoneInfo("Asia/Kathmandu")
BASE_PATH = Path(".")
# =========================================

NEPALI_NUM = str.maketrans("0123456789", "०१२३४५६७८९")

def to_nepali_num(text):
    return str(text).translate(NEPALI_NUM)

# -------- Current NPT Date --------
now = datetime.now(TIMEZONE)
today_ad = now.strftime("%Y-%m-%d")
api_month = now.strftime("%Y%m")           # 202601
API_FILE = f"date/{api_month}.json"

print("NPT time:", now)
print("Using API:", API_FILE)

# -------- Load API --------
api_path = Path(API_FILE)
if not api_path.exists():
    raise FileNotFoundError(f"API file not found: {API_FILE}")

raw = json.loads(api_path.read_text(encoding="utf-8"))

# ✅ SUPPORT BOTH FORMATS
if isinstance(raw, list):
    data = raw[0]
elif isinstance(raw, dict):
    data = raw
else:
    raise ValueError("Invalid API format")

days = data.get("days", [])
if not days:
    raise ValueError("No days found in API")

# -------- Find Today --------
today = next((d for d in days if d.get("ad") == today_ad), None)
if not today:
    raise ValueError("Today's date not found in API")

# -------- BS Date --------
bs_date = today["bs"]            # 2082-09-29
bs_year, bs_month, bs_day = bs_date.split("-")
bs_page = f"{bs_date}.html"

# -------- Events --------
event_html = ""
if today.get("event"):
    for e in today["event"].split(","):
        event_html += f'<span class="badge">{e.strip()}</span>'

# -------- Schema (SEO) --------
schema = {
    "@context": "https://schema.org",
    "@type": "Event",
    "name": "Nepali Calendar Today",
    "startDate": today_ad,
    "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
    "eventStatus": "https://schema.org/EventScheduled",
    "location": {
        "@type": "VirtualLocation",
        "url": SITE_URL
    }
}

# -------- HTML --------
html = f"""<!DOCTYPE html>
<html lang="ne">
<head>
<meta charset="utf-8">
<title>{to_nepali_num(bs_date)} | Nepali Calendar Today</title>

<meta name="description" content="Today Nepali date {to_nepali_num(bs_date)} with events">
<link rel="canonical" href="{SITE_URL}/{bs_page}">

<meta property="og:title" content="Nepali Date Today {to_nepali_num(bs_date)}">
<meta property="og:url" content="{SITE_URL}/{bs_page}">
<meta property="og:type" content="website">

<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False)}
</script>

<style>
body {{
  font-family: system-ui, sans-serif;
  background: #f7f7f7;
  margin: 0;
  padding: 20px;
}}
.card {{
  background: #fff;
  max-width: 520px;
  margin: auto;
  padding: 24px;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,.08);
}}
.badge {{
  display: inline-block;
  background: #2563eb;
  color: #fff;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 13px;
  margin: 4px 4px 0 0;
}}
.small {{ color: #555; font-size: 14px }}
</style>
</head>

<body>
<div class="card">
  <h1>आजको मिति</h1>
  <h2>{to_nepali_num(bs_year)}-{to_nepali_num(bs_month)}-{to_nepali_num(bs_day)}</h2>
  <p class="small">{today["day"]} | AD {today_ad}</p>
  <div>{event_html or "<span class='small'>आज कुनै विशेष कार्यक्रम छैन</span>"}</div>
</div>
</body>
</html>
"""

# -------- WRITE FILES --------
(BASE_PATH / bs_page).write_text(html, encoding="utf-8")

index_html = f"""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="0; url={SITE_URL}/{bs_page}">
<link rel="canonical" href="{SITE_URL}/{bs_page}">
<title>{SITE_TITLE}</title>
</head>
<body>Redirecting…</body>
</html>
"""

(BASE_PATH / "index.html").write_text(index_html, encoding="utf-8")

print("✅ Generated:", bs_page)
