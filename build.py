# build.py — Streamic RSS → JSON builder
# Updated: 2026-02-06
# - Robust image extraction (media:, enclosure, HTML <img>, srcset, data-src)
# - Resolves relative URLs against the article URL
# - Accepts images without file extensions (HEAD content-type check)
# - Stronger feed fetching (Requests + full UA) before feedparser
# - Added requested sources (TV Tech, Broadcast Beat, MESA, RedTech, IABM, Dalet)
# - Updated Ross Video feed URL

import os
import re
import json
import time
import socket
from urllib.parse import urlparse, urlunparse, urljoin

import requests
import feedparser
from bs4 import BeautifulSoup

# ------------- Settings -------------
TIMEOUT = 15
PER_SOURCE_LIMIT = 12          # max items to take from each source
HEAD_CHECK_TIMEOUT = 6
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0 Safari/537.36"
)

# ------------- Feeds by Category -------------
feeds = {
    "onair-graphics": {
        # Updated Ross URL as provided
        "Ross Video": "https://www.rossvideo.com/news/feed/",
        "Vizrt": "https://www.vizrt.com/rss.xml",
        "Maxon": "https://www.maxon.net/en/rss",
    },
    "newsroom": {
        "Avid": "https://www.avid.com/rss",
        "TVBEurope": "https://www.tvbeurope.com/feed",
        "Dalet": "https://www.dalet.com/feed/",
        "IABM": "https://theiabm.org/feed/",
    },
    "playout": {
        "Grass Valley": "https://www.grassvalley.com/blog/feed/",
        "Pebble": "https://www.pebble.tv/feed/",
        "Broadcast Beat": "https://www.broadcastbeat.com/feed/",
    },
    "ip-video": {
        "SMPTE": "https://www.smpte.org/rss.xml",
        "TV Tech": "https://www.tvtechnology.com/.rss/full/",
    },
    "audio": {
        "Calrec": "https://calrec.com/feed/",
        "RedTech": "https://www.redtech.pro/feed/",
    },
    "cloud-ai": {
        "AWS Media": "https://aws.amazon.com/blogs/media/feed/",
        "MESA Online": "https://www.mesaonline.org/feed/",
        "TV Tech": "https://www.tvtechnology.com/.rss/full/",
    },
}

# ------------- Utilities -------------

def clean_html_to_text(text: str) -> str:
    if not text:
        return ""
    try:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
        text = text.replace("\n", " ").replace("\r", " ").strip()
        return text
    except Exception:
        return text or ""

def prefer_https(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        if p.scheme == "http":
            return urlunparse(("https",) + p[1:])
        return url
    except Exception:
        return url

_EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif|webp|avif)(\?|$)", re.I)

def looks_like_image_by_ext(url: str) -> bool:
    return bool(url and _EXT_RE.search(url))

def is_image_via_head(url: str) -> bool:
    """If URL has no image extension, try a quick HEAD to confirm image content-type."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=HEAD_CHECK_TIMEOUT, allow_redirects=True, headers={"User-Agent": UA})
        ct = (r.headers.get("Content-Type") or "").lower()
        return ct.startswith("image/")
    except Exception:
        return False

def best_from_srcset(srcset: str) -> str:
    """
    Parse a srcset string, return the last (usually largest) URL.
    Example: 'small.jpg 320w, medium.jpg 640w, large.jpg 1280w'
    """
    try:
        parts = [p.strip() for p in srcset.split(",") if p.strip()]
        if not parts:
            return ""
        last = parts[-1].split()[0]
        return last
    except Exception:
        return ""

def fetch_url(url: str) -> requests.Response | None:
    """GET with robust headers and timeout."""
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
        if resp.status_code == 200:
            return resp
    except Exception:
        return None
    return None

def fetch_feed(url: str):
    """
    Fetch RSS via requests (for better UA) then parse with feedparser.
    Fallback to feedparser.parse(url) if requests fails.
    """
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
        if resp.status_code == 200 and resp.content:
            return feedparser.parse(resp.content)
    except Exception:
        pass
    # Fallback
    return feedparser.parse(url)

# ------------- Image Extraction -------------

def extract_image_from_entry(entry, page_url: str) -> str:
    """Try multiple RSS fields, then HTML in summary/content, resolving relative URLs."""
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

            # Prefer <img> with srcset/data-src/src
            for img in soup.find_all("img"):
                cand = ""
                if img.get("srcset"):
                    cand = best_from_srcset(img["srcset"])
                cand = cand or img.get("data-src") or img.get("data-original") or img.get("src") or ""

                cand = prefer_https(cand)
                if not cand:
                    continue

                # resolve relative against the article URL
                cand = urljoin(page_url, cand)

                if looks_like_image_by_ext(cand) or is_image_via_head(cand):
                    return cand
    except Exception:
        pass

    return ""

def extract_og_image(page_url: str) -> str:
    """Fetch the article page, parse og:image / twitter:image, confirm it's an image."""
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

# ------------- Main Build -------------

def build_all():
    os.makedirs("data", exist_ok=True)

    for category, sources in feeds.items():
        items = []
        seen_links = set()
        print(f"\n=== Building category: {category} ===")

        for source, url in sources.items():
            print(f"  Source: {source} -> {url}")
            try:
                parsed = fetch_feed(url)
            except Exception as ex:
                print(f"    ! feed fetch error: {ex}")
                continue

            count = 0
            for e in getattr(parsed, "entries", [])[:PER_SOURCE_LIMIT]:
                title = clean_html_to_text(getattr(e, "title", ""))
                link = (getattr(e, "link", "") or "").strip()

                if not link or link in seen_links:
                    continue

                # primary: RSS-provided image fields
