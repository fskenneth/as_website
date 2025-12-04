from fasthtml.common import *

# Site Map links
SITE_MAP_LINKS = [
    ("Home Staging", "/home-staging-services/"),
    ("Real Estate Staging", "/real-estate-staging/"),
    ("Staging Pricing", "/staging-pricing/"),
    ("Staging Portfolio", "/gallery/"),
    ("Our Differences", "/our-differences/"),
    ("Contact Astra Staging", "/contactus/"),
    ("About Astra Staging", "/about-us/"),
    ("Astra Staging Blog", "/blog/"),
]

# Area links for Google Ads (Column 1)
AREAS_COLUMN_1 = [
    ("Ajax", "/home-staging-services-in-ajax/"),
    ("Aurora", "/home-staging-services-in-aurora/"),
    ("Brampton", "/home-staging-services-in-brampton/"),
    ("Brantford", "/home-staging-services-in-brantford/"),
    ("Burlington", "/home-staging-services-in-burlington/"),
    ("Cambridge", "/home-staging-services-in-cambridge/"),
    ("Etobicoke", "/home-staging-services-in-etobicoke/"),
    ("Georgetown", "/home-staging-services-in-georgetown/"),
    ("Guelph", "/home-staging-services-in-guelph/"),
    ("Halton Hills", "/home-staging-services-in-halton-hills/"),
    ("Hamilton", "/home-staging-services-in-hamilton/"),
    ("Kitchener", "/home-staging-services-in-kitchener/"),
    ("Markham", "/home-staging-services-in-markham/"),
]

# Area links for Google Ads (Column 2)
AREAS_COLUMN_2 = [
    ("Milton", "/home-staging-services-in-milton/"),
    ("Mississauga", "/home-staging-services-in-mississauga/"),
    ("Oakville", "/home-staging-services-in-oakville/"),
    ("Oshawa", "/home-staging-services-in-oshawa/"),
    ("Pickering", "/home-staging-services-in-pickering/"),
    ("Richmond Hill", "/home-staging-services-in-richmond-hill/"),
    ("St. Catharines", "/home-staging-services-in-st-catharines/"),
    ("Stouffville", "/home-staging-services-in-stouffville/"),
    ("Toronto", "/home-staging-services-in-toronto/"),
    ("Vaughan", "/home-staging-services-in-vaughan/"),
    ("Waterloo", "/home-staging-services-in-waterloo/"),
    ("Whitby", "/home-staging-services-in-whitby/"),
]


