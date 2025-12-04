"""
Contact page for Astra Staging website.
- /contactus/
"""
from fasthtml.common import *
from page.components import create_page
from page.sections import reviews_section, trusted_by_section


def get_contact_page_styles():
    """CSS styles for contact page - Mobile first"""
    return """
    /* Contact Hero Section - Mobile First */
    .contact-hero-section {
        padding: 40px 15px 30px;
        background: var(--bg-secondary);
        text-align: center;
    }

    .contact-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
        line-height: 1.3;
    }

    .contact-hero-subtitle {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 600px;
        margin: 0 auto;
    }

    /* Contact Info Section */
    .contact-info-section {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .contact-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 25px;
        max-width: 900px;
        margin: 0 auto;
    }

    .contact-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 25px 20px;
        text-align: center;
    }

    .contact-card-icon {
        font-size: 36px;
        margin-bottom: 15px;
    }

    .contact-card-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 10px;
    }

    .contact-card-text {
        font-size: 15px;
        line-height: 1.6;
        color: var(--color-secondary);
        margin-bottom: 8px;
    }

    .contact-card-text:last-child {
        margin-bottom: 0;
    }

    .contact-card-link {
        color: var(--color-secondary);
        text-decoration: none;
        transition: color 0.3s ease;
    }

    .contact-card-link:hover {
        color: var(--color-primary);
    }

    /* Contact Form Section */
    .contact-form-section {
        padding: 40px 15px;
        background: var(--bg-secondary);
    }

    .contact-form-wrapper {
        max-width: 600px;
        margin: 0 auto;
    }

    .contact-form {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .form-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-primary);
    }

    .form-input,
    .form-textarea {
        padding: 12px 15px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-primary);
        color: var(--color-primary);
        font-size: 15px;
        font-family: inherit;
        transition: border-color 0.3s ease;
    }

    .form-input:focus,
    .form-textarea:focus {
        outline: none;
        border-color: var(--border-hover);
    }

    .form-textarea {
        min-height: 150px;
        resize: vertical;
    }

    .form-row {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .form-submit-btn {
        padding: 14px 30px;
        background: var(--color-primary);
        color: var(--bg-primary);
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.3s ease;
    }

    .form-submit-btn:hover {
        opacity: 0.8;
    }

    .form-submit-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    /* Form Status Messages */
    .form-status {
        margin-top: 15px;
        padding: 0;
        border-radius: 8px;
        text-align: center;
    }

    .form-status p {
        margin: 0;
        padding: 15px;
        border-radius: 8px;
    }

    .form-status.success p {
        background: rgba(34, 197, 94, 0.1);
        color: #16a34a;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    .form-status.error p {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    [data-theme="dark"] .form-status.success p {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
    }

    [data-theme="dark"] .form-status.error p {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
    }

    /* Map Section */
    .map-section {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .map-container {
        max-width: 900px;
        margin: 0 auto;
    }

    .map-wrapper {
        border-radius: 12px;
        overflow: hidden;
        height: 300px;
    }

    .map-wrapper iframe {
        width: 100%;
        height: 100%;
        border: none;
    }

    /* Tablet and up */
    @media (min-width: 768px) {
        .contact-hero-section {
            padding: 60px 30px 40px;
        }

        .contact-hero-title {
            font-size: 36px;
        }

        .contact-hero-subtitle {
            font-size: 18px;
        }

        .contact-info-section {
            padding: 50px 30px;
        }

        .contact-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
        }

        .contact-form-section {
            padding: 50px 30px;
        }

        .form-row {
            flex-direction: row;
        }

        .form-row .form-group {
            flex: 1;
        }

        .map-section {
            padding: 50px 30px;
        }

        .map-wrapper {
            height: 400px;
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .contact-hero-section {
            padding: 80px 40px 60px;
        }

        .contact-hero-title {
            font-size: 42px;
        }

        .contact-hero-subtitle {
            font-size: 20px;
        }

        .contact-info-section {
            padding: 60px 40px;
        }

        .contact-grid {
            gap: 30px;
        }

        .contact-card {
            padding: 30px 25px;
        }

        .contact-card-icon {
            font-size: 42px;
        }

        .contact-card-title {
            font-size: 20px;
        }

        .contact-form-section {
            padding: 60px 40px;
        }

        .map-section {
            padding: 60px 40px;
        }

        .map-wrapper {
            height: 450px;
        }
    }
    """


