"""
Staging Inquiry page for Astra Staging website.
- /staging-inquiry/
"""
from fasthtml.common import *
from page.components import create_page
from page.sections import reviews_section, trusted_by_section


def get_staging_inquiry_styles():
    """CSS styles for staging inquiry page - Mobile first"""
    return """
    /* Staging Inquiry Hero Section - Mobile First */
    .staging-inquiry-hero-section {
        padding: 40px 15px 30px;
        background: var(--bg-secondary);
        text-align: center;
    }

    .staging-inquiry-hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
        line-height: 1.3;
    }

    .staging-inquiry-hero-subtitle {
        font-size: 16px;
        line-height: 1.6;
        color: var(--color-secondary);
        max-width: 600px;
        margin: 0 auto;
    }

    /* Staging Inquiry Form Section */
    .staging-inquiry-form-section {
        padding: 40px 15px;
        background: var(--bg-primary);
    }

    .staging-inquiry-form-wrapper {
        max-width: 600px;
        margin: 0 auto;
    }

    .staging-inquiry-form {
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
    .form-textarea,
    .form-select {
        padding: 12px 15px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-secondary);
        color: var(--color-primary);
        font-size: 15px;
        font-family: inherit;
        transition: border-color 0.3s ease;
    }

    .form-input:focus,
    .form-textarea:focus,
    .form-select:focus {
        outline: none;
        border-color: var(--border-hover);
    }

    .form-input.error,
    .form-select.error {
        border-color: #dc2626;
        background: rgba(239, 68, 68, 0.05);
    }

    [data-theme="dark"] .form-input.error,
    [data-theme="dark"] .form-select.error {
        border-color: #f87171;
        background: rgba(239, 68, 68, 0.1);
    }

    .form-textarea {
        min-height: 120px;
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

    /* Tablet and up */
    @media (min-width: 768px) {
        .staging-inquiry-hero-section {
            padding: 60px 30px 40px;
        }

        .staging-inquiry-hero-title {
            font-size: 36px;
        }

        .staging-inquiry-hero-subtitle {
            font-size: 18px;
        }

        .staging-inquiry-form-section {
            padding: 50px 30px;
        }

        .form-row {
            flex-direction: row;
        }

        .form-row .form-group {
            flex: 1;
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .staging-inquiry-hero-section {
            padding: 80px 40px 60px;
        }

        .staging-inquiry-hero-title {
            font-size: 42px;
        }

        .staging-inquiry-hero-subtitle {
            font-size: 20px;
        }

        .staging-inquiry-form-section {
            padding: 60px 40px;
        }
    }
    """


def staging_inquiry_hero_section():
    """Staging inquiry page hero section"""
    return Section(
        Div(
            H1("Get Your Instant Quote", cls="staging-inquiry-hero-title"),
            P(
                "Fill out the form below and we'll provide you with a customized staging quote within 24 hours.",
                cls="staging-inquiry-hero-subtitle"
            ),
            cls="container"
        ),
        cls="staging-inquiry-hero-section"
    )


