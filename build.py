# build.py
# The Streamic: RSS aggregator for broadcast technology news
# Fetches from industry-leading sources and generates JSON feeds

import json, sys, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from html import unescape

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/122.0 Safari/537.36")

def fetch(url, timeout=20):
    """Fetch URL with custom user agent"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def try_text(node, path, default=""):
    """Safely extract text from XML element"""
    el = node.find(path)
    return (el.text or "").strip() if el is not None and el.text else default

def find_image_rss(item):
    """Extract image URL from RSS item (multiple methods)"""
    # Try media:thumbnail
    media = "{http://search.yahoo.com/mrss/}"
    thumb = item.find(f"{media}thumbnail")
    if thumb is not None and thumb.get("url"):
        return thumb.get("url")
    
    # Try media:content
    content = item.find(f"{media}content")
    if content is not None and content.get("url"):
        url = content.get("url")
        if content.get("type", "").startswith("image/"):
            return url
    
    # Try enclosure
    enc = item.find("enclosure")
    if enc is not None and enc.get("type", "").startswith("image/"):
        return enc.get("url")
    
    # Try content:encoded or description for <img> tags
    content_encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
    if content_encoded is not None and content_encoded.text:
        txt = content_encoded.text
    else:
        txt = try_text(item, "description", "")
    
    # Parse HTML for img src
    if txt:
        txt = unescape(txt)
        lower = txt.lower()
        i = lower.find("<img ")
        if i != -1:
            src_pos = lower.find("src=", i)
            if src_pos != -1:
                quote = txt[src_pos+4:src_pos+5]
                if quote in "\"'":
                    end = txt.find(quote, src_pos+5)
                    if end != -1:
                        return txt[src_pos+5:end]
    
    return ""

def parse_rss(xml_bytes):
    """Parse RSS or Atom feed"""
    items = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return items

    atom = "{http://www.w3.org/2005/Atom}"

    # RSS 2.0
    chan = root.find("channel")
    if chan is not None:
        source_title = try_text(chan, "title", "Source")
        for it in chan.findall("item"):
            title = try_text(it, "title", "Untitled")
            link = try_text(it, "link", "")
            img = find_image_rss(it)
            items.append({
                "title": title,
                "link": link,
                "source": source_title,
                "image": img or ""
            })
        return items

    # Atom
    if root.tag == f"{atom}feed":
        source_title = try_text(root, f"{atom}title", "Source")
        for it in root.findall(f"{atom}entry"):
            title = try_text(it, f"{atom}title", "Untitled")
            link = ""
            for l in it.findall(f"{atom}link"):
                if l.get("rel") in (None, "alternate"):
                    link = l.get("href", "") or link
            items.append({
                "title": title,
                "link": link,
                "source": source_title,
                "image": ""
            })
        return items

    return items

def normalize_and_trim(items, dedupe=True, limit=60):
    """Remove duplicates and limit items"""
    if dedupe:
        seen, out = set(), []
        for it in items:
            lk = it.get("link", "")
            if lk and lk not in seen:
                seen.add(lk)
                out.append(it)
        items = out
    return items[:limit]

def build_feed(out_file, sources):
    """
    Build a JSON feed from multiple RSS sources
    sources: list of dicts with 'url' and optional 'label'
    """
    all_items = []
    for src in sources:
        url = src["url"]
        try:
            print(f"Fetching: {url}")
            data = fetch(url)
            items = parse_rss(data)
            
            # Override source name if label provided
            if src.get("label"):
                for x in items:
                    x["source"] = src["label"]
            
            all_items.extend(items)
            print(f"  → Got {len(items)} items")
            time.sleep(0.5)  # Be polite
            
        except urllib.error.URLError as e:
            print(f"  ✗ URL Error: {e}")
            continue
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    all_items = normalize_and_trim(all_items, limit=60)
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Wrote {out_file} ({len(all_items)} items)\n")

def main():
    """Main build process"""
    
    # ========== STREAMING TECHNOLOGY ==========
    # Focus: OTT, streaming protocols, CDN, video delivery
    streaming_sources = [
        {"url": "https://www.streamingmedia.com/RSS/RSSFeed.aspx", "label": "Streaming Media"},
        {"url": "https://www.tvtechnology.com/rss.xml", "label": "TV Technology"},
        {"url": "https://www.broadcastingcable.com/feeds/all", "label": "Broadcasting & Cable"},
    ]
    
    # ========== NEWSROOM & NRCS ==========
    # Focus: Newsroom systems, rundown automation, graphics integration
    newsroom_sources = [
        {"url": "https://www.tvtechnology.com/rss.xml", "label": "TV Technology"},
        {"url": "https://www.broadcastingcable.com/feeds/all", "label": "Broadcasting & Cable"},
        {"url": "https://www.sportsvideo.org/feed/", "label": "Sports Video Group"},
    ]
    
    # ========== PLAYOUT & AUTOMATION ==========
    # Focus: Master control, channel playout, scheduling systems
    playout_sources = [
        {"url": "https://www.tvtechnology.com/rss.xml", "label": "TV Technology"},
        {"url": "https://www.broadcastingcable.com/feeds/all", "label": "Broadcasting & Cable"},
        {"url": "https://www.ibc.org/rss", "label": "IBC"},
    ]
    
    # ========== IP VIDEO / SMPTE 2110 ==========
    # Focus: IP workflows, SMPTE standards, uncompressed IP video
    ip_video_sources = [
        {"url": "https://www.tvtechnology.com/rss.xml", "label": "TV Technology"},
        {"url": "https://www.sportsvideo.org/feed/", "label": "Sports Video Group"},
        {"url": "https://www.ibc.org/rss", "label": "IBC"},
    ]
    
    # ========== CLOUD & AI ==========
    # Focus: Cloud production, AI/ML in broadcast, remote production
    cloud_ai_sources = [
        {"url": "https://www.tvtechnology.com/rss.xml", "label": "TV Technology"},
        {"url": "https://www.broadcastingcable.com/feeds/all", "label": "Broadcasting & Cable"},
        {"url": "https://www.ibc.org/rss", "label": "IBC"},
    ]
    
    # ========== AUDIO TECHNOLOGY ==========
    # Focus: Audio mixing, monitoring, Dante, audio over IP
    audio_sources = [
        {"url": "https://www.tvtechnology.com/rss.xml", "label": "TV Technology"},
        {"url": "https://www.sportsvideo.org/feed/", "label": "Sports Video Group"},
        {"url": "https://www.prosoundnetwork.com/feed", "label": "Pro Sound Network"},
    ]
    
    # Build all feeds
    print("=" * 60)
    print("THE STREAMIC - Building RSS Feeds")
    print("=" * 60 + "\n")
    
    build_feed("data/streaming-tech.json", streaming_sources)
    build_feed("data/newsroom.json", newsroom_sources)
    build_feed("data/playout.json", playout_sources)
    build_feed("data/ip-video.json", ip_video_sources)
    build_feed("data/cloud-ai.json", cloud_ai_sources)
    build_feed("data/audio.json", audio_sources)
    
    print("=" * 60)
    print("✓ All feeds built successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
