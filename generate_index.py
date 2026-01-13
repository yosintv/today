import json
import os
from datetime import datetime, timedelta, timezone

def generate_html():
    # Fix DeprecationWarning: Use timezone-aware UTC
    npt_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=45)
    today_str = npt_now.strftime('%Y-%m-%d')
    file_key = npt_now.strftime('%Y%m')  # e.g., "202601"
    
    file_path = f"date/{file_key}.json"
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        raw_data = json.load(f)
        # Fix KeyError: 0 by checking if data is a list or a dict
        data = raw_data[0] if isinstance(raw_data, list) else raw_data

    # Find today's specific entry
    today_data = next((d for d in data['days'] if d['ad'] == today_str), None)
    
    if not today_data:
        print(f"Warning: No data found for today's date {today_str} in {file_path}")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Today's Date - {npt_now.strftime('%B %Y')}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background: #f0f2f5; padding: 50px; color: #333; }}
            .card {{ background: white; padding: 40px; border-radius: 20px; display: inline-block; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-top: 8px solid #e74c3c; }}
            h1 {{ color: #2c3e50; font-size: 1.5rem; text-transform: uppercase; letter-spacing: 1px; }}
            .bs-date {{ font-size: 3rem; color: #e74c3c; font-weight: bold; margin: 10px 0; }}
            .ad-date {{ font-size: 1.4rem; color: #7f8c8d; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
            .event {{ margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 10px; color: #856404; font-weight: 500; }}
            .footer-info {{ margin-top: 25px; font-size: 0.9rem; color: #95a5a6; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Nepali Patro</h1>
            <p class="bs-date">{today_data['bs'] if today_data else 'N/A'}</p>
            <p class="ad-date">{today_data['ad'] if today_data else today_str} ({today_data['day'] if today_data else npt_now.strftime('%A')})</p>
            {f'<div class="event">✨ {today_data["event"]}</div>' if today_data and today_data.get('event') else ''}
            <div class="footer-info">
                Month: {", ".join(data['month_info']['bs_months'])} ({data['month_info']['ad_month']})
            </div>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w") as f:
        f.write(html_content)
    print("Successfully generated index.html")

if __name__ == "__main__":
    generate_html()
