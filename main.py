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


@rt('/')
def home():
    """Home page with hero banner"""
    content = Div(
        hero_section(),
        welcome_section(),
        cls="home-content"
    )
    return create_page("Astra Staging", content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
