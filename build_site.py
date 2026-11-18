import datetime
from html import escape
import json
import re
import urllib.request

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
  url = f"https://twitter.com{username}"
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  try:
    with urllib.request.urlopen(req, timeout=10) as response:
      html = response.read().decode("utf-8")
      match = re.search(
          r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
          html,
      )
      if not match:
        return []
      data = json.loads(match.group(1))
      entries = (
          data.get("props", {})
          .get("pageProps", {})
          .get("timeline", {})
          .get("entries", [])
      )
      tweets = []
      for entry in entries:
        tweet = entry.get("content", {}).get("tweet", {})
        if not tweet or "full_text" not in tweet:
          continue
        created_at = datetime.datetime.strptime(
            tweet["created_at"], "%a %b %d %H:%M:%S %z %Y"
        )
        tweets.append({
            "user": username,
            "name": tweet.get("user", {}).get("name", username),
            "text": tweet["full_text"],
            "date": created_at,
            "link": f"https://x.com{username}/status/{tweet['id_str']}",
        })
      return tweets
  except Exception:
    return []


all_tweets = []
for acc in ACCOUNTS:
  all_tweets.extend(fetch_tweets(acc))

all_tweets.sort(key=lambda x: x["date"], reverse=True)

cards = []
for t in all_tweets[:60]:
  time_str = t["date"].strftime("%b %d, %I:%M %p UTC")
  text_html = escape(t["text"]).replace("\n", "<br>")
  cards.append(f"""
    <div class="card">
        <div class="header">
            <span class="name">{escape(t['name'])}</span>
            <span class="handle">@{escape(t['user'])}</span>
            <span class="time">· {time_str}</span>
        </div>
        <div class="body">{text_html}</div>
        <a class="link" href="{t['link']}" target="_blank">View on X ↗</a>
    </div>""")

updated_now = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%b %d, %I:%M %p UTC"
)
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
    <title>AI Feed</title>
    <style>
        body {{ background: #000; color: #e7e9ea; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 16px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 600px; }}
        .top-bar {{ border-bottom: 1px solid #2f3336; padding-bottom: 12px; margin-bottom: 16px; position: sticky; top: 0; background: rgba(0,0,0,0.88); backdrop-filter: blur(8px); }}
        h1 {{ font-size: 20px; margin: 0 0 4px 0; }}
        .sub {{ color: #71767b; font-size: 13px; }}
        .card {{ border: 1px solid #2f3336; border-radius: 12px; padding: 15px; margin-bottom: 12px; background: #16181c; }}
        .header {{ font-size: 15px; margin-bottom: 8px; }}
        .name {{ font-weight: bold; color: #fff; }}
        .handle, .time {{ color: #71767b; font-size: 14px; }}
        .body {{ font-size: 15px; line-height: 1.45; margin-bottom: 10px; word-wrap: break-word; }}
        .link {{ color: #1d9bf0; text-decoration: none; font-size: 13px; }}
        .empty {{ color: #71767b; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>AI Following Feed</h1>
            <div class="sub">Chronological · Last updated {updated_now}</div>
        </div>
        {feed_content}
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_page)
