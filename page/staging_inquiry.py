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
            # Property Status Row - Placeholder shown by default
            Div(
                Button(Span("Vacant or Occupied", cls="placeholder-text"), cls="property-btn placeholder-btn", disabled=True),
                id="status-placeholder",
                cls="property-selector placeholder-row"
            ),
            # Property Status Row (hidden by default)
            Div(
                id="status-selector",
                cls="property-selector status-selector hidden"
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
                    Button(Span("Living Room", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="living-room", onclick="toggleArea(this)"),
                    Button(Span("Dining Room", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="dining-room", onclick="toggleArea(this)"),
                    Button(Span("Family Room", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="family-room", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 2: Kitchen Only, Kitchen with Island, Breakfast Area
                Div(
                    Button(Span("Kitchen Only", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="kitchen-only", onclick="toggleArea(this)"),
                    Button(Span("Kitchen Island", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="kitchen-island", onclick="toggleArea(this)"),
                    Button(Span("Breakfast Area", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="breakfast-area", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 3: Master Bedroom, 2nd Bedroom, 3rd Bedroom
                Div(
                    Button(Span("Master Bedroom", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="master-bedroom", onclick="toggleArea(this)"),
                    Button(Span("2nd Bedroom", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="2nd-bedroom", onclick="toggleArea(this)"),
                    Button(Span("3rd Bedroom", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="3rd-bedroom", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 4: 4th Bedroom, 5th Bedroom, 6th Bedroom
                Div(
                    Button(Span("4th Bedroom", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="4th-bedroom", onclick="toggleArea(this)"),
                    Button(Span("5th Bedroom", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="5th-bedroom", onclick="toggleArea(this)"),
                    Button(Span("6th Bedroom", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="6th-bedroom", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 5: Office, Bathrooms, Outdoor
                Div(
                    Button(Span("Office", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="office", onclick="toggleArea(this)"),
                    Button(Span("Bathrooms", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="bathrooms", onclick="toggleArea(this)"),
                    Button(Span("Outdoor", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="outdoor", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 6: Basement Living, Basement Dining, Basement Office
                Div(
                    Button(Span("Basement Living", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="basement-living", onclick="toggleArea(this)"),
                    Button(Span("Basement Dining", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="basement-dining", onclick="toggleArea(this)"),
                    Button(Span("Basement Office", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="basement-office", onclick="toggleArea(this)"),
                    cls="property-selector"
                ),
                # Row 7: Basement 1st Bedroom, Basement 2nd Bedroom
                Div(
                    Button(Span("Basement 1st Bed", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="basement-1st-bedroom", onclick="toggleArea(this)"),
                    Button(Span("Basement 2nd Bed", cls="area-name"), Span("", cls="area-price"), cls="property-btn area-btn", data_area="basement-2nd-bedroom", onclick="toggleArea(this)"),
                    Div(cls="property-btn-spacer"),
                    cls="property-selector"
                ),
                id="area-selector",
                cls="area-selector hidden"
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
                const propertyBtn = document.querySelector('.property-btn.selected:not(.size-btn):not(.status-btn):not(.area-btn)');
                const sizeBtn = document.querySelector('.size-btn.selected');
                const statusBtn = document.querySelector('.status-btn.selected');

                return {
                    propertyType: propertyBtn ? propertyBtn.getAttribute('data-type') : null,
                    propertySize: sizeBtn ? sizeBtn.getAttribute('data-size') : null,
                    occupancy: statusBtn ? statusBtn.getAttribute('data-status') : null
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
                const { propertyType, propertySize, occupancy } = getSelections();
                if (!propertyType || !propertySize) return;

                const isOccupied = occupancy === 'occupied-furniture';

                document.querySelectorAll('.area-btn').forEach(btn => {
                    const area = btn.getAttribute('data-area');
                    let price = getAreaPrice(area, propertyType, propertySize);
                    // Half price for occupied with existing furniture
                    if (isOccupied && price > 0) {
                        price = price / 2;
                    }
                    const priceSpan = btn.querySelector('.area-price');
                    if (priceSpan) {
                        priceSpan.textContent = price > 0 ? '+$' + price : 'Included';
                    }
                });

                calculateTotalFee();
            }

            // Calculate total staging fee
            function calculateTotalFee() {
                const { propertyType, propertySize, occupancy } = getSelections();
                if (!propertyType || !propertySize || !occupancy) {
                    updateBannerFee(null);
                    return;
                }

                let stagingFee = getBaseFee(propertySize);

                // Add selected area prices
                document.querySelectorAll('.area-btn.selected').forEach(btn => {
                    const area = btn.getAttribute('data-area');
                    stagingFee += getAreaPrice(area, propertyType, propertySize);
                });

                // Occupied adjustment (half the area fees)
                if (occupancy === 'occupied-furniture') {
                    stagingFee = (stagingFee - getBaseFee(propertySize)) / 2 + getBaseFee(propertySize);
                } else if (occupancy === 'occupied-accessory') {
                    // Decor only pricing
                    if (propertyType === 'condo') {
                        stagingFee = BASE_STAGING_FEE + 200;
                    } else if (propertyType === 'townhouse') {
                        stagingFee = BASE_STAGING_FEE + 500;
                    } else if (propertyType === 'house') {
                        stagingFee = BASE_STAGING_FEE + 1000;
                    }
                }

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
                    subtitle.textContent = 'select property size and occupancy';
                } else if (state === 'status-selected') {
                    title.textContent = 'Instant Quote';
                    subtitle.textContent = 'choose staging areas';
                    updateAreaPrices();
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
                const allBtns = document.querySelectorAll('.property-btn:not(.size-btn):not(.status-btn):not(.area-btn):not(.placeholder-btn)');
                const sizeSelector = document.getElementById('size-selector');
                const sizePlaceholder = document.getElementById('size-placeholder');
                const statusSelector = document.getElementById('status-selector');
                const statusPlaceholder = document.getElementById('status-placeholder');
                const areaSelector = document.getElementById('area-selector');
                const areaPlaceholder = document.getElementById('area-placeholder');

                if (btn.classList.contains('selected')) {
                    // Toggle off if already selected
                    btn.classList.remove('selected');
                    allBtns.forEach(b => b.classList.remove('dimmed'));
                    sizeSelector.classList.add('hidden');
                    sizeSelector.innerHTML = '';
                    sizePlaceholder.classList.remove('hidden');
                    statusSelector.classList.add('hidden');
                    statusSelector.innerHTML = '';
                    statusPlaceholder.classList.remove('hidden');
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

                    // Show status options immediately
                    showStatusOptions();

                    // Reset areas to placeholder (since size/status are cleared)
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

            const statusOptions = [
                { line1: 'Vacant', line2: 'No Furniture', value: 'vacant' },
                { line1: 'Occupied', line2: 'Existing Furniture', value: 'occupied-furniture' },
                { line1: 'Occupied', line2: 'Accessory Only', value: 'occupied-accessory' }
            ];

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

            function showStatusOptions() {
                const statusSelector = document.getElementById('status-selector');
                const statusPlaceholder = document.getElementById('status-placeholder');

                statusSelector.innerHTML = statusOptions.map(opt => `
                    <button class="property-btn status-btn" data-status="${opt.value}" onclick="selectStatus(this)">
                        <span class="size-line1">${opt.line1}</span>
                        <span class="size-line2">${opt.line2}</span>
                    </button>
                `).join('');

                statusPlaceholder.classList.add('hidden');
                statusSelector.classList.remove('hidden');
            }

            function checkShowAreas() {
                const { propertyType, propertySize, occupancy } = getSelections();
                const areaSelector = document.getElementById('area-selector');
                const areaPlaceholder = document.getElementById('area-placeholder');

                // Accessory Only - hide areas completely and show fixed price
                if (occupancy === 'occupied-accessory') {
                    areaSelector.classList.add('hidden');
                    areaPlaceholder.classList.add('hidden');
                    // Clear area selections
                    document.querySelectorAll('.area-btn').forEach(b => b.classList.remove('selected'));
                    // Calculate fixed accessory price
                    let accessoryFee = BASE_STAGING_FEE;
                    if (propertyType === 'condo') accessoryFee += 200;
                    else if (propertyType === 'townhouse') accessoryFee += 500;
                    else if (propertyType === 'house') accessoryFee += 1000;
                    updateBannerFee(accessoryFee);
                    return;
                }

                if (propertySize && occupancy) {
                    areaPlaceholder.classList.add('hidden');
                    areaSelector.classList.remove('hidden');
                    updateBanner('status-selected');
                    updateAreaPrices();
                } else {
                    areaSelector.classList.add('hidden');
                    areaPlaceholder.classList.remove('hidden');
                    if (document.querySelector('.property-btn.selected:not(.size-btn):not(.status-btn):not(.area-btn)')) {
                        updateBanner('property-selected');
                    }
                }
            }

            function selectStatus(btn) {
                buttonFeedback();
                const allStatusBtns = document.querySelectorAll('.status-btn');

                if (btn.classList.contains('selected')) {
                    btn.classList.remove('selected');
                    allStatusBtns.forEach(b => b.classList.remove('dimmed'));
                } else {
                    allStatusBtns.forEach(b => {
                        b.classList.remove('selected');
                        b.classList.add('dimmed');
                    });
                    btn.classList.add('selected');
                    btn.classList.remove('dimmed');
                }
                checkShowAreas();
                updateAreaPrices();
            }

            function toggleArea(btn) {
                buttonFeedback();
                btn.classList.toggle('selected');
                calculateTotalFee();
            }
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

    .size-selector.hidden,
    .status-selector.hidden {
        display: none;
    }

    .status-selector {
        margin-top: 10px;
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
