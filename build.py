# build.py
import feedparser, json, os, re
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

TIMEOUT = 10

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

def prefer_https(url: str) -> str:
    if not url: return ""
    try:
        p = urlparse(url)
        if p.scheme == "http":
            return urlunparse(("https",) + p[1:])
    except Exception:
        pass
    return url

def looks_like_image(url: str) -> bool:
    if not url: return False
    return bool(re.search(r"\\.(png|jpe?g|gif|webp|avif)(\\?|$)", url, re.I))

def extract_image_from_entry(e) -> str:
    # 1) media_content
    try:
        if hasattr(e, "media_content") and e.media_content:
            for m in e.media_content:
                u = prefer_https(m.get("url",""))
                if looks_like_image(u):
                    return u
    except Exception: pass

    # 2) media_thumbnail
    try:
        if hasattr(e, "media_thumbnail") and e.media_thumbnail:
            for m in e.media_thumbnail:
                u = prefer_https(m.get("url",""))
                if looks_like_image(u):
                    return u
    except Exception: pass

    # 3) enclosures
    try:
        if hasattr(e, "enclosures") and e.enclosures:
            for enc in e.enclosures:
                u = prefer_https(enc.get("href","") or enc.get("url",""))
                if looks_like_image(u):
                    return u
    except Exception: pass

    # 4) inline <img> in content/summary
    def first_img(html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            tag = soup.find("img")
            if tag and tag.get("src"):
                u = prefer_https(tag["src"])
                if looks_like_image(u):
                    return u
        except Exception:
            return ""
        return ""

    try:
        if hasattr(e, "content"):
            for c in e.content:
                img = first_img(c.value)
                if img: return img
    except Exception: pass

    try:
        if hasattr(e, "summary"):
            img = first_img(e.summary)
            if img: return img
    except Exception: pass

    return ""

def extract_og_image(article_url: str) -> str:
    try:
        r = requests.get(article_url, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code != 200: return ""
        soup = BeautifulSoup(r.text, "html.parser")
        # OpenGraph then Twitter
        for name in ["og:image", "twitter:image", "twitter:image:src"]:
            tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name":name})
            if tag:
                u = prefer_https(tag.get("content", ""))
                if looks_like_image(u):
                    return u
    except Exception:
        return ""
    return ""

os.makedirs("data", exist_ok=True)

for cat, sources in feeds.items():
    items = []
    for name, url in sources.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:12]:
                title = getattr(e, "title", "").strip()
                link  = getattr(e, "link", "").strip()

                # image from RSS fields
                image = extract_image_from_entry(e)

                # final fallback: scrape og:image
                if not image and link:
                    image = extract_og_image(link)

                # last cleanup
                image = prefer_https(image)

                items.append({
                    "title": title,
                    "link": link,
                    "source": name,
                    "image": image
                })
        except Exception:
            # keep going for other sources
            pass

    with open(f"data/{cat}.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(items)} items to {cat}.json")
