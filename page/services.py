"""
Service pages for Astra Staging website.
- /home-staging-services/
- /real-estate-staging/
- /our-differences/
"""
from fasthtml.common import *
from page.components import create_page
from page.sections import (
    pricing_section, why_astra_section, reviews_section,
    awards_section, trusted_by_section
)
from page.gallery_components import portfolio_carousel_section, instagram_section


def get_service_page_styles():
    """CSS styles for service pages - Mobile first"""
    return """
    /* Service Hero Section - Mobile First */
    .service-hero-section {
        padding: 40px 15px 30px;
        background: var(--bg-secondary);
        text-align: center;
    }

    .service-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
        line-height: 1.3;
    }

    .service-hero-subtitle {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 600px;
        margin: 0 auto;
    }

    /* Service Intro Section */
    .service-intro-section {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .service-intro-section.alt-bg {
        background: var(--bg-secondary);
    }

    .service-intro-text {
        font-size: 16px;
        line-height: 1.8;
        color: var(--color-secondary);
        max-width: 800px;
        margin: 0 auto 20px;
        text-align: justify;
    }

    .service-intro-text:last-child {
        margin-bottom: 0;
    }

    /* Differentiators Section */
    .differentiators-section {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .differentiators-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 20px;
        max-width: 900px;
        margin: 0 auto;
    }

    .differentiator-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 25px 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }

    .differentiator-card:hover {
        transform: translateY(-3px);
    }

    .differentiator-icon {
        font-size: 40px;
        margin-bottom: 15px;
    }

    .differentiator-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 10px;
    }

    .differentiator-text {
        font-size: 14px;
        line-height: 1.6;
        color: var(--color-secondary);
    }

    /* Get in Touch Section */
    .get-in-touch-section {
        padding: 40px 15px;
        background: var(--bg-secondary);
    }

    .contact-options {
        display: flex;
        flex-direction: column;
        gap: 20px;
        max-width: 600px;
        margin: 0 auto;
    }

    .contact-option {
        background: var(--bg-primary);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    .contact-option-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-secondary);
        margin-bottom: 8px;
    }

    .contact-option-value {
        font-size: 18px;
        font-weight: 700;
        color: var(--color-primary);
        text-decoration: none;
        transition: opacity 0.3s ease;
    }

    .contact-option-value:hover {
        opacity: 0.7;
    }

    /* Tablet and up */
    @media (min-width: 768px) {
        .service-hero-section {
            padding: 60px 30px 40px;
        }

        .service-hero-title {
            font-size: 36px;
        }

        .service-hero-subtitle {
            font-size: 18px;
        }

        .service-intro-section {
            padding: 50px 30px;
        }

        .service-intro-text {
            font-size: 17px;
        }

        .differentiators-section {
            padding: 50px 30px;
        }

        .differentiators-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
        }

        .get-in-touch-section {
            padding: 50px 30px;
        }

        .contact-options {
            flex-direction: row;
            justify-content: center;
        }

        .contact-option {
            flex: 1;
            max-width: 200px;
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .service-hero-section {
            padding: 80px 40px 60px;
        }

        .service-hero-title {
            font-size: 42px;
        }

        .service-hero-subtitle {
            font-size: 20px;
        }

        .service-intro-section {
            padding: 60px 40px;
        }

        .service-intro-text {
            font-size: 18px;
        }

        .differentiators-section {
            padding: 60px 40px;
        }

        .differentiators-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
        }

        .differentiator-card {
            padding: 30px 25px;
        }

        .differentiator-icon {
            font-size: 50px;
        }

        .differentiator-title {
            font-size: 20px;
        }

        .differentiator-text {
            font-size: 15px;
        }

        .get-in-touch-section {
            padding: 60px 40px;
        }
    }
    """


def service_hero_section(title, subtitle=""):
    """Generic service page hero section"""
    elements = [H1(title, cls="service-hero-title")]
    if subtitle:
        elements.append(P(subtitle, cls="service-hero-subtitle"))

    return Section(
        Div(*elements, cls="container"),
        cls="service-hero-section"
    )


def service_intro_section(paragraphs, alt_bg=False):
    """Service introduction text section"""
    return Section(
        Div(
            *[P(p, cls="service-intro-text") for p in paragraphs],
            cls="container"
        ),
        cls=f"service-intro-section{' alt-bg' if alt_bg else ''}"
    )