def contact_hero_section():
    """Contact page hero section"""
    return Section(
        Div(
            H1("Contact Astra Staging", cls="contact-hero-title"),
            P(
                "Have a question or ready to get started? We'd love to hear from you. Reach out today for a free consultation.",
                cls="contact-hero-subtitle"
            ),
            cls="container"
        ),
        cls="contact-hero-section"
    )


def contact_info_section():
    """Contact information cards section"""
    return Section(
        Div(
            H2("Get In Touch", cls="section-title"),
            Div(
                # Phone Card
                Div(
                    Div("📞", cls="contact-card-icon"),
                    H3("Call Us", cls="contact-card-title"),
                    P(
                        A("1-888-744-4078", href="tel:+18887444078", cls="contact-card-link"),
                        cls="contact-card-text"
                    ),
                    P("Mon-Fri: 9:00AM - 5:00PM (EST)", cls="contact-card-text"),
                    cls="contact-card"
                ),
                # Email Card
                Div(
                    Div("✉️", cls="contact-card-icon"),
                    H3("Email Us", cls="contact-card-title"),
                    P(
                        A("sales@astrastaging.com",
                          href="mailto:sales@astrastaging.com?subject=Astra%20Staging%20Website%20Inquiry",
                          cls="contact-card-link"),
                        cls="contact-card-text"
                    ),
                    P("We respond within 24 hours", cls="contact-card-text"),
                    cls="contact-card"
                ),
                # Location Card
                Div(
                    Div("📍", cls="contact-card-icon"),
                    H3("Visit Us", cls="contact-card-title"),
                    P("3600A Laird Rd, Unit 12", cls="contact-card-text"),
                    P("Mississauga, ON L5L 0A3", cls="contact-card-text"),
                    cls="contact-card"
                ),
                cls="contact-grid"
            ),
            cls="container"
        ),
        cls="contact-info-section"
    )


