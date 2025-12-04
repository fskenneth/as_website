from fasthtml.common import *
from page.components import create_page
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from tools.instagram import get_cached_posts
import httpx
import base64
import hashlib

app, rt = fast_app(live=True)

# Cache for proxied images
_image_cache = {}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@rt('/api/instagram-image/{image_id}')
async def instagram_image_proxy(image_id: str):
    """Proxy Instagram images to avoid CORS issues"""
    # Get all cached posts and find the matching image
    posts = get_cached_posts()

    for post in posts:
        # Create a hash of the image URL to match
        url_hash = hashlib.md5(post.get('image_url', '').encode()).hexdigest()[:16]
        if url_hash == image_id:
            image_url = post.get('image_url')
            break
    else:
        return Response(content=b'Image not found', status_code=404)

    # Check cache first
    if image_id in _image_cache:
        cached = _image_cache[image_id]
        return Response(
            content=cached['data'],
            media_type=cached['content_type'],
            headers={'Cache-Control': 'public, max-age=86400'}
        )

    # Fetch the image from Instagram
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.instagram.com/",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, headers=headers, timeout=10.0, follow_redirects=True)

            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'image/jpeg')
                image_data = response.content

                # Cache the image
                _image_cache[image_id] = {
                    'data': image_data,
                    'content_type': content_type
                }

                return Response(
                    content=image_data,
                    media_type=content_type,
                    headers={'Cache-Control': 'public, max-age=86400'}
                )
            else:
                return Response(content=b'Failed to fetch image', status_code=502)
    except Exception as e:
        print(f"Error proxying image: {e}")
        return Response(content=b'Error fetching image', status_code=500)


def get_proxied_image_url(image_url: str) -> str:
    """Generate a proxied URL for an Instagram image"""
    url_hash = hashlib.md5(image_url.encode()).hexdigest()[:16]
    return f"/api/instagram-image/{url_hash}"


def hero_section():
    """Hero banner section with background image"""
    return Section(
        Div(
            H1(
                Span("Wise Choice for Home Staging", cls="text-reveal hero-line"),
                Span("in Greater Toronto Area", cls="text-reveal hero-line"),
                cls="hero-title"
            ),
            Div(
                Button(
                    "General Inquiry",
                    onclick="showGeneralInquiryForm()",
                    cls="general-inquiry-btn"
                ),
                A(
                    "Instant Quote",
                    href="/quote",
                    cls="start-search-btn"
                ),
                cls="hero-booking"
            ),
            cls="hero-content"
        ),
        cls="hero-section",
        style="--hero-bg-image: url('/static/images/banner 20240201-1200x800-1.jpg');"
    )


def welcome_section():
    """Welcome section with introductory text"""
    return Section(
        Div(
            H2("Welcome to Astra Staging", cls="section-title"),
            P(
                "Welcome to Astra Staging, your go-to solution for professional home staging services that will exceed your expectations. We understand that you may have a tight schedule, which is why we prioritize professional and efficient service to ensure that your staging needs are met in a timely manner. Our team is dedicated to coordinating with you throughout the entire staging process, ensuring quick and responsive reply, clear and effective communication to guarantee an impressive end result. Trust us to help transform your home and showcase its true potential with our exceptional staging services.",
                cls="welcome-text"
            ),
            cls="container"
        ),
        cls="welcome-section"
    )


def pricing_section():
    """Pricing section with three package cards"""
    return Section(
        Div(
            H2("Pricing", cls="pricing-title"),
            Div(
                # Starter Package
                Div(
                    H3("Starter Package", cls="pricing-card-title"),
                    P("Accessories+Accent Furniture", cls="pricing-card-subtitle"),
                    P("Staging Cost:", cls="pricing-card-cost"),
                    P("$1,200-$3,500", cls="pricing-card-price"),
                    Ul(
                        Li("Wall Arts"),
                        Li("Area Rugs"),
                        Li("Lamps/Decors"),
                        Li("Beddings/Cushions"),
                        Li("Accent Chairs"),
                        Li("End Tables"),
                        Li("Console Tables"),
                        cls="pricing-card-list"
                    ),
                    cls="pricing-card"
                ),
                # Complete Package
                Div(
                    H3("Complete Package", cls="pricing-card-title"),
                    P("Accessories+Large Furniture", cls="pricing-card-subtitle"),
                    P("Staging Cost:", cls="pricing-card-cost"),
                    P("$1,600-$5,200", cls="pricing-card-price"),
                    Ul(
                        Li("Accessories"),
                        Li("Accent Furniture"),
                        Li("Working Desk"),
                        Li("Sofa/Loveseat/Sectional"),
                        Li("Dining Table Set"),
                        Li("Beds/Night Tables"),
                        cls="pricing-card-list"
                    ),
                    cls="pricing-card"
                ),
                # Add-On Service
                Div(
                    H3("Add-On Service", cls="pricing-card-title"),
                    Div(
                        P("Furniture Moving Service", cls="pricing-service-title"),
                        Ul(
                            Li("$150/hr (2 movers) for relocation to garage, basement, or off-site storage"),
                            cls="pricing-card-list"
                        ),
                        cls="pricing-service-group"
                    ),
                    Div(
                        P("Professional Photography Service (up to 2500 sqft with basement)", cls="pricing-service-title"),
                        Ul(
                            Li("$189 for photos and slideshow"),
                            Li("$259 for photos, slideshow, and 3D virtual tour"),
                            cls="pricing-card-list"
                        ),
                        cls="pricing-service-group"
                    ),
                    cls="pricing-card"
                ),
                cls="pricing-cards"
            ),
            cls="container"
        ),
        cls="pricing-section"
    )


