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


def staging_inquiry_page():
    """Staging Inquiry page"""
    content = Div(
        staging_inquiry_hero_section(),
        staging_inquiry_form_section(),
        reviews_section(),
        trusted_by_section(),
        cls="staging-inquiry-content"
    )

    additional_styles = get_staging_inquiry_styles()

    return create_page(
        "Get a Quote | Astra Staging",
        content,
        additional_styles=additional_styles,
        description="Get an instant staging quote from Astra Staging. Fill out our form with your property details and receive a customized quote within 24 hours.",
        keywords="staging quote, home staging price, staging cost estimate, GTA staging services"
    )
