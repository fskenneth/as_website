"""
Blog listing page for Astra Staging website.
"""
from fasthtml.common import *
from page.components import create_page
import json
import os


def load_blog_metadata():
    """Load blog metadata from JSON file"""
    # Try production path first, then fall back to development path
    production_path = '/var/www/as_website/logs/blog_metadata.json'
    dev_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'blog_metadata.json')

    # Normalize the dev path
    dev_path = os.path.abspath(dev_path)

    # Try production path first
    if os.path.exists(production_path):
        with open(production_path, 'r') as f:
            return json.load(f)
    # Fall back to development path
    elif os.path.exists(dev_path):
        with open(dev_path, 'r') as f:
            return json.load(f)

    return []


def get_blog_styles():
    """CSS styles for blog pages - Mobile first"""
    return """
    /* Blog Hero Section - Mobile First */
    .blog-hero-section {
        padding: 40px 15px 30px;
        background: var(--bg-secondary);
        text-align: center;
    }

    .blog-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
        line-height: 1.3;
    }

    .blog-hero-subtitle {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 600px;
        margin: 0 auto;
    }

    /* Blog Listing Section */
    .blog-listing-section {
        padding: 40px 15px;
        background: var(--bg-primary);
        min-height: 60vh;
    }

    .blog-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 25px;
        max-width: 900px;
        margin: 0 auto;
    }

    .blog-post-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 25px 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .blog-post-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }

    [data-theme="dark"] .blog-post-card:hover {
        box-shadow: 0 5px 20px rgba(255, 255, 255, 0.05);
    }

    .post-title {
        margin-bottom: 12px;
    }

    .post-title-link {
        font-size: 20px;
        font-weight: 700;
        color: var(--color-primary);
        text-decoration: none;
        transition: opacity 0.3s ease;
        line-height: 1.4;
    }

    .post-title-link:hover {
        opacity: 0.7;
    }

    .post-meta {
        margin-bottom: 15px;
        color: var(--color-secondary);
        font-size: 14px;
    }

    .date-label {
        font-weight: 600;
    }

    .post-date {
        color: var(--color-accent);
    }

    .post-summary {
        font-size: 15px;
        line-height: 1.7;
        color: var(--color-secondary);
        margin-bottom: 15px;
    }

    .read-more-link {
        color: var(--color-primary);
        text-decoration: none;
        font-weight: 600;
        font-size: 15px;
        transition: opacity 0.3s ease;
    }

    .read-more-link:hover {
        opacity: 0.7;
    }

    .no-posts-message {
        text-align: center;
        color: var(--color-secondary);
        font-size: 18px;
        padding: 40px;
    }

    /* Blog Post Page Styles */
    .blog-post {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .blog-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 15px;
        color: var(--color-primary);
        text-align: center;
        line-height: 1.3;
    }

    .blog-meta {
        text-align: center;
        margin-bottom: 30px;
        color: var(--color-secondary);
        font-size: 14px;
    }

    .blog-date {
        color: var(--color-accent);
    }

    .blog-content {
        max-width: 800px;
        margin: 0 auto 30px;
        line-height: 1.8;
        color: var(--color-primary);
    }

    .blog-content p {
        margin-bottom: 20px;
        font-size: 16px;
    }

    .blog-content h2 {
        font-size: 24px;
        font-weight: 700;
        margin: 25px 0 15px;
        color: var(--color-primary);
    }

    .blog-content h3 {
        font-size: 20px;
        font-weight: 600;
        margin: 20px 0 12px;
        color: var(--color-primary);
    }

    .blog-content ul, .blog-content ol {
        margin: 20px 0;
        padding-left: 25px;
    }

    .blog-content li {
        margin-bottom: 10px;
        font-size: 16px;
    }

    .blog-content a {
        color: var(--color-accent);
        text-decoration: underline;
    }

    .blog-content a:hover {
        opacity: 0.8;
    }

    .blog-content img {
        max-width: 100%;
        height: auto;
        margin: 20px 0;
        border-radius: 8px;
    }

    .blog-navigation {
        max-width: 800px;
        margin: 30px auto 0;
        padding-top: 30px;
        border-top: 1px solid var(--border-color);
    }

    .back-link {
        color: var(--color-primary);
        text-decoration: none;
        font-size: 16px;
        font-weight: 600;
        transition: opacity 0.3s ease;
    }

    .back-link:hover {
        opacity: 0.7;
    }

    /* Tablet and up */
    @media (min-width: 768px) {
        .blog-hero-section {
            padding: 60px 30px 40px;
        }

        .blog-hero-title {
            font-size: 36px;
        }

        .blog-hero-subtitle {
            font-size: 18px;
        }

        .blog-listing-section {
            padding: 50px 30px;
        }

        .blog-grid {
            gap: 30px;
        }

        .blog-post-card {
            padding: 30px 25px;
        }

        .post-title-link {
            font-size: 22px;
        }

        .post-summary {
            font-size: 16px;
        }

        .blog-post {
            padding: 60px 30px;
        }

        .blog-title {
            font-size: 32px;
        }

        .blog-meta {
            font-size: 16px;
        }

        .blog-content p, .blog-content li {
            font-size: 17px;
        }

        .blog-content h2 {
            font-size: 28px;
        }

        .blog-content h3 {
            font-size: 22px;
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .blog-hero-section {
            padding: 80px 40px 60px;
        }

        .blog-hero-title {
            font-size: 42px;
        }

        .blog-hero-subtitle {
            font-size: 20px;
        }

        .blog-listing-section {
            padding: 60px 40px;
        }

        .blog-post-card {
            padding: 35px 30px;
        }

        .post-title-link {
            font-size: 24px;
        }

        .blog-post {
            padding: 80px 40px;
        }

        .blog-title {
            font-size: 36px;
        }

        .blog-content p, .blog-content li {
            font-size: 18px;
        }
    }
    """


