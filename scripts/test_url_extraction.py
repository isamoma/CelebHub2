"""
Test URL extraction utilities for YouTube, TikTok, and Spotify
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils import extract_youtube_id, extract_tiktok_id, extract_spotify_id

def test_youtube_extraction():
    """Test YouTube ID extraction from various URL formats"""
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtube.com/watch?v=jNQXAC9IVRw&t=30s", "jNQXAC9IVRw"),
        ("invalid url", None),
        ("", None),
    ]
    
    print("Testing YouTube extraction:")
    for url, expected in test_cases:
        result = extract_youtube_id(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {url} -> {result} (expected {expected})")

def test_tiktok_extraction():
    """Test TikTok URL extraction"""
    test_cases = [
        ("https://vm.tiktok.com/ZMe4K2", "https://vm.tiktok.com/ZMe4K2"),
        ("https://www.tiktok.com/@tiktok/video/1234567890", "https://www.tiktok.com/@user/video/1234567890"),
        ("https://www.tiktok.com/@usernamehere", "https://www.tiktok.com/@usernamehere"),
        ("invalid", None),
        ("", None),
    ]
    
    print("\nTesting TikTok extraction:")
    for url, expected_pattern in test_cases:
        result = extract_tiktok_id(url)
        if expected_pattern is None:
            status = "✓" if result is None else "✗"
        else:
            status = "✓" if (result and expected_pattern in result) else "✗"
        print(f"  {status} {url} -> {result}")

def test_spotify_extraction():
    """Test Spotify URL extraction"""
    test_cases = [
        ("https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMwbk", "https://open.spotify.com/embed/track/0VjIjW4GlUZAMYd2vXMwbk"),
        ("https://open.spotify.com/artist/1Yxfd5W3LC5YWrhFHZr55", "https://open.spotify.com/embed/artist/1Yxfd5W3LC5YWrhFHZr55"),
        ("https://open.spotify.com/album/123456", "https://open.spotify.com/embed/album/123456"),
        ("https://open.spotify.com/playlist/xyz", "https://open.spotify.com/embed/playlist/xyz"),
        ("invalid", None),
        ("", None),
    ]
    
    print("\nTesting Spotify extraction:")
    for url, expected in test_cases:
        result = extract_spotify_id(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {url} -> {result}")

if __name__ == '__main__':
    test_youtube_extraction()
    test_tiktok_extraction()
    test_spotify_extraction()
    print("\n✅ URL extraction tests complete!")
