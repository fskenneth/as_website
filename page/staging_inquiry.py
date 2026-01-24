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

    /* Desktop (768px+) */
    @media (min-width: 768px) {
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

        .form-row {
            flex-direction: row;
        }

        .form-row .form-group {
            flex: 1;
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
                    onclick=f"openItemSelectModal('{name}')"
                ),
                cls="item-btn",
                data_item=item_id,
                data_price=str(price),
                data_name=name
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
                # Photos Section at top of Items Modal
                Div(
                    # Hidden file input for photo upload
                    Input(type="file", id="items-photo-upload-input", accept="image/*", multiple=True, onchange="handleItemsPhotoUpload(event)", style="display:none"),
                    # Camera section (mobile only)
                    Div(
                        Div(
                            Video(id="items-camera-preview", autoplay=True, playsinline=True, cls="camera-preview"),
                            Canvas(id="items-camera-canvas", cls="camera-canvas hidden"),
                            # Close button at top right
                            Button(
                                "×",
                                cls="camera-close-btn",
                                id="items-camera-close-btn",
                                onclick="closeCameraView()"
                            ),
                            # Photo thumbnail preview at bottom left
                            Button(
                                Span(id="items-photo-count-badge", cls="photo-count-badge hidden"),
                                id="items-photo-thumbnail-preview",
                                cls="photo-thumbnail-preview hidden",
                                onclick="openPhotosGallery()"
                            ),
                            # Shutter button at bottom center
                            Button(
                                Div(cls="shutter-inner"),
                                cls="shutter-btn",
                                id="items-shutter-btn",
                                onclick="captureItemsPhoto()"
                            ),
                            cls="camera-preview-container"
                        ),
                        id="items-camera-section",
                        cls="camera-section"
                    ),
                    # Photos Gallery Modal
                    Div(
                        Div(
                            Div(
                                H3("Taken Photos", cls="photos-gallery-title"),
                                Button("×", cls="photos-gallery-close-btn", onclick="closePhotosGallery()"),
                                cls="photos-gallery-header"
                            ),
                            Div(id="photos-gallery-grid", cls="photos-gallery-grid"),
                            cls="photos-gallery-content",
                            onclick="event.stopPropagation()"
                        ),
                        id="photos-gallery-modal",
                        cls="photos-gallery-modal hidden",
                        onclick="closePhotosGallery()"
                    ),
                    # Photos carousel
                    Div(
                        Div(
                            id="items-photos-carousel-container",
                            cls="photos-carousel-container"
                        ),
                        Button("‹", cls="carousel-nav-btn carousel-prev", onclick="prevItemsPhoto()", id="items-photos-prev-btn"),
                        Button("›", cls="carousel-nav-btn carousel-next", onclick="nextItemsPhoto()", id="items-photos-next-btn"),
                        Div(id="items-photos-carousel-counter", cls="photos-carousel-counter"),
                        id="items-photos-preview-grid",
                        cls="photos-carousel-wrapper"
                    ),
                    id="items-photos-section",
                    cls="items-photos-section"
                ),
                # Items Grid
                Div(
                    *item_buttons,
                    cls="items-grid-container"
                ),
                cls="modal-body items-modal-body"
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


def item_select_modal():
    """Modal for selecting specific item images from inventory"""
    return Div(
        Div(
            # Modal Header
            Div(
                H3("Select Item", cls="modal-title", id="item-select-modal-title"),
                Button("✕", cls="modal-close-btn", onclick="closeItemSelectModal()"),
                cls="modal-header"
            ),
            # Modal Body - Grid of item images
            Div(
                Div(
                    id="item-select-grid",
                    cls="item-select-grid"
                ),
                cls="modal-body item-select-modal-body"
            ),
            cls="modal-content"
        ),
        id="item-select-modal",
        cls="items-modal item-select-modal hidden"
    )


def inquiry_modal():
    """Modal for inquiry form with fields from reserve page (except Payment and Policies)"""
    return Div(
        Div(
            # Modal Header
            Div(
                H3("Request Staging Quote", cls="modal-title", id="inquiry-modal-title"),
                Button("✕", cls="modal-close-btn", onclick="closeInquiryModal()"),
                cls="modal-header"
            ),
            # Modal Body - Single form with all fields
            Div(
                Form(
                    # Staging Date
                    Div(
                        Label("Preferred Staging Date", cls="inquiry-form-label", For="inquiry-staging-date"),
                        Input(type="date", id="inquiry-staging-date", cls="inquiry-form-input"),
                        cls="inquiry-form-group"
                    ),
                    # Property Address
                    Div(
                        Label("Property Address *", cls="inquiry-form-label", For="inquiry-property-address"),
                        Input(type="text", id="inquiry-property-address", cls="inquiry-form-input",
                              placeholder="Enter property address", required=True),
                        cls="inquiry-form-group"
                    ),
                    # Name row
                    Div(
                        Div(
                            Label("First Name *", cls="inquiry-form-label", For="inquiry-first-name"),
                            Input(type="text", id="inquiry-first-name", cls="inquiry-form-input",
                                  placeholder="First name", required=True),
                            cls="inquiry-form-group"
                        ),
                        Div(
                            Label("Last Name *", cls="inquiry-form-label", For="inquiry-last-name"),
                            Input(type="text", id="inquiry-last-name", cls="inquiry-form-input",
                                  placeholder="Last name", required=True),
                            cls="inquiry-form-group"
                        ),
                        cls="inquiry-form-row"
                    ),
                    # Contact row
                    Div(
                        Div(
                            Label("Email *", cls="inquiry-form-label", For="inquiry-email"),
                            Input(type="email", id="inquiry-email", cls="inquiry-form-input",
                                  placeholder="your@email.com", required=True),
                            cls="inquiry-form-group"
                        ),
                        Div(
                            Label("Phone *", cls="inquiry-form-label", For="inquiry-phone"),
                            Input(type="tel", id="inquiry-phone", cls="inquiry-form-input",
                                  placeholder="(123) 456-7890", required=True),
                            cls="inquiry-form-group"
                        ),
                        cls="inquiry-form-row"
                    ),
                    # Add-ons
                    Div(
                        Label("Add-ons (Optional)", cls="inquiry-form-label"),
                        Div(
                            Label(
                                Input(type="checkbox", id="inquiry-addon-photos", value="photos", cls="inquiry-checkbox"),
                                Span("Professional Photography (+$199)", cls="inquiry-checkbox-label"),
                                cls="inquiry-checkbox-item"
                            ),
                            Label(
                                Input(type="checkbox", id="inquiry-addon-consultation", value="consultation", cls="inquiry-checkbox"),
                                Span("Staging Consultation (Free)", cls="inquiry-checkbox-label"),
                                cls="inquiry-checkbox-item"
                            ),
                            cls="inquiry-addons-list"
                        ),
                        cls="inquiry-form-group"
                    ),
                    # Special Requests
                    Div(
                        Label("Special Requests or Notes", cls="inquiry-form-label", For="inquiry-special-requests"),
                        Textarea(id="inquiry-special-requests", cls="inquiry-form-textarea",
                                 placeholder="Any special requests or questions? (Optional)", rows="3"),
                        cls="inquiry-form-group"
                    ),
                    # Hidden fields for staging data
                    Input(type="hidden", id="inquiry-property-type"),
                    Input(type="hidden", id="inquiry-property-size"),
                    Input(type="hidden", id="inquiry-selected-areas"),
                    Input(type="hidden", id="inquiry-selected-items"),
                    Input(type="hidden", id="inquiry-total-fee"),
                    id="inquiry-form"
                ),
                cls="modal-body inquiry-form-body"
            ),
            # Modal Footer
            Div(
                Button("Submit Inquiry", cls="inquiry-submit-btn", onclick="submitInquiry()"),
                cls="modal-footer inquiry-modal-footer"
            ),
            cls="modal-content inquiry-modal-content"
        ),
        id="inquiry-modal",
        cls="inquiry-modal hidden"
    )


def image_preview_modal():
    """Modal for displaying 2D image of 3D model"""
    return Div(
        # Close button - positioned at modal level
        Button("✕", cls="image-modal-close-btn", onclick="event.stopPropagation(); close2DImageModal()"),
        # Image container
        Div(
            Div(
                Img(id="modal-2d-image", src="", alt="2D Preview", cls="modal-2d-image", onclick="event.stopPropagation()"),
                cls="image-modal-content",
                onclick="event.stopPropagation()"
            ),
            cls="image-modal-inner",
            onclick="event.stopPropagation()"
        ),
        id="image-preview-modal",
        cls="image-preview-modal hidden",
        onclick="close2DImageModal()"
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
                    Button(Span("Living Room", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="living-room", onclick="toggleArea(this)"),
                    Button(Span("Dining Room", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="dining-room", onclick="toggleArea(this)"),
                    Button(Span("Family Room", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="family-room", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 2: Kitchen Only, Kitchen with Island, Breakfast Area
                Div(
                    Button(Span("Kitchen Only", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="kitchen-only", onclick="toggleArea(this)"),
                    Button(Span("Kitchen Island", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="kitchen-island", onclick="toggleArea(this)"),
                    Button(Span("Breakfast Area", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="breakfast-area", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 3: Master Bedroom, 2nd Bedroom, 3rd Bedroom
                Div(
                    Button(Span("Master Bedroom", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="master-bedroom", onclick="toggleArea(this)"),
                    Button(Span("2nd Bedroom", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="2nd-bedroom", onclick="toggleArea(this)"),
                    Button(Span("3rd Bedroom", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="3rd-bedroom", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 4: 4th Bedroom, 5th Bedroom, 6th Bedroom
                Div(
                    Button(Span("4th Bedroom", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="4th-bedroom", onclick="toggleArea(this)"),
                    Button(Span("5th Bedroom", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="5th-bedroom", onclick="toggleArea(this)"),
                    Button(Span("6th Bedroom", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="6th-bedroom", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 5: Office, Bathrooms, Outdoor
                Div(
                    Button(Span("Office", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="office", onclick="toggleArea(this)"),
                    Button(Span("Bathrooms", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="bathrooms", onclick="toggleArea(this)"),
                    Button(Span("Outdoor", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="outdoor", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 6: Basement Living, Basement Dining, Basement Office
                Div(
                    Button(Span("Basement Living", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="basement-living", onclick="toggleArea(this)"),
                    Button(Span("Basement Dining", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="basement-dining", onclick="toggleArea(this)"),
                    Button(Span("Basement Office", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="basement-office", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 7: Basement 1st Bedroom, Basement 2nd Bedroom
                Div(
                    Button(Span("Basement 1st Bed", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="basement-1st-bedroom", onclick="toggleArea(this)"),
                    Button(Span("Basement 2nd Bed", cls="area-name"), Span("", cls="area-price"), Div(cls="area-carousel"), Div(Span(Span(NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'), " Items", cls="area-action-btn-content"), cls="area-action-btn", onclick="openItemsModal(event, this)"), cls="area-actions"), cls="property-btn area-btn", data_area="basement-2nd-bedroom", onclick="toggleArea(this)"),
                    Div(cls="property-btn-spacer"),
                    cls="property-selector"
                ),
                id="area-selector",
                cls="area-selector hidden"
            ),
            # Items Modal
            items_modal(),
            # Item Select Modal
            item_select_modal(),
            # Inquiry Modal
            inquiry_modal(),
            # Image Preview Modal
            image_preview_modal(),
            # Floating Action Buttons
            Div(
                Button("Inquire", cls="staging-inquiry-btn", onclick="openInquiryModal()"),
                Button("Continue Booking", cls="staging-continue-btn", onclick="goToReserve()"),
                cls="staging-action-buttons",
                id="staging-action-buttons"
            ),
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
                // Don't play sounds during page load/restore
                if (isRestoring) return;
                hapticFeedback();
                playClickSound();
            }

            function playShutterSound() {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const t = audioContext.currentTime;

                // Whoosh (filtered noise sweep)
                const bufferSize = audioContext.sampleRate * 0.1;
                const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
                const data = buffer.getChannelData(0);

                for (let i = 0; i < bufferSize; i++) {
                    const envelope = Math.sin(Math.PI * i / bufferSize);
                    data[i] = (Math.random() * 2 - 1) * envelope;
                }

                const noise = audioContext.createBufferSource();
                noise.buffer = buffer;

                const filter = audioContext.createBiquadFilter();
                filter.type = 'bandpass';
                filter.frequency.setValueAtTime(500, t);
                filter.frequency.exponentialRampToValueAtTime(3000, t + 0.05);
                filter.frequency.exponentialRampToValueAtTime(800, t + 0.1);
                filter.Q.value = 2;

                const gainNode = audioContext.createGain();
                gainNode.gain.setValueAtTime(0.2, t);

                noise.connect(filter);
                filter.connect(gainNode);
                gainNode.connect(audioContext.destination);
                noise.start();

                // Click at end
                const osc = audioContext.createOscillator();
                const clickGain = audioContext.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(1000, t + 0.06);
                osc.frequency.exponentialRampToValueAtTime(300, t + 0.08);
                clickGain.gain.setValueAtTime(0.3, t + 0.06);
                clickGain.gain.exponentialRampToValueAtTime(0.001, t + 0.09);
                osc.connect(clickGain);
                clickGain.connect(audioContext.destination);
                osc.start(t + 0.06);
                osc.stop(t + 0.09);

                // Close AudioContext after sound finishes to prevent browser limit
                setTimeout(() => audioContext.close(), 200);
            }

            function playDeleteSound() {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const t = audioContext.currentTime;

                // Swoosh noise
                const bufferSize = audioContext.sampleRate * 0.15;
                const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
                const data = buffer.getChannelData(0);

                for (let i = 0; i < bufferSize; i++) {
                    const envelope = Math.sin(Math.PI * i / bufferSize);
                    data[i] = (Math.random() * 2 - 1) * envelope;
                }

                const noise = audioContext.createBufferSource();
                noise.buffer = buffer;

                const filter = audioContext.createBiquadFilter();
                filter.type = 'bandpass';
                filter.frequency.setValueAtTime(2000, t);
                filter.frequency.exponentialRampToValueAtTime(500, t + 0.15);
                filter.Q.value = 1;

                const gain = audioContext.createGain();
                gain.gain.setValueAtTime(0.3, t);
                gain.gain.exponentialRampToValueAtTime(0.01, t + 0.15);

                noise.connect(filter);
                filter.connect(gain);
                gain.connect(audioContext.destination);
                noise.start();

                // Close AudioContext after sound finishes to prevent browser limit
                setTimeout(() => audioContext.close(), 250);
            }

            // Pricing constants
            const BASE_STAGING_FEE = 1450.00;
            const HUGE_AREA = 700.00;
            const BIG_AREA = 500.00;
            const SMALL_AREA = 200.00;

            // Session Storage Key
            const STAGING_SESSION_KEY = 'astra_staging_data';

            // Save staging data to session storage
            // Track current staging ID for updates
            let currentStagingId = null;
            // Flag to prevent auto-save during initial restore
            let isRestoring = true;

            function saveStagingSession() {
                // Don't save to server during initial page restore
                if (isRestoring) {
                    return;
                }
                const { propertyType, propertySize } = getSelections();

                // Get selected areas
                const selectedAreas = [];
                document.querySelectorAll('.area-btn.selected').forEach(btn => {
                    selectedAreas.push(btn.getAttribute('data-area'));
                });

                // Get total fee from banner subtitle
                const bannerSubtitle = document.getElementById('banner-subtitle');
                let totalFee = '$0';
                if (bannerSubtitle && bannerSubtitle.textContent.includes('$')) {
                    totalFee = bannerSubtitle.textContent;
                }

                const sessionData = {
                    propertyType: propertyType || null,
                    propertySize: propertySize || null,
                    selectedAreas: selectedAreas,
                    areaItemsData: typeof areaItemsData !== 'undefined' ? areaItemsData : {},
                    areaPhotos: typeof areaPhotos !== 'undefined' ? areaPhotos : {},
                    areaSelectedItems: typeof areaSelectedItems !== 'undefined' ? areaSelectedItems : {},
                    totalFee: totalFee,
                    timestamp: Date.now()
                };

                try {
                    sessionStorage.setItem(STAGING_SESSION_KEY, JSON.stringify(sessionData));
                } catch (e) {
                    console.warn('Could not save to sessionStorage:', e);
                }

                // Auto-save to server if logged in and quote is ready
                if (propertyType && propertySize && selectedAreas.length > 0) {
                    saveToServer(sessionData);
                }
            }

            // Save staging to server (for logged-in users)
            async function saveToServer(sessionData) {
                try {
                    // Check if user is logged in
                    const authResponse = await fetch('/api/auth/check');
                    const authResult = await authResponse.json();
                    if (!authResult.authenticated) return;

                    const serverData = {
                        status: 'quote',
                        property_type: sessionData.propertyType || '',
                        property_size: sessionData.propertySize || '',
                        selected_areas: JSON.stringify(sessionData.selectedAreas || []),
                        selected_items: JSON.stringify(sessionData.areaItemsData || {}),
                        area_photos: JSON.stringify(sessionData.areaPhotos || {}),
                        area_selected_items: JSON.stringify(sessionData.areaSelectedItems || {}),
                        total_fee: sessionData.totalFee || ''
                    };

                    // Include staging ID if updating existing
                    if (currentStagingId) {
                        serverData.id = currentStagingId;
                    }

                    const response = await fetch('/api/stagings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(serverData)
                    });

                    const result = await response.json();
                    if (result.success && result.staging_id) {
                        currentStagingId = result.staging_id;
                        console.log('Staging saved to server, id:', currentStagingId);
                    }
                } catch (e) {
                    console.warn('Could not save to server:', e);
                }
            }

            // Load existing staging from server on page load
            async function loadExistingStagingFromServer() {
                try {
                    const authResponse = await fetch('/api/auth/check');
                    const authResult = await authResponse.json();
                    if (!authResult.authenticated) return;

                    const response = await fetch('/api/stagings?status=quote');
                    const result = await response.json();
                    if (result.success && result.stagings && result.stagings.length > 0) {
                        // Get the most recent quote
                        const staging = result.stagings[0];
                        currentStagingId = staging.id;

                        // Parse server data
                        const serverPhotos = staging.area_photos ? JSON.parse(staging.area_photos) : {};

                        // Always replace sessionStorage with fresh server data to ensure sync across devices
                        const serverSelectedItems = staging.area_selected_items ? JSON.parse(staging.area_selected_items) : {};
                        const serverSessionData = {
                            propertyType: staging.property_type,
                            propertySize: staging.property_size,
                            selectedAreas: staging.selected_areas ? JSON.parse(staging.selected_areas) : [],
                            areaItemsData: staging.selected_items ? JSON.parse(staging.selected_items) : {},
                            areaPhotos: serverPhotos,
                            areaSelectedItems: serverSelectedItems,
                            totalFee: staging.total_fee,
                            timestamp: Date.now()
                        };
                        sessionStorage.setItem(STAGING_SESSION_KEY, JSON.stringify(serverSessionData));
                    }
                } catch (e) {
                    console.warn('Could not load from server:', e);
                }
            }

            // Load staging data from session storage
            function loadStagingSession() {
                try {
                    const saved = sessionStorage.getItem(STAGING_SESSION_KEY);
                    if (!saved) return null;
                    return JSON.parse(saved);
                } catch (e) {
                    console.warn('Could not load from sessionStorage:', e);
                    return null;
                }
            }

            // Restore selections from session data
            function restoreStagingSession() {
                const data = loadStagingSession();
                if (!data) {
                    isRestoring = false;
                    return;
                }

                // Restore property type
                if (data.propertyType) {
                    const propertyBtn = document.querySelector(`.property-btn[data-type="${data.propertyType}"]:not(.size-btn):not(.area-btn)`);
                    if (propertyBtn) {
                        selectPropertyType(propertyBtn, true); // true = skip save
                    }
                } else {
                    // No property type, mark restore complete
                    isRestoring = false;
                    return;
                }

                // Restore property size (after a slight delay to allow size selector to show)
                if (data.propertySize) {
                    setTimeout(() => {
                        const sizeBtn = document.querySelector(`.size-btn[data-size="${data.propertySize}"]`);
                        if (sizeBtn) {
                            selectSize(sizeBtn, true); // true = skip save
                        }

                        // Restore areas (after size is selected)
                        if (data.selectedAreas && data.selectedAreas.length > 0) {
                            setTimeout(() => {
                                data.selectedAreas.forEach(area => {
                                    const areaBtn = document.querySelector(`.area-btn[data-area="${area}"]`);
                                    if (areaBtn && !areaBtn.classList.contains('selected')) {
                                        toggleArea(areaBtn, true); // true = skip save
                                    }
                                });

                                // Restore item selections
                                if (data.areaItemsData && typeof areaItemsData !== 'undefined') {
                                    Object.assign(areaItemsData, data.areaItemsData);
                                    calculateTotalFee();
                                }

                                // Restore photos
                                if (data.areaPhotos && typeof areaPhotos !== 'undefined') {
                                    Object.assign(areaPhotos, data.areaPhotos);
                                    // Update carousels for each area with photos
                                    Object.keys(data.areaPhotos).forEach(area => {
                                        if (data.areaPhotos[area] && data.areaPhotos[area].length > 0) {
                                            updateAreaCarousel(area);
                                        }
                                    });
                                }

                                // Restore selected items (images) per area
                                if (data.areaSelectedItems && typeof areaSelectedItems !== 'undefined') {
                                    Object.assign(areaSelectedItems, data.areaSelectedItems);
                                }

                                // Mark restore as complete - allow saving now
                                isRestoring = false;
                            }, 100);
                        } else {
                            // No areas to restore, mark complete
                            isRestoring = false;
                        }
                    }, 100);
                } else {
                    // No size to restore, mark complete
                    isRestoring = false;
                }
            }

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

                // Store original bulk price as data attribute for modal display
                btn.setAttribute('data-bulk-price', bulkPrice);

                // Use lesser of bulk price or item total
                let displayPrice = bulkPrice;
                if (itemTotal !== null && itemTotal < bulkPrice) {
                    displayPrice = itemTotal;
                }

                const priceSpan = btn.querySelector('.area-price');
                if (priceSpan) {
                    priceSpan.textContent = displayPrice > 0 ? '+$' + displayPrice : '$0';
                }
            }

            // Calculate total staging fee
            function calculateTotalFee() {
                const { propertyType, propertySize } = getSelections();
                if (!propertyType || !propertySize) {
                    updateBannerFee(null);
                    updateActionButtons(false);
                    return;
                }

                // Check if at least 1 area is selected
                const selectedAreas = document.querySelectorAll('.area-btn.selected');
                if (selectedAreas.length === 0) {
                    // No areas selected - show "select staging areas"
                    updateBanner('size-selected');
                    updateActionButtons(false);
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
                updateActionButtons(true);
            }

            // Show/hide action buttons
            function updateActionButtons(show) {
                const actionButtons = document.getElementById('staging-action-buttons');
                if (show) {
                    actionButtons.classList.add('visible');
                } else {
                    actionButtons.classList.remove('visible');
                }
            }

            // Navigate to reserve page (data is passed via session storage)
            function goToReserve() {
                // Save current selections to session storage before navigating
                saveStagingSession();
                // Redirect to reserve page without URL parameters
                window.location.href = '/reserve/';
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

            function selectPropertyType(btn, skipSave = false) {
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

                // Save to session storage
                if (!skipSave) saveStagingSession();
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

            function selectSize(btn, skipSave = false) {
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

                // Save to session storage
                if (!skipSave) saveStagingSession();
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

            function toggleArea(btn, skipSave = false) {
                buttonFeedback();
                btn.classList.toggle('selected');
                calculateTotalFee();

                // Save to session storage
                if (!skipSave) saveStagingSession();
            }

            // Items Modal Functions
            let currentArea = null;
            const areaItemsData = {}; // Store selected items per area
            const areaSelectedItems = {}; // Store selected item details (image, name, model_3d) per area

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

            let itemsCameraStream = null;
            let currentItemsPhotoIndex = 0;
            let itemsDragDropInitialized = false;

            function openItemsModal(event, element) {
                event.stopPropagation();

                const areaBtn = element.closest('.area-btn');
                currentArea = areaBtn.getAttribute('data-area');
                const areaName = areaNameMap[currentArea] || currentArea;

                // Update modal title
                document.getElementById('items-modal-title').textContent = 'Select ' + areaName + ' Items';

                // Update bulk price from area button's data attribute (original bulk price)
                const bulkPrice = areaBtn.getAttribute('data-bulk-price') || '0';
                document.getElementById('items-modal-bulk-price').textContent = areaName + ' Bulk Price: $' + bulkPrice;

                // Load saved items for this area
                loadAreaItems(currentArea);

                // Initialize photos array for this area if not exists
                if (!areaPhotos[currentArea]) {
                    areaPhotos[currentArea] = [];
                }

                // Reset carousel to first photo
                currentItemsPhotoIndex = 0;

                // Render photos in items modal
                renderItemsPhotosGrid();

                // Update items thumbnail
                updateItemsThumbnail();

                // Initialize drag and drop for desktop (camera on mobile only starts when Take Photos is clicked)
                const isMobile = window.innerWidth <= 767;
                if (!isMobile) {
                    initItemsDragAndDrop();
                }

                // Show modal
                document.getElementById('items-modal').classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }

            function closeItemsModal() {
                document.getElementById('items-modal').classList.add('hidden');
                document.body.style.overflow = '';

                // Stop items camera if running and hide camera section
                stopItemsCamera();
                const cameraSection = document.getElementById('items-camera-section');
                const carouselWrapper = document.getElementById('items-photos-preview-grid');
                if (cameraSection) {
                    cameraSection.style.display = 'none';
                }
                if (carouselWrapper) {
                    carouselWrapper.style.display = 'block';
                }

                currentArea = null;
            }

            // Item Select Modal Functions
            let currentItemType = null;

            async function openItemSelectModal(itemName) {
                currentItemType = itemName;
                const modal = document.getElementById('item-select-modal');
                const grid = document.getElementById('item-select-grid');
                const title = document.getElementById('item-select-modal-title');

                if (!modal || !grid) return;

                // Update title
                if (title) {
                    title.textContent = 'Select ' + itemName;
                }

                // Clear grid and show loading
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">Loading...</div>';

                // Show modal
                modal.classList.remove('hidden');
                document.body.style.overflow = 'hidden';

                try {
                    // Fetch items from API
                    const response = await fetch('/api/inventory-items?item_type=' + encodeURIComponent(itemName));
                    const data = await response.json();

                    if (data.success && data.items && data.items.length > 0) {
                        grid.innerHTML = '';

                        // Flatten all images from all items
                        const allImages = [];
                        data.items.forEach(item => {
                            if (item.images && item.images.length > 0) {
                                item.images.forEach(imageObj => {
                                    // Handle both old format (string) and new format (object)
                                    const url = typeof imageObj === 'string' ? imageObj : imageObj.url;
                                    const model3d = typeof imageObj === 'object' ? imageObj.model_3d : null;
                                    const width = typeof imageObj === 'object' ? (imageObj.width || 0) : 0;
                                    const depth = typeof imageObj === 'object' ? (imageObj.depth || 0) : 0;
                                    const height = typeof imageObj === 'object' ? (imageObj.height || 0) : 0;
                                    const front_rotation = typeof imageObj === 'object' ? imageObj.front_rotation : null;
                                    allImages.push({
                                        name: item.name,
                                        url: url,
                                        model_3d: model3d,
                                        width: width,
                                        depth: depth,
                                        height: height,
                                        front_rotation: front_rotation,
                                        count: item.count || 1
                                    });
                                });
                            }
                        });

                        if (allImages.length === 0) {
                            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No images found for ' + itemName + '</div>';
                            return;
                        }

                        // Create cards for each image
                        allImages.forEach((imageData, index) => {
                            const card = document.createElement('div');
                            card.className = 'item-select-card';
                            card.onclick = () => selectItemImage(imageData.url, imageData.name, imageData.model_3d, imageData.width, imageData.depth, imageData.height, imageData.front_rotation);

                            const img = document.createElement('img');
                            img.src = imageData.url;
                            img.alt = imageData.name;
                            img.loading = 'lazy';

                            // Add 3D icon to top-left if item has a 3D model
                            if (imageData.model_3d) {
                                const icon3d = document.createElement('div');
                                icon3d.className = 'item-3d-icon item-3d-icon-left';
                                icon3d.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>';
                                card.appendChild(icon3d);
                            }

                            // Add count label to top-right
                            const countLabel = document.createElement('div');
                            countLabel.className = 'item-count-label';
                            countLabel.textContent = imageData.count;
                            card.appendChild(countLabel);

                            const nameLabel = document.createElement('div');
                            nameLabel.className = 'item-select-name';
                            nameLabel.textContent = imageData.name;

                            card.appendChild(img);
                            card.appendChild(nameLabel);
                            grid.appendChild(card);
                        });
                    } else {
                        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No items found for ' + itemName + '</div>';
                    }
                } catch (error) {
                    console.error('Error fetching items:', error);
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">Error loading items</div>';
                }
            }

            function closeItemSelectModal() {
                const modal = document.getElementById('item-select-modal');
                if (modal) {
                    modal.classList.add('hidden');
                }
                // Don't restore body overflow since items modal is still open
                currentItemType = null;
            }

            function selectItemImage(imageUrl, itemName, model3d, width = 0, depth = 0, height = 0, frontRotation = null) {
                if (!currentItemType || !currentArea) return;

                // Find the item button for the current item type
                const itemBtn = document.querySelector(`.item-btn[data-name="${currentItemType}"]`);
                if (itemBtn) {
                    // Replace the icon with the selected image - full width of item box
                    const emojiDiv = itemBtn.querySelector('.item-emoji');
                    if (emojiDiv) {
                        let imgHtml = `<img src="${imageUrl}" alt="${itemName}">`;
                        // Add 3D icon if item has a 3D model
                        if (model3d) {
                            imgHtml += `<div class="item-3d-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg></div>`;
                        }
                        emojiDiv.innerHTML = imgHtml;
                    }

                    // Add class to item button to indicate it has a selected image
                    itemBtn.classList.add('has-selected-image');

                    // Replace the item name with the selected item name
                    const nameSpan = itemBtn.querySelector('.item-name');
                    if (nameSpan) {
                        nameSpan.textContent = itemName;
                    }

                    // Store the selected image URL, 3D model, and dimensions on the button for later use
                    itemBtn.dataset.selectedImage = imageUrl;
                    itemBtn.dataset.selectedName = itemName;
                    if (model3d) {
                        itemBtn.dataset.model3d = model3d;
                        // Make draggable if has 3D model
                        itemBtn.draggable = true;
                    } else {
                        itemBtn.draggable = false;
                        delete itemBtn.dataset.model3d;
                    }
                    itemBtn.dataset.width = width;
                    itemBtn.dataset.depth = depth;
                    itemBtn.dataset.height = height;
                    itemBtn.dataset.frontRotation = frontRotation ?? -Math.PI/2; // Default to -90° to face camera

                    // Save to areaSelectedItems for persistence
                    if (!areaSelectedItems[currentArea]) {
                        areaSelectedItems[currentArea] = {};
                    }
                    areaSelectedItems[currentArea][currentItemType] = {
                        imageUrl: imageUrl,
                        itemName: itemName,
                        model3d: model3d || null,
                        width: width,
                        depth: depth,
                        height: height,
                        frontRotation: frontRotation ?? -Math.PI/2
                    };

                    // Save to session storage
                    saveStagingSession();
                }

                closeItemSelectModal();
            }

            // Drag event handlers for items with 3D models
            let touchDragData = null;
            let touchDragClone = null;
            let touchDragSource = null;
            let touchStartX = 0;
            let touchStartY = 0;
            let isDraggingItem = false;
            const DRAG_THRESHOLD = 10; // pixels - movement needed to start drag

            function setupItemDragHandlers() {
                // Desktop: Use event delegation on the document for drag events
                document.addEventListener('dragstart', function(e) {
                    const itemBtn = e.target.closest('.item-btn');
                    if (itemBtn && itemBtn.dataset.model3d && itemBtn.classList.contains('has-selected-image')) {
                        e.dataTransfer.effectAllowed = 'copy';
                        e.dataTransfer.setData('application/x-item-3d', JSON.stringify({
                            imageUrl: itemBtn.dataset.selectedImage,
                            itemName: itemBtn.dataset.selectedName,
                            model3d: itemBtn.dataset.model3d,
                            width: parseFloat(itemBtn.dataset.width) || 0,
                            depth: parseFloat(itemBtn.dataset.depth) || 0,
                            height: parseFloat(itemBtn.dataset.height) || 0,
                            frontRotation: parseFloat(itemBtn.dataset.frontRotation) || -Math.PI/2
                        }));
                        itemBtn.classList.add('dragging');
                    }
                });

                document.addEventListener('dragend', function(e) {
                    const itemBtn = e.target.closest('.item-btn');
                    if (itemBtn) {
                        itemBtn.classList.remove('dragging');
                    }
                });

                // Mobile: Touch-based drag for items with 3D models
                document.addEventListener('touchstart', function(e) {
                    const itemBtn = e.target.closest('.item-btn');
                    if (itemBtn && itemBtn.dataset.model3d && itemBtn.classList.contains('has-selected-image')) {
                        const touch = e.touches[0];

                        // Store start position but don't start drag yet
                        touchStartX = touch.clientX;
                        touchStartY = touch.clientY;
                        isDraggingItem = false;

                        touchDragSource = itemBtn;
                        touchDragData = {
                            imageUrl: itemBtn.dataset.selectedImage,
                            itemName: itemBtn.dataset.selectedName,
                            model3d: itemBtn.dataset.model3d,
                            width: parseFloat(itemBtn.dataset.width) || 0,
                            depth: parseFloat(itemBtn.dataset.depth) || 0,
                            height: parseFloat(itemBtn.dataset.height) || 0,
                            frontRotation: parseFloat(itemBtn.dataset.frontRotation) || -Math.PI/2
                        };
                    }
                }, { passive: true });

                document.addEventListener('touchmove', function(e) {
                    if (touchDragData && !isDraggingItem) {
                        // Prevent scrolling immediately when touching a draggable item
                        e.preventDefault();

                        const touch = e.touches[0];
                        const deltaX = Math.abs(touch.clientX - touchStartX);
                        const deltaY = Math.abs(touch.clientY - touchStartY);

                        // Check if movement exceeds threshold to start visual drag
                        if (deltaX > DRAG_THRESHOLD || deltaY > DRAG_THRESHOLD) {
                            isDraggingItem = true;

                            // Create visual drag clone
                            const itemBtn = touchDragSource;
                            const img = itemBtn?.querySelector('.item-emoji img');
                            if (img) {
                                touchDragClone = document.createElement('div');
                                touchDragClone.className = 'touch-drag-clone';
                                touchDragClone.innerHTML = `<img src="${img.src}" alt="Dragging">`;
                                touchDragClone.style.cssText = `
                                    position: fixed;
                                    left: ${touch.clientX - 40}px;
                                    top: ${touch.clientY - 40}px;
                                    width: 80px;
                                    height: 80px;
                                    z-index: 10000;
                                    pointer-events: none;
                                    opacity: 0.8;
                                    border-radius: 8px;
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                                    background: white;
                                `;
                                touchDragClone.querySelector('img').style.cssText = `
                                    width: 100%;
                                    height: 100%;
                                    object-fit: contain;
                                    border-radius: 8px;
                                `;
                                document.body.appendChild(touchDragClone);
                            }

                            itemBtn?.classList.add('dragging');

                            // Show drop zone hint
                            const dropZone = document.querySelector('.items-photos-section');
                            if (dropZone) dropZone.classList.add('drag-over-3d');
                        }
                    } else if (touchDragClone && isDraggingItem) {
                        // Already dragging, update clone position
                        e.preventDefault();
                        const touch = e.touches[0];
                        touchDragClone.style.left = (touch.clientX - 40) + 'px';
                        touchDragClone.style.top = (touch.clientY - 40) + 'px';
                    }
                }, { passive: false });

                document.addEventListener('touchend', async function(e) {
                    if (touchDragData) {
                        // Check if we actually dragged or just tapped
                        if (isDraggingItem && touchDragClone) {
                            // Was dragging - handle drop
                            const touch = e.changedTouches[0];

                            // Remove drag clone
                            touchDragClone.remove();
                            touchDragClone = null;

                            // Remove dragging class
                            if (touchDragSource) {
                                touchDragSource.classList.remove('dragging');
                            }

                            // Remove drop zone hint
                            const dropZone = document.querySelector('.items-photos-section');
                            if (dropZone) dropZone.classList.remove('drag-over-3d');

                            // Check if dropped on photo carousel
                            const dropTarget = document.elementFromPoint(touch.clientX, touch.clientY);
                            const carouselContainer = dropTarget?.closest('.photos-carousel-container') ||
                                                       dropTarget?.closest('.items-photos-section');

                            if (carouselContainer) {
                                // Check if we have a photo to use as background
                                const photos = areaPhotos[currentArea] || [];
                                if (photos.length === 0) {
                                    alert('Please add a photo first before dropping 3D models.');
                                } else {
                                    // Get drop position relative to carousel container
                                    const container = document.getElementById('items-photos-carousel-container');
                                    const rect = container ? container.getBoundingClientRect() : null;
                                    let dropX = 0, dropY = 0;
                                    if (rect) {
                                        // Convert to normalized coordinates (-1 to 1)
                                        dropX = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
                                        dropY = -(((touch.clientY - rect.top) / rect.height) * 2 - 1);
                                    }

                                    // Initialize or add to 3D scene
                                    if (current3DPhotoIndex !== currentItemsPhotoIndex) {
                                        await initPhoto3DScene(currentItemsPhotoIndex, touchDragData, dropX, dropY);
                                    } else {
                                        await loadGLTFModelOnPhoto(touchDragData, dropX, dropY);
                                    }
                                }
                            }
                        }
                        // If not dragging (just tapped), allow the click event to fire naturally

                        // Reset state
                        touchDragData = null;
                        touchDragSource = null;
                        isDraggingItem = false;
                    }
                });

                // Prevent context menu on item buttons with 3D models
                document.addEventListener('contextmenu', function(e) {
                    const itemBtn = e.target.closest('.item-btn');
                    if (itemBtn && itemBtn.dataset.model3d) {
                        e.preventDefault();
                    }
                });
            }

            // Initialize drag handlers when DOM is ready
            document.addEventListener('DOMContentLoaded', setupItemDragHandlers);

            // ===== 3D VIEWER INTEGRATION =====
            let threeJsLoaded = false;
            let threeScene = null;
            let threeCamera = null;
            let threeRenderer = null;
            let currentLoadedModel = null;
            let allLoadedModels = [];
            let modelBrightness = 3.0; // Default brightness (range: 0 to 10, 3.0 ≈ old intensity of 1.0)
            const MAX_MODEL_BRIGHTNESS = 10.0; // Maximum brightness for models
            let modelTilt = 0.1745; // ~10 degrees default tilt
            const DEFAULT_TILT = 0.1745;
            const SIDE_ROTATION_ANGLE = Math.PI / 2.5; // ~72 degrees for more noticeable angled facing

            // Get position zone: 'left', 'center', or 'right'
            function getPositionZone(worldX) {
                if (!threeCamera) return 'center';

                const halfWidth = (threeCamera.right - threeCamera.left) / 2;
                const leftBound = -halfWidth;
                const totalWidth = halfWidth * 2;
                const positionPercent = (worldX - leftBound) / totalWidth;

                if (positionPercent < 0.25) return 'left';
                if (positionPercent > 0.75) return 'right';
                return 'center';
            }

            // Get rotation for a specific zone
            function getRotationForZone(zone, frontRotation) {
                if (zone === 'left') {
                    return frontRotation + SIDE_ROTATION_ANGLE; // Face right (toward center)
                } else if (zone === 'right') {
                    return frontRotation - SIDE_ROTATION_ANGLE; // Face left (toward center)
                }
                return frontRotation; // Center - face front
            }

            // Calculate rotation based on horizontal position (for initial drop)
            function getPositionBasedRotation(worldX, frontRotation) {
                const zone = getPositionZone(worldX);
                return getRotationForZone(zone, frontRotation);
            }

            // Animate rotation smoothly
            function animateRotation(model, targetRotation, duration = 300) {
                if (!model) return;

                const startRotation = model.rotation.y;
                const startTime = performance.now();

                function animate() {
                    const elapsed = performance.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1);

                    // Ease-out cubic for smooth deceleration
                    const easeProgress = 1 - Math.pow(1 - progress, 3);

                    model.rotation.y = startRotation + (targetRotation - startRotation) * easeProgress;

                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        model.rotation.y = targetRotation;
                        model.userData.yRotation = targetRotation;
                    }
                }

                requestAnimationFrame(animate);
            }

            // Update rotation only when crossing zone boundaries
            function updateRotationIfZoneChanged(model, newX) {
                if (!model || !model.userData) return;

                const frontRotation = model.userData.frontRotation ?? -Math.PI/2;
                const currentZone = model.userData.positionZone || 'center';
                const newZone = getPositionZone(newX);

                // Only update rotation when crossing zone boundaries
                if (newZone !== currentZone) {
                    const newRotation = getRotationForZone(newZone, frontRotation);
                    // Animate the rotation smoothly
                    animateRotation(model, newRotation, 250);
                    model.userData.yRotation = newRotation;
                    model.userData.positionZone = newZone;
                }
            }

            let isDraggingRotate = false;
            let isDraggingScale = false;
            let isDraggingBrightness = false;
            let isDraggingTilt = false;
            let lastMouseX = 0;
            let lastMouseY = 0;
            let current3DPhotoIndex = null;
            let current3DViewerContainer = null;
            let animationFrameId = null;

            // Background brightness drag state
            let isDraggingBgBrightness = false;
            let bgBrightnessLastX = 0;
            let bgBrightnessValue = 1.0; // 1.0 = normal, 0 = dark, 2 = bright

            function loadScript(src) {
                return new Promise((resolve, reject) => {
                    // Check if already loaded
                    if (document.querySelector(`script[src="${src}"]`)) {
                        resolve();
                        return;
                    }
                    const script = document.createElement('script');
                    script.src = src;
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            }

            async function loadThreeJS() {
                if (threeJsLoaded) return;
                await loadScript('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js');
                await loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js');
                threeJsLoaded = true;
            }

            async function initPhoto3DScene(photoIndex, itemData, dropX = 0, dropY = 0) {
                // Load Three.js if not loaded
                await loadThreeJS();

                const container = document.getElementById('items-photo-slide');
                if (!container) return;

                // Store current 3D photo
                current3DPhotoIndex = photoIndex;
                current3DViewerContainer = container;

                // Get the photo as background
                const photos = areaPhotos[currentArea] || [];
                const photoSrc = photos[photoIndex];
                if (!photoSrc) return;

                // Get container dimensions
                const containerRect = container.getBoundingClientRect();
                const width = containerRect.width;
                const height = containerRect.height;

                // Clear existing 3D scene if any
                if (threeRenderer) {
                    container.querySelector('canvas')?.remove();
                }

                // Hide the img element
                const imgEl = container.querySelector('img');
                if (imgEl) imgEl.style.display = 'none';

                // Create scene
                threeScene = new THREE.Scene();

                // Load photo as background texture
                const textureLoader = new THREE.TextureLoader();
                textureLoader.load(photoSrc, (bgTexture) => {
                    threeScene.background = bgTexture;
                }, undefined, (error) => {
                    console.error('Error loading background:', error);
                    threeScene.background = new THREE.Color(0x333333);
                });

                // Camera - orthographic
                const aspect = width / height;
                const frustumSize = 5;
                threeCamera = new THREE.OrthographicCamera(
                    frustumSize * aspect / -2,
                    frustumSize * aspect / 2,
                    frustumSize / 2,
                    frustumSize / -2,
                    1, 100
                );
                threeCamera.position.set(0, 0, 50);
                threeCamera.lookAt(0, 0, 0);

                // Renderer
                threeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                threeRenderer.setSize(width, height);
                threeRenderer.setPixelRatio(window.devicePixelRatio);
                threeRenderer.domElement.style.position = 'absolute';
                threeRenderer.domElement.style.top = '0';
                threeRenderer.domElement.style.left = '0';
                threeRenderer.domElement.style.width = '100%';
                threeRenderer.domElement.style.height = '100%';
                // Apply saved brightness to canvas
                if (bgBrightnessValue !== 1.0) {
                    threeRenderer.domElement.style.filter = `brightness(${bgBrightnessValue})`;
                }
                container.appendChild(threeRenderer.domElement);

                // Lights - brighter to illuminate 3D models properly
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                threeScene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
                directionalLight.position.set(5, 10, 7.5);
                threeScene.add(directionalLight);
                const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.6);
                directionalLight2.position.set(-5, 5, -5);
                threeScene.add(directionalLight2);

                // Mark container as 3D mode
                container.classList.add('photo-3d-mode');

                // Load the dropped model at drop position
                await loadGLTFModelOnPhoto(itemData, dropX, dropY);

                // Add control overlay
                addModelControlOverlay(container);

                // Start animation loop
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
                function animate() {
                    animationFrameId = requestAnimationFrame(animate);
                    if (threeRenderer && threeScene && threeCamera) {
                        // Continuously update depth for smooth transitions
                        updateAllModelsRenderOrder();
                        threeRenderer.render(threeScene, threeCamera);
                        updateControlOverlayPosition();
                    }
                }
                animate();

                // Add mouse handlers for model position dragging
                setupModelDragHandlers(threeRenderer.domElement);
            }

            let isDraggingModel = false;
            let modelDragOffsetX = 0; // Offset from click point to model center in world coords
            let modelDragOffsetY = 0;
            let didDragModel = false; // Track if we actually moved

            // Convert screen coordinates to world coordinates for orthographic camera
            function screenToWorld(clientX, clientY, canvas) {
                const rect = canvas.getBoundingClientRect();
                const ndcX = ((clientX - rect.left) / rect.width) * 2 - 1;
                const ndcY = -((clientY - rect.top) / rect.height) * 2 + 1;

                // For orthographic camera, convert NDC to world coordinates
                const worldX = (ndcX * (threeCamera.right - threeCamera.left) / 2) + threeCamera.position.x;
                const worldY = (ndcY * (threeCamera.top - threeCamera.bottom) / 2) + threeCamera.position.y;

                return { x: worldX, y: worldY };
            }

            function showModelControls(show) {
                const overlay = current3DViewerContainer?.querySelector('.model-control-overlay');
                if (overlay) {
                    overlay.style.display = show ? 'flex' : 'none';
                    if (show && currentLoadedModel) {
                        cachedModelHeight = 0; // Reset cache when showing controls for potentially different model
                        updateControlOverlayPosition(true);
                    }
                }
            }

            let cachedModelHeight = 0; // Cache height to avoid recalc on rotate/tilt

            function updateControlOverlayPosition(recalcHeight = false) {
                if (!currentLoadedModel || !threeCamera || !current3DViewerContainer) return;
                const overlay = current3DViewerContainer.querySelector('.model-control-overlay');
                if (!overlay || overlay.style.display === 'none') return;

                // Recalculate height when scaling or first time
                if (recalcHeight || cachedModelHeight === 0) {
                    const box = new THREE.Box3().setFromObject(currentLoadedModel);
                    cachedModelHeight = box.max.y - box.min.y;
                }

                // Position below model: center - half height - padding
                const bottomY = currentLoadedModel.position.y - (cachedModelHeight / 2) - 0.3;
                const bottomPos = new THREE.Vector3(
                    currentLoadedModel.position.x,
                    bottomY,
                    currentLoadedModel.position.z
                );

                // Project to screen coordinates
                bottomPos.project(threeCamera);

                const canvas = current3DViewerContainer.querySelector('canvas');
                if (!canvas) return;

                const rect = canvas.getBoundingClientRect();
                const screenX = ((bottomPos.x + 1) / 2) * rect.width;
                const screenY = ((-bottomPos.y + 1) / 2) * rect.height;

                // Ensure controls don't go off the edges of the container
                // 6 buttons at ~40px each + gaps = ~280px total width
                const overlayWidth = Math.max(overlay.offsetWidth, 280);
                const halfWidth = overlayWidth / 2;
                const minLeft = halfWidth + 10; // Add padding from edge
                const maxLeft = rect.width - halfWidth - 10;
                const clampedX = Math.max(minLeft, Math.min(maxLeft, screenX));

                overlay.style.left = clampedX + 'px';
                // Ensure controls don't go off the bottom of the container
                const maxBottom = rect.height - 50; // Leave space for the control buttons
                overlay.style.top = Math.min(maxBottom, screenY + 10) + 'px';
                overlay.style.transform = 'translateX(-50%)';
            }

            function getClickedModel(clientX, clientY, canvas) {
                if (!threeCamera || allLoadedModels.length === 0) return null;

                const rect = canvas.getBoundingClientRect();
                const mouse = new THREE.Vector2();
                mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;

                const raycaster = new THREE.Raycaster();
                raycaster.setFromCamera(mouse, threeCamera);

                // Check all models
                for (const model of allLoadedModels) {
                    const intersects = raycaster.intersectObject(model, true);
                    if (intersects.length > 0) {
                        return model;
                    }
                }
                return null;
            }

            function setupModelDragHandlers(canvas) {
                canvas.addEventListener('mousedown', (e) => {
                    didDragModel = false;
                    const clickedModel = getClickedModel(e.clientX, e.clientY, canvas);

                    if (clickedModel) {
                        // Select clicked model
                        currentLoadedModel = clickedModel;
                        isDraggingModel = true;

                        // Calculate offset from click point to model center
                        const worldPos = screenToWorld(e.clientX, e.clientY, canvas);
                        modelDragOffsetX = currentLoadedModel.position.x - worldPos.x;
                        modelDragOffsetY = currentLoadedModel.position.y - worldPos.y;

                        canvas.style.cursor = 'grabbing';
                        showModelControls(true);
                    } else {
                        // Clicked on background - deselect and hide controls
                        currentLoadedModel = null;
                        showModelControls(false);
                    }
                });

                canvas.addEventListener('mousemove', (e) => {
                    if (!isDraggingModel || !currentLoadedModel) return;

                    // Convert current mouse position to world coordinates
                    const worldPos = screenToWorld(e.clientX, e.clientY, canvas);

                    // Calculate new position maintaining the original offset
                    const newX = worldPos.x + modelDragOffsetX;
                    const newY = worldPos.y + modelDragOffsetY;

                    if (Math.abs(newX - currentLoadedModel.position.x) > 0.001 ||
                        Math.abs(newY - currentLoadedModel.position.y) > 0.001) {
                        didDragModel = true;
                    }

                    currentLoadedModel.position.x = newX;
                    currentLoadedModel.position.y = newY;

                    // Update rotation only when crossing zone boundaries (keep tilt, size, brightness)
                    updateRotationIfZoneChanged(currentLoadedModel, newX);

                    // Update render order based on Y position (lower Y = in front)
                    updateAllModelsRenderOrder();
                });

                canvas.addEventListener('mouseup', () => {
                    if (isDraggingModel) {
                        isDraggingModel = false;
                        canvas.style.cursor = currentLoadedModel ? 'grab' : 'default';
                        if (didDragModel) {
                            saveModelStates();
                        }
                    }
                });

                canvas.addEventListener('mouseleave', () => {
                    if (isDraggingModel) {
                        isDraggingModel = false;
                        canvas.style.cursor = currentLoadedModel ? 'grab' : 'default';
                        if (didDragModel) {
                            saveModelStates();
                        }
                    }
                });

                // Touch support for mobile
                canvas.addEventListener('touchstart', (e) => {
                    if (e.touches.length !== 1) return;
                    didDragModel = false;

                    const touch = e.touches[0];
                    const clickedModel = getClickedModel(touch.clientX, touch.clientY, canvas);

                    if (clickedModel) {
                        currentLoadedModel = clickedModel;
                        isDraggingModel = true;

                        // Calculate offset from touch point to model center
                        const worldPos = screenToWorld(touch.clientX, touch.clientY, canvas);
                        modelDragOffsetX = currentLoadedModel.position.x - worldPos.x;
                        modelDragOffsetY = currentLoadedModel.position.y - worldPos.y;

                        showModelControls(true);
                    } else {
                        currentLoadedModel = null;
                        showModelControls(false);
                    }
                }, { passive: true });

                canvas.addEventListener('touchmove', (e) => {
                    if (!isDraggingModel || !currentLoadedModel || e.touches.length !== 1) return;

                    // Convert current touch position to world coordinates
                    const worldPos = screenToWorld(e.touches[0].clientX, e.touches[0].clientY, canvas);

                    // Calculate new position maintaining the original offset
                    const newX = worldPos.x + modelDragOffsetX;
                    const newY = worldPos.y + modelDragOffsetY;

                    if (Math.abs(newX - currentLoadedModel.position.x) > 0.001 ||
                        Math.abs(newY - currentLoadedModel.position.y) > 0.001) {
                        didDragModel = true;
                    }

                    currentLoadedModel.position.x = newX;
                    currentLoadedModel.position.y = newY;

                    // Update rotation only when crossing zone boundaries (keep tilt, size, brightness)
                    updateRotationIfZoneChanged(currentLoadedModel, newX);

                    // Update render order based on Y position (lower Y = in front)
                    updateAllModelsRenderOrder();
                }, { passive: true });

                canvas.addEventListener('touchend', () => {
                    if (isDraggingModel) {
                        isDraggingModel = false;
                        if (didDragModel) {
                            saveModelStates();
                        }
                    }
                });

                // Allow drag and drop to work on canvas when in 3D mode
                canvas.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    e.dataTransfer.dropEffect = 'copy';
                    // Show visual feedback on the container
                    const container = canvas.parentElement;
                    if (container) container.classList.add('drag-over-3d');
                });

                canvas.addEventListener('dragleave', (e) => {
                    const container = canvas.parentElement;
                    if (container) container.classList.remove('drag-over-3d');
                });

                canvas.addEventListener('drop', async (e) => {
                    e.preventDefault();
                    e.stopPropagation(); // Prevent parent drop zone from also handling

                    // Remove visual feedback
                    const container = canvas.parentElement;
                    if (container) container.classList.remove('drag-over-3d');

                    const itemDataStr = e.dataTransfer.getData('application/x-item-3d');
                    if (itemDataStr) {
                        const itemData = JSON.parse(itemDataStr);
                        // Calculate drop position
                        const rect = canvas.getBoundingClientRect();
                        const dropX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                        const dropY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
                        // Add model to existing scene
                        await loadGLTFModelOnPhoto(itemData, dropX, dropY);
                    }
                });

                canvas.style.cursor = 'default';
            }

            async function loadGLTFModelOnPhoto(itemData, dropX = 0, dropY = 0) {
                if (!threeScene) return;

                const modelUrl = '/static/models/' + itemData.model3d;

                // Fetch saved defaults for this model (rotation, brightness, tilt)
                let savedDefaults = null;
                try {
                    const response = await fetch(`/api/get-default-rotation/${encodeURIComponent(itemData.model3d)}`);
                    const result = await response.json();
                    if (result.success) {
                        savedDefaults = result;
                        console.log(`Loaded saved defaults for ${itemData.model3d}:`, savedDefaults);
                    }
                } catch (error) {
                    console.log('No saved defaults found for model:', itemData.model3d);
                }

                const loader = new THREE.GLTFLoader();

                loader.load(modelUrl, (gltf) => {
                    const model = gltf.scene;

                    // Make all materials double-sided so back/side faces render solid
                    model.traverse((child) => {
                        if (child.isMesh && child.material) {
                            const materials = Array.isArray(child.material) ? child.material : [child.material];
                            materials.forEach(mat => {
                                mat.side = THREE.DoubleSide;
                            });
                        }
                    });

                    // Center and scale model based on item dimensions
                    const box = new THREE.Box3().setFromObject(model);
                    const size = box.getSize(new THREE.Vector3());
                    const maxModelDim = Math.max(size.x, size.y, size.z);

                    // Use item dimensions for scaling (dimensions are in inches)
                    // Width is typically the largest dimension for furniture
                    const itemWidth = itemData.width || 0;
                    const itemDepth = itemData.depth || 0;
                    const itemHeight = itemData.height || 0;
                    const maxItemDim = Math.max(itemWidth, itemDepth, itemHeight);

                    let targetScale = 1.5 / maxModelDim; // Default scale
                    if (maxItemDim > 0) {
                        // Scale based on item's largest dimension
                        // Reference: 48 inches = 1.2 units in scene (good size for a chair)
                        // So scale factor = (itemDim / 48) * (1.2 / maxModelDim)
                        targetScale = (maxItemDim / 48) * (1.2 / maxModelDim);
                    }

                    model.scale.setScalar(targetScale);

                    // Calculate world position from normalized drop coordinates
                    // frustumSize = 5, aspect = container width/height
                    const container = threeRenderer.domElement.parentElement;
                    const aspect = container.offsetWidth / container.offsetHeight;
                    const frustumSize = 5;
                    const worldX = dropX * (frustumSize * aspect / 2);
                    const worldY = dropY * (frustumSize / 2);
                    model.position.set(worldX, worldY, 0);

                    // Apply front rotation so model faces the user
                    // Use saved rotation if available, otherwise use itemData or default
                    let frontRotation = savedDefaults?.rotation ?? itemData.frontRotation ?? -Math.PI/2;

                    // Get initial zone and rotation based on drop position
                    const initialZone = getPositionZone(worldX);
                    const initialRotation = getRotationForZone(initialZone, frontRotation);
                    model.rotation.y = initialRotation;

                    // Apply tilt - use saved value if available
                    const modelTilt = savedDefaults?.tilt ?? itemData.tilt ?? DEFAULT_TILT;
                    model.rotation.x = modelTilt;

                    // Use saved brightness if available, otherwise default to 3.0
                    const modelBrightness = savedDefaults?.brightness ?? itemData.brightness ?? 3.0;

                    // Store item data
                    model.userData = {
                        itemName: itemData.itemName,
                        model3d: itemData.model3d,
                        imageUrl: itemData.imageUrl,
                        width: itemData.width,
                        depth: itemData.depth,
                        height: itemData.height,
                        frontRotation: frontRotation,
                        yRotation: initialRotation, // Start from position-based rotation
                        positionZone: initialZone, // Track current zone for rotation changes
                        tilt: modelTilt,
                        brightness: modelBrightness,
                        baseScale: targetScale,
                        instanceId: allLoadedModels.length
                    };

                    currentLoadedModel = model;
                    threeScene.add(model);
                    allLoadedModels.push(model);

                    // Set render order based on Z position (higher Z = in front)
                    updateModelDepthFromY(model);

                    // Update brightness
                    updateModelBrightness(model, modelBrightness);

                    // Show controls for the newly dropped model
                    showModelControls(true);

                    console.log('Loaded 3D model:', itemData.model3d);
                }, undefined, (error) => {
                    console.error('Error loading model:', error);
                });
            }

            function updateModelBrightness(model, brightness) {
                if (!model) return;
                model.traverse((child) => {
                    if (child.isMesh && child.material) {
                        const materials = Array.isArray(child.material) ? child.material : [child.material];
                        materials.forEach(mat => {
                            if (mat.color) {
                                // Map brightness (0-10) to intensity (0.2-3.0)
                                // Default brightness of 3.0 gives intensity of ~1.0 (same as old default)
                                const intensity = 0.2 + (brightness / MAX_MODEL_BRIGHTNESS) * 2.8;
                                mat.color.setScalar(intensity);
                            }
                        });
                    }
                });
            }

            function showBrightnessSlider(show) {
                const slider = current3DViewerContainer?.querySelector('#brightness-slider');
                const buttonGroup = current3DViewerContainer?.querySelector('.model-control-group');
                const btnBrightness = current3DViewerContainer?.querySelector('#btn-brightness');

                if (slider && buttonGroup && btnBrightness) {
                    if (show && currentLoadedModel) {
                        const brightness = currentLoadedModel.userData.brightness ?? 3.0;
                        const thumbPercent = brightness / MAX_MODEL_BRIGHTNESS; // 0 to 1

                        // Get button center position BEFORE hiding the button group
                        const container = current3DViewerContainer;
                        const containerRect = container.getBoundingClientRect();
                        const btnRect = btnBrightness.getBoundingClientRect();
                        const btnCenterX = btnRect.left + btnRect.width / 2 - containerRect.left;

                        // Get button top position for vertical alignment
                        const btnTop = btnRect.top - containerRect.top;

                        // Slider track width (200px from CSS, minus padding 15px each side = 170px track)
                        const sliderWidth = 200;
                        const paddingLeft = 15;
                        const trackWidth = sliderWidth - paddingLeft * 2;

                        // Calculate where thumb would be within the track
                        const thumbOffsetInTrack = thumbPercent * trackWidth;

                        // Position slider so thumb aligns with button center
                        // Position relative to container (not overlay)
                        const sliderLeft = btnCenterX - paddingLeft - thumbOffsetInTrack;

                        // Move slider out of overlay and into container for proper positioning
                        slider.style.position = 'absolute';
                        slider.style.left = sliderLeft + 'px';
                        slider.style.top = btnTop + 'px';
                        slider.style.transform = 'none';
                        slider.style.display = 'block';
                        slider.style.zIndex = '25';

                        // Move slider to container if it's still in overlay
                        if (slider.parentElement !== container) {
                            container.appendChild(slider);
                        }

                        // Hide buttons AFTER getting position
                        buttonGroup.style.display = 'none';

                        updateBrightnessSliderPosition(brightness);
                    } else {
                        slider.style.display = 'none';
                        buttonGroup.style.display = 'flex';
                    }
                }
            }

            function updateBrightnessSliderPosition(brightness) {
                const thumb = current3DViewerContainer?.querySelector('#brightness-slider-thumb');
                if (thumb) {
                    // brightness ranges from 0 to 10, convert to percentage
                    const percent = (brightness / MAX_MODEL_BRIGHTNESS) * 100;
                    thumb.style.left = percent + '%';
                }
            }

            // Update model depth based on lowest Y point
            // Lower Y (bottom/front of screen) = blocks models behind
            function updateModelDepthFromY(model) {
                if (!model) return;

                // Calculate the lowest Y point of the model (bottom of bounding box)
                const box = new THREE.Box3().setFromObject(model);
                const lowestY = box.min.y;

                // Lower Y = higher renderOrder = drawn last = appears on top
                const renderOrder = Math.round((10 - lowestY) * 1000);
                model.renderOrder = renderOrder;

                // Set Z position: lower Y = closer to camera
                // Use 5 units separation per Y unit to ensure no Z overlap between model geometries
                model.position.z = (5 - lowestY) * 5;

                // Apply to all child meshes
                model.traverse((child) => {
                    child.renderOrder = renderOrder;
                    if (child.isMesh && child.material) {
                        const materials = Array.isArray(child.material) ? child.material : [child.material];
                        materials.forEach(mat => {
                            mat.depthTest = true;
                            mat.depthWrite = true;
                            mat.side = THREE.DoubleSide;
                        });
                    }
                });
            }

            // Animate model opacity for smooth transitions
            function animateModelOpacity(model, targetOpacity, duration, callback) {
                const startTime = performance.now();
                const startOpacity = model.userData.currentOpacity || 1.0;

                function animate() {
                    const elapsed = performance.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const currentOpacity = startOpacity + (targetOpacity - startOpacity) * progress;

                    model.traverse((child) => {
                        if (child.isMesh && child.material) {
                            const materials = Array.isArray(child.material) ? child.material : [child.material];
                            materials.forEach(mat => {
                                mat.opacity = currentOpacity;
                            });
                        }
                    });
                    model.userData.currentOpacity = currentOpacity;

                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else if (callback) {
                        callback();
                    }
                }
                requestAnimationFrame(animate);
            }

            // Update depth for all models (call after any position change)
            function updateAllModelsRenderOrder() {
                allLoadedModels.forEach(model => updateModelDepthFromY(model));
            }

            function addModelControlOverlay(container) {
                // Remove existing overlay
                container.querySelector('.model-control-overlay')?.remove();

                const overlay = document.createElement('div');
                overlay.className = 'model-control-overlay';
                overlay.style.display = 'none'; // Hidden until a model is clicked
                overlay.innerHTML = `
                    <div class="model-control-group">
                        <button class="model-control-btn" id="btn-rotate" title="Rotate - Drag left/right">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                            </svg>
                        </button>
                        <button class="model-control-btn" id="btn-tilt" title="Tilt - Drag up/down">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 2v20M8 6l4-4 4 4M8 18l4 4 4-4"/>
                            </svg>
                        </button>
                        <button class="model-control-btn" id="btn-scale" title="Scale - Drag up/down">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                            </svg>
                        </button>
                        <button class="model-control-btn" id="btn-brightness" title="Brightness - Drag left/right">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="5"/>
                                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                            </svg>
                        </button>
                        <button class="model-control-btn" id="btn-image-preview" title="View 2D Image">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5"/>
                                <polyline points="21 15 16 10 5 21"/>
                            </svg>
                        </button>
                        <button class="model-control-btn" id="btn-set-default" title="Save as default (rotation, brightness, tilt)">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                            </svg>
                        </button>
                        <button class="model-control-btn model-control-danger" id="btn-delete" title="Delete model">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                            </svg>
                        </button>
                    </div>
                    <div class="brightness-slider" id="brightness-slider" style="display: none;">
                        <div class="brightness-slider-track">
                            <div class="brightness-slider-fill" id="brightness-slider-fill"></div>
                            <div class="brightness-slider-thumb" id="brightness-slider-thumb"></div>
                        </div>
                    </div>
                `;
                container.appendChild(overlay);

                // Add event listeners for controls
                setupModelControlListeners(overlay);
            }

            function setupModelControlListeners(overlay) {
                const btnBrightness = overlay.querySelector('#btn-brightness');
                const btnRotate = overlay.querySelector('#btn-rotate');
                const btnScale = overlay.querySelector('#btn-scale');
                const btnTilt = overlay.querySelector('#btn-tilt');
                const btnSetDefault = overlay.querySelector('#btn-set-default');
                const btnDelete = overlay.querySelector('#btn-delete');

                // Brightness control - mouse
                btnBrightness.addEventListener('mousedown', (e) => {
                    isDraggingBrightness = true;
                    lastMouseX = e.clientX;
                    showBrightnessSlider(true);
                    e.preventDefault();
                });
                // Brightness control - touch
                btnBrightness.addEventListener('touchstart', (e) => {
                    isDraggingBrightness = true;
                    lastMouseX = e.touches[0].clientX;
                    showBrightnessSlider(true);
                    e.preventDefault();
                }, { passive: false });

                // Rotate control - mouse
                btnRotate.addEventListener('mousedown', (e) => {
                    isDraggingRotate = true;
                    lastMouseX = e.clientX;
                    e.preventDefault();
                });
                // Rotate control - touch
                btnRotate.addEventListener('touchstart', (e) => {
                    isDraggingRotate = true;
                    lastMouseX = e.touches[0].clientX;
                    e.preventDefault();
                }, { passive: false });

                // Scale control - mouse
                btnScale.addEventListener('mousedown', (e) => {
                    isDraggingScale = true;
                    lastMouseY = e.clientY;
                    e.preventDefault();
                });
                // Scale control - touch
                btnScale.addEventListener('touchstart', (e) => {
                    isDraggingScale = true;
                    lastMouseY = e.touches[0].clientY;
                    e.preventDefault();
                }, { passive: false });

                // Tilt control - mouse
                btnTilt.addEventListener('mousedown', (e) => {
                    isDraggingTilt = true;
                    lastMouseY = e.clientY;
                    e.preventDefault();
                });
                // Tilt control - touch
                btnTilt.addEventListener('touchstart', (e) => {
                    isDraggingTilt = true;
                    lastMouseY = e.touches[0].clientY;
                    e.preventDefault();
                }, { passive: false });

                // Image Preview - click and touch
                const btnImagePreview = overlay.querySelector('#btn-image-preview');
                btnImagePreview.addEventListener('click', () => {
                    if (currentLoadedModel) {
                        show2DImageModal();
                    }
                });
                btnImagePreview.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    if (currentLoadedModel) {
                        show2DImageModal();
                    }
                });

                // Set Default Rotation - click and touch
                btnSetDefault.addEventListener('click', () => {
                    if (currentLoadedModel) {
                        setDefaultRotation();
                    }
                });
                btnSetDefault.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    if (currentLoadedModel) {
                        setDefaultRotation();
                    }
                });

                // Delete - click and touch
                btnDelete.addEventListener('click', () => {
                    if (currentLoadedModel) {
                        deleteCurrentModel();
                    }
                });
                btnDelete.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    if (currentLoadedModel) {
                        deleteCurrentModel();
                    }
                });

                // Mouse move and up handlers (document level)
                document.addEventListener('mousemove', handleModelControlMouseMove);
                document.addEventListener('mouseup', handleModelControlMouseUp);

                // Touch move and end handlers (document level)
                document.addEventListener('touchmove', handleModelControlTouchMove, { passive: false });
                document.addEventListener('touchend', handleModelControlTouchEnd);
            }

            function handleModelControlMouseMove(e) {
                if (!currentLoadedModel) return;

                if (isDraggingBrightness) {
                    const sliderTrack = current3DViewerContainer?.querySelector('.brightness-slider-track');
                    if (sliderTrack) {
                        const rect = sliderTrack.getBoundingClientRect();
                        const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                        const newBrightness = percent * MAX_MODEL_BRIGHTNESS;
                        currentLoadedModel.userData.brightness = newBrightness;
                        updateModelBrightness(currentLoadedModel, newBrightness);
                        updateBrightnessSliderPosition(newBrightness);
                    }
                }

                if (isDraggingRotate) {
                    const delta = (e.clientX - lastMouseX) * 0.02;
                    lastMouseX = e.clientX;
                    currentLoadedModel.userData.yRotation = (currentLoadedModel.userData.yRotation || 0) + delta;
                    currentLoadedModel.rotation.y = currentLoadedModel.userData.yRotation;
                }

                if (isDraggingScale) {
                    const delta = (lastMouseY - e.clientY) * 0.005;
                    lastMouseY = e.clientY;
                    const baseScale = currentLoadedModel.userData.baseScale || 1;
                    const currentScale = currentLoadedModel.scale.x;
                    const newScale = Math.max(baseScale * 0.2, Math.min(baseScale * 3, currentScale + delta));
                    currentLoadedModel.scale.setScalar(newScale);
                }

                if (isDraggingTilt) {
                    // Drag down = tilt down (positive rotation.x), drag up = tilt up toward flat (0)
                    const delta = (e.clientY - lastMouseY) * 0.005;
                    lastMouseY = e.clientY;
                    // Min 0 (flat, facing user), Max 0.7 (tilted down)
                    // Use ?? instead of || to handle 0 correctly (0 is valid, not falsy)
                    const currentTilt = currentLoadedModel.userData.tilt ?? DEFAULT_TILT;
                    const newTilt = Math.max(0, Math.min(0.7, currentTilt + delta));
                    currentLoadedModel.userData.tilt = newTilt;
                    currentLoadedModel.rotation.x = newTilt;
                }
            }

            function handleModelControlMouseUp() {
                const wasScaling = isDraggingScale;
                const wasBrightness = isDraggingBrightness;
                isDraggingBrightness = false;
                isDraggingRotate = false;
                isDraggingScale = false;
                isDraggingTilt = false;
                // Recalculate bar position if we were scaling
                if (wasScaling) {
                    updateControlOverlayPosition(true);
                }
                // Hide brightness slider
                if (wasBrightness) {
                    showBrightnessSlider(false);
                }
                // Save state after control ends
                saveModelStates();
            }

            function handleModelControlTouchMove(e) {
                if (!currentLoadedModel) return;
                if (!isDraggingBrightness && !isDraggingRotate && !isDraggingScale && !isDraggingTilt) return;

                const touch = e.touches[0];

                if (isDraggingBrightness) {
                    const sliderTrack = current3DViewerContainer?.querySelector('.brightness-slider-track');
                    if (sliderTrack) {
                        const rect = sliderTrack.getBoundingClientRect();
                        const percent = Math.max(0, Math.min(1, (touch.clientX - rect.left) / rect.width));
                        const newBrightness = percent * MAX_MODEL_BRIGHTNESS;
                        currentLoadedModel.userData.brightness = newBrightness;
                        updateModelBrightness(currentLoadedModel, newBrightness);
                        updateBrightnessSliderPosition(newBrightness);
                    }
                    e.preventDefault();
                }

                if (isDraggingRotate) {
                    const delta = (touch.clientX - lastMouseX) * 0.02;
                    lastMouseX = touch.clientX;
                    currentLoadedModel.userData.yRotation = (currentLoadedModel.userData.yRotation || 0) + delta;
                    currentLoadedModel.rotation.y = currentLoadedModel.userData.yRotation;
                    e.preventDefault();
                }

                if (isDraggingScale) {
                    const delta = (lastMouseY - touch.clientY) * 0.005;
                    lastMouseY = touch.clientY;
                    const baseScale = currentLoadedModel.userData.baseScale || 1;
                    const currentScale = currentLoadedModel.scale.x;
                    const newScale = Math.max(baseScale * 0.2, Math.min(baseScale * 3, currentScale + delta));
                    currentLoadedModel.scale.setScalar(newScale);
                    e.preventDefault();
                }

                if (isDraggingTilt) {
                    const delta = (touch.clientY - lastMouseY) * 0.005;
                    lastMouseY = touch.clientY;
                    const currentTilt = currentLoadedModel.userData.tilt ?? DEFAULT_TILT;
                    const newTilt = Math.max(0, Math.min(0.7, currentTilt + delta));
                    currentLoadedModel.userData.tilt = newTilt;
                    currentLoadedModel.rotation.x = newTilt;
                    e.preventDefault();
                }
            }

            function handleModelControlTouchEnd() {
                const wasScaling = isDraggingScale;
                const wasBrightness = isDraggingBrightness;
                isDraggingBrightness = false;
                isDraggingRotate = false;
                isDraggingScale = false;
                isDraggingTilt = false;
                // Recalculate bar position if we were scaling
                if (wasScaling) {
                    updateControlOverlayPosition(true);
                }
                // Hide brightness slider
                if (wasBrightness) {
                    showBrightnessSlider(false);
                }
                // Save state after control ends
                saveModelStates();
            }

            // Background brightness handlers
            function applyBackgroundBrightness(brightness) {
                // Apply brightness filter to the background image
                const photoSlide = document.getElementById('items-photo-slide');
                if (photoSlide) {
                    const img = photoSlide.querySelector('img');
                    if (img) {
                        img.style.filter = `brightness(${brightness})`;
                    }
                    // Apply same brightness to the 3D canvas if present
                    const canvas = photoSlide.querySelector('canvas');
                    if (canvas) {
                        canvas.style.filter = `brightness(${brightness})`;
                    }
                }
            }

            function setupBackgroundBrightnessHandlers() {
                const bgBrightnessBtn = document.getElementById('bg-brightness-btn');
                if (!bgBrightnessBtn) return;

                // Click to show slider and start dragging
                bgBrightnessBtn.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    isDraggingBgBrightness = true;
                    showPhotoBrightnessSlider(true);
                });

                // Touch to show slider and start dragging
                bgBrightnessBtn.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    isDraggingBgBrightness = true;
                    showPhotoBrightnessSlider(true);
                }, { passive: false });

                // Document-level mouse move handler
                document.addEventListener('mousemove', (e) => {
                    if (!isDraggingBgBrightness) return;
                    const sliderTrack = document.querySelector('.photo-brightness-slider-track');
                    if (sliderTrack) {
                        const rect = sliderTrack.getBoundingClientRect();
                        const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                        bgBrightnessValue = 0.2 + (percent * 3.8);
                        applyBackgroundBrightness(bgBrightnessValue);
                        updatePhotoBrightnessSliderPosition(bgBrightnessValue);
                    }
                });

                // Document-level mouse up handler
                document.addEventListener('mouseup', () => {
                    if (isDraggingBgBrightness) {
                        isDraggingBgBrightness = false;
                        showPhotoBrightnessSlider(false);
                        saveBackgroundBrightness();
                    }
                });

                // Document-level touch move handler
                document.addEventListener('touchmove', (e) => {
                    if (!isDraggingBgBrightness) return;
                    e.preventDefault();
                    const sliderTrack = document.querySelector('.photo-brightness-slider-track');
                    if (sliderTrack) {
                        const touch = e.touches[0];
                        const rect = sliderTrack.getBoundingClientRect();
                        const percent = Math.max(0, Math.min(1, (touch.clientX - rect.left) / rect.width));
                        bgBrightnessValue = 0.2 + (percent * 3.8);
                        applyBackgroundBrightness(bgBrightnessValue);
                        updatePhotoBrightnessSliderPosition(bgBrightnessValue);
                    }
                }, { passive: false });

                // Document-level touch end handler
                document.addEventListener('touchend', () => {
                    if (isDraggingBgBrightness) {
                        isDraggingBgBrightness = false;
                        showPhotoBrightnessSlider(false);
                        saveBackgroundBrightness();
                    }
                });
            }

            function showPhotoBrightnessSlider(show) {
                const slider = document.getElementById('photo-brightness-slider');
                const photoSlide = document.getElementById('items-photo-slide');

                if (!slider || !photoSlide) return;

                if (show) {
                    // Get brightness button position BEFORE hiding buttons
                    const bgBtn = document.getElementById('bg-brightness-btn');
                    if (!bgBtn) return;

                    const container = photoSlide;
                    const containerRect = container.getBoundingClientRect();
                    const btnRect = bgBtn.getBoundingClientRect();

                    // Get button center in viewport
                    const btnCenterX = btnRect.left + btnRect.width / 2;
                    const btnCenterY = btnRect.top + btnRect.height / 2;

                    // Convert to container-relative position
                    const relativeX = btnCenterX - containerRect.left;
                    const relativeY = btnCenterY - containerRect.top;

                    // Calculate current brightness percentage (0-100)
                    const brightnessPercent = ((bgBrightnessValue - 0.2) / 3.8) * 100;

                    // Position slider so the thumb (at brightnessPercent) is at button center
                    // If brightness is 75%, we want the thumb at 75% of track to be at button position
                    // So slider needs to be offset by (75% - 50%) of track width to the left
                    const sliderWidth = 200; // slider width from CSS
                    const trackWidth = sliderWidth - 30; // subtract padding (15px each side)
                    const thumbOffset = (brightnessPercent / 100) * trackWidth;
                    const centerOffset = trackWidth / 2;
                    const adjustmentX = thumbOffset - centerOffset;

                    slider.style.left = `${relativeX - adjustmentX}px`;
                    slider.style.top = `${relativeY}px`;
                    slider.style.transform = 'translate(-50%, -50%)';

                    // Update thumb and fill position based on current brightness
                    updatePhotoBrightnessSliderPosition(bgBrightnessValue);

                    // Hide all photo control buttons
                    const buttons = photoSlide.querySelectorAll('.photo-camera-inline-btn, .photo-upload-inline-btn, .photo-brightness-btn, .photo-empty-room-btn, .photo-rotate-btn, .photo-delete-btn');
                    buttons.forEach(btn => btn.style.display = 'none');

                    // Show slider
                    slider.style.display = 'block';
                } else {
                    // Hide slider
                    slider.style.display = 'none';

                    // Show all photo control buttons
                    const buttons = photoSlide.querySelectorAll('.photo-camera-inline-btn, .photo-upload-inline-btn, .photo-brightness-btn, .photo-empty-room-btn, .photo-rotate-btn, .photo-delete-btn');
                    buttons.forEach(btn => btn.style.display = 'flex');
                }
            }

            function updatePhotoBrightnessSliderPosition(brightness) {
                const thumb = document.getElementById('photo-brightness-slider-thumb');
                const fill = document.getElementById('photo-brightness-slider-fill');
                if (thumb && fill) {
                    // Map brightness (0.2-4.0) to percentage (0-100)
                    const percent = ((brightness - 0.2) / 3.8) * 100;
                    thumb.style.left = percent + '%';
                    fill.style.width = percent + '%';
                }
            }

            function saveBackgroundBrightness() {
                if (!currentArea || currentItemsPhotoIndex === null) return;
                const key = `bgBrightness_${currentArea}_photo_${currentItemsPhotoIndex}`;
                localStorage.setItem(key, bgBrightnessValue.toString());
            }

            function getBackgroundBrightness() {
                if (!currentArea) return 1.0;
                const photoIndex = currentItemsPhotoIndex || 0;
                const key = `bgBrightness_${currentArea}_photo_${photoIndex}`;
                const saved = localStorage.getItem(key);
                if (saved !== null) {
                    bgBrightnessValue = parseFloat(saved);
                    return bgBrightnessValue;
                }
                bgBrightnessValue = 1.0;
                return 1.0;
            }

            async function setDefaultRotation() {
                if (!currentLoadedModel) return;

                const model3d = currentLoadedModel.userData.model3d;
                const rotation = currentLoadedModel.rotation.y;
                const brightness = currentLoadedModel.userData.brightness || 3.0;
                const tilt = currentLoadedModel.userData.tilt || DEFAULT_TILT;

                if (!model3d) {
                    alert('Unable to identify model');
                    return;
                }

                try {
                    const response = await fetch('/api/save-default-rotation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            model3d: model3d,
                            rotation: rotation,
                            brightness: brightness,
                            tilt: tilt
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        // Update the model's frontRotation in userData
                        currentLoadedModel.userData.frontRotation = rotation;
                        currentLoadedModel.userData.yRotation = rotation;

                        // Find and update the item button's dataset for future drags
                        const itemName = currentLoadedModel.userData.itemName;
                        document.querySelectorAll('.item-btn').forEach(btn => {
                            if (btn.dataset.selectedName === itemName && btn.dataset.model3d === model3d) {
                                btn.dataset.frontRotation = rotation;
                                btn.dataset.brightness = brightness;
                                btn.dataset.tilt = tilt;
                                console.log(`Updated item button properties for ${itemName} - rotation: ${rotation}, brightness: ${brightness}, tilt: ${tilt}`);
                            }
                        });

                        // Update areaSelectedItems for persistence
                        if (currentArea && areaSelectedItems[currentArea]) {
                            Object.keys(areaSelectedItems[currentArea]).forEach(itemType => {
                                const item = areaSelectedItems[currentArea][itemType];
                                if (item.itemName === itemName && item.model3d === model3d) {
                                    item.frontRotation = rotation;
                                    item.brightness = brightness;
                                    item.tilt = tilt;
                                    console.log(`Updated areaSelectedItems properties for ${itemName}`);
                                }
                            });
                        }

                        // Save session storage with updated rotation
                        saveStagingSession();

                        // Save model states to persist the updated frontRotation
                        await saveModelStates();

                        // Visual feedback
                        const btn = document.querySelector('#btn-set-default');
                        const originalColor = btn.style.backgroundColor;
                        btn.style.backgroundColor = '#4CAF50';
                        setTimeout(() => {
                            btn.style.backgroundColor = originalColor;
                        }, 500);

                        console.log(`Saved default properties for ${model3d} - rotation: ${rotation}, brightness: ${brightness}, tilt: ${tilt}`);
                    } else {
                        alert('Failed to save default properties');
                    }
                } catch (error) {
                    console.error('Error saving default properties:', error);
                    alert('Error saving default properties');
                }
            }

            function deleteCurrentModel() {
                if (!currentLoadedModel || !threeScene) return;

                threeScene.remove(currentLoadedModel);
                const idx = allLoadedModels.indexOf(currentLoadedModel);
                if (idx > -1) allLoadedModels.splice(idx, 1);

                currentLoadedModel = allLoadedModels.length > 0 ? allLoadedModels[allLoadedModels.length - 1] : null;

                // If no models left, remove 3D mode
                if (allLoadedModels.length === 0) {
                    exitPhoto3DMode();
                }

                saveModelStates();
            }

            function exitPhoto3DMode() {
                const container = current3DViewerContainer;
                if (!container) return;

                // Cancel animation loop
                if (animationFrameId) {
                    cancelAnimationFrame(animationFrameId);
                    animationFrameId = null;
                }

                // Remove canvas and overlay
                container.querySelector('canvas')?.remove();
                container.querySelector('.model-control-overlay')?.remove();
                container.classList.remove('photo-3d-mode');

                // Show the img element again
                const imgEl = container.querySelector('img');
                if (imgEl) imgEl.style.display = '';

                // Clear 3D state
                threeScene = null;
                threeCamera = null;
                threeRenderer = null;
                currentLoadedModel = null;
                allLoadedModels = [];
                current3DPhotoIndex = null;
                current3DViewerContainer = null;
            }

            async function saveModelStates() {
                // Save model states to database
                if (!currentArea || current3DPhotoIndex === null) return;

                const photos = areaPhotos[currentArea] || [];
                const backgroundImage = photos[current3DPhotoIndex];
                if (!backgroundImage) return;

                const modelStates = allLoadedModels.map((model, idx) => ({
                    instanceId: idx,
                    modelUrl: model.userData.model3d,
                    itemName: model.userData.itemName,
                    imageUrl: model.userData.imageUrl,
                    positionX: model.position.x,
                    positionY: model.position.y,
                    positionZ: model.position.z,
                    scale: model.scale.x,
                    rotationY: model.userData.yRotation || 0,
                    tilt: model.userData.tilt ?? DEFAULT_TILT,
                    brightness: model.userData.brightness || 3.0,
                    width: model.userData.width || 0,
                    depth: model.userData.depth || 0,
                    height: model.userData.height || 0,
                    frontRotation: model.userData.frontRotation ?? -Math.PI/2
                }));

                // Get staging_id from the page if available
                const stagingId = window.stagingId || null;

                try {
                    await fetch('/api/save-staging-models', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            stagingId: stagingId,
                            area: currentArea,
                            photoIndex: current3DPhotoIndex,
                            backgroundImage: `${currentArea}_photo_${current3DPhotoIndex}`, // Use area + index as unique key
                            models: modelStates
                        })
                    });
                } catch (error) {
                    console.error('Error saving model states:', error);
                }
            }

            // Load saved models from database for current photo
            let isLoadingModels = false; // Prevent concurrent loads
            let loadedBackgroundKey = null; // Track which background has been loaded

            async function loadSavedModelsForPhoto(photoIndex) {
                const photos = areaPhotos[currentArea] || [];
                if (photos.length === 0 || photoIndex < 0 || photoIndex >= photos.length) return;

                // Use area + index as unique key
                const backgroundKey = `${currentArea}_photo_${photoIndex}`;
                const stagingId = window.stagingId || 0;

                // Don't reload if already loaded for this photo or currently loading
                if (isLoadingModels) {
                    console.log('Already loading models, skipping');
                    return;
                }
                // Check if this exact background key was already loaded with models
                if (loadedBackgroundKey === backgroundKey && allLoadedModels.length > 0) {
                    console.log('Models already loaded for this background, skipping');
                    return;
                }

                isLoadingModels = true;
                loadedBackgroundKey = backgroundKey;

                try {
                    const response = await fetch(`/api/get-staging-models?staging_id=${stagingId}&background_image=${encodeURIComponent(backgroundKey)}`);
                    const data = await response.json();

                    if (data.success && data.models && data.models.length > 0) {
                        // Load Three.js if not loaded
                        await loadThreeJS();

                        // Initialize 3D scene if not already done
                        const container = document.getElementById('items-photo-slide');
                        if (!container) return;

                        // Create scene with first model
                        const firstModel = data.models[0];
                        await initPhoto3DSceneForRestore(photoIndex, container);

                        // Load all models
                        console.log('Loading', data.models.length, 'models for background:', backgroundKey);
                        for (const modelData of data.models) {
                            await loadGLTFModelFromSaved(modelData);
                        }
                        console.log('Loaded models count:', allLoadedModels.length);

                        // Clear selection - user must click to select a model
                        currentLoadedModel = null;
                        showModelControls(false);
                    }
                } catch (error) {
                    console.error('Error loading saved models:', error);
                    loadedBackgroundKey = null; // Reset on error to allow retry
                } finally {
                    isLoadingModels = false;
                }
            }

            async function initPhoto3DSceneForRestore(photoIndex, container) {
                current3DPhotoIndex = photoIndex;
                current3DViewerContainer = container;

                const photos = areaPhotos[currentArea] || [];
                const photoSrc = photos[photoIndex];
                if (!photoSrc) return;

                const containerRect = container.getBoundingClientRect();
                const width = containerRect.width;
                const height = containerRect.height;

                // Explicitly remove all existing models from scene first
                if (threeScene) {
                    allLoadedModels.forEach(model => {
                        threeScene.remove(model);
                    });
                }

                // Clear existing 3D scene and models array
                if (threeRenderer) {
                    container.querySelector('canvas')?.remove();
                }
                allLoadedModels = [];
                currentLoadedModel = null;

                const imgEl = container.querySelector('img');
                if (imgEl) imgEl.style.display = 'none';

                threeScene = new THREE.Scene();

                const textureLoader = new THREE.TextureLoader();
                textureLoader.load(photoSrc, (bgTexture) => {
                    threeScene.background = bgTexture;
                });

                const aspect = width / height;
                const frustumSize = 5;
                threeCamera = new THREE.OrthographicCamera(
                    frustumSize * aspect / -2,
                    frustumSize * aspect / 2,
                    frustumSize / 2,
                    frustumSize / -2,
                    1, 100
                );
                threeCamera.position.set(0, 0, 50);
                threeCamera.lookAt(0, 0, 0);

                threeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                threeRenderer.setSize(width, height);
                threeRenderer.setPixelRatio(window.devicePixelRatio);
                threeRenderer.domElement.style.position = 'absolute';
                threeRenderer.domElement.style.top = '0';
                threeRenderer.domElement.style.left = '0';
                threeRenderer.domElement.style.width = '100%';
                threeRenderer.domElement.style.height = '100%';
                // Apply saved brightness to canvas
                if (bgBrightnessValue !== 1.0) {
                    threeRenderer.domElement.style.filter = `brightness(${bgBrightnessValue})`;
                }
                container.appendChild(threeRenderer.domElement);

                // Lights - brighter to illuminate 3D models properly
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                threeScene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
                directionalLight.position.set(5, 10, 7.5);
                threeScene.add(directionalLight);
                const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.6);
                directionalLight2.position.set(-5, 5, -5);
                threeScene.add(directionalLight2);

                container.classList.add('photo-3d-mode');
                addModelControlOverlay(container);

                if (animationFrameId) cancelAnimationFrame(animationFrameId);
                function animate() {
                    animationFrameId = requestAnimationFrame(animate);
                    if (threeRenderer && threeScene && threeCamera) {
                        // Continuously update depth for smooth transitions
                        updateAllModelsRenderOrder();
                        threeRenderer.render(threeScene, threeCamera);
                        updateControlOverlayPosition();
                    }
                }
                animate();

                // Add mouse handlers for model position dragging
                setupModelDragHandlers(threeRenderer.domElement);
            }

            async function loadGLTFModelFromSaved(modelData) {
                if (!threeScene) return;

                const modelUrl = '/static/models/' + modelData.modelUrl;
                const loader = new THREE.GLTFLoader();

                return new Promise((resolve) => {
                    loader.load(modelUrl, (gltf) => {
                        const model = gltf.scene;

                        // Make all materials double-sided so back/side faces render solid
                        model.traverse((child) => {
                            if (child.isMesh && child.material) {
                                const materials = Array.isArray(child.material) ? child.material : [child.material];
                                materials.forEach(mat => {
                                    mat.side = THREE.DoubleSide;
                                });
                            }
                        });

                        // Apply saved state
                        model.position.set(
                            modelData.positionX || 0,
                            modelData.positionY || -0.5,
                            modelData.positionZ || 0
                        );
                        model.scale.setScalar(modelData.scale || 1);
                        model.rotation.y = modelData.rotationY || 0;
                        model.rotation.x = modelData.tilt ?? DEFAULT_TILT;

                        // Calculate current zone based on position
                        const posX = modelData.positionX || 0;
                        const currentZone = getPositionZone(posX);

                        model.userData = {
                            model3d: modelData.modelUrl,
                            itemName: modelData.itemName,
                            imageUrl: modelData.imageUrl,
                            frontRotation: modelData.frontRotation ?? -Math.PI/2,
                            yRotation: modelData.rotationY || 0,
                            positionZone: currentZone, // Track zone for rotation changes
                            tilt: modelData.tilt ?? DEFAULT_TILT,
                            brightness: modelData.brightness || 3.0,
                            baseScale: modelData.scale || 1,
                            instanceId: allLoadedModels.length
                        };

                        currentLoadedModel = model;
                        threeScene.add(model);
                        allLoadedModels.push(model);

                        // Set render order based on Z position (higher Z = in front)
                        updateModelDepthFromY(model);
                        updateModelBrightness(model, modelData.brightness || 3.0);
                        resolve();
                    }, undefined, (error) => {
                        console.error('Error loading saved model:', error);
                        resolve();
                    });
                });
            }

            function startItemsCamera() {
                const video = document.getElementById('items-camera-preview');
                const cameraSection = document.getElementById('items-camera-section');
                if (!video || !cameraSection) return;

                // Hide camera section initially until camera starts
                cameraSection.style.display = 'none';

                navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment', width: { ideal: 3840 }, height: { ideal: 2880 }, aspectRatio: { ideal: 4/3 } },
                    audio: false
                }).then(stream => {
                    itemsCameraStream = stream;
                    video.srcObject = stream;
                    // Show camera section only when camera successfully starts
                    cameraSection.style.display = 'block';
                }).catch(err => {
                    console.log('Camera access denied:', err);
                    // Keep camera section hidden if camera fails
                    cameraSection.style.display = 'none';
                });
            }

            function stopItemsCamera() {
                if (itemsCameraStream) {
                    itemsCameraStream.getTracks().forEach(track => track.stop());
                    itemsCameraStream = null;
                }
                const video = document.getElementById('items-camera-preview');
                if (video) {
                    video.srcObject = null;
                }
            }

            // Items Modal Photo Functions
            let itemsPhotoTouchStartX = 0;
            let itemsPhotoTouchEndX = 0;

            function renderItemsPhotosGrid(direction = null) {
                const container = document.getElementById('items-photos-carousel-container');
                const counter = document.getElementById('items-photos-carousel-counter');
                const prevBtn = document.getElementById('items-photos-prev-btn');
                const nextBtn = document.getElementById('items-photos-next-btn');
                const photos = areaPhotos[currentArea] || [];
                const isMobile = window.innerWidth <= 767;

                // Save and exit 3D mode before rebuilding carousel (if switching photos)
                if (current3DPhotoIndex !== null && current3DPhotoIndex !== currentItemsPhotoIndex) {
                    // Save current models before switching
                    if (allLoadedModels.length > 0) {
                        saveModelStates();
                    }
                    exitPhoto3DMode();
                }

                if (photos.length === 0) {
                    // No photos - show upload button at top of message
                    const areaName = areaNameMap[currentArea] || currentArea;
                    container.innerHTML = `
                        <div style="text-align: center; padding: 20px;">
                            <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                                <button class="items-photo-upload-btn items-take-photo-btn" onclick="scrollToItemsCamera()" style="display: ${isMobile ? 'inline-flex' : 'none'};">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                                        <circle cx="12" cy="13" r="4"/>
                                    </svg>
                                    Take Photos
                                </button>
                                <button class="items-photo-upload-btn" onclick="document.getElementById('items-photo-upload-input').click()">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                        <polyline points="17 8 12 3 7 8"/>
                                        <line x1="12" y1="3" x2="12" y2="15"/>
                                    </svg>
                                    Upload Photos
                                </button>
                            </div>
                            <p style="color: var(--color-secondary); margin-top: 10px; font-size: 13px;">Take or upload photos from 4 different directions of the ${areaName.toLowerCase()}</p>
                        </div>`;
                    counter.innerHTML = '';
                    prevBtn.style.display = 'none';
                    nextBtn.style.display = 'none';
                    currentItemsPhotoIndex = 0;
                    return;
                }

                // Reset index if out of bounds
                if (currentItemsPhotoIndex >= photos.length) {
                    currentItemsPhotoIndex = photos.length - 1;
                }
                if (currentItemsPhotoIndex < 0) {
                    currentItemsPhotoIndex = 0;
                }

                // Show/hide nav buttons
                prevBtn.style.display = photos.length > 1 ? 'flex' : 'none';
                nextBtn.style.display = photos.length > 1 ? 'flex' : 'none';

                // Get saved brightness for this photo BEFORE building HTML
                const savedBrightness = getBackgroundBrightness();
                const brightnessStyle = savedBrightness !== 1.0 ? `filter: brightness(${savedBrightness});` : '';

                // Build slides: prev, current, next for smooth swiping
                const prevIndex = currentItemsPhotoIndex > 0 ? currentItemsPhotoIndex - 1 : null;
                const nextIndex = currentItemsPhotoIndex < photos.length - 1 ? currentItemsPhotoIndex + 1 : null;

                let slidesHTML = '';

                // Previous slide
                if (prevIndex !== null) {
                    slidesHTML += `<div class="photo-carousel-slide carousel-slide-prev"><img src="${photos[prevIndex]}" alt="Photo ${prevIndex + 1}"></div>`;
                }

                // Current slide with Upload button next to rotate button
                slidesHTML += `
                    <div class="photo-carousel-slide carousel-slide-current" id="items-photo-slide">
                        <img src="${photos[currentItemsPhotoIndex]}" alt="Photo ${currentItemsPhotoIndex + 1}" style="${brightnessStyle}">
                        <button class="photo-camera-inline-btn" onclick="scrollToItemsCamera()" title="Take Photos" style="display: ${isMobile ? 'flex' : 'none'};">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                                <circle cx="12" cy="13" r="4"/>
                            </svg>
                        </button>
                        <button class="photo-upload-inline-btn" onclick="document.getElementById('items-photo-upload-input').click()" title="Upload Photos">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="17 8 12 3 7 8"/>
                                <line x1="12" y1="3" x2="12" y2="15"/>
                            </svg>
                        </button>
                        <button class="photo-brightness-btn" id="bg-brightness-btn" title="Brightness - Drag left/right">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="5"/>
                                <line x1="12" y1="1" x2="12" y2="3"/>
                                <line x1="12" y1="21" x2="12" y2="23"/>
                                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                                <line x1="1" y1="12" x2="3" y2="12"/>
                                <line x1="21" y1="12" x2="23" y2="12"/>
                                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                            </svg>
                        </button>
                        <button class="photo-empty-room-btn" onclick="emptyRoomBackground()" title="Empty Room - Remove Furniture">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M3 10l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V10z"/>
                            </svg>
                        </button>
                        <button class="photo-rotate-btn" onclick="rotateItemsPhoto(${currentItemsPhotoIndex})">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                            </svg>
                        </button>
                        <button class="photo-delete-btn" onclick="removeItemsPhoto(${currentItemsPhotoIndex})">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                            </svg>
                        </button>
                        <div class="photo-brightness-slider" id="photo-brightness-slider" style="display: none;">
                            <div class="photo-brightness-slider-track">
                                <div class="photo-brightness-slider-fill" id="photo-brightness-slider-fill"></div>
                                <div class="photo-brightness-slider-thumb" id="photo-brightness-slider-thumb"></div>
                            </div>
                        </div>
                    </div>
                `;

                // Next slide
                if (nextIndex !== null) {
                    slidesHTML += `<div class="photo-carousel-slide carousel-slide-next"><img src="${photos[nextIndex]}" alt="Photo ${nextIndex + 1}"></div>`;
                }

                container.innerHTML = `<div class="carousel-track" id="items-carousel-track">${slidesHTML}</div>`;

                // Render counter: dots on both mobile and desktop
                if (photos.length > 1) {
                    const dots = photos.map((_, i) =>
                        `<span class="carousel-dot ${i === currentItemsPhotoIndex ? 'active' : ''}"></span>`
                    ).join('');
                    counter.innerHTML = `<div class="carousel-dots">${dots}</div>`;
                } else {
                    counter.innerHTML = '';
                }

                // Add touch event listeners for swipe
                if (isMobile) {
                    const track = document.getElementById('items-carousel-track');
                    if (track) {
                        track.addEventListener('touchstart', handleItemsTouchStart, { passive: true });
                        track.addEventListener('touchmove', handleItemsTouchMove, { passive: true });
                        track.addEventListener('touchend', handleItemsTouchEnd, { passive: false });
                    }
                }

                // Try to load saved 3D models for this photo
                loadSavedModelsForPhoto(currentItemsPhotoIndex);

                // Setup background brightness drag handlers
                setupBackgroundBrightnessHandlers();
            }

            let itemsIsDragging = false;
            let itemsCurrentTranslateX = 0;
            let itemsIsAnimating = false;

            function handleItemsTouchStart(e) {
                if (itemsIsAnimating) return;

                // Don't start carousel swipe if touching control buttons
                const target = e.target;
                const isOnControlBtn = target.closest('.model-control-btn') || target.closest('.model-control-overlay');

                if (isOnControlBtn) {
                    itemsIsDragging = false;
                    return;
                }

                // If touching canvas, check if touching a model
                if (target.tagName === 'CANVAS' && allLoadedModels.length > 0) {
                    const touch = e.changedTouches[0];
                    const clickedModel = getClickedModel(touch.clientX, touch.clientY, target);
                    if (clickedModel) {
                        // Touching a model - don't swipe carousel
                        itemsIsDragging = false;
                        return;
                    }
                }

                itemsPhotoTouchStartX = e.changedTouches[0].screenX;
                itemsIsDragging = true;
                itemsCurrentTranslateX = 0;
                const track = document.getElementById('items-carousel-track');
                if (track) {
                    track.style.transition = 'none';
                }
            }

            function handleItemsTouchMove(e) {
                if (!itemsIsDragging || itemsIsAnimating) return;
                const currentX = e.changedTouches[0].screenX;
                itemsCurrentTranslateX = currentX - itemsPhotoTouchStartX;

                const track = document.getElementById('items-carousel-track');
                if (track) {
                    const photos = areaPhotos[currentArea] || [];
                    const isAtStart = currentItemsPhotoIndex === 0 && itemsCurrentTranslateX > 0;
                    const isAtEnd = currentItemsPhotoIndex === photos.length - 1 && itemsCurrentTranslateX < 0;

                    if (isAtStart || isAtEnd) {
                        track.style.transform = `translateX(${itemsCurrentTranslateX * 0.3}px)`;
                    } else {
                        track.style.transform = `translateX(${itemsCurrentTranslateX}px)`;
                    }
                }
            }

            function handleItemsTouchEnd(e) {
                if (!itemsIsDragging || itemsIsAnimating) return;
                itemsIsDragging = false;
                itemsPhotoTouchEndX = e.changedTouches[0].screenX;

                const track = document.getElementById('items-carousel-track');
                const swipeThreshold = 30;
                const diff = itemsPhotoTouchStartX - itemsPhotoTouchEndX;
                const photos = areaPhotos[currentArea] || [];
                const containerWidth = document.getElementById('items-photos-carousel-container').offsetWidth;
                const gap = 10;

                if (Math.abs(diff) > swipeThreshold) {
                    itemsIsAnimating = true;
                    if (diff > 0 && currentItemsPhotoIndex < photos.length - 1) {
                        if (track) {
                            track.style.transition = 'transform 0.25s ease-out';
                            track.style.transform = `translateX(-${containerWidth + gap}px)`;
                            setTimeout(() => {
                                currentItemsPhotoIndex++;
                                renderItemsPhotosGrid();
                                itemsIsAnimating = false;
                            }, 250);
                        }
                    } else if (diff < 0 && currentItemsPhotoIndex > 0) {
                        if (track) {
                            track.style.transition = 'transform 0.25s ease-out';
                            track.style.transform = `translateX(${containerWidth + gap}px)`;
                            setTimeout(() => {
                                currentItemsPhotoIndex--;
                                renderItemsPhotosGrid();
                                itemsIsAnimating = false;
                            }, 250);
                        }
                    } else {
                        if (track) {
                            track.style.transition = 'transform 0.2s ease-out';
                            track.style.transform = 'translateX(0)';
                        }
                        itemsIsAnimating = false;
                    }
                } else {
                    if (track) {
                        track.style.transition = 'transform 0.2s ease-out';
                        track.style.transform = 'translateX(0)';
                    }
                }
            }

            function prevItemsPhoto() {
                const photos = areaPhotos[currentArea] || [];
                if (itemsIsAnimating || currentItemsPhotoIndex <= 0) return;

                const track = document.getElementById('items-carousel-track');
                const container = document.getElementById('items-photos-carousel-container');
                if (!track || !container) return;

                const containerWidth = container.offsetWidth;
                const gap = 10;

                itemsIsAnimating = true;
                track.style.transition = 'transform 0.25s ease-out';
                track.style.transform = `translateX(${containerWidth + gap}px)`;

                setTimeout(() => {
                    currentItemsPhotoIndex--;
                    renderItemsPhotosGrid('prev');
                    itemsIsAnimating = false;
                }, 250);
            }

            function nextItemsPhoto() {
                const photos = areaPhotos[currentArea] || [];
                if (itemsIsAnimating || currentItemsPhotoIndex >= photos.length - 1) return;

                const track = document.getElementById('items-carousel-track');
                const container = document.getElementById('items-photos-carousel-container');
                if (!track || !container) return;

                const containerWidth = container.offsetWidth;
                const gap = 10;

                itemsIsAnimating = true;
                track.style.transition = 'transform 0.25s ease-out';
                track.style.transform = `translateX(-${containerWidth + gap}px)`;

                setTimeout(() => {
                    currentItemsPhotoIndex++;
                    renderItemsPhotosGrid('next');
                    itemsIsAnimating = false;
                }, 250);
            }

            function captureItemsPhoto() {
                hapticFeedback();
                playShutterSound();

                const video = document.getElementById('items-camera-preview');
                const canvas = document.getElementById('items-camera-canvas');

                if (!video || !canvas || !itemsCameraStream) return;

                const ctx = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0);

                const photoData = canvas.toDataURL('image/jpeg', 0.8);

                if (!areaPhotos[currentArea]) {
                    areaPhotos[currentArea] = [];
                }
                areaPhotos[currentArea].push(photoData);
                currentItemsPhotoIndex = areaPhotos[currentArea].length - 1;

                renderItemsPhotosGrid();
                updateItemsThumbnail();
                updateAreaCarousel(currentArea);
                saveStagingSession();
            }

            function handleItemsPhotoUpload(event) {
                const files = event.target.files;
                if (!files || files.length === 0) return;

                if (!areaPhotos[currentArea]) {
                    areaPhotos[currentArea] = [];
                }

                // Track how many files are being processed
                let filesProcessed = 0;
                const totalFiles = files.length;

                Array.from(files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Compress the image using canvas
                        const img = new Image();
                        img.onload = function() {
                            const canvas = document.createElement('canvas');
                            const ctx = canvas.getContext('2d');

                            // Resize if image is too large (max 1920px on longest side)
                            const maxSize = 1920;
                            let width = img.width;
                            let height = img.height;

                            if (width > maxSize || height > maxSize) {
                                if (width > height) {
                                    height = Math.round(height * maxSize / width);
                                    width = maxSize;
                                } else {
                                    width = Math.round(width * maxSize / height);
                                    height = maxSize;
                                }
                            }

                            canvas.width = width;
                            canvas.height = height;
                            ctx.drawImage(img, 0, 0, width, height);

                            // Compress to JPEG with 0.8 quality (same as camera photos)
                            const compressedData = canvas.toDataURL('image/jpeg', 0.8);

                            areaPhotos[currentArea].push(compressedData);
                            currentItemsPhotoIndex = areaPhotos[currentArea].length - 1;
                            renderItemsPhotosGrid();
                            updateItemsThumbnail();
                            updateAreaCarousel(currentArea);

                            // Only save after ALL files have been processed
                            filesProcessed++;
                            if (filesProcessed === totalFiles) {
                                saveStagingSession();
                            }
                        };
                        img.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                });

                event.target.value = '';
            }

            function initItemsDragAndDrop() {
                const isMobile = window.innerWidth <= 767;
                if (isMobile) return; // Only enable on desktop

                // Check if already initialized to prevent duplicate event listeners
                if (itemsDragDropInitialized) return;

                const dropZone = document.getElementById('items-photos-section');
                if (!dropZone) return;

                function preventDefaults(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }

                function handleDragEnter(e) {
                    preventDefaults(e);
                    // Check if it's a 3D item drag (don't show file drop zone)
                    if (e.dataTransfer.types.includes('application/x-item-3d')) {
                        dropZone.classList.add('drag-over-3d');
                    } else {
                        dropZone.classList.add('drag-over');
                    }
                }

                function handleDragOver(e) {
                    preventDefaults(e);
                    // Check if it's a 3D item drag
                    if (e.dataTransfer.types.includes('application/x-item-3d')) {
                        dropZone.classList.add('drag-over-3d');
                        e.dataTransfer.dropEffect = 'copy';
                    } else {
                        dropZone.classList.add('drag-over');
                    }
                }

                function handleDragLeave(e) {
                    preventDefaults(e);
                    dropZone.classList.remove('drag-over');
                    dropZone.classList.remove('drag-over-3d');
                }

                async function handleDrop(e) {
                    preventDefaults(e);
                    dropZone.classList.remove('drag-over');
                    dropZone.classList.remove('drag-over-3d');

                    const dt = e.dataTransfer;

                    // Check if it's a 3D item drop
                    const itemDataStr = dt.getData('application/x-item-3d');
                    if (itemDataStr) {
                        const itemData = JSON.parse(itemDataStr);

                        // Check if we have a photo to use as background
                        const photos = areaPhotos[currentArea] || [];
                        if (photos.length === 0) {
                            alert('Please add a photo first before dropping 3D models.');
                            return;
                        }

                        // Get drop position relative to carousel container
                        const container = document.getElementById('items-photos-carousel-container');
                        const rect = container ? container.getBoundingClientRect() : null;
                        let dropX = 0, dropY = 0;
                        if (rect) {
                            // Convert to normalized coordinates (-1 to 1)
                            dropX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                            dropY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
                        }

                        // Initialize or add to 3D scene
                        if (current3DPhotoIndex !== currentItemsPhotoIndex) {
                            await initPhoto3DScene(currentItemsPhotoIndex, itemData, dropX, dropY);
                        } else {
                            // Add another model to existing scene
                            await loadGLTFModelOnPhoto(itemData, dropX, dropY);
                        }
                        return;
                    }

                    // Handle file drops
                    const files = dt.files;
                    if (!files || files.length === 0) return;

                    // Initialize photos array for this area if not exists
                    if (!areaPhotos[currentArea]) {
                        areaPhotos[currentArea] = [];
                    }

                    // Filter to only image files and track processing
                    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
                    if (imageFiles.length === 0) return;

                    let filesProcessed = 0;
                    const totalFiles = imageFiles.length;

                    // Process files same as file input with compression
                    imageFiles.forEach(file => {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            // Compress the image using canvas
                            const img = new Image();
                            img.onload = function() {
                                const canvas = document.createElement('canvas');
                                const ctx = canvas.getContext('2d');

                                // Resize if image is too large (max 1920px on longest side)
                                const maxSize = 1920;
                                let width = img.width;
                                let height = img.height;

                                if (width > maxSize || height > maxSize) {
                                    if (width > height) {
                                        height = Math.round(height * maxSize / width);
                                        width = maxSize;
                                    } else {
                                        width = Math.round(width * maxSize / height);
                                        height = maxSize;
                                    }
                                }

                                canvas.width = width;
                                canvas.height = height;
                                ctx.drawImage(img, 0, 0, width, height);

                                // Compress to JPEG with 0.8 quality (same as camera photos)
                                const compressedData = canvas.toDataURL('image/jpeg', 0.8);

                                areaPhotos[currentArea].push(compressedData);
                                currentItemsPhotoIndex = areaPhotos[currentArea].length - 1;
                                renderItemsPhotosGrid();
                                updateItemsThumbnail();
                                updateAreaCarousel(currentArea);

                                // Only save after ALL files have been processed
                                filesProcessed++;
                                if (filesProcessed === totalFiles) {
                                    saveStagingSession();
                                }
                            };
                            img.src = e.target.result;
                        };
                        reader.readAsDataURL(file);
                    });
                }

                // Add event listeners
                dropZone.addEventListener('dragenter', handleDragEnter, false);
                dropZone.addEventListener('dragover', handleDragOver, false);
                dropZone.addEventListener('dragleave', handleDragLeave, false);
                dropZone.addEventListener('drop', handleDrop, false);

                // Mark as initialized
                itemsDragDropInitialized = true;
            }

            function rotateItemsPhoto(index) {
                hapticFeedback();
                if (!areaPhotos[currentArea] || !areaPhotos[currentArea][index]) return;

                const img = new Image();
                img.src = areaPhotos[currentArea][index];
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    canvas.width = img.height;
                    canvas.height = img.width;

                    ctx.translate(0, canvas.height);
                    ctx.rotate(-90 * Math.PI / 180);
                    ctx.drawImage(img, 0, 0);

                    areaPhotos[currentArea][index] = canvas.toDataURL('image/jpeg', 0.8);
                    renderItemsPhotosGrid();
                    updateAreaCarousel(currentArea);
                    saveStagingSession();
                };
            }

            function removeItemsPhoto(index) {
                hapticFeedback();
                if (!areaPhotos[currentArea]) return;

                areaPhotos[currentArea].splice(index, 1);

                if (currentItemsPhotoIndex >= areaPhotos[currentArea].length) {
                    currentItemsPhotoIndex = Math.max(0, areaPhotos[currentArea].length - 1);
                }

                renderItemsPhotosGrid();
                updateItemsThumbnail();
                updateAreaCarousel(currentArea);
                saveStagingSession();
            }

            function updateItemsThumbnail() {
                const thumbnail = document.getElementById('items-photo-thumbnail-preview');
                const badge = document.getElementById('items-photo-count-badge');
                if (!thumbnail) return;

                const photos = areaPhotos[currentArea] || [];
                if (photos.length > 0) {
                    thumbnail.style.backgroundImage = `url(${photos[photos.length - 1]})`;
                    thumbnail.classList.remove('hidden');
                    if (badge) {
                        badge.textContent = photos.length;
                        badge.classList.remove('hidden');
                    }
                } else {
                    thumbnail.style.backgroundImage = '';
                    thumbnail.classList.add('hidden');
                    if (badge) {
                        badge.classList.add('hidden');
                    }
                }
            }

            function scrollToItemsPhotosCarousel() {
                const carousel = document.getElementById('items-photos-preview-grid');
                if (carousel) {
                    carousel.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }

            function scrollToItemsCamera() {
                const cameraSection = document.getElementById('items-camera-section');
                const carouselWrapper = document.getElementById('items-photos-preview-grid');
                if (cameraSection && carouselWrapper) {
                    // Hide carousel, show camera inline
                    carouselWrapper.style.display = 'none';
                    cameraSection.style.display = 'block';
                    startItemsCamera();
                    // Scroll to top of items modal
                    const itemsPhotosSection = document.getElementById('items-photos-section');
                    if (itemsPhotosSection) {
                        itemsPhotosSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            }

            function closeCameraView() {
                const cameraSection = document.getElementById('items-camera-section');
                const carouselWrapper = document.getElementById('items-photos-preview-grid');
                if (cameraSection && carouselWrapper) {
                    cameraSection.style.display = 'none';
                    carouselWrapper.style.display = 'block';
                    stopItemsCamera();
                }
            }

            function openPhotosGallery() {
                hapticFeedback();
                const modal = document.getElementById('photos-gallery-modal');
                const grid = document.getElementById('photos-gallery-grid');
                if (!modal || !grid) return;

                const photos = areaPhotos[currentArea] || [];
                if (photos.length === 0) return;

                // Render photo grid
                grid.innerHTML = photos.map((photo, index) => `
                    <div class="photos-gallery-item">
                        <img src="${photo}" alt="Photo ${index + 1}">
                        <button class="photos-gallery-delete-btn" onclick="deletePhotoFromGallery(${index})">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                            </svg>
                        </button>
                    </div>
                `).join('');

                modal.classList.remove('hidden');
            }

            function closePhotosGallery() {
                hapticFeedback();
                const modal = document.getElementById('photos-gallery-modal');
                if (modal) {
                    modal.classList.add('hidden');
                }
            }

            function deletePhotoFromGallery(index) {
                hapticFeedback();
                if (!areaPhotos[currentArea]) return;

                if (confirm('Delete this photo?')) {
                    areaPhotos[currentArea].splice(index, 1);

                    if (currentItemsPhotoIndex >= areaPhotos[currentArea].length) {
                        currentItemsPhotoIndex = Math.max(0, areaPhotos[currentArea].length - 1);
                    }

                    // Refresh gallery
                    if (areaPhotos[currentArea].length === 0) {
                        closePhotosGallery();
                    } else {
                        openPhotosGallery();
                    }

                    // Update other UI elements
                    renderItemsPhotosGrid();
                    updateItemsThumbnail();
                    updateAreaCarousel(currentArea);
                    saveStagingSession();
                }
            }

            let areaPhotos = {}; // Store photos per area

            async function cleanupOrphanedPhotos() {
                // Collect all valid photo URLs from all areas
                const allValidUrls = [];
                for (const area in areaPhotos) {
                    const photos = areaPhotos[area] || [];
                    photos.forEach(url => {
                        if (url.startsWith('/static/')) {
                            allValidUrls.push(url);
                        }
                    });
                }

                try {
                    await fetch('/api/staging-photos/cleanup', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ valid_urls: allValidUrls })
                    });
                } catch (e) {
                    console.warn('Cleanup error:', e);
                }
            }

            // Track current index for each area carousel
            const areaCarouselIndices = {};

            function updateAreaCarousel(area) {
                const areaBtn = document.querySelector('.area-btn[data-area="' + area + '"]');
                if (!areaBtn) return;

                const carousel = areaBtn.querySelector('.area-carousel');
                if (!carousel) return;

                const photos = areaPhotos[area] || [];

                if (photos.length === 0) {
                    carousel.classList.remove('has-photos');
                    carousel.innerHTML = '';
                    delete areaCarouselIndices[area];
                    return;
                }

                // Initialize index for this area if not exists
                if (typeof areaCarouselIndices[area] === 'undefined') {
                    areaCarouselIndices[area] = 0;
                }

                const currentIndex = areaCarouselIndices[area];

                // Reset index if out of bounds
                if (currentIndex >= photos.length) {
                    areaCarouselIndices[area] = photos.length - 1;
                }
                if (currentIndex < 0) {
                    areaCarouselIndices[area] = 0;
                }

                renderAreaCarousel(area, areaBtn, carousel);
            }

            function renderAreaCarousel(area, areaBtn, carousel) {
                const photos = areaPhotos[area] || [];
                const currentIndex = areaCarouselIndices[area] || 0;

                // Build slides: prev, current, next
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : null;
                const nextIndex = currentIndex < photos.length - 1 ? currentIndex + 1 : null;

                let slidesHTML = '';

                // Previous slide
                if (prevIndex !== null) {
                    slidesHTML += `<div class="area-carousel-slide area-slide-prev"><img src="${photos[prevIndex]}" alt="Photo ${prevIndex + 1}"></div>`;
                }

                // Current slide
                slidesHTML += `<div class="area-carousel-slide area-slide-current"><img src="${photos[currentIndex]}" alt="Photo ${currentIndex + 1}"></div>`;

                // Next slide
                if (nextIndex !== null) {
                    slidesHTML += `<div class="area-carousel-slide area-slide-next"><img src="${photos[nextIndex]}" alt="Photo ${nextIndex + 1}"></div>`;
                }

                const trackHTML = `<div class="area-carousel-track">${slidesHTML}</div>`;

                // Add arrows for desktop
                const isMobile = window.innerWidth <= 767;
                let arrowsHTML = '';
                if (!isMobile && photos.length > 1) {
                    arrowsHTML = `
                        <button class="area-carousel-arrow area-carousel-prev" data-area="${area}">‹</button>
                        <button class="area-carousel-arrow area-carousel-next" data-area="${area}">›</button>
                    `;
                }

                // Add dots if more than 1 photo
                let dotsHTML = '';
                if (photos.length > 1) {
                    dotsHTML = '<div class="area-carousel-dots">';
                    photos.forEach((_, index) => {
                        dotsHTML += '<span class="area-carousel-dot' + (index === currentIndex ? ' active' : '') + '"></span>';
                    });
                    dotsHTML += '</div>';
                }

                carousel.innerHTML = trackHTML + arrowsHTML + dotsHTML;
                carousel.classList.add('has-photos');

                // Add touch event listeners for swipe
                const track = carousel.querySelector('.area-carousel-track');
                let isAnimating = false;
                let isDragging = false;

                if (track) {
                    let touchStartX = 0;
                    let currentTranslateX = 0;

                    function handleTouchStart(e) {
                        if (isAnimating) return;
                        touchStartX = e.touches ? e.touches[0].clientX : e.clientX;
                        isDragging = true;
                        currentTranslateX = 0;
                        track.style.transition = 'none';
                    }

                    function handleTouchMove(e) {
                        if (!isDragging || isAnimating) return;
                        const currentX = e.touches ? e.touches[0].clientX : e.clientX;
                        currentTranslateX = currentX - touchStartX;

                        const isAtStart = currentIndex === 0 && currentTranslateX > 0;
                        const isAtEnd = currentIndex === photos.length - 1 && currentTranslateX < 0;

                        if (isAtStart || isAtEnd) {
                            // Apply resistance at edges
                            track.style.transform = `translateX(${currentTranslateX * 0.3}px)`;
                        } else {
                            track.style.transform = `translateX(${currentTranslateX}px)`;
                        }
                    }

                    function handleTouchEnd(e) {
                        if (!isDragging || isAnimating) return;
                        isDragging = false;
                        const touchEndX = e.changedTouches ? e.changedTouches[0].clientX : e.clientX;

                        const swipeThreshold = 30;
                        const diff = touchStartX - touchEndX;
                        const containerWidth = carousel.offsetWidth;

                        if (Math.abs(diff) > swipeThreshold) {
                            isAnimating = true;
                            if (diff > 0 && currentIndex < photos.length - 1) {
                                // Swipe left - next photo only
                                track.style.transition = 'transform 0.25s ease-out';
                                track.style.transform = `translateX(-${containerWidth}px)`;
                                setTimeout(() => {
                                    areaCarouselIndices[area]++;
                                    renderAreaCarousel(area, areaBtn, carousel);
                                    isAnimating = false;
                                }, 250);
                            } else if (diff < 0 && currentIndex > 0) {
                                // Swipe right - prev photo only
                                track.style.transition = 'transform 0.25s ease-out';
                                track.style.transform = `translateX(${containerWidth}px)`;
                                setTimeout(() => {
                                    areaCarouselIndices[area]--;
                                    renderAreaCarousel(area, areaBtn, carousel);
                                    isAnimating = false;
                                }, 250);
                            } else {
                                // Snap back at edges
                                track.style.transition = 'transform 0.25s ease-out';
                                track.style.transform = 'translateX(0)';
                                isAnimating = false;
                            }
                        } else {
                            // Snap back if not enough swipe - this is a tap!
                            track.style.transition = 'transform 0.25s ease-out';
                            track.style.transform = 'translateX(0)';
                            isAnimating = false;

                            // Open items modal on tap (small movement)
                            if (Math.abs(diff) < 10) {
                                const itemsBtn = areaBtn.querySelector('.area-action-btn');
                                if (itemsBtn) {
                                    openItemsModal(e, itemsBtn);
                                }
                            }
                        }
                    }

                    // Touch events
                    track.addEventListener('touchstart', handleTouchStart, { passive: true });
                    track.addEventListener('touchmove', handleTouchMove, { passive: true });
                    track.addEventListener('touchend', handleTouchEnd, { passive: false });

                    // Mouse events (for desktop/testing)
                    track.addEventListener('mousedown', (e) => {
                        handleTouchStart(e);
                    });

                    track.addEventListener('mousemove', (e) => {
                        if (isDragging) {
                            e.preventDefault(); // Prevent text selection during drag
                            handleTouchMove(e);
                        }
                    });

                    track.addEventListener('mouseup', handleTouchEnd);
                    track.addEventListener('mouseleave', (e) => {
                        if (isDragging) {
                            handleTouchEnd(e);
                        }
                    });
                }

                // Add arrow click handlers for desktop
                const prevArrow = carousel.querySelector('.area-carousel-prev');
                const nextArrow = carousel.querySelector('.area-carousel-next');

                if (prevArrow) {
                    prevArrow.onclick = function(e) {
                        e.stopPropagation();
                        if (currentIndex > 0 && !isAnimating) {
                            isAnimating = true;
                            const track = carousel.querySelector('.area-carousel-track');
                            const containerWidth = carousel.offsetWidth;
                            track.style.transition = 'transform 0.25s ease-out';
                            track.style.transform = `translateX(${containerWidth}px)`;
                            setTimeout(() => {
                                areaCarouselIndices[area]--;
                                renderAreaCarousel(area, areaBtn, carousel);
                                isAnimating = false;
                            }, 250);
                        }
                    };
                }

                if (nextArrow) {
                    nextArrow.onclick = function(e) {
                        e.stopPropagation();
                        if (currentIndex < photos.length - 1 && !isAnimating) {
                            isAnimating = true;
                            const track = carousel.querySelector('.area-carousel-track');
                            const containerWidth = carousel.offsetWidth;
                            track.style.transition = 'transform 0.25s ease-out';
                            track.style.transform = `translateX(-${containerWidth}px)`;
                            setTimeout(() => {
                                areaCarouselIndices[area]++;
                                renderAreaCarousel(area, areaBtn, carousel);
                                isAnimating = false;
                            }, 250);
                        }
                    };
                }

                // Add click listener to open items modal
                carousel.onclick = function(e) {
                    if (!isDragging) {
                        e.stopPropagation();
                        const itemsBtn = areaBtn.querySelector('.area-action-btn');
                        if (itemsBtn) {
                            openItemsModal(e, itemsBtn);
                        }
                    }
                };
            }

            function loadAreaItems(area) {
                // Use saved items if exists, otherwise load defaults from CSV data
                let itemsToLoad = areaItemsData[area];
                if (!itemsToLoad) {
                    itemsToLoad = getDefaultItems(area) || {};
                }

                // Get saved selected items for this area
                const savedSelectedItems = areaSelectedItems[area] || {};

                // Reset all items first
                document.querySelectorAll('.item-btn').forEach(btn => {
                    const itemId = btn.getAttribute('data-item');
                    const itemName = btn.getAttribute('data-name');
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

                    // Restore selected item image if exists
                    const selectedItem = savedSelectedItems[itemName];
                    if (selectedItem && selectedItem.imageUrl) {
                        const emojiDiv = btn.querySelector('.item-emoji');
                        if (emojiDiv) {
                            let imgHtml = `<img src="${selectedItem.imageUrl}" alt="${selectedItem.itemName}">`;
                            if (selectedItem.model3d) {
                                imgHtml += `<div class="item-3d-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg></div>`;
                            }
                            emojiDiv.innerHTML = imgHtml;
                        }
                        btn.classList.add('has-selected-image');

                        // Update name span
                        const nameSpan = btn.querySelector('.item-name');
                        if (nameSpan) {
                            nameSpan.textContent = selectedItem.itemName;
                        }

                        // Store on button
                        btn.dataset.selectedImage = selectedItem.imageUrl;
                        btn.dataset.selectedName = selectedItem.itemName;
                        if (selectedItem.model3d) {
                            btn.dataset.model3d = selectedItem.model3d;
                            btn.draggable = true;
                        } else {
                            btn.draggable = false;
                        }
                        // Store dimensions and front rotation
                        btn.dataset.width = selectedItem.width || 0;
                        btn.dataset.depth = selectedItem.depth || 0;
                        btn.dataset.height = selectedItem.height || 0;
                        btn.dataset.frontRotation = selectedItem.frontRotation ?? -Math.PI/2;
                    } else {
                        // Reset draggable, dimensions and frontRotation if no selected item
                        btn.draggable = false;
                        delete btn.dataset.model3d;
                        btn.dataset.width = 0;
                        btn.dataset.depth = 0;
                        btn.dataset.height = 0;
                        btn.dataset.frontRotation = -Math.PI/2;
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

                // Save to session storage
                saveStagingSession();
            }

            // Close modal on backdrop click (mobile only - desktop should not close on backdrop click)
            document.addEventListener('click', function(event) {
                const modal = document.getElementById('items-modal');
                const isMobile = window.innerWidth < 768;
                if (event.target === modal && isMobile) {
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
                    const inquiryModal = document.getElementById('inquiry-modal');
                    if (!inquiryModal.classList.contains('hidden')) {
                        closeInquiryModal();
                    }
                }
            });

            // Inquiry Modal Functions
            function openInquiryModal() {
                const { propertyType, propertySize } = getSelections();

                // Populate hidden fields with current staging data
                document.getElementById('inquiry-property-type').value = propertyType || '';
                document.getElementById('inquiry-property-size').value = propertySize || '';

                // Get selected areas
                const selectedAreas = [];
                document.querySelectorAll('.area-btn.selected').forEach(btn => {
                    selectedAreas.push(btn.getAttribute('data-area'));
                });
                document.getElementById('inquiry-selected-areas').value = selectedAreas.join(',');

                // Get selected items
                document.getElementById('inquiry-selected-items').value = typeof areaItemsData !== 'undefined' ? JSON.stringify(areaItemsData) : '{}';

                // Get total fee from banner subtitle
                const bannerSubtitle = document.getElementById('banner-subtitle');
                let totalFee = '$0';
                if (bannerSubtitle && bannerSubtitle.textContent.includes('$')) {
                    totalFee = bannerSubtitle.textContent;
                }
                document.getElementById('inquiry-total-fee').value = totalFee;

                // Show modal
                document.getElementById('inquiry-modal').classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }

            function closeInquiryModal() {
                document.getElementById('inquiry-modal').classList.add('hidden');
                document.body.style.overflow = '';
            }

            // 2D Image Preview Modal Functions
            function show2DImageModal() {
                if (!currentLoadedModel) return;

                // Get the image URL from the model's userData
                const imageUrl = currentLoadedModel.userData.imageUrl;
                if (!imageUrl) {
                    alert('No 2D image available for this model');
                    return;
                }

                // Set the image source
                const modalImage = document.getElementById('modal-2d-image');
                if (modalImage) {
                    modalImage.src = imageUrl;
                }

                // Show the modal
                const modal = document.getElementById('image-preview-modal');
                if (modal) {
                    modal.classList.remove('hidden');
                    document.body.style.overflow = 'hidden';
                }
            }

            function close2DImageModal() {
                const modal = document.getElementById('image-preview-modal');
                if (modal) {
                    modal.classList.add('hidden');
                    document.body.style.overflow = '';
                }
            }

            // Close inquiry modal on backdrop click
            document.getElementById('inquiry-modal').addEventListener('click', function(event) {
                if (event.target === this) {
                    closeInquiryModal();
                }
            });

            // Format phone number as user types
            document.getElementById('inquiry-phone').addEventListener('input', function(e) {
                let value = e.target.value.replace(/\\D/g, '');
                if (value.length > 10) value = value.slice(0, 10);
                if (value.length >= 6) {
                    value = '(' + value.slice(0, 3) + ') ' + value.slice(3, 6) + '-' + value.slice(6);
                } else if (value.length >= 3) {
                    value = '(' + value.slice(0, 3) + ') ' + value.slice(3);
                }
                e.target.value = value;
            });

            // Submit inquiry form
            async function submitInquiry() {
                const form = document.getElementById('inquiry-form');
                const submitBtn = document.querySelector('.inquiry-submit-btn');

                // Get form values
                const stagingDate = document.getElementById('inquiry-staging-date').value || 'Flexible';
                const propertyAddress = document.getElementById('inquiry-property-address').value;
                const firstName = document.getElementById('inquiry-first-name').value;
                const lastName = document.getElementById('inquiry-last-name').value;
                const email = document.getElementById('inquiry-email').value;
                const phone = document.getElementById('inquiry-phone').value;
                const specialRequests = document.getElementById('inquiry-special-requests').value;

                // Get add-ons
                const addons = [];
                if (document.getElementById('inquiry-addon-photos').checked) addons.push('Professional Photography');
                if (document.getElementById('inquiry-addon-consultation').checked) addons.push('Staging Consultation');

                // Get staging data from hidden fields
                const propertyType = document.getElementById('inquiry-property-type').value;
                const propertySize = document.getElementById('inquiry-property-size').value;
                const selectedAreas = document.getElementById('inquiry-selected-areas').value;
                const selectedItems = document.getElementById('inquiry-selected-items').value;
                const totalFee = document.getElementById('inquiry-total-fee').value;

                // Validate required fields
                if (!propertyAddress || !firstName || !lastName || !email || !phone) {
                    alert('Please fill in all required fields.');
                    return;
                }

                // Email validation
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                if (!emailRegex.test(email)) {
                    alert('Please enter a valid email address.');
                    return;
                }

                // Disable button and show loading state
                submitBtn.disabled = true;
                submitBtn.textContent = 'Submitting...';

                try {
                    const response = await fetch('/api/staging-inquiry', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            stagingDate,
                            propertyAddress,
                            firstName,
                            lastName,
                            email,
                            phone,
                            addons,
                            specialRequests,
                            propertyType,
                            propertySize,
                            selectedAreas,
                            selectedItems,
                            totalFee
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        alert('Thank you! Your staging inquiry has been submitted. We will contact you within 24 hours.');
                        closeInquiryModal();
                        // Clear form
                        form.reset();
                    } else {
                        alert('There was an error submitting your inquiry. Please try again or call us at 1-888-744-4078.');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('There was an error submitting your inquiry. Please try again or call us at 1-888-744-4078.');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit Inquiry';
                }
            }

            // Add touch handlers to Items buttons for mobile
            function initItemsButtonTouchHandlers() {
                document.querySelectorAll('.area-action-btn').forEach(btn => {
                    btn.addEventListener('touchend', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        openItemsModal(e, this);
                    }, { passive: false });
                });
            }

            // Restore session data on page load
            document.addEventListener('DOMContentLoaded', async function() {
                // Initialize touch handlers for Items buttons
                initItemsButtonTouchHandlers();
                // First, try to load from server if logged in
                await loadExistingStagingFromServer();
                // Then restore from session storage
                setTimeout(restoreStagingSession, 50);
            });

            // Empty Room - Remove furniture from background
            async function emptyRoomBackground() {
                const photos = window.itemsPhotos || [];
                if (photos.length === 0 || currentItemsPhotoIndex === null) {
                    alert('No photo available to process');
                    return;
                }

                const currentPhotoSrc = photos[currentItemsPhotoIndex];

                // Show progress modal
                const modal = document.getElementById('empty-room-modal');
                modal.classList.add('active');

                const statusEl = document.getElementById('empty-room-status');
                const progressText = document.getElementById('progress-text');
                const progressFill = document.getElementById('progress-circle-fill');
                const creditsEl = document.getElementById('credits-remaining');

                statusEl.textContent = 'Fetching credits...';
                progressText.textContent = '0%';
                progressFill.style.strokeDashoffset = '408.4';

                try {
                    // Fetch remaining credits
                    const creditsResponse = await fetch('/api/decor8-credits');
                    const creditsData = await creditsResponse.json();

                    if (creditsData.credits !== undefined) {
                        creditsEl.textContent = creditsData.credits;
                    } else {
                        creditsEl.textContent = 'Unknown';
                    }

                    // Convert image to base64
                    statusEl.textContent = 'Preparing image...';
                    updateProgress(10);

                    const response = await fetch(currentPhotoSrc);
                    const blob = await response.blob();
                    const reader = new FileReader();

                    const base64Image = await new Promise((resolve, reject) => {
                        reader.onloadend = () => resolve(reader.result);
                        reader.onerror = reject;
                        reader.readAsDataURL(blob);
                    });

                    statusEl.textContent = 'Removing furniture... (1-2 minutes)';
                    updateProgress(20);

                    // Call API to remove furniture
                    const inpaintResponse = await fetch('/api/test-inpainting', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            image: base64Image,
                            method: 5
                        })
                    });

                    updateProgress(90);

                    const result = await inpaintResponse.json();

                    if (result.success && result.result.result_base64) {
                        statusEl.textContent = 'Adding to carousel...';
                        updateProgress(95);

                        // Add the empty room image to photos array
                        const emptyRoomImage = result.result.result_base64;
                        window.itemsPhotos.push(emptyRoomImage);

                        // Navigate to the new image
                        currentItemsPhotoIndex = window.itemsPhotos.length - 1;
                        updateItemsPhotoDisplay();

                        statusEl.textContent = 'Complete!';
                        updateProgress(100);

                        // Close modal after success
                        setTimeout(() => {
                            modal.classList.remove('active');
                        }, 1500);
                    } else {
                        throw new Error(result.error || 'Failed to remove furniture');
                    }
                } catch (error) {
                    console.error('Empty room error:', error);
                    statusEl.textContent = 'Error: ' + error.message;
                    statusEl.style.color = '#dc2626';

                    // Close modal after error
                    setTimeout(() => {
                        modal.classList.remove('active');
                        alert('Failed to remove furniture: ' + error.message);
                    }, 2000);
                }
            }

            function updateProgress(percent) {
                const progressText = document.getElementById('progress-text');
                const progressFill = document.getElementById('progress-circle-fill');

                progressText.textContent = Math.round(percent) + '%';

                // Calculate stroke-dashoffset (408.4 is full circle, 0 is complete)
                const offset = 408.4 - (408.4 * percent / 100);
                progressFill.style.strokeDashoffset = offset;
            }
        """),
        # Empty Room Progress Modal
        Div(
            Div(
                H3("Removing Furniture..."),
                Div(
                    Div(
                        f'<svg class="progress-circle" width="150" height="150" viewBox="0 0 150 150">',
                        f'<circle class="progress-circle-bg" cx="75" cy="75" r="65"></circle>',
                        f'<circle class="progress-circle-fill" cx="75" cy="75" r="65" '
                        f'stroke-dasharray="408.4" stroke-dashoffset="408.4" id="progress-circle-fill"></circle>',
                        f'</svg>',
                        NotStr=True
                    ),
                    Div("0%", id="progress-text", cls="progress-text"),
                    cls="progress-circle-container"
                ),
                Div("Initializing...", id="empty-room-status", cls="empty-room-status"),
                Div(
                    Div("Remaining Credits: ", Strong("Loading...", id="credits-remaining")),
                    cls="credits-info"
                ),
                cls="empty-room-modal-content"
            ),
            id="empty-room-modal",
            cls="empty-room-modal"
        ),
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
        border-width: 2px;
        background: var(--bg-secondary);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    [data-theme="dark"] .property-btn.selected {
        border-color: #fff;
        box-shadow: 0 4px 16px rgba(255, 255, 255, 0.08);
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

    /* Area button specific styles - mobile first */
    .area-btn {
        padding-top: 10px;
        padding-bottom: 10px;
        min-height: auto;
        justify-content: flex-start;
    }

    /* Taller height when area has photos */
    .area-btn:has(.area-carousel.has-photos) {
        min-height: 220px;
        padding-bottom: 70px;
    }

    /* Taller height when selected (for buttons) */
    .area-btn.selected {
        min-height: 120px;
        padding-bottom: 70px;
    }

    .area-btn.selected:has(.area-carousel.has-photos) {
        min-height: 220px;
    }

    /* Area button text styles */
    .area-name {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-primary);
        line-height: 1.2;
        text-align: center;
        margin-bottom: 2px;
    }

    .area-price {
        font-size: 12px;
        font-weight: 500;
        color: var(--color-secondary);
        margin-top: 2px;
    }

    .area-btn.selected .area-price {
        color: var(--color-primary);
    }

    /* Area Photo Carousel */
    .area-carousel {
        display: none;
        width: calc(100% - 16px);
        margin: 8px auto 0;
        position: relative;
        flex-shrink: 0;
        overflow: hidden;
        border-radius: 8px;
    }

    .area-carousel.has-photos {
        display: block;
    }

    .area-carousel-track {
        display: flex;
        position: relative;
        width: 100%;
        aspect-ratio: 1/1;
        touch-action: pan-y;
    }

    .area-carousel-slide {
        position: absolute;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border-radius: 8px;
        overflow: hidden;
    }

    .area-carousel-slide.area-slide-prev {
        left: -100%;
    }

    .area-carousel-slide.area-slide-current {
        left: 0;
    }

    .area-carousel-slide.area-slide-next {
        left: 100%;
    }

    .area-carousel-slide img {
        max-width: 100%;
        max-height: 100%;
        height: auto;
        width: auto;
        object-fit: contain;
    }

    .area-carousel-dots {
        display: flex;
        justify-content: center;
        gap: 4px;
        margin-top: 6px;
        margin-bottom: 10px;
    }

    .area-carousel-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--border-color);
        cursor: pointer;
        transition: background 0.2s;
    }

    .area-carousel-dot.active {
        background: var(--color-primary);
    }

    /* Area Carousel Arrows - hidden on mobile, shown on desktop */
    .area-carousel-arrow {
        display: none;
        position: absolute;
        top: 45%;
        transform: translateY(-50%);
        width: 36px;
        height: 36px;
        border: none;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        font-size: 24px;
        cursor: pointer;
        z-index: 10;
        transition: all 0.2s ease;
        align-items: center;
        justify-content: center;
    }

    .area-carousel-arrow:hover {
        background: rgba(0, 0, 0, 0.7);
    }

    .area-btn:hover .area-carousel-arrow,
    .area-carousel:hover .area-carousel-arrow {
        display: flex;
    }

    .area-carousel-prev {
        left: 8px;
    }

    .area-carousel-next {
        right: 8px;
    }

    /* Items button full width when carousel has photos */
    .area-carousel.has-photos + .area-actions {
        display: flex;
    }

    .area-carousel.has-photos + .area-actions .area-action-btn {
        width: 100%;
    }

    /* Area Action Buttons Container */
    .area-actions {
        display: none;
        gap: 8px;
        margin-top: auto;
        width: 100%;
        padding: 0 8px 8px 8px;
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        box-sizing: border-box;
        z-index: 10;
    }

    .area-btn.selected .area-actions {
        display: flex;
    }

    .area-action-btn {
        width: 100%;
        font-size: 13px;
        font-weight: 600;
        padding: 10px 12px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1);
        color: var(--color-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        -webkit-tap-highlight-color: rgba(76, 175, 80, 0.3);
        user-select: none;
        -webkit-user-select: none;
    }

    .area-action-btn-content {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        min-width: 70px;
        justify-content: flex-start;
    }

    .area-action-btn svg {
        width: 14px;
        height: 14px;
        flex-shrink: 0;
    }

    .area-actions {
        display: none;
        flex-direction: column;
        gap: 8px;
        margin-top: auto;
        width: 100%;
        padding: 0 8px 8px 8px;
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        box-sizing: border-box;
        align-items: stretch;
        z-index: 10;
    }

    [data-theme="light"] .area-action-btn {
        background: rgba(0, 0, 0, 0.06);
    }

    .area-action-btn:hover {
        background: rgba(76, 175, 80, 0.25);
        color: var(--color-primary);
    }

    .area-btn.selected .area-action-btn {
        background: rgba(255, 255, 255, 0.1);
        color: var(--color-primary);
    }

    [data-theme="light"] .area-btn.selected .area-action-btn {
        background: rgba(0, 0, 0, 0.06);
    }

    .area-btn.selected .area-action-btn:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    [data-theme="light"] .area-btn.selected .area-action-btn:hover {
        background: rgba(0, 0, 0, 0.1);
    }

    /* Items Modal */
    .items-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--bg-primary);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
    }

    .items-modal.hidden {
        display: none;
    }

    .items-modal .modal-content {
        max-width: 800px;
        width: 100%;
        height: 100%;
        border-radius: 0;
        border: none;
        box-shadow: none;
        background: var(--bg-primary);
        position: relative;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .items-modal .modal-header {
        padding: 15px;
        flex-shrink: 0;
        z-index: 10;
        border-bottom: none;
    }

    [data-theme="light"] .items-modal .modal-header {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px) saturate(120%);
        -webkit-backdrop-filter: blur(12px) saturate(120%);
    }

    [data-theme="dark"] .items-modal .modal-header {
        background: rgba(26, 26, 26, 0.9);
        backdrop-filter: blur(12px) saturate(120%);
        -webkit-backdrop-filter: blur(12px) saturate(120%);
    }

    .items-modal .modal-body {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 0;
        background: var(--bg-primary);
        overflow: hidden;
    }

    .items-modal .items-photos-section {
        flex-shrink: 0;
        padding: 0;
    }

    .items-modal .items-photos-section .photos-carousel-wrapper {
        width: 100%;
        margin-left: 0;
        margin-right: 0;
        padding: 0;
    }

    .items-modal .items-photos-section .photos-carousel-container {
        width: 100%;
        min-height: 150px;
    }

    @media (min-width: 768px) {
        .items-modal .items-photos-section {
            padding: 0 15px;
            max-width: 800px;
            margin: 0 auto;
        }

        /* Desktop: Full screen modal */
        .items-modal .modal-content {
            max-width: 100%;
            width: 100vw;
            height: 100vh;
        }

        /* Desktop: Constrain modal body content to 800px */
        .items-modal .modal-body {
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }

        .items-modal .modal-header {
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }

        .items-modal .modal-footer {
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
    }

    .items-modal .items-grid-container {
        flex: 1;
        overflow-y: auto;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        padding: 8px;
        padding-bottom: 80px;
    }

    /* Item Select Modal */
    .item-select-modal .modal-body {
        flex: 1;
        overflow-y: auto;
        padding: 8px;
    }

    .item-select-modal .modal-footer {
        display: none !important;
    }

    .item-select-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
    }

    @media (min-width: 768px) {
        .item-select-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }

    .item-select-card {
        aspect-ratio: 1;
        border-radius: 8px;
        overflow: hidden;
        cursor: pointer;
        position: relative;
        background: #ffffff;
        border: 2px solid transparent;
        transition: all 0.2s ease;
    }

    .item-select-card:hover {
        border-color: var(--accent-color);
    }

    .item-select-card.selected {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 2px var(--accent-color);
    }

    .item-select-card img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    .item-select-card .item-select-name {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 4px 6px;
        background: rgba(255, 255, 255, 0.9);
        color: #000000;
        font-size: 10px;
        font-weight: 500;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .item-3d-icon-container {
        position: absolute;
        top: 6px;
        right: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
        z-index: 2;
    }

    /* 3D icon in select modal - top left */
    .item-3d-icon-left {
        position: absolute;
        top: 6px;
        left: 6px;
        width: 28px;
        height: 28px;
        background: none;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000000;
        z-index: 2;
    }

    .item-3d-icon-left svg {
        width: 18px;
        height: 18px;
        stroke: #000000;
    }

    /* Count label - top right */
    .item-count-label {
        position: absolute;
        top: 6px;
        right: 6px;
        background: #ffffff;
        color: #000000;
        font-size: 12px;
        font-weight: 700;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #000000;
        z-index: 2;
    }

    /* 3D icon in item button - top left */
    .item-btn .item-3d-icon {
        position: absolute;
        top: 4px;
        left: 4px;
        width: 24px;
        height: 24px;
        z-index: 2;
    }

    .item-btn .item-3d-icon svg {
        width: 14px;
        height: 14px;
        stroke: #000000;
    }

    .items-modal .modal-footer {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 800px;
        background: transparent;
        border-top: none;
        padding: 12px 15px;
        z-index: 10;
        align-items: center;
    }

    .items-modal .modal-apply-btn {
        padding: 0 28px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 700;
        height: 45px;
        border: none;
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        transition: all 0.3s ease;
    }

    [data-theme="light"] .items-modal .modal-apply-btn {
        background: rgba(0, 0, 0, 0.06);
        color: #000000;
        border: 2px solid rgba(0, 0, 0, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    [data-theme="light"] .items-modal .modal-apply-btn:active {
        background: rgba(0, 0, 0, 0.15);
        transform: scale(0.98);
    }

    [data-theme="dark"] .items-modal .modal-apply-btn {
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    [data-theme="dark"] .items-modal .modal-apply-btn:active {
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0.98);
    }

    .items-modal .modal-reset-btn,
    .items-modal .modal-clear-btn {
        padding: 0 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        height: 36px;
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
    }

    [data-theme="light"] .items-modal .modal-reset-btn,
    [data-theme="light"] .items-modal .modal-clear-btn {
        background: rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.15);
        color: rgba(0, 0, 0, 0.6);
    }

    [data-theme="dark"] .items-modal .modal-reset-btn,
    [data-theme="dark"] .items-modal .modal-clear-btn {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.6);
    }

    /* Camera Section - hidden by default, inline in modal */
    .camera-section {
        display: none;
        position: relative;
        width: 100%;
        background: #000;
        margin: 0;
        padding: 0;
    }

    @media (max-width: 767px) {
        .upload-section {
            display: none !important;
        }

        /* Disable focus/hover effects on mobile buttons */
        .modal-upload-btn,
        .modal-upload-btn:hover,
        .modal-upload-btn:focus,
        .modal-upload-btn:active {
            background: var(--bg-secondary) !important;
            outline: none !important;
            box-shadow: none !important;
            -webkit-tap-highlight-color: transparent;
        }

        .modal-apply-btn:focus,
        .modal-apply-btn:active {
            outline: none !important;
            box-shadow: none !important;
            -webkit-tap-highlight-color: transparent;
        }

        /* Mobile carousel adjustments */
        .photos-carousel-wrapper {
            width: calc(100% + 30px);
            margin-left: -15px;
            margin-right: -15px;
            padding: 0;
            scroll-snap-align: start;
            scroll-snap-stop: always;
        }

        .photo-carousel-slide {
            cursor: grab;
            touch-action: pan-y pinch-zoom;
        }

        .photo-carousel-slide:active {
            cursor: grabbing;
        }

        .photos-carousel-counter {
            margin-top: 16px;
            padding: 0 15px;
        }
    }

    .camera-preview-container {
        width: 100%;
        aspect-ratio: 3/4;
        background: #000;
        border-radius: 0;
        overflow: hidden;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0;
    }

    .camera-preview {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    .camera-canvas {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    .camera-canvas.hidden {
        display: none;
    }

    /* Photo Thumbnail Preview */
    .photo-thumbnail-preview {
        position: absolute;
        bottom: calc(80px + env(safe-area-inset-bottom, 0px));
        left: 30px;
        width: 50px;
        height: 50px;
        border-radius: 8px;
        border: 3px solid white;
        cursor: pointer;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        opacity: 1;
        z-index: 10;
    }

    .photo-thumbnail-preview.hidden {
        opacity: 0;
        pointer-events: none;
    }

    .photo-thumbnail-preview:active {
        transform: scale(0.9);
    }

    /* Photo Count Badge */
    .photo-count-badge {
        position: absolute;
        top: -8px;
        right: -8px;
        min-width: 24px;
        height: 24px;
        padding: 0 6px;
        background: #dc2626;
        color: white;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #000;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        z-index: 1;
    }

    .photo-count-badge.hidden {
        display: none;
    }

    /* Camera Close Button */
    .camera-close-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        font-size: 32px;
        line-height: 1;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 10;
        padding: 0;
    }

    .camera-close-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: scale(1.1);
    }

    .camera-close-btn:active {
        transform: scale(0.9);
    }

    /* Photos Gallery Modal */
    .photos-gallery-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.95);
        z-index: 10001;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }

    .photos-gallery-modal.hidden {
        display: none;
    }

    .photos-gallery-content {
        width: 100%;
        max-width: 600px;
        max-height: 80vh;
        background: var(--bg-secondary);
        border-radius: 12px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }

    .photos-gallery-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 20px;
        border-bottom: 1px solid var(--border-color);
    }

    .photos-gallery-title {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
    }

    .photos-gallery-close-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--bg-primary);
        color: var(--color-primary);
        border: none;
        font-size: 28px;
        line-height: 1;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        padding: 0;
    }

    .photos-gallery-close-btn:hover {
        background: var(--border-color);
    }

    .photos-gallery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 15px;
        padding: 20px;
        overflow-y: auto;
        max-height: calc(80vh - 70px);
    }

    .photos-gallery-item {
        position: relative;
        aspect-ratio: 1;
        border-radius: 8px;
        overflow: hidden;
        background: var(--bg-primary);
    }

    .photos-gallery-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .photos-gallery-delete-btn {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: rgba(220, 38, 38, 0.9);
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        padding: 0;
    }

    .photos-gallery-delete-btn:hover {
        background: rgba(185, 28, 28, 1);
        transform: scale(1.1);
    }

    .photos-gallery-delete-btn:active {
        transform: scale(0.9);
    }

    @media (max-width: 767px) {
        .photos-gallery-content {
            max-width: 100%;
            max-height: 90vh;
            border-radius: 0;
        }

        .photos-gallery-grid {
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
            padding: 15px;
        }
    }

    /* Shutter Button */
    .shutter-btn {
        position: absolute;
        bottom: calc(80px + env(safe-area-inset-bottom, 0px));
        left: 50%;
        transform: translateX(-50%);
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        border: 4px solid white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
        opacity: 1;
        z-index: 10;
    }

    .shutter-btn.hidden {
        opacity: 0;
        pointer-events: none;
    }

    .shutter-btn:hover {
        background: rgba(255, 255, 255, 0.4);
        transform: translateX(-50%) scale(1.05);
    }

    .shutter-btn:focus {
        outline: none;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
        -webkit-tap-highlight-color: transparent;
    }

    .shutter-btn:active {
        transform: translateX(-50%) scale(0.95);
    }

    .shutter-inner {
        width: 54px;
        height: 54px;
        border-radius: 50%;
        background: white;
        border: none;
        transition: all 0.15s ease;
    }

    .shutter-btn:active .shutter-inner {
        background: #e0e0e0;
    }

    /* Upload Section */
    .upload-section {
        display: flex;
        justify-content: center;
        padding: 12px 0;
    }

    .photo-upload-btn {
        padding: 12px 24px;
        background: var(--bg-secondary);
        color: var(--color-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .photo-upload-btn:hover {
        border-color: #4CAF50;
        background: rgba(76, 175, 80, 0.1);
    }

    /* Photos Carousel */
    .photos-carousel-wrapper {
        position: relative;
        width: calc(100% + 30px);
        margin-left: -15px;
        margin-right: -15px;
        padding: 0;
        overflow: hidden;
    }

    .photos-carousel-container {
        width: 100%;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    .carousel-track {
        display: flex;
        align-items: center;
        width: 100%;
        position: relative;
    }

    .photo-carousel-slide {
        position: relative;
        min-width: 100%;
        width: 100%;
        aspect-ratio: 1/1;
        border-radius: 0;
        overflow: hidden;
        background: transparent;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .carousel-slide-prev {
        position: absolute;
        left: calc(-100% - 10px);
    }

    .carousel-slide-current {
        position: relative;
    }

    .carousel-slide-next {
        position: absolute;
        left: calc(100% + 10px);
    }

    .photo-carousel-slide img {
        max-width: 100%;
        max-height: 100%;
        height: auto;
        width: auto;
        object-fit: contain;
    }

    .photo-rotate-btn {
        position: absolute;
        top: 12px;
        left: calc(50% + 88px);
        transform: translateX(-50%);
        width: 36px;
        height: 36px;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        z-index: 25;
        justify-content: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .photo-rotate-btn svg {
        width: 18px;
        height: 18px;
        stroke: white;
    }

    .photo-rotate-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: translateX(-50%) scale(1.1);
    }

    .photo-delete-btn {
        position: absolute;
        top: 12px;
        left: calc(50% + 132px);
        transform: translateX(-50%);
        width: 36px;
        height: 36px;
        background: rgba(220, 38, 38, 0.6);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        z-index: 25;
    }

    .photo-delete-btn svg {
        width: 18px;
        height: 18px;
        stroke: white;
    }

    .photo-delete-btn:hover {
        background: rgba(220, 38, 38, 0.8);
        transform: translateX(-50%) scale(1.1);
    }

    .carousel-nav-btn {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 44px;
        height: 44px;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 10;
    }

    .carousel-nav-btn:hover {
        background: rgba(0, 0, 0, 0.7);
    }

    .carousel-prev {
        left: 8px;
    }

    .carousel-next {
        right: 8px;
    }

    .photos-carousel-counter {
        text-align: center;
        color: var(--color-secondary);
        font-size: 14px;
        margin-top: 12px;
        padding-bottom: 4px;
    }

    .carousel-dots {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
        overflow: visible;
    }

    .carousel-dot {
        width: 8px;
        height: 8px;
        min-width: 8px;
        min-height: 8px;
        border-radius: 50%;
        background: var(--color-secondary);
        opacity: 0.4;
        transition: all 0.2s ease;
        display: block;
        flex-shrink: 0;
    }

    .carousel-dot.active {
        opacity: 1;
        background: var(--color-accent);
        transform: scale(1.25);
    }

    .modal-content {
        background: var(--bg-secondary);
        border: 0px;
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
        gap: 6px;
        padding: 6px;
    }

    /* Items Modal Photos Section */
    .items-modal-body {
        display: block;
        padding: 0 !important;
        overflow-y: auto;
    }

    .items-photos-section {
        padding: 0;
        border-bottom: none;
        transition: all 0.3s ease;
    }

    /* Drag and drop visual feedback - Desktop only */
    @media (min-width: 768px) {
        .items-photos-section {
            margin-left: -1px;
            margin-right: -1px;
            width: calc(100% + 2px);
        }

        .items-photos-section.drag-over {
            background: rgba(76, 175, 80, 0.1);
            border: 2px dashed #4CAF50;
            border-radius: 8px;
            margin-left: 0;
            margin-right: 0;
            width: 100%;
        }

        .items-photos-section.drag-over .photos-carousel-container::after {
            content: 'Drop images here';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 18px;
            font-weight: 600;
            color: #4CAF50;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px 30px;
            border-radius: 8px;
            pointer-events: none;
            z-index: 100;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        /* Desktop: Ensure photos fill full width with no padding */
        .items-photos-section .photos-carousel-wrapper {
            width: 100%;
            margin-left: 0px;
            margin-right: 0px;
            padding: 0;
        }

        .items-photos-section .photos-carousel-container {
            width: 100%;
        }

        .items-photos-section .carousel-track {
            width: 100%;
        }

        .items-photos-section .photo-carousel-slide {
            width: 100%;
            min-width: 100%;
        }

        .items-photos-section .photo-carousel-slide img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
    }

    .items-photos-section .photos-carousel-wrapper {
        position: relative;
        width: 100%;
        padding: 0;
        overflow: hidden;
    }

    .items-photos-section .photos-carousel-container {
        width: 100%;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .items-photos-section .photo-carousel-slide {
        aspect-ratio: 4/3;
        width: 100%;
    }

    .items-photos-section .photo-carousel-slide img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .items-grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        padding: 6px;
    }

    /* Desktop: 6 columns for items grid (full screen modal) */
    @media (min-width: 768px) {
        .items-modal .items-grid-container {
            grid-template-columns: repeat(6, 1fr);
            padding: 15px;
            gap: 10px;
        }
    }

    /* Upload button when no photos */
    .items-photo-upload-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: var(--color-primary);
        color: white;
        border: none;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .items-photo-upload-btn:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }

    .items-photo-upload-btn svg {
        stroke: white;
    }

    /* Camera button inline - positioned to the left of upload button (mobile only) */
    .photo-camera-inline-btn {
        position: absolute;
        top: 12px;
        left: calc(50% - 88px);
        transform: translateX(-50%);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 25;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .photo-camera-inline-btn svg {
        width: 18px;
        height: 18px;
        stroke: white;
    }

    .photo-camera-inline-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: translateX(-50%) scale(1.1);
    }

    /* Upload button inline with rotate button - positioned to the left of rotate */
    .photo-upload-inline-btn {
        position: absolute;
        top: 12px;
        left: calc(50% - 44px);
        transform: translateX(-50%);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 25;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .photo-upload-inline-btn svg {
        width: 18px;
        height: 18px;
        stroke: white;
    }

    .photo-upload-inline-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: translateX(-50%) scale(1.1);
    }

    .photo-brightness-btn {
        position: absolute;
        top: 12px;
        left: 50%;
        transform: translateX(-50%);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        border: none;
        cursor: grab;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 25;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .photo-brightness-btn svg {
        width: 18px;
        height: 18px;
        stroke: white;
    }

    .photo-brightness-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: translateX(-50%) scale(1.1);
    }

    .photo-brightness-btn:active {
        cursor: grabbing;
        background: rgba(0, 0, 0, 0.8);
    }

    .photo-empty-room-btn {
        position: absolute;
        top: 12px;
        left: calc(50% + 44px);
        transform: translateX(-50%);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 25;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    .photo-empty-room-btn svg {
        width: 18px;
        height: 18px;
        stroke: white;
        fill: none;
        transform: translateY(-1px);
    }

    .photo-empty-room-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: translateX(-50%) scale(1.1);
    }

    .photo-empty-room-btn:active {
        background: rgba(0, 0, 0, 0.8);
    }

    /* Empty Room Progress Modal */
    .empty-room-modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 10000;
        align-items: center;
        justify-content: center;
    }

    .empty-room-modal.active {
        display: flex;
    }

    .empty-room-modal-content {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        max-width: 400px;
        width: 90%;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    }

    .empty-room-modal h3 {
        margin: 0 0 1.5rem 0;
        color: #333;
        font-size: 1.5rem;
    }

    .progress-circle-container {
        position: relative;
        width: 150px;
        height: 150px;
        margin: 1rem auto;
    }

    .progress-circle {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
    }

    .progress-circle-bg {
        fill: none;
        stroke: #e5e7eb;
        stroke-width: 8;
    }

    .progress-circle-fill {
        fill: none;
        stroke: #667eea;
        stroke-width: 8;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.3s ease;
    }

    .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
    }

    .credits-info {
        margin-top: 1.5rem;
        padding: 1rem;
        background: #f3f4f6;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #666;
    }

    .credits-info strong {
        color: #333;
        font-size: 1.1rem;
    }

    .empty-room-status {
        margin-top: 1rem;
        color: #667eea;
        font-size: 0.9rem;
        min-height: 20px;
    }

    /* Photo Brightness Slider */
    .photo-brightness-slider {
        position: absolute;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 9999px;
        padding: 10px 15px;
        width: 200px;
        z-index: 30;
    }

    .photo-brightness-slider-track {
        position: relative;
        height: 8px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 9999px;
        cursor: pointer;
    }

    .photo-brightness-slider-fill {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: linear-gradient(to right, #666, #fff);
        border-radius: 9999px;
        pointer-events: none;
    }

    .photo-brightness-slider-thumb {
        position: absolute;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 16px;
        height: 16px;
        background: white;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        pointer-events: none;
    }

    .item-btn {
        position: relative;
        background: var(--bg-secondary);
        border: 2px solid var(--border-color);
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        overflow: visible;
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
        padding: 6px 4px;
    }

    .item-btn.selected {
        border-color: var(--color-primary);
    }

    [data-theme="dark"] .item-btn.selected {
        border-color: #fff;
    }

    .item-btn[draggable="true"] {
        cursor: grab;
    }

    .item-btn[draggable="true"]:active {
        cursor: grabbing;
    }

    .item-btn.dragging {
        opacity: 0.5;
        transform: scale(0.95);
    }

    .item-btn.has-selected-image {
        padding: 0;
        overflow: visible;
    }

    .item-btn.has-selected-image .item-btn-content {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .item-btn.has-selected-image .item-emoji {
        width: 100% !important;
        height: auto !important;
        aspect-ratio: 1;
        flex-shrink: 0;
        display: block;
        position: relative;
    }

    .item-btn.has-selected-image .item-emoji img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 8px 8px 0 0;
        background: #fff;
        display: block;
    }

    .item-btn.has-selected-image .item-name {
        padding-top: 4px;
    }

    .item-btn.has-selected-image .item-unit-price,
    .item-btn.has-selected-image .item-total-price {
        display: block;
    }

    .item-btn.has-selected-image .item-qty-controls {
        padding: 4px 0;
    }

    .item-btn-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0;
    }

    .item-emoji {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
    }

    .item-emoji svg {
        width: 100%;
        height: 100%;
        stroke: var(--color-primary);
    }

    .item-name {
        font-size: 10px;
        font-weight: 600;
        color: var(--color-primary);
        text-align: center;
        line-height: 1.1;
        margin-top: 0;
    }

    .item-unit-price {
        font-size: 10px;
        font-weight: 500;
        color: var(--color-secondary);
        margin-top: 0;
    }

    .item-total-price {
        font-size: 10px;
        font-weight: 500;
        color: var(--color-primary);
        display: none;
        margin-top: 0;
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
        gap: 4px;
        margin-top: 1px;
    }

    .qty-btn {
        width: 22px;
        height: 22px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        border-radius: 50%;
        font-size: 14px;
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
        font-size: 12px;
        font-weight: 600;
        color: var(--color-primary);
        min-width: 16px;
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

    .modal-upload-btn {
        padding: 12px 20px;
        background: var(--bg-secondary);
        color: var(--color-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .modal-upload-btn:hover {
        background: var(--bg-tertiary, #f0f0f0);
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

    /* Inquiry Modal */
    .inquiry-modal {
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

    .inquiry-modal.hidden {
        display: none;
    }

    .inquiry-modal-content {
        max-width: 500px;
        max-height: 100%;
    }

    .inquiry-form-body {
        padding: 20px;
        overflow-y: auto;
    }

    .inquiry-form-group {
        margin-bottom: 16px;
    }

    .inquiry-form-row {
        display: flex;
        gap: 12px;
    }

    .inquiry-form-row .inquiry-form-group {
        flex: 1;
    }

    .inquiry-form-label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 6px;
    }

    .inquiry-form-input,
    .inquiry-form-textarea {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-secondary);
        color: var(--color-primary);
        font-size: 14px;
        font-family: inherit;
        transition: border-color 0.2s ease;
        box-sizing: border-box;
    }

    .inquiry-form-input:focus,
    .inquiry-form-textarea:focus {
        outline: none;
        border-color: var(--color-primary);
    }

    .inquiry-form-textarea {
        resize: vertical;
        min-height: 70px;
    }

    .inquiry-addons-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .inquiry-checkbox-item {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        padding: 8px 12px;
        background: var(--bg-secondary);
        border-radius: 8px;
        transition: background 0.2s ease;
    }

    .inquiry-checkbox-item:hover {
        background: var(--border-color);
    }

    .inquiry-checkbox {
        width: 18px;
        height: 18px;
        accent-color: var(--color-primary);
    }

    .inquiry-checkbox-label {
        font-size: 14px;
        color: var(--color-primary);
    }

    .inquiry-modal-footer {
        justify-content: center;
    }

    .inquiry-submit-btn {
        width: 100%;
        padding: 14px 24px;
        background: var(--color-primary);
        color: var(--bg-primary);
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }

    .inquiry-submit-btn:hover {
        opacity: 0.85;
    }

    .inquiry-submit-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Image Preview Modal */
    .image-preview-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.95);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
        cursor: pointer;
    }

    .image-preview-modal.hidden {
        display: none;
    }

    .image-modal-container {
        position: relative;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }

    .image-modal-inner {
        position: relative;
        max-width: 100%;
        max-height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .image-modal-content {
        max-width: 100%;
        max-height: calc(100vh - 40px);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .modal-2d-image {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        cursor: default;
    }

    .image-modal-close-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        color: white;
        font-size: 28px;
        font-weight: 400;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        z-index: 10002;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .image-modal-close-btn:hover {
        background: rgba(255, 255, 255, 0.35);
        border-color: rgba(255, 255, 255, 0.5);
        transform: scale(1.1);
    }

    .image-modal-close-btn:active {
        transform: scale(0.95);
    }

    /* Desktop (768px+) */
    @media (min-width: 768px) {
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

        .property-btn {
            border-radius: 20px;
        }

        .placeholder-btn {
            height: calc((600px - 40px) / 3 * 2 / 3);
        }

        .area-placeholder-btn {
            height: calc(((600px - 40px) / 3 * 2 / 3) * 7 + 80px);
        }

        /* Area buttons - ensure title, carousel, and buttons fit */
        .area-btn {
            min-height: auto;
            padding-top: 12px;
            padding-bottom: 12px;
        }

        .area-btn:has(.area-carousel.has-photos) {
            min-height: 240px;
            padding-bottom: 80px;
        }

        .area-btn.selected {
            min-height: 150px;
            padding-bottom: 80px;
        }

        .area-btn.selected:has(.area-carousel.has-photos) {
            min-height: 240px;
        }

        .area-btn .area-carousel {
            margin-top: 8px;
        }

        .area-carousel-track {
            max-height: 120px;
        }

        .area-carousel {
            margin-bottom: 8px;
        }

        .area-carousel-arrow {
            display: flex;
        }

        .area-actions {
            padding: 0 10px 10px 10px;
            gap: 6px;
        }

        /* Fix photo modal dots positioning on desktop */
        .photos-content {
            gap: 0;
        }

        .photos-carousel-counter {
            margin-top: 16px;
        }

        /* Image Preview Modal - Desktop max-width */
        .image-modal-content {
            max-width: 800px;
        }

        .modal-2d-image {
            border-radius: 12px;
        }
    }

    /* Staging Action Buttons */
    .staging-action-buttons {
        position: fixed;
        bottom: 30px;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        max-width: 960px;
        margin: 0 auto;
        padding: 0 40px;
        padding-right: 110px; /* Leave space for WhatsApp button */
        box-sizing: border-box;
        z-index: 999;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
    }

    .staging-action-buttons.visible {
        opacity: 1;
        pointer-events: auto;
    }

    .staging-inquiry-btn,
    .staging-continue-btn {
        padding: 0 28px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
        line-height: 1.2;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        transition: all 0.3s ease;
        cursor: pointer;
    }

    /* Light theme */
    [data-theme="light"] .staging-inquiry-btn {
        background: rgba(0, 0, 0, 0.06);
        color: #000000;
        border: 2px solid rgba(0, 0, 0, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    [data-theme="light"] .staging-inquiry-btn:hover {
        transform: translateY(-3px) scale(1.02);
        background: rgba(0, 0, 0, 0.15);
        border-color: rgba(0, 0, 0, 0.4);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2), 0 16px 60px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    [data-theme="light"] .staging-continue-btn {
        background: rgba(0, 0, 0, 0.06);
        color: #000000;
        border: 2px solid rgba(0, 0, 0, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        animation: staging-btn-glow-light 2s ease-in-out infinite;
    }

    [data-theme="light"] .staging-continue-btn:hover {
        transform: translateY(-3px) scale(1.02);
        background: rgba(0, 0, 0, 0.15);
        border-color: rgba(0, 0, 0, 0.4);
        animation-play-state: paused;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2), 0 16px 60px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    /* Dark theme */
    [data-theme="dark"] .staging-inquiry-btn {
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    [data-theme="dark"] .staging-inquiry-btn:hover {
        transform: translateY(-3px) scale(1.02);
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.7);
        box-shadow: 0 8px 35px rgba(255, 255, 255, 0.3), 0 16px 70px rgba(255, 255, 255, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    [data-theme="dark"] .staging-continue-btn {
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: staging-btn-glow-dark 2s ease-in-out infinite;
    }

    [data-theme="dark"] .staging-continue-btn:hover {
        transform: translateY(-3px) scale(1.02);
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.7);
        animation-play-state: paused;
        box-shadow: 0 8px 35px rgba(255, 255, 255, 0.3), 0 16px 70px rgba(255, 255, 255, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    /* Glow animations */
    @keyframes staging-btn-glow-light {
        0%, 100% {
            transform: scale(1);
            background: rgba(0, 0, 0, 0.06);
            border-color: rgba(0, 0, 0, 0.2);
        }
        50% {
            transform: scale(1.02);
            background: rgba(0, 0, 0, 0.12);
            border-color: rgba(0, 0, 0, 0.35);
        }
    }

    @keyframes staging-btn-glow-dark {
        0%, 100% {
            transform: scale(1);
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.35);
        }
        50% {
            transform: scale(1.02);
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.5);
        }
    }

    .staging-inquiry-btn:active,
    .staging-continue-btn:active {
        transform: translateY(-1px) scale(1.01) !important;
    }

    /* Mobile adjustments */
    @media (max-width: 767px) {
        .staging-action-buttons {
            bottom: 20px;
            padding: 0 10px;
            padding-right: 75px; /* Space for WhatsApp button (45px + 20px right + gap) */
        }

        .staging-inquiry-btn,
        .staging-continue-btn {
            font-size: 13px;
            height: 45px; /* Match WhatsApp button height on mobile */
            padding: 0 16px;
        }

        /* Area button mobile styles */
        .area-carousel-track {
            max-height: 100px;
        }

        .area-carousel-slide {
            max-height: 100px;
        }

        .area-carousel-dots {
            margin-bottom: 60px;
        }

        .area-actions {
            flex-direction: column;
            gap: 4px;
            padding: 0 8px 8px 8px;
        }

        .area-action-btn {
            font-size: 13px;
            padding: 6px 4px;
            border-radius: 6px;
        }

        /* Full-screen inquiry modal on mobile */
        .inquiry-modal {
            top: 0;
            bottom: 0;
            padding: 0;
            z-index: 10000;
            background: var(--bg-primary);
        }

        .inquiry-modal .modal-content,
        .inquiry-modal .inquiry-modal-content {
            max-width: 100%;
            width: 100%;
            height: 100%;
            border-radius: 0;
            border: none;
            box-shadow: none;
            background: transparent;
            position: relative;
            overflow-y: auto;
        }

        .inquiry-modal .modal-header {
            padding: 15px;
            position: sticky;
            top: 0;
            z-index: 10;
            border-bottom: none;
        }

        [data-theme="light"] .inquiry-modal .modal-header {
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(12px) saturate(120%);
            -webkit-backdrop-filter: blur(12px) saturate(120%);
        }

        [data-theme="dark"] .inquiry-modal .modal-header {
            background: rgba(26, 26, 26, 0.5);
            backdrop-filter: blur(12px) saturate(120%);
            -webkit-backdrop-filter: blur(12px) saturate(120%);
        }

        .inquiry-modal .modal-body,
        .inquiry-modal .inquiry-form-body {
            flex: none;
            padding: 0 15px 80px 15px;
            background: var(--bg-primary);
            overflow: visible;
            min-height: min-content;
        }

        .inquiry-modal .modal-footer,
        .inquiry-modal .inquiry-modal-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: transparent;
            border-top: none;
            padding: 12px 15px;
            z-index: 10;
            display: flex;
            justify-content: center;
        }

        .inquiry-modal .inquiry-submit-btn {
            padding: 0 28px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 700;
            height: 45px;
            border: none;
            backdrop-filter: blur(20px) saturate(150%);
            -webkit-backdrop-filter: blur(20px) saturate(150%);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        [data-theme="light"] .inquiry-modal .inquiry-submit-btn {
            background: rgba(0, 0, 0, 0.06);
            color: #000000;
            border: 2px solid rgba(0, 0, 0, 0.2);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        [data-theme="light"] .inquiry-modal .inquiry-submit-btn:active {
            background: rgba(0, 0, 0, 0.15);
            transform: scale(0.98);
        }

        [data-theme="dark"] .inquiry-modal .inquiry-submit-btn {
            background: rgba(255, 255, 255, 0.12);
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.35);
            box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        [data-theme="dark"] .inquiry-modal .inquiry-submit-btn:active {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0.98);
        }

        /* Disable focus/active blue highlight on mobile for action buttons */
        .staging-inquiry-btn,
        .staging-inquiry-btn:focus,
        .staging-inquiry-btn:active,
        .staging-continue-btn,
        .staging-continue-btn:focus,
        .staging-continue-btn:active {
            outline: none !important;
            box-shadow: none !important;
            -webkit-tap-highlight-color: transparent;
        }
    }

    /* 3D Model Viewer Styles */
    .photo-carousel-slide.photo-3d-mode {
        position: relative;
    }

    .photo-carousel-slide.photo-3d-mode img {
        display: none;
    }

    .photos-carousel-container.drag-over-3d,
    .items-photos-section.drag-over-3d .photos-carousel-container {
        outline: 3px dashed #4CAF50;
        outline-offset: -3px;
        background: rgba(76, 175, 80, 0.1);
    }

    .items-photos-section.drag-over-3d .photos-carousel-container::after {
        content: 'Drop 3D model here';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 18px;
        font-weight: 600;
        color: #4CAF50;
        background: rgba(255, 255, 255, 0.95);
        padding: 15px 30px;
        border-radius: 8px;
        z-index: 10;
    }

    .model-control-overlay {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 20;
    }

    .model-control-group {
        display: flex;
        gap: 8px;
        background: transparent;
        padding: 4px;
    }

    .model-control-btn {
        width: 36px;
        height: 36px;
        background: rgba(0, 0, 0, 0.5);
        border: none;
        border-radius: 50%;
        color: white;
        cursor: grab;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }

    .model-control-btn:hover {
        background: rgba(0, 0, 0, 0.7);
        transform: scale(1.1);
    }

    .model-control-btn:active {
        cursor: grabbing;
        background: rgba(0, 0, 0, 0.8);
    }

    .model-control-btn.model-control-danger {
        background: rgba(220, 38, 38, 0.6);
    }

    .model-control-btn.model-control-danger:hover {
        background: rgba(220, 38, 38, 0.8);
    }

    .model-control-btn svg {
        width: 18px;
        height: 18px;
    }

    /* Brightness Slider */
    .brightness-slider {
        background: rgba(0, 0, 0, 0.7);
        border-radius: 9999px;
        padding: 10px 15px;
        width: 200px;
    }

    .brightness-slider-track {
        position: relative;
        height: 8px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 9999px;
    }

    .brightness-slider-fill {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: linear-gradient(to right, #666, #fff);
        border-radius: 4px;
        width: 100%;
    }

    .brightness-slider-thumb {
        position: absolute;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 16px;
        height: 16px;
        background: white;
        border: 2px solid rgba(0, 0, 0, 0.3);
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    /* Mobile adjustments for 3D controls */
    @media (max-width: 767px) {
        .model-control-group {
            gap: 4px;
            padding: 6px 8px;
        }

        .model-control-btn {
            width: 36px;
            height: 36px;
        }

        .model-control-btn svg {
            width: 18px;
            height: 18px;
        }

        .model-control-overlay {
            top: 5px;
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
