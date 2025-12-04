"""
Instagram Public Profile Scraper
Fetches recent posts from a public Instagram profile without authentication.
"""

import httpx
import json
from typing import Optional
import asyncio

INSTAGRAM_APP_ID = "936619743392459"
INSTAGRAM_USERNAME = "astra_home_staging_gta"

HEADERS = {
    "x-ig-app-id": INSTAGRAM_APP_ID,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
    "Origin": "https://www.instagram.com",
    "Referer": "https://www.instagram.com/",
}


async def fetch_instagram_profile(username: str = INSTAGRAM_USERNAME) -> Optional[dict]:
    """
    Fetch Instagram profile data including recent posts.

    Args:
        username: Instagram username to fetch

    Returns:
        Profile data dict or None if failed
    """
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("user")
            else:
                print(f"Error fetching profile: {response.status_code}")
                return None
    except Exception as e:
        print(f"Exception fetching Instagram profile: {e}")
        return None


def extract_posts(user_data: dict, limit: int = 12) -> list:
    """
    Extract post data from user profile response.

    Args:
        user_data: User data from Instagram API
        limit: Maximum number of posts to return

    Returns:
        List of post dictionaries with url, image_url, caption, etc.
    """
    posts = []

    if not user_data:
        return posts

    # Get posts from edge_owner_to_timeline_media
    media_edge = user_data.get("edge_owner_to_timeline_media", {})
    edges = media_edge.get("edges", [])

    for edge in edges[:limit]:
        node = edge.get("node", {})

        post = {
            "id": node.get("id"),
            "shortcode": node.get("shortcode"),
            "url": f"https://www.instagram.com/p/{node.get('shortcode')}/",
            "image_url": node.get("display_url") or node.get("thumbnail_src"),
            "thumbnail_url": node.get("thumbnail_src"),
            "is_video": node.get("is_video", False),
            "caption": "",
            "likes": node.get("edge_liked_by", {}).get("count", 0),
            "comments": node.get("edge_media_to_comment", {}).get("count", 0),
        }

        # Extract caption
        caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
        if caption_edges:
            post["caption"] = caption_edges[0].get("node", {}).get("text", "")

        posts.append(post)

    return posts


async def get_instagram_posts(username: str = INSTAGRAM_USERNAME, limit: int = 12) -> list:
    """
    Main function to get Instagram posts for display.

    Args:
        username: Instagram username
        limit: Number of posts to fetch

    Returns:
        List of post data dictionaries
    """
    user_data = await fetch_instagram_profile(username)
    return extract_posts(user_data, limit)


def get_instagram_posts_sync(username: str = INSTAGRAM_USERNAME, limit: int = 12) -> list:
    """
    Synchronous wrapper for get_instagram_posts.
    """
    return asyncio.run(get_instagram_posts(username, limit))


# Cache for storing posts
_cached_posts = []
_cache_time = None

def get_cached_posts(max_age_seconds: int = 3600) -> list:
    """
    Get cached posts or fetch new ones if cache is stale.

    Args:
        max_age_seconds: Maximum age of cache in seconds (default 1 hour)

    Returns:
        List of post data
    """
    import time
    global _cached_posts, _cache_time

    current_time = time.time()

    if _cache_time is None or (current_time - _cache_time) > max_age_seconds:
        try:
            _cached_posts = get_instagram_posts_sync()
            _cache_time = current_time
        except Exception as e:
            print(f"Error refreshing Instagram cache: {e}")
            # Return old cache if refresh fails
            if not _cached_posts:
                _cached_posts = []

    return _cached_posts


if __name__ == "__main__":
    # Test the scraper
    import asyncio

    async def test():
        print("Fetching Instagram profile...")
        user_data = await fetch_instagram_profile()

        if user_data:
            print(f"\nProfile: {user_data.get('username')}")
            print(f"Full Name: {user_data.get('full_name')}")
            print(f"Followers: {user_data.get('edge_followed_by', {}).get('count', 0)}")
            print(f"Posts: {user_data.get('edge_owner_to_timeline_media', {}).get('count', 0)}")

            posts = extract_posts(user_data, 12)
            print(f"\nFetched {len(posts)} posts:")

            for i, post in enumerate(posts, 1):
                print(f"\n{i}. {post['url']}")
                print(f"   Image: {post['image_url'][:80]}...")
                print(f"   Likes: {post['likes']}, Comments: {post['comments']}")
                caption_preview = post['caption'][:50] + "..." if len(post['caption']) > 50 else post['caption']
                print(f"   Caption: {caption_preview}")
        else:
            print("Failed to fetch profile data")

    asyncio.run(test())
