# build.py — Streamic RSS → JSON builder
# Updated: 2026-02-06
# - Robust feed fetch (Requests UA) then feedparser
# - Better image extraction (media:*, enclosure, HTML <img>, srcset, data-src)
# - Joins relative URLs to page URL; accepts no-extension images via HEAD
# - Adds STREAMING-TECH category; expands IP/SMPTE 2110 sources
# - De-dup by link; graceful error handling

import os
import re
import json
import socket
from urllib.parse import urlparse, urlunparse, urljoin

import requests
import feedparser
from bs4 import BeautifulSoup

TIMEOUT = 15
PER_SOURCE_LIMIT = 12
HEAD_CHECK_TIMEOUT = 6
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/121.0 Safari/537.36")

# ----------------- CATEGORIES & FEEDS -----------------
feeds = {
    # NEW: Streaming Tech (replaces "onair-graphics")
    # Sources: StreamingMedia (Featured News/Articles), AWS Media, AWS Networking & CDN (CloudFront),
    # Akamai blog, Cloudflare blog
    # refs: streamingmedia.com RSS list; AWS RSS lists; IP streaming/CDN blogs
    "streaming-tech": {
        "StreamingMedia News": "http://feeds.infotoday.com/StreamingMediaMagazine-FeaturedNews",
        "StreamingMedia Articles": "http://feeds.infotoday.com/StreamingMediaMagazine-FeaturedArticles",
        "AWS Media": "https://aws.amazon.com/blogs/media/feed/",
        "AWS Networking & CDN": "https://aws.amazon.com/blogs/networking-and-content-delivery/feed/",
        "Akamai": "https://www.akamai.com/blog.rss",
        "Cloudflare": "https://blog.cloudflare.com/rss/"
    },

    # Newsroom & NRCS (kept as-is, works for you)
    "newsroom": {
        "Avid": "https://www.avid.com/rss",
        "TVBEurope": "https://www.tvbeurope.com/feed",
        "Dalet": "https://www.dalet.com/feed/",
        "IABM": "https://theiabm.org/feed/"
    },

    # Playout & Automation (kept, plus Broadcast Beat)
    "playout": {
        "Grass Valley": "https://www.grassvalley.com/blog/feed/",
        "Pebble": "https://www.pebble.tv/feed/",
        "Broadcast Beat": "https://www.broadcastbeat.com/feed/"
    },

    # IP / SMPTE 2110 — EXPANDED to avoid "no feeds"
    # Sources: SMPTE (rss.xml), TVTechnology, Lawo (ST 2110 deployments/news)
    "ip-video": {
        "SMPTE": "https://www.smpte.org/rss.xml",
        "TV Technology": "https://www.tvtechnology.com/.rss/full/",
        "Lawo": "https://lawo.com/feed/"
    },

    # Audio Technology (kept; added RedTech)
    "audio": {
        "Calrec": "https://calrec.com/feed/",
        "RedTech": "https://www.redtech.pro/feed/"
    },

    # Cloud & AI (kept; added MESA Online + TV Technology cross-posts)
    "cloud-ai": {
        "AWS Media": "https://aws.amazon.com/blogs/media/feed/",
        "MESA Online": "https://www.mesaonline.org/feed/",
        "TV Technology": "https://www.tvtechnology.com/.rss/full/"
    }
}

# ----------------- UTILITIES -----------------
def clean_html_to_text(text: str) -> str:
    if not text:
        return ""
    try:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
        return text.replace("\n", " ").replace("\r", " ").strip()
    except Exception:
        return text or ""

def prefer_https(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        if p.scheme == "http":
            return urlunparse(("https",) + p[1:])
    except Exception:
        pass
    return url

EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif|webp|avif)(\?|$)", re.I)

def looks_like_image_by_ext(url: str) -> bool:
    return bool(url and EXT_RE.search(url))

def is_image_via_head(url: str) -> bool:
    if not url:
        return False
    try:
        r = requests.head(url, timeout=HEAD_CHECK_TIMEOUT, allow_redirects=True,
                          headers={"User-Agent": UA})
        ct = (r.headers.get("Content-Type") or "").lower()
        return ct.startswith("image/")
    except Exception:
        return False