def differentiators_section():
    """What makes us different section"""
    differentiators = [
        ("$", "Affordable Pricing", "Budget-friendly rates without compromising quality. Free consultations across the GTA."),
        ("*", "Transparent & Honest", "Clear pricing with no hidden fees. What you see is what you get."),
        ("~", "Fast & Responsive", "Quotes within hours, staging in 2-5 days. We work on your timeline."),
        ("^", "70+ Five-Star Reviews", "Our reputation speaks for itself with consistently excellent customer feedback."),
        ("#", "20+ Cities Covered", "Serving the entire Greater Toronto Area with professional staging services."),
        ("@", "Quality Guaranteed", "Attention to detail and professionalism in every project we complete."),
    ]

    return Section(
        Div(
            H2("What Makes Us Different", cls="section-title"),
            Div(
                *[
                    Div(
                        Div(icon, cls="differentiator-icon"),
                        H3(title, cls="differentiator-title"),
                        P(text, cls="differentiator-text"),
                        cls="differentiator-card"
                    )
                    for icon, title, text in differentiators
                ],
                cls="differentiators-grid"
            ),
            cls="container"
        ),
        cls="differentiators-section"
    )


# =============================================================================
# HOME STAGING SERVICES PAGE
# =============================================================================

def home_staging_services_page():
    """Home Staging Services page"""
    from page.gallery_components import get_gallery_carousel_styles, get_gallery_carousel_scripts

    content = Div(
        service_hero_section(
            "Transforming Your Property into the Buyer's Dream Home",
            "Professional home staging services to help your property sell faster and for a higher price in the Greater Toronto Area."
        ),
        service_intro_section([
            "At Astra Staging, we offer expert home staging, design, and decoration services that showcase your property's best features while minimizing any drawbacks. Our approach combines years of industry experience with customer-focused service from initial consultation through final walk-through.",
            "Whether you have an occupied home that needs refreshing or a vacant property that needs full staging, our team will create a customized plan to transform your space into a buyer's dream home."
        ]),
        why_astra_section(),
        pricing_section(),
        portfolio_carousel_section(title="Our Work", alt_bg=True),
        reviews_section(),
        awards_section(),
        trusted_by_section(),
        cls="home-staging-services-content"
    )

    additional_styles = get_service_page_styles() + get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        "Home Staging Services | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description="Professional home staging services in the Greater Toronto Area. Transform your property into a buyer's dream home. Free consultation, staging from $800.",
        keywords="home staging services, home staging GTA, professional staging, property staging, house staging Toronto"
    )


# =============================================================================
# REAL ESTATE STAGING PAGE
# =============================================================================

def real_estate_staging_page():
    """Real Estate Staging page"""
    from page.gallery_components import get_gallery_carousel_styles, get_gallery_carousel_scripts

    content = Div(
        service_hero_section(
            "Real Estate Staging",
            "Help your listings stand out and sell faster with professional staging services."
        ),
        service_intro_section([
            "In today's competitive real estate market, staging is no longer optional - it's essential. Astra Staging partners with real estate professionals across the Greater Toronto Area to help properties sell faster and for higher prices.",
            "Our staging services are designed to highlight a property's best features, create an emotional connection with potential buyers, and help them envision themselves living in the space. From condos to luxury homes, we have the expertise and inventory to stage any property."
        ]),
        why_astra_section(),
        pricing_section(),
        portfolio_carousel_section(title="Portfolio", alt_bg=True),
        reviews_section(),
        awards_section(),
        trusted_by_section(),
        cls="real-estate-staging-content"
    )

    additional_styles = get_service_page_styles() + get_gallery_carousel_styles()
    additional_scripts = get_gallery_carousel_scripts()

    return create_page(
        "Real Estate Staging | Astra Staging",
        content,
        additional_styles=additional_styles,
        additional_scripts=additional_scripts,
        description="Real estate staging services for agents and brokers in the GTA. Help your listings sell faster with professional staging. Free consultation available.",
        keywords="real estate staging, staging for realtors, property staging Toronto, real estate photography, listing staging"
    )


# =============================================================================
# OUR DIFFERENCES PAGE
# =============================================================================

def our_differences_page():
    """Our Differences page"""
    content = Div(
        service_hero_section(
            "Our Differences",
            "Every property has unique potential. We help you showcase yours."
        ),
        service_intro_section([
            "At Astra Staging, we believe that quality staging shouldn't come with a premium price tag. Our mission is to provide exceptional home staging services that are accessible to all homeowners and real estate professionals in the Greater Toronto Area.",
            "What sets us apart is our commitment to transparent pricing, responsive communication, and attention to detail. We've built our reputation on delivering consistent results that exceed expectations, as evidenced by our 70+ five-star Google reviews."
        ]),
        differentiators_section(),
        why_astra_section(),
        reviews_section(),
        awards_section(),
        trusted_by_section(),
        cls="our-differences-content"
    )

    additional_styles = get_service_page_styles()

    return create_page(
        "Our Differences | Astra Staging",
        content,
        additional_styles=additional_styles,
        description="Discover what makes Astra Staging different. Affordable pricing, transparent communication, 70+ five-star reviews, and coverage across 20+ GTA cities.",
        keywords="why choose astra staging, staging company differences, best home staging Toronto, affordable staging GTA"
    )
