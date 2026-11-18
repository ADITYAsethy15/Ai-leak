import datetime
import html
import urllib.request
import xml.etree.ElementTree as ET

ACCOUNTS = [
    "to_zix",
    "GoogleAIStudio",
    "notjazii",
    "CodeByNZ",
    "itsvishaltwt",
    "lyraxana",
    "JensenHuang",
    "arena",
    "ArtificialAnlys",
    "AI_Screening",
    "LuminaBench",
    "GoogleLabs",
]

def fetch_tweets(username):
    # Using FxTwitter's robust public XML RSS endpoint
    feed_url = f"https://fxtwitter.com/{username}/feed.xml"
    req = urllib.request.Request(
        feed_url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    tweets = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Find all items (posts) in the RSS feed
            for item in root.findall(".//item"):
                title = item.find("title")
                description = item.find("description")
                pub_date = item.find("pubDate")
                link = item.find("link")
                
                text = description.text if description is not None and description.text else (title.text if title is not None else "")
                post_link = link.text if link is not None else f"https://x.com/{username}"
                
                # Parse date string
                dt = datetime.datetime.now(datetime.timezone.utc)
                if pub_date is not None and pub_date.text:
                    try:
                        # Standard RSS date format parsing
                        dt = datetime.datetime.strptime(pub_date.text.strip(), "%a, %d %b %Y %H:%M:%S %z")
                    except Exception:
                        try:
                            dt = datetime.datetime.strptime(pub_date.text.strip()[:25], "%Y-%m-%dT%H:%M:%S")
                            dt = dt.replace(tzinfo=datetime.timezone.utc)
                        except Exception:
                            pass

                tweets.append({
                    "user": username,
                    "text": text,
                    "date": dt,
                    "link": post_link,
                })
    except Exception as e:
        print(f"Error fetching @{username}: {e}")
    
    return tweets

print("Fetching updates from all accounts...")
all_tweets = []
for acc in ACCOUNTS:
    all_tweets.extend(fetch_tweets(acc))

# Sort chronologically newest first
all_tweets.sort(key=lambda x: x["date"], reverse=True)

cards = []
for t in all_tweets[:80]:
    # Convert UTC time to Indian Standard Time (IST -> UTC + 5:30)
    ist_time = t["date"].astimezone(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    time_str = ist_time.strftime("%b %d, %I:%M %p IST")
    
    # Clean up text and parse line breaks safely
    clean_text = html.escape(t["text"]).replace("&lt;br&gt;", "<br>").replace("\n", "<br>")
    
    cards.append(f"""
    <div class="card">
        <div class="header">
            <span class="handle">@{html.escape(t['user'])}</span>
            <span class="time">· {time_str}</span>
        </div>
        <div class="body">{clean_text}</div>
        <a class="link" href="{t['link']}" target="_blank">View on X ↗</a>
    </div>""")

updated_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%b %d, %I:%M %p IST")

feed_content = (
    "\n".join(cards)
    if cards
    else "<p class='empty'>No posts fetched on this run. It will retry automatically next hour.</p>"
)

html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Feed - Custom Hub</title>
    <style>
        body {{ background: #000; color: #e7e9ea; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 16px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 600px; }}
        .top-bar {{ border-bottom: 1px solid #2f3336; padding-bottom: 12px; margin-bottom: 16px; position: sticky; top: 0; background: rgba(0,0,0,0.88); backdrop-filter: blur(8px); z-index: 10; padding-top: 4px; }}
        h1 {{ font-size: 20px; margin: 0 0 4px 0; color: #fff; }}
        .sub {{ color: #71767b; font-size: 13px; }}
        .card {{ border: 1px solid #2f3336; border-radius: 12px; padding: 15px; margin-bottom: 12px; background: #16181c; }}
        .header {{ font-size: 14px; margin-bottom: 8px; display: flex; justify-content: space-between; }}
        .handle {{ font-weight: bold; color: #1d9bf0; }}
        .time {{ color: #71767b; }}
        .body {{ font-size: 15px; line-height: 1.45; margin-bottom: 10px; word-wrap: break-word; white-space: pre-wrap; }}
        .link {{ color: #1d9bf0; text-decoration: none; font-size: 13px; display: inline-block; margin-top: 4px; }}
        .link:hover {{ text-decoration: underline; }}
        .empty {{ color: #71767b; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>AI Following Feed</h1>
            <div class="sub">Chronological · Last updated {updated_now} (IST)</div>
        </div>
        {feed_content}
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_page)

print("Website index.html built successfully!")