def contact_form_section():
    """Contact form section with API submission"""
    return Section(
        Div(
            H2("Send Us A Message", cls="section-title"),
            Div(
                Form(
                    Div(
                        Div(
                            Label("Name", cls="form-label", for_="name"),
                            Input(type="text", id="name", name="name", placeholder="Your name", cls="form-input", required=True),
                            cls="form-group"
                        ),
                        Div(
                            Label("Phone", cls="form-label", for_="phone"),
                            Input(type="tel", id="phone", name="phone", placeholder="Your phone number", cls="form-input"),
                            cls="form-group"
                        ),
                        cls="form-row"
                    ),
                    Div(
                        Label("Email", cls="form-label", for_="email"),
                        Input(type="email", id="email", name="email", placeholder="Your email address", cls="form-input", required=True),
                        cls="form-group"
                    ),
                    Div(
                        Label("Property Address", cls="form-label", for_="address"),
                        Input(type="text", id="address", name="address", placeholder="Property address (optional)", cls="form-input"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Message", cls="form-label", for_="message"),
                        Textarea(id="message", name="message", placeholder="Tell us about your project...", cls="form-textarea", required=True),
                        cls="form-group"
                    ),
                    Button("Send Message", type="submit", cls="form-submit-btn", id="submit-btn"),
                    Div(id="form-status", cls="form-status"),
                    cls="contact-form",
                    id="contact-form",
                    onsubmit="return submitContactForm(event)"
                ),
                cls="contact-form-wrapper"
            ),
            cls="container"
        ),
        Script("""
            // Format name: capitalize first letter of each word
            function formatName(input) {
                const value = input.value.trim().replace(/\\s+/g, ' ');
                if (value) {
                    input.value = value.split(' ').map(word =>
                        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                    ).join(' ');
                }
            }

            // Format email: lowercase, no spaces
            function formatEmail(input) {
                const value = input.value.trim().toLowerCase().replace(/\\s+/g, '');
                input.value = value;
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                if (value && !emailRegex.test(value)) {
                    input.setCustomValidity('Please enter a valid email address');
                } else {
                    input.setCustomValidity('');
                }
            }

            // Format phone: Canadian format
            function formatPhone(input) {
                let value = input.value.replace(/\\D/g, '');
                if (value.startsWith('1') && value.length === 11) {
                    value = '1 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7);
                } else if (value.length === 10) {
                    value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6);
                } else if (value.length > 10 && !value.startsWith('1')) {
                    const originalValue = input.value.trim();
                    if (originalValue.startsWith('+')) {
                        value = '+' + value;
                    }
                }
                input.value = value;
            }

            // Initialize Google Places Autocomplete for Canada only
            function initContactAutocomplete() {
                const addressInput = document.getElementById('address');
                if (!addressInput || typeof google === 'undefined') return;

                const autocomplete = new google.maps.places.Autocomplete(addressInput, {
                    types: ['address'],
                    componentRestrictions: { country: 'ca' },
                    fields: ['formatted_address']
                });

                autocomplete.addListener('place_changed', function() {
                    const place = autocomplete.getPlace();
                    if (place.formatted_address) {
                        addressInput.value = place.formatted_address;
                    }
                });
            }

            // Add event listeners for formatting
            document.addEventListener('DOMContentLoaded', function() {
                const nameInput = document.getElementById('name');
                const emailInput = document.getElementById('email');
                const phoneInput = document.getElementById('phone');

                if (nameInput) nameInput.addEventListener('blur', function() { formatName(this); });
                if (emailInput) emailInput.addEventListener('blur', function() { formatEmail(this); });
                if (phoneInput) phoneInput.addEventListener('blur', function() { formatPhone(this); });
            });

            // Initialize autocomplete after Google Maps script loads (async/defer)
            window.addEventListener('load', function() {
                if (typeof google !== 'undefined' && google.maps && google.maps.places) {
                    initContactAutocomplete();
                }
            });

            async function submitContactForm(event) {
                event.preventDefault();

                const form = document.getElementById('contact-form');
                const submitBtn = document.getElementById('submit-btn');
                const statusDiv = document.getElementById('form-status');

                // Disable button and show loading state
                submitBtn.disabled = true;
                submitBtn.textContent = 'Sending...';
                statusDiv.innerHTML = '';
                statusDiv.className = 'form-status';

                // Collect form data
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                // Build subject: "Contact Us" + property address if provided
                data.subject = 'Contact Us' + (data.address && data.address.trim() ? ' - ' + data.address.trim() : '');

                try {
                    const response = await fetch('/api/contact', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (result.success) {
                        statusDiv.innerHTML = '<p>✓ Thank you! Your message has been sent successfully. We will get back to you within 24 hours.</p>';
                        statusDiv.className = 'form-status success';
                        form.reset();
                    } else {
                        statusDiv.innerHTML = '<p>✗ Sorry, there was an error sending your message. Please try again or contact us directly at sales@astrastaging.com</p>';
                        statusDiv.className = 'form-status error';
                    }
                } catch (error) {
                    statusDiv.innerHTML = '<p>✗ Connection error. Please try again or contact us directly at sales@astrastaging.com</p>';
                    statusDiv.className = 'form-status error';
                }

                // Re-enable button
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Message';

                return false;
            }
        """),
        cls="contact-form-section"
    )


def map_section():
    """Google Maps embed section"""
    # Google Maps embed URL for 3600A Laird Rd, Unit 12, Mississauga, ON L5L 0A3
    map_embed_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2889.2!2d-79.708!3d43.52!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b41a0b1c6b0e5%3A0x1234567890abcdef!2s3600A%20Laird%20Rd%2C%20Mississauga%2C%20ON%20L5L%200A3!5e0!3m2!1sen!2sca!4v1234567890"

    return Section(
        Div(
            H2("Our Location", cls="section-title"),
            Div(
                Iframe(
                    src=map_embed_url,
                    loading="lazy",
                    referrerpolicy="no-referrer-when-downgrade",
                    title="Astra Staging Location"
                ),
                cls="map-wrapper"
            ),
            cls="map-container"
        ),
        cls="map-section"
    )


def contact_page():
    """Contact page"""
    content = Div(
        contact_hero_section(),
        contact_info_section(),
        contact_form_section(),
        map_section(),
        reviews_section(),
        trusted_by_section(),
        cls="contact-content"
    )

    additional_styles = get_contact_page_styles()

    return create_page(
        "Contact Us | Astra Staging",
        content,
        additional_styles=additional_styles,
        description="Contact Astra Staging for professional home staging services in the Greater Toronto Area. Call 1-888-744-4078 or email sales@astrastaging.com.",
        keywords="contact astra staging, home staging contact, staging inquiry, GTA staging services"
    )
