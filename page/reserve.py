from fasthtml.common import *
from page.components import create_page
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import math

# Load environment variables
load_dotenv()


def reserve_page(req: Request):
    """Create the staging reservation page with deposit payment"""

    # Get Google API key from environment
    google_api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')

    reserve_styles = """
        .reserve-container {
            max-width: 960px;
            margin: 30px auto 40px;
            padding: 0 20px 40px 20px;
        }

        .reserve-header {
            text-align: center;
            margin-bottom: 60px;
        }

        .reserve-title {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 16px;
            letter-spacing: -0.02em;
        }

        .reserve-subtitle {
            font-size: 18px;
            color: var(--color-secondary);
            opacity: 0.8;
        }

        .reserve-grid {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 40px;
            margin-bottom: 40px;
        }

        .reserve-sections {
            display: flex;
            flex-direction: column;
            gap: 32px;
        }

        .reserve-section {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 32px;
            transition: all 0.3s ease;
        }

        [data-theme="light"] .reserve-section {
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }

        .reserve-section:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .section-title {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .section-icon {
            font-size: 28px;
        }

        /* Price Summary Sidebar */
        .price-summary {
            position: sticky;
            top: 140px;
            height: fit-content;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        [data-theme="light"] .price-summary {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.03) 0%, rgba(0, 0, 0, 0.01) 100%);
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }

        .price-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-theme="light"] .price-item {
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }

        .price-item:last-of-type {
            border-bottom: none;
        }

        .price-label {
            font-size: 15px;
            color: var(--color-secondary);
        }

        .price-value {
            font-size: 16px;
            font-weight: 500;
        }

        .total-label {
            font-size: 18px;
            font-weight: 600;
        }

        .total-value {
            font-size: 24px;
            font-weight: 700;
            color: #4CAF50;
        }

        /* Form Styles */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group.full-width {
            grid-column: 1 / -1;
        }

        .form-label {
            font-size: 14px;
            font-weight: 500;
            color: var(--color-secondary);
        }

        .form-input {
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--color-primary);
            font-size: 15px;
            transition: all 0.3s ease;
        }

        [data-theme="light"] .form-input {
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }

        .form-input:focus {
            outline: none;
            border-color: #4CAF50;
            border-width: 2px;
            background: rgba(255, 255, 255, 0.08);
        }

        [data-theme="light"] .form-input:focus {
            border-color: #4CAF50;
            background: rgba(0, 0, 0, 0.02);
        }

        /* Summary item list */
        .summary-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .summary-item {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        [data-theme="light"] .summary-item {
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }

        .summary-item:last-child {
            border-bottom: none;
        }

        .summary-item-label {
            font-size: 14px;
            color: var(--color-secondary);
            flex-shrink: 0;
        }

        .summary-item-value {
            font-size: 14px;
            font-weight: 500;
            text-align: right;
            max-width: 200px;
        }

        .summary-items-list {
            font-size: 13px;
            color: var(--color-secondary);
            margin-top: 4px;
            line-height: 1.4;
        }

        /* Policy Styles */
        .policy-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .policy-item {
            display: flex;
            gap: 12px;
            padding: 16px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
        }

        [data-theme="light"] .policy-item {
            background: rgba(0, 0, 0, 0.01);
        }

        .policy-icon {
            font-size: 20px;
            flex-shrink: 0;
        }

        .policy-content {
            flex: 1;
        }

        .policy-title {
            font-weight: 500;
            margin-bottom: 4px;
        }

        .policy-desc {
            font-size: 14px;
            color: var(--color-secondary);
            opacity: 0.8;
            line-height: 1.5;
        }

        /* Reserve Now Button */
        .reserve-now-btn {
            padding: 18px 60px;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
        }

        .reserve-now-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(76, 175, 80, 0.4);
        }

        .reserve-now-btn:active {
            transform: translateY(0);
        }

        .reserve-now-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }

        /* Add-on checkbox styles */
        .addon-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .addon-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        [data-theme="light"] .addon-item {
            background: rgba(0, 0, 0, 0.01);
        }

        .addon-item:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        [data-theme="light"] .addon-item:hover {
            background: rgba(0, 0, 0, 0.03);
        }

        .addon-checkbox {
            width: 20px;
            height: 20px;
            flex-shrink: 0;
            margin-top: 2px;
            accent-color: #4CAF50;
        }

        .addon-content {
            flex: 1;
        }

        .addon-title {
            font-weight: 500;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .addon-price {
            color: #4CAF50;
            font-weight: 600;
        }

        .addon-desc {
            font-size: 14px;
            color: var(--color-secondary);
            opacity: 0.8;
        }

        /* Date picker styles */
        .date-picker-container {
            position: relative;
        }

        .date-input {
            cursor: pointer;
        }

        /* Date type selector buttons */
        .date-type-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .date-type-btn {
            flex: 1;
            padding: 16px 12px;
            background: rgba(255, 255, 255, 0.03);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: var(--color-primary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        [data-theme="light"] .date-type-btn {
            background: rgba(0, 0, 0, 0.02);
            border: 2px solid rgba(0, 0, 0, 0.1);
        }

        .date-type-btn:hover {
            border-color: rgba(76, 175, 80, 0.5);
        }

        .date-type-btn.selected {
            border-color: #4CAF50;
            background: rgba(76, 175, 80, 0.1);
        }

        .calendar-container {
            display: none;
        }

        .calendar-container.visible {
            display: block;
        }

        /* Date picker visibility - desktop shows single calendar, mobile shows scrollable months */
        .desktop-date-picker {
            display: block;
        }

        .mobile-date-picker {
            display: none;
        }

        @media (max-width: 767px) {
            .desktop-date-picker {
                display: none;
            }
            .mobile-date-picker {
                display: block;
            }
        }

        .mobile-months-container {
            display: flex;
            flex-direction: column;
            gap: 24px;
            max-height: 400px;
            overflow-y: auto;
            padding: 16px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }

        .mobile-months-container::-webkit-scrollbar {
            display: none;
        }

        [data-theme="light"] .mobile-months-container {
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }

        .calendar-month {
            background: transparent;
        }

        .calendar-header {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 12px 0;
            margin-bottom: 8px;
        }

        .calendar-month-year {
            font-size: 16px;
            font-weight: 600;
            color: var(--color-primary);
        }

        .calendar-nav-btn {
            background: transparent;
            border: 1px solid var(--color-primary);
            color: var(--color-primary);
            font-size: 16px;
            cursor: pointer;
            padding: 6px 12px;
            border-radius: 6px;
            transition: all 0.2s ease;
            margin: 0 12px;
        }

        .calendar-nav-btn:hover {
            background: var(--color-primary);
            color: var(--bg-primary);
        }

        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
        }

        .calendar-day-header {
            text-align: center;
            padding: 8px 4px;
            font-size: 12px;
            font-weight: 500;
            color: var(--color-secondary);
        }

        .calendar-day {
            text-align: center;
            padding: 10px 4px;
            cursor: pointer;
            border-radius: 8px;
            border: 1px solid transparent;
            transition: all 0.2s ease;
            color: var(--color-primary);
            font-size: 14px;
        }

        .calendar-day:hover:not(.disabled):not(.empty) {
            background: rgba(76, 175, 80, 0.2);
            border-color: #4CAF50;
        }

        .calendar-day.selected {
            background: #4CAF50;
            color: white;
            font-weight: 600;
        }

        .calendar-day.disabled {
            color: var(--color-secondary);
            opacity: 0.3;
            cursor: not-allowed;
        }

        .calendar-day.empty {
            visibility: hidden;
        }

        /* Responsive Design */
        @media (max-width: 1040px) {
            .reserve-container {
                margin: 30px auto 40px;
            }

            .reserve-header {
                margin-bottom: 40px;
            }

            .reserve-grid {
                grid-template-columns: 1fr;
                display: flex;
                flex-direction: column;
            }

            .price-summary {
                position: relative;
                top: 0;
                order: -1;
                margin-bottom: 32px;
            }

            .reserve-sections {
                order: 1;
            }

            /* Move Staging Information to top on mobile (after summary) */
            .staging-info-section {
                order: -1;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .reserve-title {
                font-size: 28px;
            }

            .reserve-subtitle {
                font-size: 16px;
            }
        }

        @media (max-width: 767px) {
            .reserve-title {
                font-size: 24px;
            }

            .section-title {
                font-size: 20px;
            }

            .section-icon {
                font-size: 24px;
            }

            .total-label {
                font-size: 16px;
            }

            .total-value {
                font-size: 20px;
            }

            .price-label {
                font-size: 14px;
            }

            .price-value {
                font-size: 15px;
            }

        }

        @media (max-width: 390px) {
            .total-value {
                font-size: 18px;
            }

            .total-label {
                font-size: 15px;
            }
        }
    """

    reserve_scripts = f"""
        // Staging data from URL parameters or session
        let stagingData = {{
            propertyType: '',
            propertySize: '',
            selectedAreas: [],
            selectedItems: {{}},
            totalFee: 0,
            addons: []
        }};

        // Add-on prices
        const addonPrices = {{
            'photos': 150,
            'floorplan': 200,
            'virtual-tour': 300
        }};

        // Item ID to display name mapping
        const itemNameMap = {{
            'sofa': 'Sofa',
            'coffee-table': 'Coffee Table',
            'area-rug': 'Area Rug',
            'accent-chair': 'Accent Chair',
            'side-table': 'Side Table',
            'floor-lamp': 'Floor Lamp',
            'table-lamp': 'Table Lamp',
            'throw-pillows': 'Throw Pillows',
            'wall-art': 'Wall Art',
            'plant': 'Plant',
            'dining-table': 'Dining Table',
            'dining-chair': 'Dining Chair',
            'buffet': 'Buffet',
            'centerpiece': 'Centerpiece',
            'bar-cart': 'Bar Cart',
            'tv-stand': 'TV Stand',
            'console-table': 'Console Table',
            'bookshelf': 'Bookshelf',
            'ottoman': 'Ottoman',
            'bar-stool': 'Bar Stool',
            'counter-stool': 'Counter Stool',
            'kitchen-accessories': 'Kitchen Accessories',
            'queen-bed-frame': 'Queen Bed Frame',
            'queen-headboard': 'Queen Headboard',
            'queen-mattress': 'Queen Mattress',
            'queen-beddings': 'Queen Beddings',
            'nightstand': 'Nightstand',
            'dresser': 'Dresser',
            'mirror': 'Mirror',
            'king-bed-frame': 'King Bed Frame',
            'king-headboard': 'King Headboard',
            'king-mattress': 'King Mattress',
            'king-beddings': 'King Beddings',
            'double-bed-frame': 'Double Bed Frame',
            'double-headboard': 'Double Headboard',
            'double-mattress': 'Double Mattress',
            'double-beddings': 'Double Beddings',
            'single-bed-frame': 'Single Bed Frame',
            'single-headboard': 'Single Headboard',
            'single-mattress': 'Single Mattress',
            'single-beddings': 'Single Beddings',
            'desk': 'Desk',
            'chair': 'Chair',
            'patio-set': 'Patio Set',
            'towels': 'Towels',
            'bath-accessories': 'Bath Accessories'
        }};

        // Parse URL parameters on load
        function loadStagingData() {{
            const urlParams = new URLSearchParams(window.location.search);

            stagingData.propertyType = urlParams.get('propertyType') || '';
            stagingData.propertySize = urlParams.get('propertySize') || '';
            stagingData.totalFee = parseFloat(urlParams.get('totalFee')) || 0;

            // Parse selected areas
            const areasParam = urlParams.get('areas');
            if (areasParam) {{
                stagingData.selectedAreas = areasParam.split(',');
            }}

            // Parse selected items (JSON encoded)
            const itemsParam = urlParams.get('items');
            if (itemsParam) {{
                try {{
                    stagingData.selectedItems = JSON.parse(decodeURIComponent(itemsParam));
                }} catch (e) {{
                    console.error('Error parsing items:', e);
                }}
            }}

            updateSummaryDisplay();
            updateDueToday();
        }}

        // Update the staging summary display
        function updateSummaryDisplay() {{
            // Update property type (capitalized)
            const propTypeEl = document.getElementById('summary-property-type');
            if (propTypeEl) {{
                const propType = stagingData.propertyType || '';
                propTypeEl.textContent = propType ? propType.charAt(0).toUpperCase() + propType.slice(1) : 'Not selected';
            }}

            // Update property size (with sq ft)
            const propSizeEl = document.getElementById('summary-property-size');
            if (propSizeEl) {{
                const propSize = stagingData.propertySize || '';
                propSizeEl.textContent = propSize ? propSize + ' sq ft' : 'Not selected';
            }}

            // Update selected areas and items (grouped by area)
            const areasItemsEl = document.getElementById('summary-areas-items');
            if (areasItemsEl) {{
                // Format item name from ID (e.g., "end-table" -> "End Table")
                function formatItemName(itemId) {{
                    if (itemNameMap[itemId]) return itemNameMap[itemId];
                    return itemId.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                }}

                // Area slug to display name mapping
                const areaDisplayNames = {{
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
                    'basement-1st-bedroom': 'Basement 1st Bed',
                    'basement-2nd-bedroom': 'Basement 2nd Bed'
                }};

                if (Object.keys(stagingData.selectedItems).length > 0) {{
                    // Build display by area
                    const areaLines = [];
                    for (const [areaSlug, items] of Object.entries(stagingData.selectedItems)) {{
                        const areaName = areaDisplayNames[areaSlug] || areaSlug;
                        const areaNameNbsp = areaName.replace(/ /g, '\u00A0');

                        // Build items list for this area
                        const itemsList = [];
                        for (const [itemId, qty] of Object.entries(items)) {{
                            if (qty > 0) {{
                                const itemName = formatItemName(itemId);
                                const displayName = qty > 1 ? itemName + 's' : itemName;
                                const displayNameNbsp = displayName.replace(/ /g, '\u00A0');
                                itemsList.push(`${{qty}}\u00A0${{displayNameNbsp}}`);
                            }}
                        }}

                        if (itemsList.length > 0) {{
                            areaLines.push(`<div style="margin-bottom: 8px;"><strong>${{areaNameNbsp}}:</strong> ${{itemsList.join(', ')}}</div>`);
                        }}
                    }}

                    if (areaLines.length > 0) {{
                        areasItemsEl.innerHTML = areaLines.join('');
                    }} else {{
                        areasItemsEl.textContent = 'None selected';
                    }}
                }} else {{
                    areasItemsEl.textContent = 'None selected';
                }}
            }}

            // Update total fee
            const totalEl = document.getElementById('summary-total-fee');
            if (totalEl) {{
                totalEl.textContent = '$' + stagingData.totalFee.toLocaleString('en-CA', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}) + ' CAD';
            }}
        }}

        // Calculate and update Due Today amount
        function updateDueToday() {{
            let totalWithAddons = stagingData.totalFee;

            // Add selected add-ons
            stagingData.addons.forEach(addon => {{
                totalWithAddons += addonPrices[addon] || 0;
            }});

            // Due Today = floor of half the total, rounded down to nearest 500
            const halfTotal = totalWithAddons / 2;
            const dueToday = Math.floor(halfTotal / 500) * 500;

            // Update display
            const dueTodayEl = document.getElementById('due-today-amount');
            if (dueTodayEl) {{
                dueTodayEl.textContent = '$' + Math.max(500, dueToday).toLocaleString('en-CA', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}) + ' CAD';
            }}

            // Update total with add-ons
            const totalWithAddonsEl = document.getElementById('total-with-addons');
            if (totalWithAddonsEl) {{
                totalWithAddonsEl.textContent = '$' + totalWithAddons.toLocaleString('en-CA', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}) + ' CAD';
            }}
        }}

        // Handle add-on checkbox changes
        function handleAddonChange(checkbox) {{
            const addon = checkbox.value;
            if (checkbox.checked) {{
                if (!stagingData.addons.includes(addon)) {{
                    stagingData.addons.push(addon);
                }}
            }} else {{
                stagingData.addons = stagingData.addons.filter(a => a !== addon);
            }}
            updateDueToday();
        }}

        // Calendar state
        let selectedDate = null;
        let selectedWeekStart = null;
        let selectedWeekEnd = null;
        let currentDisplayMonth = new Date();

        // Statutory holidays (Ontario, Canada) - format: 'YYYY-MM-DD'
        const statHolidays = [
            // 2025
            '2025-01-01', // New Year's Day
            '2025-02-17', // Family Day
            '2025-04-18', // Good Friday
            '2025-05-19', // Victoria Day
            '2025-07-01', // Canada Day
            '2025-08-04', // Civic Holiday
            '2025-09-01', // Labour Day
            '2025-10-13', // Thanksgiving
            '2025-12-25', // Christmas Day
            '2025-12-26', // Boxing Day
            // 2026
            '2026-01-01', // New Year's Day
            '2026-02-16', // Family Day
            '2026-04-03', // Good Friday
            '2026-05-18', // Victoria Day
            '2026-07-01', // Canada Day
            '2026-08-03', // Civic Holiday
            '2026-09-07', // Labour Day
            '2026-10-12', // Thanksgiving
            '2026-12-25', // Christmas Day
            '2026-12-26', // Boxing Day
        ];

        function isStatHoliday(date) {{
            const dateStr = date.getFullYear() + '-' +
                String(date.getMonth() + 1).padStart(2, '0') + '-' +
                String(date.getDate()).padStart(2, '0');
            return statHolidays.includes(dateStr);
        }}

        // Generate calendar months
        function generateCalendarMonths() {{
            const container = document.getElementById('mobile-months');
            const desktopContainer = document.getElementById('desktop-calendar');
            if (!container && !desktopContainer) return;

            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                               'July', 'August', 'September', 'October', 'November', 'December'];
            const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

            // Mobile: Generate 3 months (current + 2)
            if (container) {{
                container.innerHTML = '';
                for (let m = 0; m < 3; m++) {{
                    const monthDate = new Date(today.getFullYear(), today.getMonth() + m, 1);
                    container.appendChild(createMonthElement(monthDate, today, monthNames, dayNames));
                }}
            }}

            // Desktop: Generate single month with navigation
            if (desktopContainer) {{
                renderDesktopCalendar(today, monthNames, dayNames);
            }}
        }}

        function createMonthElement(monthDate, today, monthNames, dayNames) {{
            const monthDiv = document.createElement('div');
            monthDiv.className = 'calendar-month';

            // Header
            const header = document.createElement('div');
            header.className = 'calendar-header';
            const monthYear = document.createElement('span');
            monthYear.className = 'calendar-month-year';
            monthYear.textContent = monthNames[monthDate.getMonth()] + ' ' + monthDate.getFullYear();
            header.appendChild(monthYear);
            monthDiv.appendChild(header);

            // Day headers
            const grid = document.createElement('div');
            grid.className = 'calendar-grid';

            dayNames.forEach(day => {{
                const dayHeader = document.createElement('div');
                dayHeader.className = 'calendar-day-header';
                dayHeader.textContent = day;
                grid.appendChild(dayHeader);
            }});

            // Calculate days
            const firstDay = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
            const lastDay = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0);
            const startingDay = firstDay.getDay();

            // Empty cells before first day
            for (let i = 0; i < startingDay; i++) {{
                const emptyCell = document.createElement('div');
                emptyCell.className = 'calendar-day empty';
                grid.appendChild(emptyCell);
            }}

            // Days of month
            for (let day = 1; day <= lastDay.getDate(); day++) {{
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day';
                dayCell.textContent = day;

                const cellDate = new Date(monthDate.getFullYear(), monthDate.getMonth(), day);

                // Disable past dates, weekends (Sat=6, Sun=0), and stat holidays
                const dayOfWeek = cellDate.getDay();
                if (cellDate < today || dayOfWeek === 0 || dayOfWeek === 6 || isStatHoliday(cellDate)) {{
                    dayCell.classList.add('disabled');
                }} else {{
                    dayCell.onclick = () => selectDate(cellDate);
                }}

                // Highlight selected date or week
                if (selectedDateType === 'week' && selectedWeekStart && selectedWeekEnd) {{
                    // Check if this date is within the selected week
                    const cellTime = cellDate.getTime();
                    const startTime = new Date(selectedWeekStart.getFullYear(), selectedWeekStart.getMonth(), selectedWeekStart.getDate()).getTime();
                    const endTime = new Date(selectedWeekEnd.getFullYear(), selectedWeekEnd.getMonth(), selectedWeekEnd.getDate()).getTime();
                    if (cellTime >= startTime && cellTime <= endTime) {{
                        dayCell.classList.add('selected');
                    }}
                }} else if (selectedDate &&
                    cellDate.getDate() === selectedDate.getDate() &&
                    cellDate.getMonth() === selectedDate.getMonth() &&
                    cellDate.getFullYear() === selectedDate.getFullYear()) {{
                    dayCell.classList.add('selected');
                }}

                grid.appendChild(dayCell);
            }}

            monthDiv.appendChild(grid);
            return monthDiv;
        }}

        function renderDesktopCalendar(today, monthNames, dayNames) {{
            const container = document.getElementById('desktop-calendar');
            if (!container) return;

            container.innerHTML = '';

            // Navigation header
            const navHeader = document.createElement('div');
            navHeader.className = 'calendar-header';
            navHeader.style.justifyContent = 'space-between';

            const prevBtn = document.createElement('button');
            prevBtn.className = 'calendar-nav-btn';
            prevBtn.innerHTML = '&larr;';
            prevBtn.onclick = () => navigateMonth(-1);

            const monthYear = document.createElement('span');
            monthYear.className = 'calendar-month-year';
            monthYear.textContent = monthNames[currentDisplayMonth.getMonth()] + ' ' + currentDisplayMonth.getFullYear();

            const nextBtn = document.createElement('button');
            nextBtn.className = 'calendar-nav-btn';
            nextBtn.innerHTML = '&rarr;';
            nextBtn.onclick = () => navigateMonth(1);

            // Disable prev if current month
            const currentMonth = new Date();
            currentMonth.setDate(1);
            currentMonth.setHours(0, 0, 0, 0);
            const displayFirst = new Date(currentDisplayMonth.getFullYear(), currentDisplayMonth.getMonth(), 1);
            if (displayFirst <= currentMonth) {{
                prevBtn.disabled = true;
                prevBtn.style.opacity = '0.3';
            }}

            // Disable next if 2 months ahead
            const maxMonth = new Date(today.getFullYear(), today.getMonth() + 2, 1);
            if (displayFirst >= maxMonth) {{
                nextBtn.disabled = true;
                nextBtn.style.opacity = '0.3';
            }}

            navHeader.appendChild(prevBtn);
            navHeader.appendChild(monthYear);
            navHeader.appendChild(nextBtn);
            container.appendChild(navHeader);

            // Calendar grid
            const grid = document.createElement('div');
            grid.className = 'calendar-grid';

            dayNames.forEach(day => {{
                const dayHeader = document.createElement('div');
                dayHeader.className = 'calendar-day-header';
                dayHeader.textContent = day;
                grid.appendChild(dayHeader);
            }});

            const firstDay = new Date(currentDisplayMonth.getFullYear(), currentDisplayMonth.getMonth(), 1);
            const lastDay = new Date(currentDisplayMonth.getFullYear(), currentDisplayMonth.getMonth() + 1, 0);
            const startingDay = firstDay.getDay();

            for (let i = 0; i < startingDay; i++) {{
                const emptyCell = document.createElement('div');
                emptyCell.className = 'calendar-day empty';
                grid.appendChild(emptyCell);
            }}

            for (let day = 1; day <= lastDay.getDate(); day++) {{
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day';
                dayCell.textContent = day;

                const cellDate = new Date(currentDisplayMonth.getFullYear(), currentDisplayMonth.getMonth(), day);

                // Disable past dates, weekends (Sat=6, Sun=0), and stat holidays
                const dayOfWeek = cellDate.getDay();
                if (cellDate < today || dayOfWeek === 0 || dayOfWeek === 6 || isStatHoliday(cellDate)) {{
                    dayCell.classList.add('disabled');
                }} else {{
                    dayCell.onclick = () => selectDate(cellDate);
                }}

                // Highlight selected date or week
                if (selectedDateType === 'week' && selectedWeekStart && selectedWeekEnd) {{
                    // Check if this date is within the selected week
                    const cellTime = cellDate.getTime();
                    const startTime = new Date(selectedWeekStart.getFullYear(), selectedWeekStart.getMonth(), selectedWeekStart.getDate()).getTime();
                    const endTime = new Date(selectedWeekEnd.getFullYear(), selectedWeekEnd.getMonth(), selectedWeekEnd.getDate()).getTime();
                    if (cellTime >= startTime && cellTime <= endTime) {{
                        dayCell.classList.add('selected');
                    }}
                }} else if (selectedDate &&
                    cellDate.getDate() === selectedDate.getDate() &&
                    cellDate.getMonth() === selectedDate.getMonth() &&
                    cellDate.getFullYear() === selectedDate.getFullYear()) {{
                    dayCell.classList.add('selected');
                }}

                grid.appendChild(dayCell);
            }}

            container.appendChild(grid);
        }}

        function navigateMonth(direction) {{
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const newMonth = new Date(currentDisplayMonth.getFullYear(), currentDisplayMonth.getMonth() + direction, 1);
            const currentMonth = new Date(today.getFullYear(), today.getMonth(), 1);
            const maxMonth = new Date(today.getFullYear(), today.getMonth() + 2, 1);

            if (newMonth >= currentMonth && newMonth <= maxMonth) {{
                currentDisplayMonth = newMonth;
                const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                                   'July', 'August', 'September', 'October', 'November', 'December'];
                const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                renderDesktopCalendar(today, monthNames, dayNames);
            }}
        }}

        // Date type selection - default to week
        let selectedDateType = 'week';

        function selectDateType(btn) {{
            // Remove selected from all date type buttons
            document.querySelectorAll('.date-type-btn').forEach(b => b.classList.remove('selected'));

            // Add selected to clicked button
            btn.classList.add('selected');

            selectedDateType = btn.getAttribute('data-type');

            // Store the date type
            const dateTypeInput = document.getElementById('staging-date-type');
            if (dateTypeInput) {{
                dateTypeInput.value = selectedDateType;
            }}

            // Show calendar (both options require calendar)
            const calendarContainer = document.getElementById('calendar-container');
            const dateDisplay = document.getElementById('staging-date-display');
            const dateInput = document.getElementById('staging-date');

            // Clear previous selection
            selectedDate = null;
            selectedWeekStart = null;
            selectedWeekEnd = null;

            calendarContainer.classList.add('visible');
            if (dateDisplay) dateDisplay.value = '';
            if (dateInput) dateInput.value = '';

            if (selectedDateType === 'week') {{
                if (dateDisplay) dateDisplay.placeholder = 'Select a week, we\\'ll select a date';
            }} else if (selectedDateType === 'date') {{
                if (dateDisplay) dateDisplay.placeholder = 'Select a staging date';
            }}

            generateCalendarMonths();
        }}

        function selectDate(date) {{
            selectedDate = date;

            // Update display based on date type
            const dateInput = document.getElementById('staging-date-display');
            const hiddenInput = document.getElementById('staging-date');

            if (selectedDateType === 'week') {{
                // Calculate the week: find Monday and Friday of the clicked date's week
                const dayOfWeek = date.getDay(); // 0=Sun, 1=Mon, ..., 6=Sat

                // Calculate Monday (start of week)
                let mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
                selectedWeekStart = new Date(date);
                selectedWeekStart.setDate(date.getDate() + mondayOffset);

                // Calculate Friday (end of week)
                selectedWeekEnd = new Date(selectedWeekStart);
                selectedWeekEnd.setDate(selectedWeekStart.getDate() + 4);

                // Format: "Dec 16 to Dec 20"
                if (dateInput) {{
                    const startOptions = {{ month: 'short', day: 'numeric' }};
                    const endOptions = {{ month: 'short', day: 'numeric' }};
                    const startStr = selectedWeekStart.toLocaleDateString('en-CA', startOptions);
                    const endStr = selectedWeekEnd.toLocaleDateString('en-CA', endOptions);
                    dateInput.value = startStr + ' to ' + endStr;
                }}
                if (hiddenInput) {{
                    hiddenInput.value = 'week-' + selectedWeekStart.toISOString().split('T')[0] + '-to-' + selectedWeekEnd.toISOString().split('T')[0];
                }}
            }} else {{
                // Clear week selection
                selectedWeekStart = null;
                selectedWeekEnd = null;

                // Show specific date
                if (dateInput) {{
                    const options = {{ weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' }};
                    dateInput.value = date.toLocaleDateString('en-CA', options);
                }}
                if (hiddenInput) {{
                    hiddenInput.value = date.toISOString().split('T')[0];
                }}
            }}

            // Regenerate calendars to update selection
            generateCalendarMonths();
        }}

        // Initialize Google Maps Autocomplete for property address
        function initAutocomplete() {{
            const addressInput = document.getElementById('property-address');
            if (!addressInput) return;

            const autocomplete = new google.maps.places.Autocomplete(addressInput, {{
                types: ['address'],
                componentRestrictions: {{ country: 'ca' }},
                fields: ['address_components', 'formatted_address']
            }});

            autocomplete.addListener('place_changed', function() {{
                const place = autocomplete.getPlace();
                if (!place.address_components) return;

                let streetNumber = '';
                let route = '';
                let city = '';
                let province = '';
                let postalCode = '';

                for (const component of place.address_components) {{
                    const types = component.types;
                    if (types.includes('street_number')) {{
                        streetNumber = component.long_name;
                    }} else if (types.includes('route')) {{
                        route = component.long_name;
                    }} else if (types.includes('locality')) {{
                        city = component.long_name;
                    }} else if (types.includes('administrative_area_level_1')) {{
                        province = component.short_name;
                    }} else if (types.includes('postal_code')) {{
                        postalCode = component.long_name;
                    }}
                }}

                // Format the address
                const fullAddress = `${{streetNumber}} ${{route}}, ${{city}}, ${{province}} ${{postalCode}}`.trim();
                addressInput.value = fullAddress;
            }});
        }}

        // Auto-formatting functions
        function formatName(input) {{
            let value = input.value.trim().replace(/\\s+/g, ' ');
            if (value) {{
                input.value = value.split(' ').map(word =>
                    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                ).join(' ');
            }}
        }}

        function formatEmail(input) {{
            input.value = input.value.trim().toLowerCase().replace(/\\s+/g, '');
            const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            const errorMsg = document.getElementById('email-error');
            if (input.value && !emailRegex.test(input.value)) {{
                input.setCustomValidity('Please enter a valid email address');
                if (errorMsg) errorMsg.style.display = 'block';
            }} else {{
                input.setCustomValidity('');
                if (errorMsg) errorMsg.style.display = 'none';
            }}
        }}

        function formatPhone(input) {{
            let value = input.value.replace(/\\D/g, '');
            if (value.startsWith('1') && value.length === 11) {{
                value = '1 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7);
            }} else if (value.length === 10) {{
                value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6);
            }}
            input.value = value;
        }}

        function formatPostalCode(input) {{
            let v = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            if (v.length > 3) {{
                v = v.substring(0, 3) + ' ' + v.substring(3, 6);
            }}
            input.value = v;

            // Validate Canadian postal code format
            if (v.length === 7) {{
                if (!/^[A-Z][0-9][A-Z] [0-9][A-Z][0-9]$/.test(v)) {{
                    input.setCustomValidity('Invalid postal code format');
                    input.style.borderColor = '#ff4444';
                }} else {{
                    input.setCustomValidity('');
                    input.style.borderColor = '';
                }}
            }}
        }}

        // Form submission
        async function submitReservation() {{
            const stagingDate = document.getElementById('staging-date').value;
            const propertyAddress = document.getElementById('property-address').value;
            const firstName = document.getElementById('first-name').value;
            const lastName = document.getElementById('last-name').value;
            const email = document.getElementById('email').value;
            const phone = document.getElementById('phone').value;
            const postalCode = document.getElementById('billing-zip').value;
            const specialRequests = document.getElementById('special-requests').value;

            // Validate required fields
            if (!stagingDate) {{
                alert('Please select a staging date');
                return;
            }}
            if (!propertyAddress) {{
                alert('Please enter the property address');
                return;
            }}
            if (!firstName || !lastName || !email || !phone) {{
                alert('Please fill in all guest information fields');
                return;
            }}

            const submitButton = document.querySelector('.reserve-now-btn');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';

            // Prepare form data
            const formData = {{
                stagingDate,
                propertyAddress,
                firstName,
                lastName,
                email,
                phone,
                postalCode,
                specialRequests,
                ...stagingData
            }};

            try {{
                // For now, just show success (API endpoint to be implemented)
                console.log('Reservation data:', formData);
                alert('Thank you! Your staging reservation request has been submitted. We will contact you shortly to confirm.');
                // window.location.href = '/staging-thanks';
            }} catch (error) {{
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }} finally {{
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }}
        }}

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {{
            loadStagingData();
            // Show calendar by default (week mode is selected)
            const calendarContainer = document.getElementById('calendar-container');
            if (calendarContainer) calendarContainer.classList.add('visible');
            const dateDisplay = document.getElementById('staging-date-display');
            if (dateDisplay) dateDisplay.placeholder = 'Select a week, we\\'ll select a date';
            generateCalendarMonths();
        }});

        // Make initAutocomplete globally available
        window.initAutocomplete = initAutocomplete;
    """

    content = Div(
        Div(
            Div(
                H1("Complete Your Reservation", cls="reserve-title"),
                cls="reserve-header"
            ),

            Div(
                # Left Column - Form Sections
                Div(
                    # Staging Information Section (moves to top on mobile)
                    Div(
                        H2(
                            Span("📅", cls="section-icon"),
                            "Staging Information",
                            cls="section-title"
                        ),
                        # Date Type Selector
                        Div(
                            Button("Pick a Week", cls="date-type-btn selected", data_type="week", onclick="selectDateType(this)"),
                            Button("Pick a Date", cls="date-type-btn", data_type="date", onclick="selectDateType(this)"),
                            cls="date-type-selector"
                        ),
                        Div(
                            Div(
                                Label("Staging Date *", cls="form-label", For="staging-date-display"),
                                Input(type="hidden", id="staging-date", name="staging-date"),
                                Input(type="hidden", id="staging-date-type", name="staging-date-type"),
                                # Desktop date picker
                                Div(
                                    Input(type="text", id="staging-date-display", cls="form-input date-input",
                                          placeholder="Select a staging date", readonly=True),
                                    Div(id="desktop-calendar", cls="desktop-date-picker",
                                        style="margin-top: 16px;"),
                                    cls="date-picker-container"
                                ),
                                # Mobile date picker - scrollable months
                                Div(
                                    Div(id="mobile-months", cls="mobile-months-container"),
                                    cls="mobile-date-picker"
                                ),
                                cls="form-group full-width"
                            ),
                            id="calendar-container",
                            cls="calendar-container"
                        ),
                        Div(
                            Div(
                                Label("Property Address *", cls="form-label", For="property-address"),
                                Input(type="text", id="property-address", cls="form-input", required=True,
                                      placeholder="Start typing the property address...",
                                      autocomplete="off"),
                                cls="form-group full-width"
                            ),
                            cls="form-grid"
                        ),
                        cls="reserve-section staging-info-section"
                    ),

                    # Add-ons Section
                    Div(
                        H2(
                            Span("✨", cls="section-icon"),
                            "Add-ons",
                            cls="section-title"
                        ),
                        Div(
                            Label(
                                Input(type="checkbox", value="photos", cls="addon-checkbox",
                                      onchange="handleAddonChange(this)"),
                                Div(
                                    Div(
                                        Span("Professional Photography"),
                                        Span("+$150", cls="addon-price"),
                                        cls="addon-title"
                                    ),
                                    Div("High-quality photos of your staged property", cls="addon-desc"),
                                    cls="addon-content"
                                ),
                                cls="addon-item"
                            ),
                            Label(
                                Input(type="checkbox", value="floorplan", cls="addon-checkbox",
                                      onchange="handleAddonChange(this)"),
                                Div(
                                    Div(
                                        Span("Floor Plan"),
                                        Span("+$200", cls="addon-price"),
                                        cls="addon-title"
                                    ),
                                    Div("Detailed floor plan with measurements", cls="addon-desc"),
                                    cls="addon-content"
                                ),
                                cls="addon-item"
                            ),
                            Label(
                                Input(type="checkbox", value="virtual-tour", cls="addon-checkbox",
                                      onchange="handleAddonChange(this)"),
                                Div(
                                    Div(
                                        Span("Virtual Tour"),
                                        Span("+$300", cls="addon-price"),
                                        cls="addon-title"
                                    ),
                                    Div("360-degree virtual walkthrough of the property", cls="addon-desc"),
                                    cls="addon-content"
                                ),
                                cls="addon-item"
                            ),
                            cls="addon-list"
                        ),
                        cls="reserve-section"
                    ),

                    # Guest Information Section
                    Div(
                        H2(
                            Span("👤", cls="section-icon"),
                            "Guest Information",
                            cls="section-title"
                        ),
                        Div(
                            Div(
                                Label("First Name *", cls="form-label", For="first-name"),
                                Input(type="text", id="first-name", cls="form-input", required=True,
                                      placeholder="Enter your first name",
                                      onblur="formatName(this)"),
                                cls="form-group"
                            ),
                            Div(
                                Label("Last Name *", cls="form-label", For="last-name"),
                                Input(type="text", id="last-name", cls="form-input", required=True,
                                      placeholder="Enter your last name",
                                      onblur="formatName(this)"),
                                cls="form-group"
                            ),
                            Div(
                                Label("Email *", cls="form-label", For="email"),
                                Input(type="email", id="email", cls="form-input", required=True,
                                      placeholder="your@email.com",
                                      onblur="formatEmail(this)"),
                                Div("Please enter a valid email address", id="email-error",
                                    style="display: none; color: #ff4444; font-size: 12px; margin-top: 4px;"),
                                cls="form-group"
                            ),
                            Div(
                                Label("Phone *", cls="form-label", For="phone"),
                                Input(type="tel", id="phone", cls="form-input", required=True,
                                      placeholder="(123) 456-7890",
                                      onblur="formatPhone(this)"),
                                cls="form-group"
                            ),
                            cls="form-grid"
                        ),
                        cls="reserve-section"
                    ),

                    # Payment Information Section
                    Div(
                        H2(
                            Span("💳", cls="section-icon"),
                            "Payment Information",
                            cls="section-title"
                        ),
                        Div(
                            Div(
                                Label("Postal Code *", cls="form-label", For="billing-zip"),
                                Input(type="text", id="billing-zip", cls="form-input", required=True,
                                      placeholder="A1A 1A1", maxlength="7",
                                      oninput="formatPostalCode(this)"),
                                cls="form-group"
                            ),
                            P("Payment will be collected upon confirmation of your staging date.",
                              style="font-size: 14px; color: var(--color-secondary); margin-top: 12px;"),
                            cls="form-grid"
                        ),
                        cls="reserve-section"
                    ),

                    # Additional Information Section
                    Div(
                        H2(
                            Span("📝", cls="section-icon"),
                            "Additional Information",
                            cls="section-title"
                        ),
                        Div(
                            Textarea(
                                id="special-requests",
                                cls="form-input",
                                placeholder="Any special requests or notes? (Optional)",
                                rows="4",
                                style="width: 100%; resize: vertical;"
                            ),
                            cls="form-group"
                        ),
                        cls="reserve-section"
                    ),

                    # Policies Section
                    Div(
                        H2(
                            Span("📋", cls="section-icon"),
                            "Policies",
                            cls="section-title"
                        ),
                        Div(
                            Div(
                                Span("📦", cls="policy-icon"),
                                Div(
                                    Div("Staging Period", cls="policy-title"),
                                    Div("Standard staging period is 60 days. Extensions available upon request.", cls="policy-desc"),
                                    cls="policy-content"
                                ),
                                cls="policy-item"
                            ),
                            Div(
                                Span("🔄", cls="policy-icon"),
                                Div(
                                    Div("Rescheduling", cls="policy-title"),
                                    Div("Free rescheduling up to 7 days before staging date.", cls="policy-desc"),
                                    cls="policy-content"
                                ),
                                cls="policy-item"
                            ),
                            Div(
                                Span("❌", cls="policy-icon"),
                                Div(
                                    Div("Cancellation", cls="policy-title"),
                                    Div("Full refund if cancelled 14+ days before staging. 50% refund for 7-14 days notice.", cls="policy-desc"),
                                    cls="policy-content"
                                ),
                                cls="policy-item"
                            ),
                            Div(
                                Span("🏠", cls="policy-icon"),
                                Div(
                                    Div("Property Access", cls="policy-title"),
                                    Div("Property must be clean, empty, and accessible on staging day.", cls="policy-desc"),
                                    cls="policy-content"
                                ),
                                cls="policy-item"
                            ),
                            cls="policy-list"
                        ),
                        cls="reserve-section"
                    ),

                    cls="reserve-sections"
                ),

                # Right Column - Staging Summary
                Div(
                    H2(
                        Span("📝", cls="section-icon"),
                        "Staging Summary",
                        cls="section-title"
                    ),
                    Div(
                        # Property Type
                        Div(
                            Span("Property Type", cls="price-label"),
                            Span("Not selected", cls="price-value", id="summary-property-type"),
                            cls="price-item"
                        ),
                        # Property Size
                        Div(
                            Span("Property Size", cls="price-label"),
                            Span("Not selected", cls="price-value", id="summary-property-size"),
                            cls="price-item"
                        ),
                        # Selected Areas and Items
                        Div(
                            Span("Selected Areas and Items", cls="price-label"),
                            Div(id="summary-areas-items", style="font-size: 13px;"),
                            cls="price-item"
                        ),
                        # Staging Fee
                        Div(
                            Span("Staging Fee", cls="price-label"),
                            Span("$0.00 CAD", cls="price-value", id="summary-total-fee"),
                            cls="price-item"
                        ),
                        # Total with Add-ons
                        Div(
                            Span("Total (with add-ons)", cls="total-label"),
                            Span("$0.00 CAD", cls="total-value", id="total-with-addons"),
                            cls="price-item"
                        ),
                        # Due Today
                        Div(
                            Span("Due Today", cls="total-label"),
                            Span("$500.00 CAD", cls="total-value", id="due-today-amount"),
                            cls="price-item"
                        ),
                    ),
                    cls="price-summary"
                ),

                cls="reserve-grid"
            ),

            # Reserve Now Button
            Div(
                Button("Reserve Now", cls="reserve-now-btn", onclick="submitReservation()"),
                style="text-align: center; padding: 20px 0;"
            ),

            cls="reserve-container"
        )
    )

    # Add Google Maps script
    content_with_scripts = Div(
        Script(src=f"https://maps.googleapis.com/maps/api/js?key={google_api_key}&libraries=places&callback=initAutocomplete", defer="defer") if google_api_key else "",
        content
    )

    return create_page(
        "Complete Your Reservation | Astra Staging",
        content_with_scripts,
        additional_styles=reserve_styles,
        additional_scripts=reserve_scripts,
        description="Complete your staging reservation with Astra Staging. Secure your staging date and provide property details.",
        keywords="staging reservation, home staging booking, Astra Staging reserve",
        hide_floating_buttons=True
    )
