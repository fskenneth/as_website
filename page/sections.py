"""
Reusable section modules for Astra Staging website.
All sections follow mobile-first responsive design.
"""
from fasthtml.common import *
from tools.google_reviews import fetch_google_reviews
from tools.instagram import get_cached_posts
import hashlib


def get_proxied_image_url(image_url: str) -> str:
    """Generate a proxied URL for an Instagram image"""
    url_hash = hashlib.md5(image_url.encode()).hexdigest()[:16]
    return f"/api/instagram-image/{url_hash}"


# =============================================================================
# HOME PAGE SECTIONS
# =============================================================================

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
        style="--hero-bg-image: url('/static/images/banner_hero.jpg');"
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


def reviews_section():
    """Google Reviews section"""
    reviews_data = fetch_google_reviews()
    GOOGLE_REVIEWS_URL = "https://www.google.com/maps/place/Astra+Staging/@43.5196939,-79.7069249,17z"

    # Create star rating display
    def create_stars(count=5):
        return Span(*["★" for _ in range(count)], cls="stars")

    # Function to truncate text and add read more
    def create_review_text(text, review_id, max_chars=150):
        if len(text) <= max_chars:
            return P(text, cls="review-text", id=f"review-text-{review_id}", data_full_text=text)

        truncated = text[:max_chars].rsplit(' ', 1)[0] + '...'
        return P(truncated, cls="review-text truncated", id=f"review-text-{review_id}", data_full_text=text)

    # Sort reviews by recency
    time_order = {
        '1 week ago': 1,
        '2 weeks ago': 2,
        '3 weeks ago': 3,
        '1 month ago': 4,
        'a month ago': 4,
        '2 months ago': 5,
        '3 months ago': 6,
        '4 months ago': 7,
        '5 months ago': 8,
        '6 months ago': 9
    }

    # Filter 5-star reviews and sort by recency
    five_star_reviews = [r for r in reviews_data["reviews"] if r.get("rating", 0) == 5]
    sorted_five_star_reviews = sorted(five_star_reviews,
                                      key=lambda r: time_order.get(r.get('time', ''), 99))

    # Get the 12 most recent 5-star reviews
    recent_five_star_reviews = sorted_five_star_reviews[:12]

    # Create the initial display - first 6 for desktop
    initial_desktop_reviews = recent_five_star_reviews[:6]
    additional_desktop_reviews = recent_five_star_reviews[6:12]

    return Section(
        Div(
            Div(
                H2("Our Clients Love Us", cls="section-title"),
                Div(
                    Div(
                        Img(src="/static/images/logo_google.png", alt="Google", cls="google-logo-rating"),
                        Span(f"{reviews_data['rating']} ", cls="rating-number"),
                        create_stars(5),
                        cls="rating-display"
                    ),
                    Div(
                        Span("We Received "),
                        Span(f"{reviews_data['total_reviews']}", style="font-weight: 700;"),
                        Span(" Google Reviews"),
                        cls="total-reviews section-subtitle"
                    ),
                    cls="reviews-header"
                ),
                Div(
                    Div(
                        # First 6 reviews (all visible on desktop, only first 4 on mobile/tablet)
                        *[
                            Div(
                                Div(
                                    Div(
                                        Span(review["author_name"], cls="reviewer-name"),
                                        create_stars(review["rating"]),
                                        cls="review-header"
                                    ),
                                    create_review_text(review["text"], f"review-{idx}"),
                                    Div(
                                        Span(review["time"], cls="review-time"),
                                        Span("Read more", cls="read-more-btn", onclick=f"expandReview('review-{idx}')", tabindex="0") if len(review["text"]) > 150 else None,
                                        cls="review-footer"
                                    ),
                                    cls="review-content"
                                ),
                                cls=f"review-card{' mobile-tablet-hidden' if idx >= 4 else ''}"
                            )
                            for idx, review in enumerate(initial_desktop_reviews)
                        ],
                        # Reviews 7-12 (hidden by default on all devices)
                        *[
                            Div(
                                Div(
                                    Div(
                                        Span(review["author_name"], cls="reviewer-name"),
                                        create_stars(review["rating"]),
                                        cls="review-header"
                                    ),
                                    create_review_text(review["text"], f"review-{idx+6}"),
                                    Div(
                                        Span(review["time"], cls="review-time"),
                                        Span("Read more", cls="read-more-btn", onclick=f"expandReview('review-{idx+6}')", tabindex="0") if len(review["text"]) > 150 else None,
                                        cls="review-footer"
                                    ),
                                    cls="review-content"
                                ),
                                cls="review-card additional-review mobile-tablet-hidden desktop-hidden"
                            )
                            for idx, review in enumerate(additional_desktop_reviews)
                        ],
                        cls="reviews-row"
                    ),
                    cls="reviews-grid",
                    id="reviews-grid"
                ),
                Div(
                    Span("More Reviews", onclick="toggleMoreReviews()", cls="more-reviews-btn", tabindex="0"),
                    cls="more-reviews-wrapper"
                ),
                cls="section-container"
            ),
            cls="container"
        ),
        Script("""
            function expandReview(reviewId) {
                const textElement = document.getElementById('review-text-' + reviewId);
                const btnElement = document.querySelector(`[onclick="expandReview('${reviewId}')"]`);
                const fullText = textElement.getAttribute('data-full-text');

                if (textElement.classList.contains('truncated')) {
                    textElement.textContent = fullText;
                    textElement.classList.remove('truncated');
                    btnElement.textContent = 'Read less';
                } else {
                    const truncatedText = fullText.substring(0, 150).lastIndexOf(' ');
                    textElement.textContent = fullText.substring(0, truncatedText) + '...';
                    textElement.classList.add('truncated');
                    btnElement.textContent = 'Read more';
                }
            }

            function toggleMoreReviews() {
                const moreBtn = document.querySelector('.more-reviews-btn');
                const isExpanded = moreBtn.textContent === 'Less Reviews';

                const isMobileTablet = window.matchMedia('(max-width: 1023px)').matches;
                const isDesktop = window.matchMedia('(min-width: 1024px)').matches;

                if (isMobileTablet) {
                    const mobileHiddenReviews = document.querySelectorAll('.mobile-tablet-hidden');
                    mobileHiddenReviews.forEach(review => {
                        if (isExpanded) {
                            review.classList.remove('show-mobile');
                        } else {
                            review.classList.add('show-mobile');
                        }
                    });
                } else if (isDesktop) {
                    const additionalReviews = document.querySelectorAll('.additional-review');
                    additionalReviews.forEach(review => {
                        if (isExpanded) {
                            review.classList.add('desktop-hidden');
                        } else {
                            review.classList.remove('desktop-hidden');
                        }
                    });
                }

                moreBtn.textContent = isExpanded ? 'More Reviews' : 'Less Reviews';
            }
        """),
        cls="reviews-section",
        id="reviews"
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


def awards_section():
    """Consumer Choice Award section"""
    return Section(
        Div(
            H2("Accreditation", cls="section-title"),
            P(
                "Astra Staging is honoured to have received the Consumers' Choice Award (CCA) for Home Staging in the Greater Toronto Area.",
                cls="awards-text"
            ),
            Div(
                Img(src="/static/images/logo_cca_2024.png", alt="Consumer Choice Award 2024", cls="award-badge"),
                Img(src="/static/images/logo_cca_2025.png", alt="Consumer Choice Award 2025", cls="award-badge"),
                cls="awards-badges"
            ),
            cls="container"
        ),
        cls="awards-section"
    )


def trusted_by_section():
    """Trusted By real estate companies section"""
    logos = [
        ("logo_remax.jpg", "RE/MAX"),
        ("logo_homelife.jpg", "HomeLife"),
        ("logo_sutton.jpg", "Sutton"),
        ("logo_keller_williams.jpg", "Keller Williams"),
        ("logo_royal_lepage.png", "Royal LePage"),
        ("logo_sothebys.png", "Sotheby's International Realty"),
        ("logo_century21.png", "Century 21"),
        ("logo_right_at_home.png", "Right at Home Realty"),
        ("logo_exp.jpg", "eXp Realty"),
        ("logo_cityscape.png", "Cityscape Real Estate"),
        ("logo_kingsway.png", "Kingsway Real Estate"),
        ("logo_forest_hill.png", "Forest Hill Real Estate"),
    ]

    logo_items = [
        Div(
            Img(src=f"/static/images/{filename}", alt=name, cls="partner-logo"),
            cls="logo-item"
        )
        for filename, name in logos
    ]

    return Section(
        Div(
            H2("Trusted By", cls="section-title"),
            Div(
                *logo_items,
                cls="logos-grid"
            ),
            cls="container"
        ),
        cls="trusted-by-section"
    )


# =============================================================================
# ABOUT PAGE SECTIONS
# =============================================================================

def about_hero_section():
    """About page hero section"""
    return Section(
        Div(
            H1("About Astra Staging", cls="about-hero-title"),
            P(
                "We're more than just a home staging service - we're your partner in transforming your home and making it truly shine.",
                cls="about-hero-subtitle"
            ),
            cls="container"
        ),
        cls="about-hero-section"
    )


def our_story_section():
    """Our Story section for About page"""
    return Section(
        Div(
            H2("Our Story", cls="section-title"),
            P(
                "Astra Staging was established to address the scheduling challenges homeowners face when preparing their properties for sale. We understand the demands of busy lives - juggling work, family, and countless responsibilities while trying to sell your home.",
                cls="story-text"
            ),
            P(
                "That's why we created Astra Staging: to simplify the home staging process and take the stress out of preparing your property for the market. Our team is dedicated to providing professional, efficient service that fits seamlessly into your schedule.",
                cls="story-text"
            ),
            cls="container"
        ),
        cls="our-story-section"
    )


def our_commitment_section():
    """Our Commitment section for About page"""
    return Section(
        Div(
            H2("Our Commitment", cls="section-title"),
            P(
                "From the moment you connect with us, you become the hero of your home-selling journey. Our dedicated team guides you through every step of the staging process, ensuring a smooth and stress-free experience.",
                cls="commitment-text"
            ),
            P(
                "We pride ourselves on quick responses, transparent communication, and outstanding results. Your success is our success, and we're committed to helping you achieve the best possible outcome when selling your home.",
                cls="commitment-text"
            ),
            cls="container"
        ),
        cls="our-commitment-section"
    )


def why_choose_section():
    """Why Choose Astra Staging section for About page"""
    return Section(
        Div(
            H2("Why Choose Astra Staging", cls="section-title"),
            Div(
                # Affordability card
                Div(
                    Div("💰", cls="choose-icon"),
                    Div(
                        H3("Affordability", cls="choose-title"),
                        P(
                            "Free consultations with budget-friendly rates and a transparent pricing structure. No hidden fees - what you see is what you get.",
                            cls="choose-description"
                        ),
                        cls="choose-content"
                    ),
                    cls="choose-card"
                ),
                # Reliability card
                Div(
                    Div("⭐", cls="choose-icon"),
                    Div(
                        H3("Reliability", cls="choose-title"),
                        P(
                            "Professional, creative designs backed by 5-star Google reviews. Our outstanding reputation speaks to our commitment to excellence.",
                            cls="choose-description"
                        ),
                        cls="choose-content"
                    ),
                    cls="choose-card"
                ),
                # Speed card
                Div(
                    Div("⚡", cls="choose-icon"),
                    Div(
                        H3("Speed", cls="choose-title"),
                        P(
                            "Quick inquiry responses, 24-hour call returns, and prompt customer service. We accommodate tight timelines to meet your needs.",
                            cls="choose-description"
                        ),
                        cls="choose-content"
                    ),
                    cls="choose-card"
                ),
                cls="choose-cards"
            ),
            cls="container"
        ),
        cls="why-choose-section"
    )


# =============================================================================
# SERVICE PAGE SECTIONS (for area pages and service pages)
# =============================================================================

def service_hero_section(title, subtitle=""):
    """Generic service page hero section"""
    return Section(
        Div(
            H1(title, cls="service-hero-title"),
            P(subtitle, cls="service-hero-subtitle") if subtitle else None,
            cls="container"
        ),
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


def get_in_touch_section():
    """Get in Touch section with contact options"""
    return Section(
        Div(
            H2("Get in Touch with Us", cls="section-title"),
            Div(
                # Call
                Div(
                    P("Call", cls="contact-option-label"),
                    A("1-888-744-4078", href="tel:+18887444078", cls="contact-option-value"),
                    cls="contact-option"
                ),
                # Chat
                Div(
                    P("Chat", cls="contact-option-label"),
                    A("Message Us", href="https://wa.me/16475585677", target="_blank", cls="contact-option-value"),
                    cls="contact-option"
                ),
                # Inquire
                Div(
                    P("Inquire", cls="contact-option-label"),
                    A("Get a Quote", href="/staging-inquiry/", cls="contact-option-value"),
                    cls="contact-option"
                ),
                cls="contact-options"
            ),
            cls="container"
        ),
        cls="get-in-touch-section"
    )
