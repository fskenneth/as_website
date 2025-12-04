"""
Area landing pages for Google Ads keyword mapping.
Template-based pages for each city in the GTA.
"""
from fasthtml.common import *
from page.components import create_page
from page.sections import (
    pricing_section, why_astra_section, reviews_section,
    trusted_by_section
)
from page.gallery_components import portfolio_carousel_section, get_gallery_carousel_styles, get_gallery_carousel_scripts


# All areas with their URL slugs
AREAS = [
    ("Ajax", "ajax"),
    ("Aurora", "aurora"),
    ("Brampton", "brampton"),
    ("Brantford", "brantford"),
    ("Burlington", "burlington"),
    ("Cambridge", "cambridge"),
    ("Etobicoke", "etobicoke"),
    ("Georgetown", "georgetown"),
    ("Guelph", "guelph"),
    ("Halton Hills", "halton-hills"),
    ("Hamilton", "hamilton"),
    ("Kitchener", "kitchener"),
    ("Markham", "markham"),
    ("Milton", "milton"),
    ("Mississauga", "mississauga"),
    ("Oakville", "oakville"),
    ("Oshawa", "oshawa"),
    ("Pickering", "pickering"),
    ("Richmond Hill", "richmond-hill"),
    ("St. Catharines", "st-catharines"),
    ("Stouffville", "stouffville"),
    ("Toronto", "toronto"),
    ("Vaughan", "vaughan"),
    ("Waterloo", "waterloo"),
    ("Whitby", "whitby"),
]


def get_area_page_styles():
    """CSS styles for area landing pages - Mobile first"""
    return """
    /* Area Hero Section - Mobile First */
    .area-hero-section {
        padding: 40px 15px 30px;
        background: var(--bg-secondary);
        text-align: center;
    }

    .area-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
        line-height: 1.3;
    }

    .area-hero-subtitle {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 600px;
        margin: 0 auto;
    }

    /* Area Intro Section */
    .area-intro-section {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .area-intro-text {
        font-size: 16px;
        line-height: 1.8;
        color: var(--color-secondary);
        max-width: 800px;
        margin: 0 auto 20px;
        text-align: justify;
    }

    .area-intro-text:last-child {
        margin-bottom: 0;
    }

    /* Area CTA Section */
    .area-cta-section {
        padding: 40px 15px;
        background: var(--bg-secondary);
        text-align: center;
    }

    .area-cta-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
    }

    .area-cta-text {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 600px;
        margin: 0 auto 25px;
    }

    .area-cta-buttons {
        display: flex;
        flex-direction: column;
        gap: 15px;
        justify-content: center;
        align-items: center;
    }

    .area-cta-btn {
        display: inline-block;
        padding: 14px 30px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
        min-width: 200px;
        text-align: center;
    }

    .area-cta-btn.primary {
        background: var(--color-primary);
        color: var(--bg-primary);
    }

    .area-cta-btn.primary:hover {
        opacity: 0.8;
    }

    .area-cta-btn.secondary {
        background: transparent;
        color: var(--color-primary);
        border: 2px solid var(--border-color);
    }

    .area-cta-btn.secondary:hover {
        border-color: var(--border-hover);
    }

    /* Tablet and up */
    @media (min-width: 768px) {
        .area-hero-section {
            padding: 60px 30px 40px;
        }

        .area-hero-title {
            font-size: 32px;
        }

        .area-hero-subtitle {
            font-size: 18px;
        }

        .area-intro-section {
            padding: 50px 30px;
        }

        .area-intro-text {
            font-size: 17px;
        }

        .area-cta-section {
            padding: 50px 30px;
        }

        .area-cta-title {
            font-size: 28px;
        }

        .area-cta-buttons {
            flex-direction: row;
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .area-hero-section {
            padding: 80px 40px 60px;
        }

        .area-hero-title {
            font-size: 38px;
        }

        .area-hero-subtitle {
            font-size: 20px;
        }

        .area-intro-section {
            padding: 60px 40px;
        }

        .area-intro-text {
            font-size: 18px;
        }

        .area-cta-section {
            padding: 60px 40px;
        }

        .area-cta-title {
            font-size: 32px;
        }
    }
    """


def area_hero_section(city_name):
    """Area landing page hero section"""
    return Section(
        Div(
            H1(f"Home Staging Services in {city_name}", cls="area-hero-title"),
            P(
                f"Professional home staging to help your {city_name} property sell faster and for a higher price.",
                cls="area-hero-subtitle"
            ),
            cls="container"
        ),
        cls="area-hero-section"
    )


def area_intro_section(city_name):
    """Area-specific introduction section"""
    paragraphs = [
        f"Looking for professional home staging services in {city_name}? Astra Staging is your trusted partner for transforming properties into buyer-ready homes. Our experienced team understands the {city_name} real estate market and knows exactly what local buyers are looking for.",
        f"Whether you're selling a condo, townhouse, or detached home in {city_name}, our staging services will help showcase your property's best features. We work with homeowners, real estate agents, and property investors throughout the Greater Toronto Area to deliver stunning results that drive faster sales at higher prices."
    ]

    return Section(
        Div(
            *[P(p, cls="area-intro-text") for p in paragraphs],
            cls="container"
        ),
        cls="area-intro-section"
    )


def area_cta_section(city_name):
    """Area-specific call-to-action section"""
    return Section(
        Div(
            H2(f"Ready to Stage Your {city_name} Property?", cls="area-cta-title"),
            P(
                "Contact us today for a free consultation. Our team will visit your property and provide a customized staging plan tailored to your needs and budget.",
                cls="area-cta-text"
            ),
            Div(
                A("Get Free Quote", href="/quote", cls="area-cta-btn primary"),
                A("Call 1-888-744-4078", href="tel:+18887444078", cls="area-cta-btn secondary"),
                cls="area-cta-buttons"
            ),
            cls="container"
        ),
        cls="area-cta-section"
    )


def create_area_page(city_name, url_slug):
    """Create an area landing page for the specified city"""
    content = Div(
        area_hero_section(city_name),
        area_intro_section(city_name),
        why_astra_section(),
        pricing_section(),
        portfolio_carousel_section(title="Our Work", alt_bg=True),
        reviews_section(),
        area_cta_section(city_name),
        trusted_by_section(),
        cls="area-page-content"
    )

    additional_styles = get_area_page_styles() + get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        f"Home Staging Services in {city_name} | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description=f"Professional home staging services in {city_name}. Transform your property into a buyer's dream home. Free consultation, staging from $800. Call 1-888-744-4078.",
        keywords=f"home staging {city_name}, {city_name} home staging, property staging {city_name}, real estate staging {city_name}, staging services {city_name}"
    )


# Generate page functions for each area
def get_area_page_function(city_name, url_slug):
    """Factory function to create area page handlers"""
    def area_page():
        return create_area_page(city_name, url_slug)
    area_page.__name__ = f"area_{url_slug.replace('-', '_')}_page"
    return area_page


# Create a dictionary of area page functions for easy registration
AREA_PAGE_FUNCTIONS = {
    url_slug: get_area_page_function(city_name, url_slug)
    for city_name, url_slug in AREAS
}