def get_footer_styles():
    """CSS styles for the comprehensive footer - Mobile first"""
    return """
    /* Footer Styles - Mobile First */
    .site-footer {
        background: var(--bg-secondary);
        padding: 40px 15px 30px;
        margin-top: auto;
        flex-shrink: 0;
    }

    .footer-container {
        max-width: 960px;
        margin: 0 auto;
    }

    .footer-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
    }

    /* Mobile: Row 1 = Site Map + Contact, Row 2 = Areas (full width) */
    .footer-column {
        color: var(--color-secondary);
    }

    .footer-column.sitemap-column {
        order: 1;
    }

    .footer-column.contact-column {
        order: 2;
    }

    .footer-column.areas-column {
        order: 3;
        grid-column: 1 / -1;
    }

    .footer-column-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-color);
    }

    .footer-links {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .footer-links li {
        margin-bottom: 8px;
    }

    .footer-links a {
        color: var(--color-secondary);
        text-decoration: none;
        font-size: 14px;
        transition: color 0.3s ease;
    }

    .footer-links a:hover {
        color: var(--color-primary);
    }

    /* Areas 2-column layout with divider */
    .areas-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px 30px;
    }

    .areas-subcolumn {
        position: relative;
    }

    .areas-subcolumn:first-child {
        padding-right: 15px;
    }

    .areas-subcolumn:last-child {
        padding-left: 15px;
    }

    /* Contact column specific styles */
    .contact-label {
        font-weight: 600;
        color: var(--color-primary);
        margin-top: 15px;
        margin-bottom: 5px;
        font-size: 14px;
    }

    .contact-label:first-child {
        margin-top: 0;
    }

    .contact-info {
        font-size: 14px;
        line-height: 1.6;
        color: var(--color-secondary);
    }

    .contact-info a {
        color: var(--color-secondary);
        text-decoration: none;
        transition: color 0.3s ease;
    }

    .contact-info a:hover {
        color: var(--color-primary);
    }

    .footer-bottom {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
        text-align: center;
    }

    .footer-copyright {
        color: var(--color-secondary);
        font-size: 14px;
        margin: 0;
    }

    /* Desktop: 3 columns (Site Map, Areas with 2 sub-columns, Contact) */
    @media (min-width: 900px) {
        .site-footer {
            padding: 60px 40px 40px;
        }

        .footer-grid {
            grid-template-columns: 1fr 2fr 1fr;
            gap: 40px;
        }

        .footer-column.sitemap-column {
            order: 1;
        }

        .footer-column.areas-column {
            order: 2;
            grid-column: auto;
        }

        .footer-column.contact-column {
            order: 3;
        }

        .footer-column-title {
            font-size: 18px;
        }

        .footer-links a,
        .contact-info,
        .contact-label {
            font-size: 15px;
        }

        .areas-grid {
            gap: 8px 40px;
        }

        .areas-subcolumn:first-child {
            padding-right: 20px;
        }

        .areas-subcolumn:last-child {
            padding-left: 20px;
        }
    }
    """


def comprehensive_footer():
    """Comprehensive footer with Site Map, Areas, and Contact"""
    return Footer(
        Div(
            Div(
                # Site Map Column
                Div(
                    H3("Site Map", cls="footer-column-title"),
                    Ul(
                        *[Li(A(name, href=url)) for name, url in SITE_MAP_LINKS],
                        cls="footer-links"
                    ),
                    cls="footer-column sitemap-column"
                ),
                # Areas Column (with 2 sub-columns and divider)
                Div(
                    H3("Areas", cls="footer-column-title"),
                    Div(
                        # Sub-column 1 (Ajax to Markham)
                        Div(
                            Ul(
                                *[Li(A(name, href=url)) for name, url in AREAS_COLUMN_1],
                                cls="footer-links"
                            ),
                            cls="areas-subcolumn"
                        ),
                        # Sub-column 2 (Milton to Whitby)
                        Div(
                            Ul(
                                *[Li(A(name, href=url)) for name, url in AREAS_COLUMN_2],
                                cls="footer-links"
                            ),
                            cls="areas-subcolumn"
                        ),
                        cls="areas-grid"
                    ),
                    cls="footer-column areas-column"
                ),
                # Contact Column
                Div(
                    H3("Contact Astra Staging", cls="footer-column-title"),
                    Div(
                        P("Inquiry", cls="contact-label"),
                        P(
                            A("1-888-744-4078", href="tel:+18887444078"),
                            cls="contact-info"
                        ),
                        P(
                            A("sales@astrastaging.com", href="mailto:sales@astrastaging.com?subject=Astra%20Staging%20Website%20Inquiry"),
                            cls="contact-info"
                        ),
                        P("Head Office", cls="contact-label"),
                        P("3600A Laird Rd, Unit 12", cls="contact-info"),
                        P("Mississauga, ON L5L 0A3", cls="contact-info"),
                        P("Office Hours", cls="contact-label"),
                        P("9:00AM to 5:00PM (EST)", cls="contact-info"),
                        P("Mondays to Fridays", cls="contact-info"),
                    ),
                    cls="footer-column contact-column"
                ),
                cls="footer-grid"
            ),
            Div(
                P("© 2025 Astra Staging. All rights reserved.", cls="footer-copyright"),
                cls="footer-bottom"
            ),
            cls="footer-container"
        ),
        cls="site-footer"
    )
