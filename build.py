# build.py — Streamic RSS → JSON builder (robust)
# Updated: 2026-02-06
# - Keeps robust fetching, image heuristics, de-dup, HTTPS preference
# - Adds "Edit & Post" as three sub-categories + one combined file
# - Sorts combined by published date (newest first), graceful fallbacks

import os
import re
import json
import socket
from time import mktime
from urllib.parse import urlparse, urlunparse, urljoin

import requests
import feedparser
from bs4 import BeautifulSoup

# ---------- Settings ----------
TIMEOUT = 15
PER_SOURCE_LIMIT = 12
HEAD_CHECK_TIMEOUT = 6
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0 Safari/537.36"
)

# ---------- Categories & Feeds ----------
feeds = {
    # NEW: Streaming Tech
    "streaming-tech": {
        "StreamingMedia News": "http://feeds.infotoday.com/StreamingMediaMagazine-FeaturedNews",
        "StreamingMedia Articles": "http://feeds.infotoday.com/StreamingMediaMagazine-FeaturedArticles",
        "AWS Media": "https://aws.amazon.com/blogs/media/feed/",
        "AWS Networking & CDN": "https://aws.amazon.com/blogs/networking-and-content-delivery/feed/",
        "Akamai": "https://www.akamai.com/blog.rss",
        "Cloudflare": "https://blog.cloudflare.com/rss/",
    },

    # Newsroom & NRCS
    "newsroom": {
        "Avid": "https://www.avid.com/rss",
        "TVBEurope": "https://www.tvbeurope.com/feed",
        "Dalet": "https://www.dalet.com/feed/",
        "IABM": "https://theiabm.org/feed/",
    },

    # Playout & Automation
    "playout": {
        "Grass Valley": "https://www.grassvalley.com/blog/feed/",
        "Pebble": "https://www.pebble.tv/feed/",
        "Broadcast Beat": "https://www.broadcastbeat.com/feed/",
    },

    # IP / SMPTE 2110
    "ip-video": {
        "SMPTE": "https://www.smpte.org/rss.xml",
        "TV Technology": "https://www.tvtechnology.com/.rss/full/",
        "Lawo": "https://lawo.com/feed/",
    },

    # Audio Technology
    "audio": {
        "Calrec": "https://calrec.com/feed/",
        "RedTech": "https://www.redtech.pro/feed/",
    },

    # Cloud & AI
    "cloud-ai": {
        "AWS Media": "https://aws.amazon.com/blogs/media/feed/",
        "MESA Online": "https://www.mesaonline.org/feed/",
        "TV Technology": "https://www.tvtechnology.com/.rss/full/",
    },

    # ------------------ NEW: Edit & Post (three sub-categories) ------------------
    # 3D & VFX  (C4D, Maya, Redshift)
    "edit-post-3d-vfx": {
        "Maxon News": "https://www.maxon.net/en/news/rss",
        "Autodesk AREA": "https://area.autodesk.com/feed/",
    },
    # Editing & Post  (Premiere, After Effects, Frame.io Cloud)
    "edit-post-editing": {
        "Adobe Blog (News)": "https://blog.adobe.com/en/topics/news.rss",
        "Frame.io": "https://blog.frame.io/feed/",
    },
    # Hardware / IT  (Hardware Encoders, IP Graphics)
    "edit-post-hardware": {
        "TV Technology": "https://www.tvtechnology.com/.rss/full/",
    },
}

# Combined alias: we will merge these into data/edit-post.json
EDIT_POST_PARTS = ["edit-post-3d-vfx", "edit-post-editing", "edit-post-hardware"]

# ---------- Utilities ----------
def clean_html_to_text(text: str) -> str:
    if not text:
        return ""
    try:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
        return text.replace("\n", " ").replace("\r", " ").strip()
    except Exception:
        return text or ""

EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif|webp|avif)(\?|$)", re.I)

def prefer_https(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        if p.scheme == "http":
            return "https://" + p.netloc + p.path + (("?" + p.query) if p.query else "")
    except Exception:
        pass
    return url

def looks_like_image_by_ext(url: str) -> bool:
    return bool(url and EXT_RE.search(url))

def is_image_via_head(url: str) -> bool:
    if not url:
        return False
    try:
        r = requests.head(url, timeout=HEAD_CHECK_TIMEOUT, allow_redirects=True, headers={"User-Agent": UA})
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

# ---------- Image extraction ----------
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

# ---------- Builders ----------
def collect_category(category: str, sources: dict):
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

            # Published timestamp (epoch) for sorting later
            ts = None
            try:
                if getattr(e, "published_parsed", None):
                    ts = int(mktime(e.published_parsed))
                elif getattr(e, "updated_parsed", None):
                    ts = int(mktime(e.updated_parsed))
            except Exception:
                ts = None

            image = extract_image_from_entry(e, page_url=link) or extract_og_image(link)
            image = prefer_https(image)

            items.append({
                "title": title,
                "link": link,
                "source": source,
                "image": image,
                "timestamp": ts
            })
            seen_links.add(link)
            count += 1

        print(f"    Collected: {count} items")
    return items

def write_json(path: str, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f" -> wrote {path} ({len(obj)} items)")

def build_all():
    os.makedirs("data", exist_ok=True)
    built = {}

    # First pass: build every configured category
    for category, sources in feeds.items():
        items = collect_category(category, sources)
        write_json(f"data/{category}.json", items)
        built[category] = items

    # Second pass: build combined Edit & Post file (union of the three)
    combined = []
    seen = set()
    for part in EDIT_POST_PARTS:
        for it in built.get(part, []):
            if it["link"] in seen:
                continue
            combined.append(it)
            seen.add(it["link"])

    # Sort by timestamp desc (unknowns last)
    combined.sort(key=lambda x: (x.get("timestamp") is None, -(x.get("timestamp") or 0)))
    write_json("data/edit-post.json", combined)

if __name__ == "__main__":
    socket.setdefaulttimeout(TIMEOUT)
    build_all()
