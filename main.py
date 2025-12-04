from fasthtml.common import *
from page.components import create_page
from page.gallery_components import (
    get_gallery_carousel_styles,
    get_gallery_carousel_scripts,
    portfolio_carousel_section,
    before_after_carousel_section,
    instagram_section as instagram_section_module
)
from page.sections import (
    hero_section, welcome_section, pricing_section, why_astra_section,
    reviews_section, instagram_section, awards_section, trusted_by_section,
    about_hero_section, our_story_section, our_commitment_section, why_choose_section
)
from page.services import (
    home_staging_services_page,
    real_estate_staging_page,
    our_differences_page
)
from page.contact import contact_page
from page.areas import AREAS, AREA_PAGE_FUNCTIONS
from page.blog_listing import blog_listing_page, load_blog_metadata
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from tools.instagram import get_cached_posts
from tools.google_reviews import fetch_google_reviews
from tools.email_service import send_inquiry_emails
from starlette.requests import Request
import httpx
import hashlib
import json

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


@rt('/api/contact', methods=['POST'])
async def contact_api(request: Request):
    """Handle contact form submission - sends confirmation and notification emails"""
    try:
        data = await request.json()

        customer_data = {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'subject': data.get('subject', 'General Inquiry'),
            'message': data.get('message', '')
        }

        # Validate required fields
        if not customer_data['name'] or not customer_data['email'] or not customer_data['message']:
            return Response(
                content=json.dumps({'success': False, 'error': 'Missing required fields'}),
                media_type='application/json',
                status_code=400
            )

        # Send emails to sales@astrastaging.com
        result = send_inquiry_emails(customer_data)

        return Response(
            content=json.dumps({'success': result['success']}),
            media_type='application/json'
        )

    except Exception as e:
        print(f"Contact form error: {e}")
        return Response(
            content=json.dumps({'success': False, 'error': str(e)}),
            media_type='application/json',
            status_code=500
        )


# =============================================================================
# ROUTES
# =============================================================================

@rt('/gallery')
def gallery():
    """Gallery page with Portfolio, Before/After, and Instagram sections"""
    content = Div(
        portfolio_carousel_section(title="Portfolio", alt_bg=False),
        before_after_carousel_section(title="Before and After", alt_bg=True),
        instagram_section_module(alt_bg=False),
        cls="gallery-content"
    )

    # Combine gallery carousel styles with any additional styles
    additional_styles = get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        "Portfolio | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description="View our portfolio of professional home staging projects, before and after transformations, and latest Instagram posts.",
        keywords="home staging portfolio, staging before after, home staging photos, real estate staging gallery"
    )


@rt('/staging-pricing')
def staging_pricing():
    """Staging Pricing page with pricing packages, why astra, portfolio and instagram"""
    content = Div(
        pricing_section(),
        why_astra_section(),
        portfolio_carousel_section(title="Portfolio", alt_bg=True),
        instagram_section_module(alt_bg=False),
        cls="staging-pricing-content"
    )

    # Include gallery carousel styles and scripts
    additional_styles = get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        "Staging Pricing | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description="Professional home staging pricing packages. Starter package from $1,200, Complete package from $1,600. Free consultation in GTA.",
        keywords="home staging pricing, staging cost, staging packages, home staging rates, GTA staging prices"
    )


