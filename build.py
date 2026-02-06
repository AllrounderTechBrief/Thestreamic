import feedparser, json, os

feeds = {
 "onair-graphics": {
  "Ross Video": "https://www.rossvideo.com/company/news/rss/",
  "Vizrt": "https://www.vizrt.com/rss.xml",
  "Maxon": "https://www.maxon.net/en/rss"
 },
 "newsroom": {
  "Avid": "https://www.avid.com/rss",
  "TVBEurope": "https://www.tvbeurope.com/feed"
 },
 "playout": {
  "Grass Valley": "https://www.grassvalley.com/blog/feed/",
  "Pebble": "https://www.pebble.tv/feed/"
 },
 "ip-video": {
  "SMPTE": "https://www.smpte.org/rss.xml"
 },
 "audio": {
  "Calrec": "https://calrec.com/feed/"
 },
 "cloud-ai": {
  "AWS Media": "https://aws.amazon.com/blogs/media/feed/"
 }
}

os.makedirs("data", exist_ok=True)

for cat, sources in feeds.items():
 items = []
 for name, url in sources.items():
  try:
   feed = feedparser.parse(url)
   for e in feed.entries[:10]:
    image = ""
    if hasattr(e, 'media_content') and e.media_content:
     image = e.media_content[0].get("url", "")
    items.append({
     "title": getattr(e, 'title', ''),
     "link": getattr(e, 'link', ''),
     "source": name,
     "image": image
    })
  except Exception:
   pass
 with open(f"data/{cat}.json", "w", encoding='utf-8') as f:
  json.dump(items, f, ensure_ascii=False, indent=2)
 print(f"Wrote {len(items)} items to {cat}.json")