def best_from_srcset(srcset: str) -> str:
    try:
        parts = [p.strip() for p in srcset.split(",") if p.strip()]
        if not parts:
            return ""
        return parts[-1].split()[0]
    except Exception:
        return ""

def fetch_feed(url: str):
    """GET with UA, then parse content. Fallback to direct feedparser if needed."""
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
        if resp.status_code == 200 and resp.content:
            return feedparser.parse(resp.content)
    except Exception:
        pass
    return feedparser.parse(url)

# ----------------- IMAGE EXTRACTION -----------------
def extract_image_from_entry(entry, page_url: str) -> str:
    # media:content
    try:
        for m in getattr(entry, "media_content", []):
            u = prefer_https(m.get("url", ""))
            if u and (looks_like_image_by_ext(u) or is_image_via_head(u)):
                return urljoin(page_url, u)
    except Exception:
        pass

    # media:thumbnail
    try:
        for m in getattr(entry, "media_thumbnail", []):
            u = prefer_https(m.get("url", ""))
            if u and (looks_like_image_by_ext(u) or is_image_via_head(u)):
                return urljoin(page_url, u)
    except Exception:
        pass

    # enclosures
    try:
        for enc in getattr(entry, "enclosures", []):
            u = prefer_https(enc.get("href") or enc.get("url", ""))
            if u and (looks_like_image_by_ext(u) or is_image_via_head(u)):
                return urljoin(page_url, u)
    except Exception:
        pass

    # HTML blocks (summary/content)
    try:
        blocks = []
        if hasattr(entry, "content"):
            blocks = [c.value for c in entry.content if getattr(c, "value", None)]
        elif hasattr(entry, "summary"):
            blocks = [entry.summary]

        for html in blocks:
            soup = BeautifulSoup(html, "html.parser")
            for img in soup.find_all("img"):
                cand = ""
                if img.get("srcset"):
                    cand = best_from_srcset(img["srcset"])
                cand = cand or img.get("data-src") or img.get("data-original") or img.get("src") or ""
                cand = prefer_https(cand)
                if not cand:
                    continue
                cand = urljoin(page_url, cand)
                if looks_like_image_by_ext(cand) or is_image_via_head(cand):
                    return cand
    except Exception:
        pass

    return ""

def extract_og_image(page_url: str) -> str:
    try:
        r = requests.get(page_url, timeout=TIMEOUT, headers={"User-Agent": UA})
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "html.parser")
        candidates = [
            soup.find("meta", property="og:image"),
            soup.find("meta", attrs={"name": "og:image"}),
            soup.find("meta", attrs={"name": "twitter:image"}),
            soup.find("meta", attrs={"name": "twitter:image:src"}),
        ]
        for tag in candidates:
            if not tag:
                continue
            u = prefer_https(tag.get("content", ""))
            if not u:
                continue
            u = urljoin(page_url, u)
            if looks_like_image_by_ext(u) or is_image_via_head(u):
                return u
    except Exception:
        return ""
    return ""

# ----------------- BUILD -----------------
def build_all():
    os.makedirs("data", exist_ok=True)

    for category, sources in feeds.items():
        print(f"\n=== Building category: {category} ===")
        items = []
        seen_links = set()

        for source, url in sources.items():
            print(f"  Source: {source} -> {url}")
            try:
                parsed = fetch_feed(url)
            except Exception as ex:
                print(f"    ! feed fetch error: {ex}")
                continue

            count = 0
            for e in getattr(parsed, "entries", [])[:PER_SOURCE_LIMIT]:
                title = clean_html_to_text(getattr(e, "title", "")) or "Untitled"
                link = (getattr(e, "link", "") or "").strip()
                if not link or link in seen_links:
                    continue

                image = extract_image_from_entry(e, page_url=link) or extract_og_image(link)
                image = prefer_https(image)

                items.append({
                    "title": title,
                    "link": link,
                    "source": source,
                    "image": image
                })
                seen_links.add(link)
                count += 1

            print(f"    Collected: {count} items")

        out = f"data/{category}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f" -> {category}: {len(items)} items written to {out}")

if __name__ == "__main__":
    socket.setdefaulttimeout(TIMEOUT)
    build_all()