def get_about_page_styles():
    """CSS styles specific to the about page"""
    return """
    /* About Hero Section */
    .about-hero-section {
        padding: 80px 40px 60px;
        background: var(--bg-secondary);
        text-align: center;
    }
    .about-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(32px, 5vw, 48px);
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 20px;
    }
    .about-hero-subtitle {
        font-size: 20px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 700px;
        margin: 0 auto;
    }
    @media (max-width: 767px) {
        .about-hero-section {
            padding: 60px 20px 40px;
        }
        .about-hero-subtitle {
            font-size: 18px;
        }
    }

    /* Our Story Section */
    .our-story-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .story-text {
        font-size: 18px;
        line-height: 1.8;
        color: var(--color-secondary);
        max-width: 800px;
        margin: 0 auto 20px;
        text-align: justify;
    }
    .story-text:last-child {
        margin-bottom: 0;
    }
    @media (max-width: 767px) {
        .our-story-section {
            padding: 40px 20px;
        }
        .story-text {
            font-size: 16px;
            line-height: 1.7;
        }
    }

    /* Our Commitment Section */
    .our-commitment-section {
        padding: 60px 40px;
        background: var(--bg-secondary);
    }
    .commitment-text {
        font-size: 18px;
        line-height: 1.8;
        color: var(--color-secondary);
        max-width: 800px;
        margin: 0 auto 20px;
        text-align: justify;
    }
    .commitment-text:last-child {
        margin-bottom: 0;
    }
    @media (max-width: 767px) {
        .our-commitment-section {
            padding: 40px 20px;
        }
        .commitment-text {
            font-size: 16px;
            line-height: 1.7;
        }
    }

    /* Why Choose Section */
    .why-choose-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .choose-cards {
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 40px;
        max-width: 960px;
        margin: 0 auto;
    }
    .choose-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        max-width: 280px;
        padding: 30px 20px;
        background: var(--bg-secondary);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .choose-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    [data-theme="dark"] .choose-card:hover {
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.05);
    }
    .choose-icon {
        width: 70px;
        height: 70px;
        margin-bottom: 20px;
        font-size: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .choose-title {
        font-family: 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 15px;
        color: var(--color-primary);
    }
    .choose-description {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
    }
    @media (max-width: 767px) {
        .why-choose-section {
            padding: 40px 20px;
        }
        .choose-cards {
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }
        .choose-card {
            max-width: 100%;
            width: 100%;
            padding: 25px 20px;
        }
        .choose-icon {
            width: 60px;
            height: 60px;
            font-size: 40px;
        }
        .choose-title {
            font-size: 20px;
        }
        .choose-description {
            font-size: 15px;
        }
    }

    /* Override awards section background for about page */
    .about-content .awards-section {
        background: var(--bg-secondary);
    }
    """


@rt('/about-us')
def about_us():
    """About page with company story, commitment, and why choose us"""
    content = Div(
        about_hero_section(),
        our_story_section(),
        our_commitment_section(),
        why_choose_section(),
        awards_section(),
        reviews_section(),
        trusted_by_section(),
        cls="about-content"
    )

    return create_page(
        "About Us | Astra Staging",
        content,
        additional_styles=get_about_page_styles(),
        description="Learn about Astra Staging - your partner in professional home staging services in the Greater Toronto Area. Award-winning, reliable, and affordable.",
        keywords="about astra staging, home staging company, staging services GTA, professional stagers"
    )


# =============================================================================
# SERVICE PAGES
# =============================================================================

@rt('/home-staging-services/')
def home_staging_services():
    """Home Staging Services page"""
    return home_staging_services_page()


@rt('/real-estate-staging/')
def real_estate_staging():
    """Real Estate Staging page"""
    return real_estate_staging_page()


@rt('/our-differences/')
def our_differences():
    """Our Differences page"""
    return our_differences_page()


@rt('/contactus/')
def contactus():
    """Contact page"""
    return contact_page()


# =============================================================================
# AREA LANDING PAGES (Google Ads)
# =============================================================================

# Register all area landing page routes
for city_name, url_slug in AREAS:
    route_path = f"/home-staging-services-in-{url_slug}/"
    page_func = AREA_PAGE_FUNCTIONS[url_slug]
    rt(route_path)(page_func)


# =============================================================================
# BLOG ROUTES
# =============================================================================

@rt('/blog/')
def blog():
    """Blog listing page"""
    return blog_listing_page()


# Dynamically register blog post routes
def register_blog_routes():
    """Register routes for individual blog posts"""
    import importlib
    blog_posts = load_blog_metadata()

    for post in blog_posts:
        slug = post['slug']
        seo_url = slug.replace('_', '-')
        filename = post['filename']

        # Convert filename to module path (e.g., page/blog/blog_20251201.py -> page.blog.blog_20251201)
        module_path = filename.replace('/', '.').replace('.py', '')

        # Import the module and get the page function
        try:
            module = importlib.import_module(module_path)
            func_name = f"{filename.split('/')[-1].replace('.py', '')}_page"
            page_func = getattr(module, func_name)

            # Register the route
            rt(f"/{seo_url}/")(page_func)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load blog post {slug}: {e}")


register_blog_routes()


@rt('/')
def home():
    """Home page with hero banner"""
    content = Div(
        hero_section(),
        welcome_section(),
        why_astra_section(),
        pricing_section(),
        instagram_section(),
        reviews_section(),
        awards_section(),
        trusted_by_section(),
        cls="home-content"
    )
    return create_page("Astra Staging", content, is_homepage=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