def staging_inquiry_form_section():
    """Staging inquiry form section"""
    return Section(
        Div(
            H2("Property Details", cls="section-title"),
            Div(
                Form(
                    Div(
                        Div(
                            Label("Name *", cls="form-label", for_="name"),
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
                        Label("Email *", cls="form-label", for_="email"),
                        Input(type="email", id="email", name="email", placeholder="Your email address", cls="form-input", required=True),
                        cls="form-group"
                    ),
                    Div(
                        Label("Property Address *", cls="form-label", for_="address"),
                        Input(type="text", id="address", name="address", placeholder="Full property address", cls="form-input", required=True),
                        cls="form-group"
                    ),
                    Div(
                        Div(
                            Label("Property Type *", cls="form-label", for_="property_type"),
                            Select(
                                Option("Select property type", value="", disabled=True, selected=True),
                                Option("Detached House", value="Detached House"),
                                Option("Semi-Detached House", value="Semi-Detached House"),
                                Option("Townhouse", value="Townhouse"),
                                Option("Condo Apartment", value="Condo Apartment"),
                                Option("Condo Townhouse", value="Condo Townhouse"),
                                Option("Other", value="Other"),
                                id="property_type",
                                name="property_type",
                                cls="form-select",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Square Footage", cls="form-label", for_="sqft"),
                            Input(type="text", id="sqft", name="sqft", placeholder="Approx. square footage", cls="form-input"),
                            cls="form-group"
                        ),
                        cls="form-row"
                    ),
                    Div(
                        Div(
                            Label("Number of Bedrooms *", cls="form-label", for_="bedrooms"),
                            Select(
                                Option("Select bedrooms", value="", disabled=True, selected=True),
                                Option("1 Bedroom", value="1"),
                                Option("2 Bedrooms", value="2"),
                                Option("3 Bedrooms", value="3"),
                                Option("4 Bedrooms", value="4"),
                                Option("5+ Bedrooms", value="5+"),
                                id="bedrooms",
                                name="bedrooms",
                                cls="form-select",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Number of Bathrooms", cls="form-label", for_="bathrooms"),
                            Select(
                                Option("Select bathrooms", value="", disabled=True, selected=True),
                                Option("1 Bathroom", value="1"),
                                Option("2 Bathrooms", value="2"),
                                Option("3 Bathrooms", value="3"),
                                Option("4+ Bathrooms", value="4+"),
                                id="bathrooms",
                                name="bathrooms",
                                cls="form-select"
                            ),
                            cls="form-group"
                        ),
                        cls="form-row"
                    ),
                    Div(
                        Label("Property Status *", cls="form-label", for_="property_status"),
                        Select(
                            Option("Select property status", value="", disabled=True, selected=True),
                            Option("Vacant - Ready for staging", value="Vacant"),
                            Option("Occupied - Furniture needs moving", value="Occupied - Moving"),
                            Option("Occupied - Accessory staging only", value="Occupied - Accessory"),
                            id="property_status",
                            name="property_status",
                            cls="form-select",
                            required=True
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Preferred Staging Date", cls="form-label", for_="staging_date"),
                        Input(type="date", id="staging_date", name="staging_date", cls="form-input"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Additional Information", cls="form-label", for_="message"),
                        Textarea(id="message", name="message", placeholder="Tell us more about your project, any special requirements, or questions you have...", cls="form-textarea"),
                        cls="form-group"
                    ),
                    Button("Get My Quote", type="submit", cls="form-submit-btn", id="submit-btn"),
                    Div(id="form-status", cls="form-status"),
                    cls="staging-inquiry-form",
                    id="staging-inquiry-form",
                    onsubmit="return submitStagingInquiryForm(event)"
                ),
                cls="staging-inquiry-form-wrapper"
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

            // Format email: lowercase, no spaces, validate format
            function formatEmail(input) {
                const value = input.value.trim().toLowerCase().replace(/\\s+/g, '');
                input.value = value;
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                if (value && !emailRegex.test(value)) {
                    input.classList.add('error');
                    input.setCustomValidity('Please enter a valid email address');
                } else {
                    input.classList.remove('error');
                    input.setCustomValidity('');
                }
            }

            // Format phone: Canadian format, validate length
            function formatPhone(input) {
                let value = input.value.replace(/\\D/g, '');
                let isValid = false;

                if (value.startsWith('1') && value.length === 11) {
                    value = '1 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7);
                    isValid = true;
                } else if (value.length === 10) {
                    value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6);
                    isValid = true;
                } else if (value.length > 10 && !value.startsWith('1')) {
                    const originalValue = input.value.trim();
                    if (originalValue.startsWith('+')) {
                        value = '+' + value;
                        isValid = true; // International format
                    }
                } else if (value.length === 0) {
                    isValid = true; // Empty is OK (optional field)
                }

                input.value = value;

                if (!isValid && value.length > 0) {
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            }

            // Track if a valid address was selected from autocomplete
            let addressSelected = false;

            // Validate address: must be selected from autocomplete
            function validateAddress(input) {
                const value = input.value.trim();
                if (value && !addressSelected) {
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            }

            // Initialize Google Places Autocomplete for Canada only
            function initStagingInquiryAutocomplete() {
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
                        addressSelected = true;
                        addressInput.classList.remove('error');
                    }
                });

                // Reset addressSelected when user types
                addressInput.addEventListener('input', function() {
                    addressSelected = false;
                });

                // Validate on blur
                addressInput.addEventListener('blur', function() {
                    validateAddress(this);
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

            // Initialize autocomplete after Google Maps script loads
            window.addEventListener('load', function() {
                if (typeof google !== 'undefined' && google.maps && google.maps.places) {
                    initStagingInquiryAutocomplete();
                }
            });

            async function submitStagingInquiryForm(event) {
                event.preventDefault();

                const form = document.getElementById('staging-inquiry-form');
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

                // Build subject with property details
                let subject = 'Staging Quote Request';
                if (data.address && data.address.trim()) {
                    subject += ' - ' + data.address.trim();
                }
                data.subject = subject;

                // Build message with all property details
                let message = 'STAGING QUOTE REQUEST\\n';
                message += '========================\\n\\n';
                message += 'Property Details:\\n';
                message += '- Address: ' + (data.address || 'Not provided') + '\\n';
                message += '- Property Type: ' + (data.property_type || 'Not provided') + '\\n';
                message += '- Square Footage: ' + (data.sqft || 'Not provided') + '\\n';
                message += '- Bedrooms: ' + (data.bedrooms || 'Not provided') + '\\n';
                message += '- Bathrooms: ' + (data.bathrooms || 'Not provided') + '\\n';
                message += '- Property Status: ' + (data.property_status || 'Not provided') + '\\n';
                message += '- Preferred Staging Date: ' + (data.staging_date || 'Flexible') + '\\n';
                message += '\\nAdditional Information:\\n';
                message += data.message || 'None provided';

                data.message = message;

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
                        statusDiv.innerHTML = '<p>Thank you! Your quote request has been submitted successfully. We will review your property details and get back to you within 24 hours with a customized quote.</p>';
                        statusDiv.className = 'form-status success';
                        form.reset();
                        addressSelected = false;
                    } else {
                        statusDiv.innerHTML = '<p>Sorry, there was an error submitting your request. Please try again or contact us directly at sales@astrastaging.com</p>';
                        statusDiv.className = 'form-status error';
                    }
                } catch (error) {
                    statusDiv.innerHTML = '<p>Connection error. Please try again or contact us directly at sales@astrastaging.com</p>';
                    statusDiv.className = 'form-status error';
                }

                // Re-enable button
                submitBtn.disabled = false;
                submitBtn.textContent = 'Get My Quote';

                return false;
            }
        """),
        cls="staging-inquiry-form-section"
    )


def notification_banner():
    """Sticky notification banner that updates based on selection state"""
    return Div(
        Div(
            Div("Instant Quote", cls="banner-title", id="banner-title"),
            Div("click a property type to start", cls="banner-subtitle", id="banner-subtitle"),
            cls="banner-content"
        ),
        id="notification-banner",
        cls="notification-banner"
    )


def items_modal():
    """Modal for selecting individual items for an area"""
    # SVG icons for each item
    svg_icons = {
        "Sofa": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="28" width="52" height="16" rx="2"/><rect x="10" y="22" width="44" height="10" rx="2"/><line x1="10" y1="44" x2="10" y2="50"/><line x1="54" y1="44" x2="54" y2="50"/></svg>',
        "Accent Chair": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="16" y="28" width="32" height="16" rx="3"/><path d="M18 28 L18 16 Q18 12 24 12 L40 12 Q46 12 46 16 L46 28"/><rect x="12" y="30" width="6" height="14" rx="2"/><rect x="46" y="30" width="6" height="14" rx="2"/><line x1="20" y1="44" x2="20" y2="52"/><line x1="44" y1="44" x2="44" y2="52"/></svg>',
        "Coffee Table": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="32" cy="28" rx="24" ry="8"/><ellipse cx="32" cy="32" rx="24" ry="8"/><line x1="20" y1="36" x2="20" y2="48"/><line x1="44" y1="36" x2="44" y2="48"/></svg>',
        "End Table": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="16" y="18" width="32" height="6" rx="1"/><rect x="18" y="24" width="28" height="20" rx="1"/><line x1="20" y1="44" x2="20" y2="52"/><line x1="44" y1="44" x2="44" y2="52"/><line x1="18" y1="34" x2="46" y2="34"/></svg>',
        "Console": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="18" width="52" height="6" rx="1"/><line x1="10" y1="24" x2="10" y2="50"/><line x1="54" y1="24" x2="54" y2="50"/><rect x="12" y="30" width="40" height="12" rx="1"/></svg>',
        "Bench": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="28" width="48" height="10" rx="2"/><line x1="14" y1="38" x2="14" y2="50"/><line x1="50" y1="38" x2="50" y2="50"/></svg>',
        "Area Rug": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="20" width="48" height="32" rx="1"/><rect x="12" y="24" width="40" height="24" rx="1"/><line x1="8" y1="16" x2="8" y2="20"/><line x1="56" y1="16" x2="56" y2="20"/><line x1="8" y1="52" x2="8" y2="56"/><line x1="56" y1="52" x2="56" y2="56"/></svg>',
        "Lamp": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12 L44 12 L40 32 L24 32 Z"/><rect x="28" y="32" width="8" height="12"/><ellipse cx="32" cy="48" rx="12" ry="4"/></svg>',
        "Cushion": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="34" rx="6" ry="12"/><ellipse cx="52" cy="34" rx="6" ry="12"/><rect x="12" y="22" width="40" height="24"/></svg>',
        "Throw": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="12" y="24" width="40" height="24" rx="2"/><path d="M12 32 L52 32"/><path d="M12 40 L52 40"/><line x1="16" y1="48" x2="16" y2="54"/><line x1="24" y1="48" x2="24" y2="54"/><line x1="32" y1="48" x2="32" y2="54"/><line x1="40" y1="48" x2="40" y2="54"/><line x1="48" y1="48" x2="48" y2="54"/></svg>',
        "Table Decor": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><path d="M26 52 L26 40 Q26 36 22 36 L22 52 Z"/><path d="M38 52 L38 40 Q38 36 42 36 L42 52 Z"/><ellipse cx="32" cy="54" rx="14" ry="4"/><path d="M32 36 Q24 28 28 16"/><path d="M32 36 Q40 28 36 16"/><path d="M32 36 L32 20"/></svg>',
        "Wall Art": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="10" y="14" width="44" height="36" rx="2"/><rect x="14" y="18" width="36" height="28" rx="1"/><line x1="32" y1="10" x2="32" y2="14"/></svg>',
        "Formal Dining Set": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="10" y="20" width="44" height="20" rx="2"/><line x1="14" y1="40" x2="14" y2="50"/><line x1="50" y1="40" x2="50" y2="50"/><rect x="4" y="28" width="6" height="14" rx="1"/><rect x="54" y="28" width="6" height="14" rx="1"/><rect x="26" y="12" width="12" height="10" rx="1"/></svg>',
        "Bar Stool": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="32" cy="18" rx="14" ry="6"/><line x1="32" y1="24" x2="32" y2="52"/><line x1="20" y1="52" x2="44" y2="52"/><line x1="22" y1="40" x2="42" y2="40"/></svg>',
        "Casual Dining Set": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><circle cx="32" cy="28" r="16"/><line x1="32" y1="44" x2="32" y2="52"/><rect x="8" y="24" width="8" height="12" rx="1"/><rect x="48" y="24" width="8" height="12" rx="1"/></svg>',
        "Queen Bed Frame": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="28" width="52" height="18" rx="1"/><rect x="6" y="28" width="6" height="18"/><rect x="52" y="28" width="6" height="18"/><line x1="8" y1="46" x2="8" y2="52"/><line x1="56" y1="46" x2="56" y2="52"/></svg>',
        "Queen Headboard": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="12" width="48" height="36" rx="2"/><line x1="24" y1="12" x2="24" y2="48"/><line x1="40" y1="12" x2="40" y2="48"/></svg>',
        "Queen Mattress": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="24" width="48" height="20" rx="3"/><rect x="8" y="28" width="48" height="12" rx="2"/><line x1="12" y1="32" x2="52" y2="32"/><line x1="12" y1="36" x2="52" y2="36"/></svg>',
        "Queen Beddings": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="20" width="48" height="28" rx="2"/><path d="M8 28 Q32 36 56 28"/><rect x="10" y="14" width="16" height="8" rx="2"/><rect x="38" y="14" width="16" height="8" rx="2"/></svg>',
        "King Bed Frame": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="28" width="56" height="18" rx="1"/><rect x="4" y="28" width="6" height="18"/><rect x="54" y="28" width="6" height="18"/><line x1="6" y1="46" x2="6" y2="52"/><line x1="58" y1="46" x2="58" y2="52"/></svg>',
        "King Headboard": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="12" width="56" height="36" rx="2"/><line x1="22" y1="12" x2="22" y2="48"/><line x1="42" y1="12" x2="42" y2="48"/></svg>',
        "King Mattress": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="24" width="56" height="20" rx="3"/><rect x="4" y="28" width="56" height="12" rx="2"/><line x1="8" y1="32" x2="56" y2="32"/><line x1="8" y1="36" x2="56" y2="36"/></svg>',
        "King Beddings": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="20" width="56" height="28" rx="2"/><path d="M4 28 Q32 36 60 28"/><rect x="6" y="14" width="18" height="8" rx="2"/><rect x="40" y="14" width="18" height="8" rx="2"/></svg>',
        "Double Bed Frame": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="28" width="48" height="18" rx="1"/><rect x="8" y="28" width="6" height="18"/><rect x="50" y="28" width="6" height="18"/><line x1="10" y1="46" x2="10" y2="52"/><line x1="54" y1="46" x2="54" y2="52"/></svg>',
        "Double Headboard": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="10" y="12" width="44" height="36" rx="2"/><line x1="26" y1="12" x2="26" y2="48"/><line x1="38" y1="12" x2="38" y2="48"/></svg>',
        "Double Mattress": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="10" y="24" width="44" height="20" rx="3"/><rect x="10" y="28" width="44" height="12" rx="2"/><line x1="14" y1="32" x2="50" y2="32"/><line x1="14" y1="36" x2="50" y2="36"/></svg>',
        "Double Bedding": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="10" y="20" width="44" height="28" rx="2"/><path d="M10 28 Q32 36 54 28"/><rect x="12" y="14" width="14" height="8" rx="2"/><rect x="38" y="14" width="14" height="8" rx="2"/></svg>',
        "Night Stand": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="14" y="14" width="36" height="36" rx="2"/><line x1="14" y1="32" x2="50" y2="32"/><circle cx="32" cy="23" r="2"/><circle cx="32" cy="41" r="2"/><line x1="18" y1="50" x2="18" y2="56"/><line x1="46" y1="50" x2="46" y2="56"/></svg>',
        "Single Bed Frame": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="12" y="28" width="40" height="18" rx="1"/><rect x="12" y="28" width="6" height="18"/><rect x="46" y="28" width="6" height="18"/><line x1="14" y1="46" x2="14" y2="52"/><line x1="50" y1="46" x2="50" y2="52"/></svg>',
        "Single Headboard": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="14" y="12" width="36" height="36" rx="2"/><line x1="26" y1="12" x2="26" y2="48"/><line x1="38" y1="12" x2="38" y2="48"/></svg>',
        "Single Mattress": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="14" y="24" width="36" height="20" rx="3"/><rect x="14" y="28" width="36" height="12" rx="2"/><line x1="18" y1="32" x2="46" y2="32"/><line x1="18" y1="36" x2="46" y2="36"/></svg>',
        "Single Beddings": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="14" y="20" width="36" height="28" rx="2"/><path d="M14 28 Q32 36 50 28"/><rect x="20" y="14" width="24" height="8" rx="2"/></svg>',
        "Desk": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="18" width="52" height="6" rx="1"/><rect x="8" y="24" width="18" height="24" rx="1"/><line x1="8" y1="36" x2="26" y2="36"/><line x1="50" y1="24" x2="50" y2="50"/><line x1="14" y1="48" x2="14" y2="54"/><line x1="50" y1="50" x2="50" y2="54"/></svg>',
        "Chair": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="18" y="28" width="28" height="10" rx="2"/><path d="M20 28 L20 10 L44 10 L44 28"/><line x1="22" y1="38" x2="22" y2="54"/><line x1="42" y1="38" x2="42" y2="54"/></svg>',
        "Patio Set": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="12" y="22" width="40" height="14" rx="2"/><line x1="16" y1="36" x2="16" y2="48"/><line x1="48" y1="36" x2="48" y2="48"/><rect x="4" y="28" width="10" height="12" rx="2"/><rect x="50" y="28" width="10" height="12" rx="2"/></svg>',
    }

    # Items data: name, price
    items_data = [
        ("Sofa", 250),
        ("Accent Chair", 100),
        ("Coffee Table", 100),
        ("End Table", 50),
        ("Console", 75),
        ("Bench", 65),
        ("Area Rug", 80),
        ("Lamp", 40),
        ("Cushion", 15),
        ("Throw", 18),
        ("Table Decor", 10),
        ("Wall Art", 40),
        ("Formal Dining Set", 400),
        ("Bar Stool", 40),
        ("Casual Dining Set", 250),
        ("Queen Bed Frame", 20),
        ("Queen Headboard", 90),
        ("Queen Mattress", 50),
        ("Queen Beddings", 120),
        ("King Bed Frame", 20),
        ("King Headboard", 130),
        ("King Mattress", 50),
        ("King Beddings", 150),
        ("Double Bed Frame", 20),
        ("Double Headboard", 80),
        ("Double Mattress", 50),
        ("Double Bedding", 120),
        ("Night Stand", 60),
        ("Single Bed Frame", 20),
        ("Single Headboard", 75),
        ("Single Mattress", 50),
        ("Single Beddings", 80),
        ("Desk", 100),
        ("Chair", 50),
        ("Patio Set", 150),
    ]

    # Generate item buttons
    item_buttons = []
    for name, price in items_data:
        item_id = name.lower().replace(" ", "-")
        svg_icon = svg_icons.get(name, "")
        item_buttons.append(
            Div(
                Div(
                    Div(NotStr(svg_icon), cls="item-emoji"),
                    Span(name, cls="item-name"),
                    Span(f"${price}", cls="item-unit-price"),
                    Span("$0", cls="item-total-price"),
                    Div(
                        Button("-", cls="qty-btn qty-minus", onclick=f"decrementItem('{item_id}')"),
                        Span("0", cls="item-qty", id=f"qty-{item_id}"),
                        Button("+", cls="qty-btn qty-plus", onclick=f"incrementItem('{item_id}')"),
                        cls="item-qty-controls"
                    ),
                    cls="item-btn-content",
                    onclick=f"toggleItem('{item_id}')"
                ),
                cls="item-btn",
                data_item=item_id,
                data_price=str(price)
            )
        )

    return Div(
        Div(
            # Modal Header
            Div(
                H3("Select Living Room Items", cls="modal-title", id="items-modal-title"),
                Span("Total Item Price: $0", cls="modal-total", id="items-modal-total"),
                Span("Bulk Price: $500.00", cls="modal-bulk-price", id="items-modal-bulk-price"),
                Button("✕", cls="modal-close-btn", onclick="closeItemsModal()"),
                cls="modal-header"
            ),
            # Modal Body
            Div(
                *item_buttons,
                cls="modal-body items-grid"
            ),
            # Modal Footer
            Div(
                Div(
                    Button("Reset", cls="modal-reset-btn", onclick="resetItemsToDefault()"),
                    Button("Clear", cls="modal-clear-btn", onclick="clearAllItems()"),
                    cls="modal-footer-left"
                ),
                Button("Apply", cls="modal-apply-btn", onclick="applyItemsSelection()"),
                cls="modal-footer"
            ),
            cls="modal-content"
        ),
        id="items-modal",
        cls="items-modal hidden"
    )


def property_type_selector():
    """Property type selector with 3 square buttons"""
    return Section(
        notification_banner(),
        Div(
            # Property Type Row
            Div(
                Button(
                    Span("🏢", cls="property-icon"),
                    Span("Condo", cls="property-label"),
                    cls="property-btn",
                    data_type="condo",
                    onclick="selectPropertyType(this)"
                ),
                Button(
                    Span("🏘️", cls="property-icon"),
                    Span("Townhouse", cls="property-label"),
                    cls="property-btn",
                    data_type="townhouse",
                    onclick="selectPropertyType(this)"
                ),
                Button(
                    Span("🏡", cls="property-icon"),
                    Span("House", cls="property-label"),
                    cls="property-btn",
                    data_type="house",
                    onclick="selectPropertyType(this)"
                ),
                cls="property-selector"
            ),
            # Property Size Row - Placeholder shown by default
            Div(
                Button(Span("Property Size", cls="placeholder-text"), cls="property-btn placeholder-btn", disabled=True),
                id="size-placeholder",
                cls="property-selector placeholder-row"
            ),
            # Property Size Row (hidden by default)
            Div(
                id="size-selector",
                cls="property-selector size-selector hidden"
            ),
            # Area Placeholder (shown by default)
            Div(
                Button(Span("Staging Areas", cls="placeholder-text"), cls="property-btn placeholder-btn area-placeholder-btn", disabled=True),
                id="area-placeholder",
                cls="property-selector placeholder-row"
            ),
            # Area Selection Rows (hidden by default)
            Div(
                # Row 1: Living Room, Dining Room, Family Room
                Div(
                    Button(Span("Living Room", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="living-room", onclick="toggleArea(this)"),
                    Button(Span("Dining Room", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="dining-room", onclick="toggleArea(this)"),
                    Button(Span("Family Room", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="family-room", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 2: Kitchen Only, Kitchen with Island, Breakfast Area
                Div(
                    Button(Span("Kitchen Only", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="kitchen-only", onclick="toggleArea(this)"),
                    Button(Span("Kitchen Island", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="kitchen-island", onclick="toggleArea(this)"),
                    Button(Span("Breakfast Area", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="breakfast-area", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 3: Master Bedroom, 2nd Bedroom, 3rd Bedroom
                Div(
                    Button(Span("Master Bedroom", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="master-bedroom", onclick="toggleArea(this)"),
                    Button(Span("2nd Bedroom", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="2nd-bedroom", onclick="toggleArea(this)"),
                    Button(Span("3rd Bedroom", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="3rd-bedroom", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 4: 4th Bedroom, 5th Bedroom, 6th Bedroom
                Div(
                    Button(Span("4th Bedroom", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="4th-bedroom", onclick="toggleArea(this)"),
                    Button(Span("5th Bedroom", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="5th-bedroom", onclick="toggleArea(this)"),
                    Button(Span("6th Bedroom", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="6th-bedroom", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 5: Office, Bathrooms, Outdoor
                Div(
                    Button(Span("Office", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="office", onclick="toggleArea(this)"),
                    Button(Span("Bathrooms", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="bathrooms", onclick="toggleArea(this)"),
                    Button(Span("Outdoor", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="outdoor", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 6: Basement Living, Basement Dining, Basement Office
                Div(
                    Button(Span("Basement Living", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="basement-living", onclick="toggleArea(this)"),
                    Button(Span("Basement Dining", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="basement-dining", onclick="toggleArea(this)"),
                    Button(Span("Basement Office", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="basement-office", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 7: Basement 1st Bedroom, Basement 2nd Bedroom
                Div(
                    Button(Span("Basement 1st Bed", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="basement-1st-bedroom", onclick="toggleArea(this)"),
                    Button(Span("Basement 2nd Bed", cls="area-name"), Span("", cls="area-price"), Span("Selected Items", cls="area-selected-items", onclick="openItemsModal(event, this)"), cls="property-btn area-btn", data_area="basement-2nd-bedroom", onclick="toggleArea(this)"),
                    Div(cls="property-btn-spacer"),
                    cls="property-selector"
                ),
                id="area-selector",
                cls="area-selector hidden"
            ),
            # Items Modal
            items_modal(),
            cls="container"
        ),
        Script("""
            // Haptic feedback (vibration) for mobile
            function hapticFeedback() {
                if ('vibrate' in navigator) {
                    navigator.vibrate(10); // 10ms subtle vibration
                }
            }

            // Click sound using Web Audio API - sharp tick
            let audioContext = null;
            function playClickSound() {
                try {
                    if (!audioContext) {
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    }

                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();

                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);

                    // Sharp tick/click sound
                    oscillator.frequency.value = 3500;
                    oscillator.type = 'square';

                    gainNode.gain.setValueAtTime(0.08, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.02);

                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.02);
                } catch (e) {}
            }

            // Combined feedback
            function buttonFeedback() {
                hapticFeedback();
                playClickSound();
            }

            // Pricing constants
            const BASE_STAGING_FEE = 1450.00;
            const HUGE_AREA = 700.00;
            const BIG_AREA = 500.00;
            const SMALL_AREA = 200.00;

            // Get current selections
            function getSelections() {
                const propertyBtn = document.querySelector('.property-btn.selected:not(.size-btn):not(.area-btn)');
                const sizeBtn = document.querySelector('.size-btn.selected');

                return {
                    propertyType: propertyBtn ? propertyBtn.getAttribute('data-type') : null,
                    propertySize: sizeBtn ? sizeBtn.getAttribute('data-size') : null
                };
            }

            // Calculate base fee based on size
            function getBaseFee(propertySize) {
                let fee = BASE_STAGING_FEE;
                if (['2000-3000', '3000-4000', 'over-4000'].includes(propertySize)) {
                    fee += 800;
                } else if (propertySize === '1000-2000') {
                    fee += 200;
                }
                return fee;
            }

            // Get area price based on property type, size, and area
            function getAreaPrice(area, propertyType, propertySize) {
                const isLargeHouse = propertyType === 'house' && ['3000-4000', 'over-4000'].includes(propertySize);
                const isSmallCondo = propertyType === 'condo' && propertySize === 'under-1000';

                switch(area) {
                    case 'living-room':
                        return isLargeHouse ? HUGE_AREA : BIG_AREA;
                    case 'dining-room':
                        if (isSmallCondo) return SMALL_AREA;
                        return isLargeHouse ? HUGE_AREA : BIG_AREA;
                    case 'family-room':
                        return isLargeHouse ? HUGE_AREA : BIG_AREA;
                    case 'kitchen-only':
                        return 0;
                    case 'kitchen-island':
                        if (isSmallCondo) return 100;
                        return isLargeHouse ? 300 : 200;
                    case 'breakfast-area':
                        return SMALL_AREA;
                    case 'master-bedroom':
                        if (isSmallCondo) return SMALL_AREA;
                        return isLargeHouse ? HUGE_AREA : BIG_AREA;
                    case '2nd-bedroom':
                        return isLargeHouse ? BIG_AREA : SMALL_AREA;
                    case '3rd-bedroom':
                    case '4th-bedroom':
                    case '5th-bedroom':
                    case '6th-bedroom':
                        return SMALL_AREA;
                    case 'office':
                        return isLargeHouse ? BIG_AREA : SMALL_AREA;
                    case 'bathrooms':
                        return 0;
                    case 'basement-living':
                        return BIG_AREA;
                    case 'basement-dining':
                    case 'basement-1st-bedroom':
                    case 'basement-2nd-bedroom':
                    case 'basement-office':
                        return SMALL_AREA;
                    case 'outdoor':
                        return 150;
                    default:
                        return 0;
                }
            }

            // Update area button prices
            function updateAreaPrices() {
                const { propertyType, propertySize } = getSelections();
                if (!propertyType || !propertySize) return;

                document.querySelectorAll('.area-btn').forEach(btn => {
                    const area = btn.getAttribute('data-area');
                    updateAreaButtonPrice(btn, area, propertyType, propertySize);
                });

                calculateTotalFee();
            }

            // Update single area button price display
            function updateAreaButtonPrice(btn, area, propertyType, propertySize) {
                const bulkPrice = getAreaPrice(area, propertyType, propertySize);
                const itemTotal = getAreaItemTotal(area);

                // Use lesser of bulk price or item total
                let displayPrice = bulkPrice;
                if (itemTotal !== null && itemTotal < bulkPrice) {
                    displayPrice = itemTotal;
                }

                const priceSpan = btn.querySelector('.area-price');
                if (priceSpan) {
                    priceSpan.textContent = displayPrice > 0 ? '+$' + displayPrice : 'Included';
                }
            }

            // Calculate total staging fee
            function calculateTotalFee() {
                const { propertyType, propertySize } = getSelections();
                if (!propertyType || !propertySize) {
                    updateBannerFee(null);
                    return;
                }

                // Check if at least 1 area is selected
                const selectedAreas = document.querySelectorAll('.area-btn.selected');
                if (selectedAreas.length === 0) {
                    // No areas selected - show "select staging areas"
                    updateBanner('size-selected');
                    return;
                }

                let stagingFee = getBaseFee(propertySize);

                // Add selected area prices (use lesser of bulk price or item total)
                selectedAreas.forEach(btn => {
                    const area = btn.getAttribute('data-area');
                    const bulkPrice = getAreaPrice(area, propertyType, propertySize);
                    const itemTotal = getAreaItemTotal(area);

                    // Use item total if available and less than bulk price
                    if (itemTotal !== null && itemTotal < bulkPrice) {
                        stagingFee += itemTotal;
                    } else {
                        stagingFee += bulkPrice;
                    }
                });

                updateBannerFee(stagingFee);
            }

            // Update banner with fee
            function updateBannerFee(fee) {
                const title = document.getElementById('banner-title');
                const subtitle = document.getElementById('banner-subtitle');

                if (fee !== null) {
                    title.textContent = 'Staging Fee';
                    subtitle.textContent = '$' + fee.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' CAD';
                }
            }

            function updateBanner(state) {
                const title = document.getElementById('banner-title');
                const subtitle = document.getElementById('banner-subtitle');

                if (state === 'initial') {
                    title.textContent = 'Instant Quote';
                    subtitle.textContent = 'click a property type to start';
                } else if (state === 'property-selected') {
                    title.textContent = 'Instant Quote';
                    subtitle.textContent = 'select property size';
                } else if (state === 'size-selected') {
                    title.textContent = 'Instant Quote';
                    subtitle.textContent = 'select staging areas';
                }
            }

            const sizeOptions = {
                condo: [
                    { line1: '< 1000', line2: 'sq ft', value: 'under-1000' },
                    { line1: '1000 - 2000', line2: 'sq ft', value: '1000-2000' },
                    { line1: '2000 - 3000', line2: 'sq ft', value: '2000-3000' }
                ],
                townhouse: [
                    { line1: '1000 - 2000', line2: 'sq ft', value: '1000-2000' },
                    { line1: '2000 - 3000', line2: 'sq ft', value: '2000-3000' },
                    { line1: '3000 - 4000', line2: 'sq ft', value: '3000-4000' }
                ],
                house: [
                    { line1: '2000 - 3000', line2: 'sq ft', value: '2000-3000' },
                    { line1: '3000 - 4000', line2: 'sq ft', value: '3000-4000' },
                    { line1: '> 4000', line2: 'sq ft', value: 'over-4000' }
                ]
            };

            function selectPropertyType(btn) {
                buttonFeedback();
                const allBtns = document.querySelectorAll('.property-btn:not(.size-btn):not(.area-btn):not(.placeholder-btn)');
                const sizeSelector = document.getElementById('size-selector');
                const sizePlaceholder = document.getElementById('size-placeholder');
                const areaSelector = document.getElementById('area-selector');
                const areaPlaceholder = document.getElementById('area-placeholder');

                if (btn.classList.contains('selected')) {
                    // Toggle off if already selected
                    btn.classList.remove('selected');
                    allBtns.forEach(b => b.classList.remove('dimmed'));
                    sizeSelector.classList.add('hidden');
                    sizeSelector.innerHTML = '';
                    sizePlaceholder.classList.remove('hidden');
                    areaSelector.classList.add('hidden');
                    areaPlaceholder.classList.remove('hidden');
                    document.querySelectorAll('.area-btn').forEach(b => b.classList.remove('selected'));
                    updateBanner('initial');
                } else {
                    // Deselect all, select clicked one, dim others
                    allBtns.forEach(b => {
                        b.classList.remove('selected');
                        b.classList.add('dimmed');
                    });
                    btn.classList.add('selected');
                    btn.classList.remove('dimmed');

                    // Clear size selection and show size options
                    const type = btn.getAttribute('data-type');
                    showSizeOptions(type);

                    // Reset areas to placeholder (since size is cleared)
                    areaSelector.classList.add('hidden');
                    areaPlaceholder.classList.remove('hidden');
                    document.querySelectorAll('.area-btn').forEach(b => b.classList.remove('selected'));

                    updateBanner('property-selected');
                }
            }

            function showSizeOptions(type) {
                const sizeSelector = document.getElementById('size-selector');
                const sizePlaceholder = document.getElementById('size-placeholder');
                const options = sizeOptions[type];

                sizeSelector.innerHTML = options.map(opt => `
                    <button class="property-btn size-btn" data-size="${opt.value}" onclick="selectSize(this)">
                        <span class="size-line1">${opt.line1}</span>
                        <span class="size-line2">${opt.line2}</span>
                    </button>
                `).join('');

                sizePlaceholder.classList.add('hidden');
                sizeSelector.classList.remove('hidden');
            }

            function selectSize(btn) {
                buttonFeedback();
                const allSizeBtns = document.querySelectorAll('.size-btn');

                if (btn.classList.contains('selected')) {
                    btn.classList.remove('selected');
                    allSizeBtns.forEach(b => b.classList.remove('dimmed'));
                } else {
                    allSizeBtns.forEach(b => {
                        b.classList.remove('selected');
                        b.classList.add('dimmed');
                    });
                    btn.classList.add('selected');
                    btn.classList.remove('dimmed');
                }
                checkShowAreas();
                updateAreaPrices();
            }

            function checkShowAreas() {
                const { propertyType, propertySize } = getSelections();
                const areaSelector = document.getElementById('area-selector');
                const areaPlaceholder = document.getElementById('area-placeholder');

                if (propertyType && propertySize) {
                    areaPlaceholder.classList.add('hidden');
                    areaSelector.classList.remove('hidden');
                    updateBanner('size-selected');
                    updateAreaPrices();
                } else {
                    areaSelector.classList.add('hidden');
                    areaPlaceholder.classList.remove('hidden');
                    if (document.querySelector('.property-btn.selected:not(.size-btn):not(.area-btn)')) {
                        updateBanner('property-selected');
                    }
                }
            }

            function toggleArea(btn) {
                buttonFeedback();
                btn.classList.toggle('selected');
                calculateTotalFee();
            }

            // Items Modal Functions
            let currentArea = null;
            const areaItemsData = {}; // Store selected items per area

            // Area name mapping for modal title
            const areaNameMap = {
                'living-room': 'Living Room',
                'dining-room': 'Dining Room',
                'family-room': 'Family Room',
                'kitchen-only': 'Kitchen Only',
                'kitchen-island': 'Kitchen Island',
                'breakfast-area': 'Breakfast Area',
                'master-bedroom': 'Master Bedroom',
                '2nd-bedroom': '2nd Bedroom',
                '3rd-bedroom': '3rd Bedroom',
                '4th-bedroom': '4th Bedroom',
                '5th-bedroom': '5th Bedroom',
                '6th-bedroom': '6th Bedroom',
                'office': 'Office',
                'bathrooms': 'Bathrooms',
                'outdoor': 'Outdoor',
                'basement-living': 'Basement Living',
                'basement-dining': 'Basement Dining',
                'basement-office': 'Basement Office',
                'basement-1st-bedroom': 'Basement 1st Bedroom',
                'basement-2nd-bedroom': 'Basement 2nd Bedroom'
            };

            // Item column order from CSV
            const itemColumns = ['sofa','accent-chair','coffee-table','end-table','console','bench','area-rug','lamp','cushion','throw','table-decor','wall-art','formal-dining-set','bar-stool','casual-dining-set','queen-bed-frame','queen-headboard','queen-mattress','queen-beddings','king-bed-frame','king-headboard','king-mattress','king-beddings','double-bed-frame','double-headboard','double-mattress','double-bedding','night-stand','single-bed-frame','single-headboard','single-mattress','single-beddings','desk','chair','patio-set'];

            // Item prices lookup
            const itemPrices = {
                'sofa': 250, 'accent-chair': 100, 'coffee-table': 100, 'end-table': 50,
                'console': 75, 'bench': 65, 'area-rug': 80, 'lamp': 40, 'cushion': 15,
                'throw': 18, 'table-decor': 10, 'wall-art': 40, 'formal-dining-set': 400,
                'bar-stool': 40, 'casual-dining-set': 250, 'queen-bed-frame': 20,
                'queen-headboard': 90, 'queen-mattress': 50, 'queen-beddings': 120,
                'king-bed-frame': 20, 'king-headboard': 130, 'king-mattress': 50,
                'king-beddings': 150, 'double-bed-frame': 20, 'double-headboard': 80,
                'double-mattress': 50, 'double-bedding': 120, 'night-stand': 60,
                'single-bed-frame': 20, 'single-headboard': 75, 'single-mattress': 50,
                'single-beddings': 80, 'desk': 100, 'chair': 50, 'patio-set': 150
            };

            // Calculate item total for an area (uses saved items or defaults)
            function getAreaItemTotal(area) {
                // Use saved items if exists, otherwise use defaults
                let items = areaItemsData[area];
                if (!items) {
                    items = getDefaultItems(area);
                }
                if (!items) return null;

                let total = 0;
                for (const [itemId, qty] of Object.entries(items)) {
                    const price = itemPrices[itemId] || 0;
                    total += price * qty;
                }
                return total;
            }

            // Default items data: defaultAreaItems[suiteType][size][areaSlug] = [qty array matching itemColumns]
            const defaultAreaItems = {
                'condo': {
                    '<1000': {
                        'living-room': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,0,0,0,0,0,0,2,6,1,0,2,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'bathrooms': [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-living': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    },
                    '1000-2000': {
                        'living-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,2,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,1,0,1,0,1,1,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-living': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    },
                    '2000-3000': {
                        'living-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,2,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,1,0,1,0,1,1,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-living': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    }
                },
                'townhouse': {
                    '1000-2000': {
                        'living-room': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,0,0,1,0,1,0,2,6,1,0,2,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        'basement-living': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0]
                    },
                    '2000-3000': {
                        'living-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,2,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,1,0,1,0,1,1,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        'basement-living': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0]
                    },
                    '3000-4000': {
                        'living-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,2,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,1,0,1,0,1,1,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,1,3,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        'basement-living': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0]
                    }
                },
                'house': {
                    '2000-3000': {
                        'living-room': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,0,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,2,0,1,0,1,1,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,1,4,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        'basement-living': [1,2,1,2,0,0,1,2,4,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,0,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0]
                    },
                    '3000-4000': {
                        'living-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,3,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,2,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,1,0,1,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [1,0,1,0,0,1,1,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,2,4,1,0,2,0,0,0,1,1,1,0,0,0,0,0,2,2,2,1,2,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,2,4,0,0,2,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        'basement-living': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,2,4,0,0,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0]
                    },
                    '>4000': {
                        'living-room': [1,2,1,2,1,1,1,2,6,1,7,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-only': [0,0,0,0,0,0,0,0,0,0,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'kitchen-island': [0,0,0,0,0,0,0,0,0,0,3,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'breakfast-area': [0,0,0,0,0,0,0,0,0,0,2,3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'dining-room': [0,0,0,0,1,0,1,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'family-room': [1,2,1,2,1,1,1,2,6,1,7,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'master-bedroom': [0,0,0,0,0,0,0,2,6,1,0,2,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,2,0,0,0,0,0,0,0],
                        '2nd-bedroom': [0,0,0,0,0,0,0,2,4,1,0,2,0,0,0,1,1,1,0,0,0,0,0,2,2,2,1,2,0,0,0,0,0,0,0],
                        '3rd-bedroom': [0,0,0,0,0,0,0,2,4,0,0,2,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        '4th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '5th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        '6th-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                        'office': [0,0,0,0,0,0,1,0,0,0,4,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'bathrooms': [0,0,0,0,1,0,0,0,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'outdoor': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        'basement-living': [1,2,1,2,1,1,1,2,6,1,7,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-dining': [0,0,0,0,0,0,0,0,0,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                        'basement-office': [0,0,0,0,0,0,1,0,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
                        'basement-1st-bedroom': [0,0,0,0,0,0,0,2,4,1,0,2,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
                        'basement-2nd-bedroom': [0,0,0,0,0,0,0,1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0]
                    }
                }
            };

            // Get current property type and size from selected buttons
            function getCurrentPropertyType() {
                const selectedBtn = document.querySelector('.property-btn.selected');
                if (!selectedBtn) return null;
                const text = selectedBtn.textContent.toLowerCase();
                if (text.includes('condo')) return 'condo';
                if (text.includes('townhouse')) return 'townhouse';
                if (text.includes('house')) return 'house';
                return null;
            }

            function getCurrentSize() {
                const selectedBtn = document.querySelector('.size-btn.selected');
                if (!selectedBtn) return null;
                const text = selectedBtn.textContent.replace(/\\s+/g, '');
                if (text.includes('<1000')) return '<1000';
                if (text.includes('1000-2000') || text.includes('1000')) return '1000-2000';
                if (text.includes('2000-3000') || text.includes('2000')) return '2000-3000';
                if (text.includes('3000-4000') || text.includes('3000')) return '3000-4000';
                if (text.includes('>4000') || text.includes('4000')) return '>4000';
                return null;
            }

            function getDefaultItems(area) {
                const propertyType = getCurrentPropertyType();
                const size = getCurrentSize();
                if (!propertyType || !size) return null;
                const typeData = defaultAreaItems[propertyType];
                if (!typeData) return null;
                const sizeData = typeData[size];
                if (!sizeData) return null;
                const areaDefaults = sizeData[area];
                if (!areaDefaults) return null;

                // Convert array to object with item IDs
                const result = {};
                itemColumns.forEach((itemId, index) => {
                    if (areaDefaults[index] > 0) {
                        result[itemId] = areaDefaults[index];
                    }
                });
                return result;
            }

            function openItemsModal(event, element) {
                event.stopPropagation();
                buttonFeedback();

                const areaBtn = element.closest('.area-btn');
                currentArea = areaBtn.getAttribute('data-area');
                const areaName = areaNameMap[currentArea] || currentArea;

                // Update modal title
                document.getElementById('items-modal-title').textContent = 'Select ' + areaName + ' Items';

                // Update bulk price from area button
                const areaPriceEl = areaBtn.querySelector('.area-price');
                const bulkPrice = areaPriceEl ? areaPriceEl.textContent : '$0';
                document.getElementById('items-modal-bulk-price').textContent = areaName + ' Bulk Price: ' + bulkPrice.replace('+', '');

                // Load saved items for this area
                loadAreaItems(currentArea);

                // Show modal
                document.getElementById('items-modal').classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }

            function closeItemsModal() {
                buttonFeedback();
                document.getElementById('items-modal').classList.add('hidden');
                document.body.style.overflow = '';
                currentArea = null;
            }

            function loadAreaItems(area) {
                // Use saved items if exists, otherwise load defaults from CSV data
                let itemsToLoad = areaItemsData[area];
                if (!itemsToLoad) {
                    itemsToLoad = getDefaultItems(area) || {};
                }

                // Reset all items first
                document.querySelectorAll('.item-btn').forEach(btn => {
                    const itemId = btn.getAttribute('data-item');
                    const qty = itemsToLoad[itemId] || 0;
                    const qtySpan = document.getElementById('qty-' + itemId);

                    if (qtySpan) {
                        qtySpan.textContent = qty;
                    }

                    // Update selection state
                    if (qty > 0) {
                        btn.classList.add('selected');
                    } else {
                        btn.classList.remove('selected');
                    }

                    // Update total price display
                    updateItemTotalPrice(btn);
                });

                updateModalTotal();
            }

            function toggleItem(itemId) {
                buttonFeedback();
                const btn = document.querySelector('.item-btn[data-item="' + itemId + '"]');
                const qtySpan = document.getElementById('qty-' + itemId);
                const currentQty = parseInt(qtySpan.textContent);

                if (currentQty === 0) {
                    // Select: set to 1
                    qtySpan.textContent = '1';
                    btn.classList.add('selected');
                } else {
                    // Deselect: set to 0
                    qtySpan.textContent = '0';
                    btn.classList.remove('selected');
                }

                updateItemTotalPrice(btn);
                updateModalTotal();
            }

            function incrementItem(itemId) {
                event.stopPropagation();
                buttonFeedback();
                const btn = document.querySelector('.item-btn[data-item="' + itemId + '"]');
                const qtySpan = document.getElementById('qty-' + itemId);
                const currentQty = parseInt(qtySpan.textContent);

                qtySpan.textContent = currentQty + 1;
                btn.classList.add('selected');

                updateItemTotalPrice(btn);
                updateModalTotal();
            }

            function decrementItem(itemId) {
                event.stopPropagation();
                buttonFeedback();
                const btn = document.querySelector('.item-btn[data-item="' + itemId + '"]');
                const qtySpan = document.getElementById('qty-' + itemId);
                const currentQty = parseInt(qtySpan.textContent);

                if (currentQty > 0) {
                    const newQty = currentQty - 1;
                    qtySpan.textContent = newQty;

                    if (newQty === 0) {
                        btn.classList.remove('selected');
                    }

                    updateItemTotalPrice(btn);
                    updateModalTotal();
                }
            }

            function updateItemTotalPrice(btn) {
                const price = parseInt(btn.getAttribute('data-price'));
                const itemId = btn.getAttribute('data-item');
                const qty = parseInt(document.getElementById('qty-' + itemId).textContent);
                const totalPriceSpan = btn.querySelector('.item-total-price');

                if (totalPriceSpan) {
                    totalPriceSpan.textContent = '$' + (price * qty);
                }
            }

            function updateModalTotal() {
                let total = 0;

                document.querySelectorAll('.item-btn').forEach(btn => {
                    const price = parseInt(btn.getAttribute('data-price'));
                    const itemId = btn.getAttribute('data-item');
                    const qty = parseInt(document.getElementById('qty-' + itemId).textContent);
                    total += price * qty;
                });

                document.getElementById('items-modal-total').textContent = 'Total Item Price: $' + total;
            }

            function resetItemsToDefault() {
                buttonFeedback();
                if (!currentArea) return;

                // Get default items for this area
                const defaults = getDefaultItems(currentArea) || {};

                // Reset all items to defaults
                document.querySelectorAll('.item-btn').forEach(btn => {
                    const itemId = btn.getAttribute('data-item');
                    const qty = defaults[itemId] || 0;
                    const qtySpan = document.getElementById('qty-' + itemId);

                    if (qtySpan) {
                        qtySpan.textContent = qty;
                    }

                    if (qty > 0) {
                        btn.classList.add('selected');
                    } else {
                        btn.classList.remove('selected');
                    }

                    updateItemTotalPrice(btn);
                });

                updateModalTotal();
            }

            function clearAllItems() {
                buttonFeedback();

                // Set all items to 0
                document.querySelectorAll('.item-btn').forEach(btn => {
                    const itemId = btn.getAttribute('data-item');
                    const qtySpan = document.getElementById('qty-' + itemId);

                    if (qtySpan) {
                        qtySpan.textContent = '0';
                    }

                    btn.classList.remove('selected');
                    updateItemTotalPrice(btn);
                });

                updateModalTotal();
            }

            function applyItemsSelection() {
                buttonFeedback();

                if (!currentArea) {
                    closeItemsModal();
                    return;
                }

                // Save current selections for this area
                const selections = {};
                document.querySelectorAll('.item-btn').forEach(btn => {
                    const itemId = btn.getAttribute('data-item');
                    const qty = parseInt(document.getElementById('qty-' + itemId).textContent);
                    if (qty > 0) {
                        selections[itemId] = qty;
                    }
                });

                areaItemsData[currentArea] = selections;

                // Update the area button price display
                const { propertyType, propertySize } = getSelections();
                const areaBtn = document.querySelector('.area-btn[data-area="' + currentArea + '"]');
                if (areaBtn && propertyType && propertySize) {
                    updateAreaButtonPrice(areaBtn, currentArea, propertyType, propertySize);
                }

                closeItemsModal();

                // Recalculate total fee with new item selections
                calculateTotalFee();
            }

            // Close modal on backdrop click
            document.addEventListener('click', function(event) {
                const modal = document.getElementById('items-modal');
                if (event.target === modal) {
                    closeItemsModal();
                }
            });

            // Close modal on Escape key
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape') {
                    const modal = document.getElementById('items-modal');
                    if (!modal.classList.contains('hidden')) {
                        closeItemsModal();
                    }
                }
            });
        """),
        cls="property-type-section"
    )


def get_property_selector_styles():
    """CSS for property type selector - Mobile first"""
    return """
    /* Notification Banner */
    .notification-banner {
        position: fixed;
        top: 59px;
        left: 0;
        right: 0;
        z-index: 100;
        color: var(--color-primary);
        padding: 12px 15px;
        text-align: center;
    }

    [data-theme="light"] .notification-banner {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
    }

    [data-theme="dark"] .notification-banner {
        background: rgba(26, 26, 26, 0.3);
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
    }

    .banner-content {
        max-width: 600px;
        margin: 0 auto;
    }

    .banner-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .banner-subtitle {
        font-size: 14px;
        font-weight: 400;
        opacity: 0.9;
    }

    /* Property Type Section */
    .property-type-section {
        padding: 0 10px 20px;
        background: var(--bg-primary);
    }

    .property-type-section > .container {
        padding-top: 85px;  /* Account for fixed banner height (~77px) */
    }

    .property-selector {
        display: flex;
        gap: 10px;
        width: 100%;
        margin-top: 10px;
    }

    .property-selector:first-child {
        margin-top: 0;
    }

    .size-selector {
        margin-top: 10px;
    }

    .size-selector.hidden {
        display: none;
    }

    .property-btn {
        flex: 1;
        aspect-ratio: 3 / 2;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: var(--bg-secondary);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        -webkit-tap-highlight-color: transparent;
    }

    /* Hover effect only for devices with hover capability */
    @media (hover: hover) {
        .property-btn:hover {
            border-color: var(--border-hover);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
    }

    .property-btn.selected {
        border-color: var(--color-primary);
        background: var(--bg-secondary);
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1), 0 4px 16px rgba(0, 0, 0, 0.08);
    }

    [data-theme="dark"] .property-btn.selected {
        border-color: #fff;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.15), 0 4px 16px rgba(255, 255, 255, 0.05);
    }

    .property-btn.dimmed {
        opacity: 0.4;
    }

    .property-btn-spacer {
        flex: 1;
        aspect-ratio: 3 / 2;
        visibility: hidden;
    }

    .property-icon {
        font-size: calc((100vw - 40px) / 3 * 2 / 3 * 0.5);
        line-height: 1;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        margin-top: -12%;
    }

    .property-label {
        position: absolute;
        bottom: 10px;
        left: 0;
        right: 0;
        font-size: 12px;
        font-weight: 600;
        color: var(--color-primary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
    }

    /* Size button text styles */
    .size-btn {
        justify-content: center;
        gap: 2px;
    }

    .size-line1 {
        font-size: 14px;
        font-weight: 700;
        color: var(--color-primary);
        line-height: 1.2;
    }

    .size-line2 {
        font-size: 14px;
        font-weight: 700;
        color: var(--color-primary);
        line-height: 1.2;
    }

    /* Placeholder Buttons */
    .placeholder-row {
        margin-top: 10px;
    }

    .placeholder-row.hidden {
        display: none;
    }

    .placeholder-btn {
        flex: 1;
        aspect-ratio: auto;
        height: calc((100vw - 40px) / 3 * 2 / 3);
        cursor: not-allowed;
        opacity: 0.5;
    }

    .placeholder-btn:disabled {
        pointer-events: none;
    }

    .placeholder-text {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-secondary);
    }

    .area-placeholder-btn {
        height: calc(((100vw - 40px) / 3 * 2 / 3) * 7 + 60px);
    }

    /* Area Selector */
    .area-selector {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 10px;
    }

    .area-selector.hidden {
        display: none;
    }

    .area-selector .property-selector {
        margin-top: 0;
    }

    /* Area button text styles */
    .area-name {
        font-size: 12px;
        font-weight: 600;
        color: var(--color-primary);
        line-height: 1.2;
        text-align: center;
    }

    .area-price {
        font-size: 11px;
        font-weight: 500;
        color: var(--color-secondary);
        margin-top: 2px;
    }

    .area-btn.selected .area-price {
        color: var(--color-primary);
    }

    /* Selected Items Link */
    .area-selected-items {
        font-size: 10px;
        font-weight: 500;
        color: var(--color-secondary);
        text-decoration: underline;
        margin-top: 4px;
        cursor: pointer;
        transition: color 0.2s ease;
    }

    .area-selected-items:hover {
        color: var(--color-primary);
    }

    .area-btn.selected .area-selected-items {
        color: var(--color-primary);
    }

    /* Items Modal */
    .items-modal {
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        bottom: 80px;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 15px;
    }

    .items-modal.hidden {
        display: none;
    }

    .modal-content {
        background: var(--bg-primary);
        border-radius: 16px;
        width: 100%;
        max-width: 600px;
        height: 100%;
        max-height: 100%;
        display: flex;
        flex-direction: column;
        position: relative;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        padding: 20px;
        border-bottom: 1px solid var(--border-color);
        position: relative;
    }

    .modal-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--color-primary);
        margin: 0;
        padding-right: 40px;
    }

    .modal-total {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-secondary);
        display: block;
        margin-top: 4px;
    }

    .modal-bulk-price {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-primary);
        display: block;
        margin-top: 2px;
    }

    .modal-close-btn {
        position: absolute;
        top: 15px;
        right: 15px;
        width: 32px;
        height: 32px;
        border: none;
        background: var(--bg-secondary);
        border-radius: 50%;
        font-size: 18px;
        cursor: pointer;
        color: var(--color-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: opacity 0.2s ease;
    }

    .modal-close-btn:hover {
        opacity: 0.7;
    }

    .modal-body {
        padding: 15px;
        overflow-y: auto;
        flex: 1;
    }

    .items-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
    }

    .item-btn {
        aspect-ratio: 2 / 3;
        background: var(--bg-secondary);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        overflow: visible;
    }

    .item-btn:hover {
        border-color: var(--border-hover);
    }

    .item-btn.selected {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
    }

    [data-theme="dark"] .item-btn.selected {
        border-color: #fff;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
    }

    .item-btn-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        height: 100%;
        padding: 0;
        gap: 0;
    }

    .item-emoji {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 50%;
        width: 100%;
        padding: 8px;
    }

    .item-emoji svg {
        width: 100%;
        height: 100%;
        max-width: 64px;
        max-height: 64px;
        stroke: var(--color-primary);
    }

    .item-name {
        font-size: 12px;
        font-weight: 600;
        color: var(--color-primary);
        text-align: center;
        line-height: 1.1;
        margin-top: 4px;
    }

    .item-unit-price {
        font-size: 12px;
        font-weight: 500;
        color: var(--color-secondary);
        margin-top: 2px;
    }

    .item-total-price {
        font-size: 12px;
        font-weight: 500;
        color: var(--color-primary);
        display: none;
        margin-top: 2px;
    }

    .item-btn.selected .item-total-price {
        display: block;
    }

    .item-btn.selected .item-unit-price {
        display: none;
    }

    .item-qty-controls {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4px;
    }

    .qty-btn {
        width: 28px;
        height: 28px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        border-radius: 50%;
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        line-height: 1;
        -webkit-tap-highlight-color: transparent;
    }

    .qty-btn:hover {
        background: var(--bg-secondary);
    }

    .qty-btn:active {
        transform: scale(0.95);
    }

    .item-qty {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-primary);
        min-width: 20px;
        text-align: center;
    }

    .modal-footer {
        padding: 15px 20px;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
    }

    .modal-reset-btn {
        padding: 12px 20px;
        background: transparent;
        color: var(--color-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .modal-reset-btn:hover {
        background: var(--bg-secondary);
        border-color: var(--color-secondary);
    }

    .modal-clear-btn {
        padding: 12px 20px;
        background: transparent;
        color: var(--color-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .modal-clear-btn:hover {
        background: var(--bg-secondary);
        border-color: var(--color-secondary);
    }

    .modal-footer-left {
        display: flex;
        gap: 10px;
    }

    .modal-apply-btn {
        padding: 12px 30px;
        background: var(--color-primary);
        color: var(--bg-primary);
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }

    .modal-apply-btn:hover {
        opacity: 0.8;
    }

    /* Tablet and up */
    @media (min-width: 768px) {
        .property-type-section {
            padding: 0 20px 30px;
        }

        .property-type-section > .container {
            padding-top: 65px;  /* Account for fixed banner height */
        }

        .property-selector {
            gap: 15px;
            max-width: 500px;
            margin: 15px auto 0;
        }

        .property-selector:first-child {
            margin-top: 0;
        }

        .property-icon {
            font-size: calc((500px - 30px) / 3 * 2 / 3 * 0.5);
        }

        .property-label {
            font-size: 13px;
        }

        .property-btn {
            border-radius: 20px;
        }

        .placeholder-btn {
            height: calc((500px - 30px) / 3 * 2 / 3);
        }

        .area-placeholder-btn {
            height: calc(((500px - 30px) / 3 * 2 / 3) * 7 + 60px);
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .property-type-section {
            padding: 0 30px 40px;
        }

        .property-type-section > .container {
            padding-top: 70px;  /* Account for fixed banner height */
        }

        .property-selector {
            gap: 20px;
            max-width: 600px;
            margin: 20px auto 0;
        }

        .property-selector:first-child {
            margin-top: 0;
        }

        .property-icon {
            font-size: calc((600px - 40px) / 3 * 2 / 3 * 0.5);
        }

        .property-label {
            font-size: 14px;
        }

        .placeholder-btn {
            height: calc((600px - 40px) / 3 * 2 / 3);
        }

        .area-placeholder-btn {
            height: calc(((600px - 40px) / 3 * 2 / 3) * 7 + 80px);
        }
    }
    """


def staging_inquiry_page():
    """Staging Inquiry page"""
    content = Div(
        property_type_selector(),
        cls="staging-inquiry-content"
    )

    additional_styles = get_property_selector_styles()

    return create_page(
        "Get a Quote | Astra Staging",
        content,
        additional_styles=additional_styles,
        description="Get an instant staging quote from Astra Staging. Fill out our form with your property details and receive a customized quote within 24 hours.",
        keywords="staging quote, home staging price, staging cost estimate, GTA staging services",
        hide_floating_buttons=True
    )
