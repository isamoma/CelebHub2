"""
URL extraction utilities for social media embeds.
Convert raw user-pasted URLs to embed-ready IDs/URLs.
"""
import re
from urllib.parse import urlparse, parse_qs


def extract_youtube_id(url):
    """
    Extract YouTube video ID from various URL formats.
    Supports: https://www.youtube.com/watch?v=XXXXX, https://youtu.be/XXXXX, etc.
    Returns: video ID or None
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Match youtube.com/watch?v=XXXXX
    match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    
    return None


def extract_tiktok_id(url):
    """
    Extract TikTok video/user ID from URL.
    Supports: https://www.tiktok.com/@username/video/XXXXX, https://vm.tiktok.com/XXXXX, etc.
    Returns: TikTok embed-ready link or None
    """
    if not url:
        return None
    
    url = url.strip()
    
    # For vm.tiktok.com (mobile share links), return as-is (TikTok oEmbed will redirect)
    if 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
        return url
    
    # Match tiktok.com/@username/video/XXXXX
    match = re.search(r'tiktok\.com\/@[\w\.-]+\/video\/(\d+)', url)
    if match:
        video_id = match.group(1)
        return f"https://www.tiktok.com/@user/video/{video_id}"
    
    # Match tiktok.com/@username (user profile)
    match = re.search(r'tiktok\.com\/(@[\w\.-]+)', url)
    if match:
        username = match.group(1)
        return f"https://www.tiktok.com/{username}"
    
    return url if 'tiktok.com' in url else None


def extract_spotify_id(url):
    """
    Extract Spotify track/artist/album ID from URL.
    Supports: https://open.spotify.com/track/XXXXX, https://open.spotify.com/artist/XXXXX, etc.
    Returns: embed-ready Spotify URL or None
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Match open.spotify.com/track/XXXXX or /artist/XXXXX or /album/XXXXX
    match = re.search(r'open\.spotify\.com\/(track|artist|album|playlist)\/([a-zA-Z0-9]+)', url)
    if match:
        resource_type = match.group(1)
        resource_id = match.group(2)
        return f"https://open.spotify.com/embed/{resource_type}/{resource_id}"
    
    return None


def is_valid_url(url):
    """Simple URL validation."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
