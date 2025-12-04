from fasthtml.common import *
from page.components import create_page
from starlette.staticfiles import StaticFiles

app, rt = fast_app(live=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


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


@rt('/')
def home():
    """Home page with hero banner"""
    content = Div(
        hero_section(),
        welcome_section(),
        why_astra_section(),
        pricing_section(),
        cls="home-content"
    )
    return create_page("Astra Staging", content, is_homepage=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