def why_astra_section():
    """Why choose Astra Staging section with three feature cards"""
    return Section(
        Div(
            H2(
                Span("When Use Astra Staging", cls="why-astra-title-line"),
                Span("Home Sells Faster with Higher Price", cls="why-astra-title-line"),
                cls="why-astra-title"
            ),
            Div(
                # Reasonable Pricing card
                Div(
                    Div("💰", cls="feature-icon"),
                    Div(
                        H3("Reasonable Pricing", cls="feature-title"),
                        Div(
                            P("Free consultation (GTA)"),
                            P("Occupied property from $800"),
                            P("Vacant property from $1600"),
                            cls="feature-description"
                        ),
                        cls="feature-content"
                    ),
                    cls="feature-card"
                ),
                # Responsive and Fast card
                Div(
                    Div("⚡", cls="feature-icon"),
                    Div(
                        H3("Responsive and Fast", cls="feature-title"),
                        Div(
                            P("Quote within hours"),
                            P("Stage in 2-5 Days"),
                            P("Complete in 1 day"),
                            cls="feature-description"
                        ),
                        cls="feature-content"
                    ),
                    cls="feature-card"
                ),
                # Preview Chosen Furniture card
                Div(
                    Div("🖼️", cls="feature-icon"),
                    Div(
                        H3("Preview Chosen Furniture", cls="feature-title"),
                        Div(
                            P("Visualize before staging"),
                            P("Delivery exact as promised"),
                            P("Flexible with changing"),
                            cls="feature-description"
                        ),
                        cls="feature-content"
                    ),
                    cls="feature-card"
                ),
                cls="why-astra-features"
            ),
            cls="container"
        ),
        cls="why-astra-section"
    )


def instagram_section():
    """Instagram feed section showing latest posts"""
    INSTAGRAM_USERNAME = "astra_home_staging_gta"
    INSTAGRAM_URL = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/"

    # Get cached posts (refreshes every hour)
    posts = get_cached_posts(max_age_seconds=3600)

    # Instagram icon SVG
    instagram_icon = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
    </svg>'''

    # Video play icon SVG
    video_icon = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 5v14l11-7z"/>
    </svg>'''

    if posts:
        # Create grid items for each post
        grid_items = []
        for post in posts[:12]:  # Show up to 12 posts
            # Use proxied image URL to avoid CORS issues
            image_url = post.get('image_url', '')
            proxied_url = get_proxied_image_url(image_url) if image_url else ''

            item_content = [
                A(
                    Img(
                        src=proxied_url,
                        alt=post.get('caption', 'Instagram post')[:100] if post.get('caption') else 'Instagram post',
                        loading="lazy"
                    ),
                    href=post.get('url', INSTAGRAM_URL),
                    target="_blank",
                    rel="noopener noreferrer"
                )
            ]

            # Add video indicator if it's a video/reel
            if post.get('is_video'):
                item_content.append(
                    Div(
                        NotStr(video_icon),
                        cls="video-indicator"
                    )
                )

            grid_items.append(Div(*item_content, cls="instagram-item"))

        content = Div(
            H2(
                A("Check Our Instagram", href=INSTAGRAM_URL, target="_blank"),
                cls="instagram-title"
            ),
            Div(*grid_items, cls="instagram-grid"),
            Div(
                A(
                    NotStr(instagram_icon),
                    "Follow @astra_home_staging_gta",
                    href=INSTAGRAM_URL,
                    target="_blank",
                    rel="noopener noreferrer",
                    cls="instagram-follow-btn"
                ),
                cls="instagram-actions"
            ),
            cls="container"
        )
    else:
        # Fallback if posts couldn't be loaded
        content = Div(
            H2(
                A("Check Our Instagram", href=INSTAGRAM_URL, target="_blank"),
                cls="instagram-title"
            ),
            Div(
                P("Follow us on Instagram to see our latest staging projects!"),
                A(
                    NotStr(instagram_icon),
                    "Follow @astra_home_staging_gta",
                    href=INSTAGRAM_URL,
                    target="_blank",
                    rel="noopener noreferrer",
                    cls="instagram-follow-btn"
                ),
                cls="instagram-error"
            ),
            cls="container"
        )

    return Section(content, cls="instagram-section")


@rt('/')
def home():
    """Home page with hero banner"""
    content = Div(
        hero_section(),
        welcome_section(),
        why_astra_section(),
        pricing_section(),
        instagram_section(),
        cls="home-content"
    )
    return create_page("Astra Staging", content, is_homepage=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
