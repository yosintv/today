import os
from datetime import datetime
from urllib.parse import urljoin

# ================= CONFIG =================
BASE_URL = "https://today.singhyogendra.com.np/"  # change this
OUTPUT_FILE = "sitemap.xml"
EXCLUDE_DIRS = {".git", ".github", "node_modules", "__pycache__"}
# ==========================================

urls = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for file in files:
        if file.endswith(".html"):
            full_path = os.path.join(root, file)
            url_path = full_path.replace("./", "").replace("\\", "/")

            if url_path.endswith("index.html"):
                url_path = url_path.replace("index.html", "")

            urls.append(urljoin(BASE_URL, url_path))

now = datetime.utcnow().strftime("%Y-%m-%d")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

    for url in sorted(set(urls)):
        f.write("  <url>\n")
        f.write(f"    <loc>{url}</loc>\n")
        f.write(f"    <lastmod>{now}</lastmod>\n")
        f.write("    <changefreq>daily</changefreq>\n")
        f.write("    <priority>0.8</priority>\n")
        f.write("  </url>\n")

    f.write("</urlset>")

print("✅ sitemap.xml generated successfully!")