def blog_hero_section():
    """Blog hero section"""
    return Section(
        Div(
            H1("Astra Staging Blog", cls="blog-hero-title"),
            P(
                "Tips, insights, and inspiration for home staging and real estate in the Greater Toronto Area",
                cls="blog-hero-subtitle"
            ),
            cls="container"
        ),
        cls="blog-hero-section"
    )


def blog_post_card(post):
    """Create a blog post card"""
    # Convert underscore slug to SEO-friendly hyphenated URL
    seo_url = post['slug'].replace('_', '-')
    return Article(
        Div(
            H2(
                A(
                    post['title'],
                    href=f"/{seo_url}/",
                    cls="post-title-link"
                ),
                cls="post-title"
            ),
            Div(
                Span("Published: ", cls="date-label"),
                Span(post.get('date', 'Recently'), cls="post-date"),
                cls="post-meta"
            ),
            P(
                post['summary'],
                cls="post-summary"
            ),
            A(
                "Read More",
                href=f"/{seo_url}/",
                cls="read-more-link"
            ),
            cls="post-content"
        ),
        cls="blog-post-card"
    )


def blog_listing_page():
    """Main blog listing page"""

    # Load blog metadata
    blog_posts = load_blog_metadata()

    # Create blog post cards
    post_cards = [blog_post_card(post) for post in blog_posts]

    content = Div(
        blog_hero_section(),
        Section(
            Div(
                Div(
                    *post_cards if post_cards else [
                        P("Blog posts coming soon! Check back for tips on home staging, real estate, and more.", cls="no-posts-message")
                    ],
                    cls="blog-grid"
                ),
                cls="container"
            ),
            cls="blog-listing-section"
        )
    )

    return create_page(
        "Blog | Astra Staging",
        content,
        additional_styles=get_blog_styles(),
        description="Read the Astra Staging blog for tips on home staging, real estate insights, and inspiration for preparing your GTA property for sale.",
        keywords="home staging blog, staging tips, real estate staging blog, GTA home staging, staging advice"
    )
