"""Staging Design Page - Visual presentation of staging design with areas and items"""
from fasthtml.common import *


def design_page(req: Request, staging_id: str = None):
    """Design page showing staging areas with photos and items"""

    # Get the title
    page_title = "Staging Design | Astra Staging"

    # Create the main content without navbar/footer
    content = Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title(page_title),
            Link(rel="icon", href="/static/images/astra_staging_logo.png", type="image/png"),
            Style(get_design_styles()),
            Script(get_design_scripts(staging_id))
        ),
        Body(
            # Sticky Header Container
            Div(
                H1("Staging Design", cls="design-title"),
                P("Review your staging design with photos and selected items", cls="design-subtitle"),

                # Area Tabs
                Div(
                    id="area-tabs",
                    cls="area-tabs"
                ),

                cls="sticky-header"
            ),

            # Tab Content Container (scrollable)
            Div(
                # Carousel Container (will be inserted here per tab)
                Div(
                    id="carousel-container",
                    cls="carousel-container"
                ),

                # Items Grid (scrollable)
                Div(
                    id="items-container",
                    cls="items-container"
                ),

                cls="content-wrapper"
            ),

            cls="design-page"
        )
    )

    return content


def get_design_styles():
    """CSS styles for design page"""
    return """
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --color-primary: #1a1a1a;
        --color-secondary: #6c757d;
        --border-color: #dee2e6;
        --border-hover: #adb5bd;
    }

    [data-theme="dark"] {
        --bg-primary: #1a1a1a;
        --bg-secondary: #2d2d2d;
        --color-primary: #ffffff;
        --color-secondary: #adb5bd;
        --border-color: #404040;
        --border-hover: #606060;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html {
        scrollbar-width: none;
        -ms-overflow-style: none;
    }

    html::-webkit-scrollbar {
        display: none;
    }

    body.design-page {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        background: var(--bg-primary);
        color: var(--color-primary);
        overflow-y: auto;
        overflow-x: hidden;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }

    body.design-page::-webkit-scrollbar {
        display: none;
    }

    /* Header (no longer fixed) */
    .sticky-header {
        background: var(--bg-primary);
        padding: 20px;
    }

    .design-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 8px;
        text-align: center;
    }

    .design-subtitle {
        font-size: 14px;
        color: var(--color-secondary);
        margin-bottom: 16px;
        text-align: center;
    }

    /* Area Tabs */
    .area-tabs {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 8px;
        scrollbar-width: none;
    }

    .area-tabs::-webkit-scrollbar {
        display: none;
    }

    .area-tab {
        padding: 10px 16px;
        border-radius: 8px;
        background: var(--bg-secondary);
        color: var(--color-secondary);
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.2s ease;
        border: 2px solid transparent;
        flex-shrink: 0;
    }

    .area-tab:hover {
        background: var(--bg-primary);
        border-color: var(--border-hover);
    }

    .area-tab.active {
        background: #4CAF50;
        color: white;
        border-color: #4CAF50;
    }

    /* Content Wrapper */
    .content-wrapper {
        max-width: 100%;
        margin: 0 auto;
    }

    /* Carousel Container */
    .carousel-container {
        padding: 0 20px 20px;
        max-width: 100%;
        margin: 0 auto;
    }

    .area-carousel {
        position: relative;
        width: 100%;
        aspect-ratio: 4/3;
        background: var(--bg-primary);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-theme="dark"] .area-carousel {
        background: #000000;
    }

    .carousel-track {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .carousel-slide {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.25s ease-out;
    }

    .carousel-slide img {
        max-width: 100%;
        max-height: 100%;
        height: auto;
        width: auto;
        object-fit: contain;
    }

    .carousel-slide-prev {
        transform: translateX(calc(-100% - 10px));
    }

    .carousel-slide-current {
        transform: translateX(0);
    }

    .carousel-slide-next {
        transform: translateX(calc(100% + 10px));
    }

    /* Carousel Navigation - Same as photo modal */
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

    .carousel-dots {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 6px;
        z-index: 10;
    }

    .carousel-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        transition: background 0.2s;
    }

    .carousel-dot.active {
        background: white;
    }

    /* Items Container - Scrollable */
    .items-container {
        padding: 0 20px 40px;
        max-width: 100%;
        margin: 0 auto;
    }

    /* Items Grid - Always 3 columns */
    .items-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
    }

    /* Item Card - Same as items modal */
    .item-btn {
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

    .item-qty-display {
        font-size: 12px;
        font-weight: 600;
        color: #4CAF50;
        margin-top: 2px;
    }

    /* No Photos/Items Message */
    .no-content {
        padding: 40px 20px;
        text-align: center;
        color: var(--color-secondary);
        font-size: 14px;
        background: var(--bg-secondary);
        border-radius: 12px;
    }

    /* Mobile Specific */
    @media (max-width: 767px) {
        .sticky-header {
            padding: 15px;
        }

        .design-title {
            font-size: 24px;
        }

        .design-subtitle {
            font-size: 13px;
        }

        .carousel-container {
            padding: 0 15px 15px;
        }

        .items-container {
            padding: 0 15px 30px;
        }
    }

    /* Desktop Specific */
    @media (min-width: 768px) {
        body.design-page {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .sticky-header {
            padding: 24px 40px;
            width: 100%;
            max-width: 960px;
        }

        .design-title {
            font-size: 32px;
        }

        .area-tabs {
            padding-left: 0;
            padding-right: 0;
        }

        .content-wrapper {
            max-width: 960px;
            width: 100%;
        }

        .carousel-container {
            padding: 0 40px 24px;
        }

        .items-container {
            padding: 0 40px 40px;
        }

        .items-grid {
            gap: 8px;
        }
    }
    """


def get_design_scripts(staging_id):
    """JavaScript for design page"""
    return f"""
    // SVG icons for items
    const svgIcons = {{
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
        "Patio Set": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2"><rect x="12" y="22" width="40" height="14" rx="2"/><line x1="16" y1="36" x2="16" y2="48"/><line x1="48" y1="36" x2="48" y2="48"/><rect x="4" y="28" width="10" height="12" rx="2"/><rect x="50" y="28" width="10" height="12" rx="2"/></svg>'
    }};

    // Global state
    let currentStaging = null;
    let currentAreaIndex = 0;
    let carouselIndices = {{}};
    let touchStartX = 0;
    let touchEndX = 0;
    let isDragging = false;
    let currentTranslateX = 0;

    // Load staging data
    async function loadStagingData() {{
        try {{
            const stagingId = new URLSearchParams(window.location.search).get('id');
            if (!stagingId) {{
                window.location.href = '/portal';
                return;
            }}

            const response = await fetch(`/api/stagings/${{stagingId}}`);
            if (!response.ok) {{
                throw new Error('Failed to load staging data');
            }}

            const data = await response.json();
            currentStaging = transformStagingData(data.staging);
            renderDesign();
            initTouchListeners();
        }} catch (error) {{
            console.error('Error loading staging:', error);
            alert('Failed to load staging data');
        }}
    }}

    // Transform staging data from API format to design format
    function transformStagingData(staging) {{
        const selectedAreas = JSON.parse(staging.selected_areas || '[]');
        const selectedItems = JSON.parse(staging.selected_items || '{{}}');
        const areaPhotos = JSON.parse(staging.area_photos || '{{}}');

        // Area name mapping
        const areaNames = {{
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
            'basement-1st-bed': 'Basement 1st Bed',
            'basement-2nd-bed': 'Basement 2nd Bed'
        }};

        // Item ID to name and price mapping
        const itemsMap = {{
            'sofa': {{ name: 'Sofa', price: 250 }},
            'accent-chair': {{ name: 'Accent Chair', price: 100 }},
            'coffee-table': {{ name: 'Coffee Table', price: 100 }},
            'end-table': {{ name: 'End Table', price: 50 }},
            'console': {{ name: 'Console', price: 75 }},
            'bench': {{ name: 'Bench', price: 65 }},
            'area-rug': {{ name: 'Area Rug', price: 80 }},
            'lamp': {{ name: 'Lamp', price: 40 }},
            'cushion': {{ name: 'Cushion', price: 15 }},
            'throw': {{ name: 'Throw', price: 18 }},
            'table-decor': {{ name: 'Table Decor', price: 10 }},
            'wall-art': {{ name: 'Wall Art', price: 40 }},
            'formal-dining-set': {{ name: 'Formal Dining Set', price: 400 }},
            'bar-stool': {{ name: 'Bar Stool', price: 40 }},
            'casual-dining-set': {{ name: 'Casual Dining Set', price: 250 }},
            'queen-bed-frame': {{ name: 'Queen Bed Frame', price: 20 }},
            'queen-headboard': {{ name: 'Queen Headboard', price: 90 }},
            'queen-mattress': {{ name: 'Queen Mattress', price: 50 }},
            'queen-beddings': {{ name: 'Queen Beddings', price: 120 }},
            'king-bed-frame': {{ name: 'King Bed Frame', price: 20 }},
            'king-headboard': {{ name: 'King Headboard', price: 130 }},
            'king-mattress': {{ name: 'King Mattress', price: 50 }},
            'king-beddings': {{ name: 'King Beddings', price: 150 }},
            'double-bed-frame': {{ name: 'Double Bed Frame', price: 20 }},
            'double-headboard': {{ name: 'Double Headboard', price: 80 }},
            'double-mattress': {{ name: 'Double Mattress', price: 50 }},
            'double-bedding': {{ name: 'Double Bedding', price: 120 }},
            'night-stand': {{ name: 'Night Stand', price: 60 }},
            'single-bed-frame': {{ name: 'Single Bed Frame', price: 20 }},
            'single-headboard': {{ name: 'Single Headboard', price: 75 }},
            'single-mattress': {{ name: 'Single Mattress', price: 50 }},
            'single-beddings': {{ name: 'Single Beddings', price: 80 }},
            'desk': {{ name: 'Desk', price: 100 }},
            'chair': {{ name: 'Chair', price: 50 }},
            'patio-set': {{ name: 'Patio Set', price: 150 }}
        }};

        // Get default items based on property type and size
        const propertyType = staging.property_type;
        const propertySize = staging.property_size;

        const areas = {{}};
        selectedAreas.forEach(areaKey => {{
            // Convert items object to array with details
            const areaItemsObj = selectedItems[areaKey] || {{}};
            const itemsArray = [];

            // If there are selected items, use them
            if (Object.keys(areaItemsObj).length > 0) {{
                for (const [itemId, count] of Object.entries(areaItemsObj)) {{
                    const itemInfo = itemsMap[itemId];
                    if (itemInfo && count > 0) {{
                        itemsArray.push({{
                            id: itemId,
                            name: itemInfo.name,
                            price: itemInfo.price,
                            count: count
                        }});
                    }}
                }}
            }} else {{
                // Otherwise, use default items
                const defaults = getDefaultItemsForArea(propertyType, propertySize, areaKey, itemsMap);
                itemsArray.push(...defaults);
            }}

            areas[areaKey] = {{
                name: areaNames[areaKey] || areaKey,
                items: itemsArray,
                photos: areaPhotos[areaKey] || []
            }};
        }});

        return {{ areas }};
    }}

    // Get default items for an area based on property type and size
    function getDefaultItemsForArea(propertyType, propertySize, area, itemsMap) {{
        const itemColumns = ['sofa','accent-chair','coffee-table','end-table','console','bench','area-rug','lamp','cushion','throw','table-decor','wall-art','formal-dining-set','bar-stool','casual-dining-set','queen-bed-frame','queen-headboard','queen-mattress','queen-beddings','king-bed-frame','king-headboard','king-mattress','king-beddings','double-bed-frame','double-headboard','double-mattress','double-bedding','night-stand','single-bed-frame','single-headboard','single-mattress','single-beddings','desk','chair','patio-set'];

        const defaultData = {{
            'house': {{
                '3000-4000': {{
                    'living-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    'dining-room': [0,0,0,0,1,0,1,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    'family-room': [1,2,1,2,1,1,1,2,4,1,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                }}
            }}
        }};

        const typeDefaults = defaultData[propertyType];
        if (!typeDefaults) return [];

        const sizeDefaults = typeDefaults[propertySize];
        if (!sizeDefaults) return [];

        const areaDefaults = sizeDefaults[area];
        if (!areaDefaults) return [];

        const items = [];
        areaDefaults.forEach((count, index) => {{
            if (count > 0) {{
                const itemId = itemColumns[index];
                const itemInfo = itemsMap[itemId];
                if (itemInfo) {{
                    items.push({{
                        id: itemId,
                        name: itemInfo.name,
                        price: itemInfo.price,
                        count: count
                    }});
                }}
            }}
        }});

        return items;
    }}

    // Render the design interface
    function renderDesign() {{
        if (!currentStaging || !currentStaging.areas) {{
            document.getElementById('area-tabs').innerHTML = '<p class="no-content">No areas selected</p>';
            return;
        }}

        const areas = currentStaging.areas;
        const areaKeys = Object.keys(areas);

        if (areaKeys.length === 0) {{
            document.getElementById('area-tabs').innerHTML = '<p class="no-content">No areas selected</p>';
            return;
        }}

        // Render tabs
        const tabsHtml = areaKeys.map((areaKey, index) => {{
            const area = areas[areaKey];
            return `<div class="area-tab ${{index === 0 ? 'active' : ''}}" onclick="switchTab(${{index}})">${{area.name}}</div>`;
        }}).join('');

        document.getElementById('area-tabs').innerHTML = tabsHtml;

        // Initialize carousel indices
        areaKeys.forEach((_, index) => {{
            carouselIndices[index] = 0;
        }});

        // Render first tab content
        switchTab(0);
    }}

    // Switch between area tabs
    function switchTab(index) {{
        currentAreaIndex = index;

        // Update tab active state
        document.querySelectorAll('.area-tab').forEach((tab, i) => {{
            tab.classList.toggle('active', i === index);
        }});

        // Render content for selected tab
        const areas = currentStaging.areas;
        const areaKeys = Object.keys(areas);
        const areaKey = areaKeys[index];
        const area = areas[areaKey];

        renderAreaContent(area, index);
    }}

    // Render area content (photos + items)
    function renderAreaContent(area, index) {{
        const hasPhotos = area.photos && area.photos.length > 0;
        const hasItems = area.items && area.items.length > 0;

        // Render carousel
        let carouselHtml = '';
        if (hasPhotos) {{
            const currentPhotoIndex = carouselIndices[index] || 0;
            const prevIndex = currentPhotoIndex > 0 ? currentPhotoIndex - 1 : null;
            const nextIndex = currentPhotoIndex < area.photos.length - 1 ? currentPhotoIndex + 1 : null;

            let slidesHtml = '';

            // Previous slide
            if (prevIndex !== null) {{
                slidesHtml += `<div class="carousel-slide carousel-slide-prev"><img src="${{area.photos[prevIndex]}}" alt="${{area.name}} photo ${{prevIndex + 1}}"></div>`;
            }}

            // Current slide
            slidesHtml += `<div class="carousel-slide carousel-slide-current"><img src="${{area.photos[currentPhotoIndex]}}" alt="${{area.name}} photo ${{currentPhotoIndex + 1}}"></div>`;

            // Next slide
            if (nextIndex !== null) {{
                slidesHtml += `<div class="carousel-slide carousel-slide-next"><img src="${{area.photos[nextIndex]}}" alt="${{area.name}} photo ${{nextIndex + 1}}"></div>`;
            }}

            const dotsHtml = area.photos.map((_, photoIndex) => {{
                return `<div class="carousel-dot ${{photoIndex === currentPhotoIndex ? 'active' : ''}}" onclick="goToSlide(${{index}}, ${{photoIndex}})"></div>`;
            }}).join('');

            const isMobile = window.innerWidth <= 767;

            carouselHtml = `
                <div class="area-carousel" id="carousel-${{index}}">
                    <div class="carousel-track" id="carousel-track-${{index}}">
                        ${{slidesHtml}}
                    </div>
                    ${{area.photos.length > 1 ? `
                        <button class="carousel-nav-btn carousel-prev" onclick="prevSlide(${{index}})" style="display: ${{isMobile ? 'none' : 'flex'}}">‹</button>
                        <button class="carousel-nav-btn carousel-next" onclick="nextSlide(${{index}})" style="display: ${{isMobile ? 'none' : 'flex'}}">›</button>
                        <div class="carousel-dots">${{dotsHtml}}</div>
                    ` : ''}}
                </div>
            `;
        }} else {{
            carouselHtml = '<div class="no-content">No photos uploaded for this area</div>';
        }}

        document.getElementById('carousel-container').innerHTML = carouselHtml;

        // Add touch event listeners for swipe
        if (hasPhotos) {{
            const isMobile = window.innerWidth <= 767;
            if (isMobile) {{
                const track = document.getElementById(`carousel-track-${{index}}`);
                if (track) {{
                    track.addEventListener('touchstart', handleTouchStart, {{ passive: true }});
                    track.addEventListener('touchmove', handleTouchMove, {{ passive: true }});
                    track.addEventListener('touchend', handleTouchEnd, {{ passive: false }});
                }}
            }}
        }}

        // Render items
        let itemsHtml = '';
        if (hasItems) {{
            itemsHtml = `
                <div class="items-grid">
                    ${{area.items.map(item => {{
                        const icon = svgIcons[item.name] || '';
                        const totalPrice = item.price * item.count;
                        return `
                            <div class="item-btn selected">
                                <div class="item-btn-content">
                                    <div class="item-emoji">${{icon}}</div>
                                    <div class="item-name">${{item.name}}</div>
                                    <div class="item-unit-price">$${{item.price}}</div>
                                    <div class="item-total-price">$${{totalPrice}}</div>
                                    <div class="item-qty-display">Qty: ${{item.count}}</div>
                                </div>
                            </div>
                        `;
                    }}).join('')}}
                </div>
            `;
        }} else {{
            itemsHtml = '<div class="no-content">No items selected for this area</div>';
        }}

        document.getElementById('items-container').innerHTML = itemsHtml;
    }}

    // Carousel navigation
    function nextSlide(areaIndex) {{
        updateCarousel(areaIndex, 1);
    }}

    function prevSlide(areaIndex) {{
        updateCarousel(areaIndex, -1);
    }}

    function goToSlide(areaIndex, slideIndex) {{
        const areas = currentStaging.areas;
        const areaKeys = Object.keys(areas);
        const area = areas[areaKeys[areaIndex]];

        carouselIndices[areaIndex] = slideIndex;

        // Re-render the area content to update the three-slide system
        renderAreaContent(area, areaIndex);
    }}

    function updateCarousel(areaIndex, direction) {{
        const areas = currentStaging.areas;
        const areaKeys = Object.keys(areas);
        const area = areas[areaKeys[areaIndex]];
        const photos = area.photos || [];

        if (photos.length === 0) return;

        const currentIndex = carouselIndices[areaIndex] || 0;
        let nextIndex = currentIndex + direction;

        if (nextIndex < 0) nextIndex = photos.length - 1;
        if (nextIndex >= photos.length) nextIndex = 0;

        // Update index and re-render
        carouselIndices[areaIndex] = nextIndex;
        renderAreaContent(area, areaIndex);
    }}

    // Touch/swipe support for carousel
    function initTouchListeners() {{
        // Touch listeners are now added per-carousel in renderAreaContent
    }}

    function handleTouchStart(e) {{
        touchStartX = e.changedTouches[0].screenX;
        isDragging = true;
    }}

    function handleTouchMove(e) {{
        if (!isDragging) return;
        // Prevent default to avoid scrolling
        e.preventDefault();
    }}

    function handleTouchEnd(e) {{
        if (!isDragging) return;
        isDragging = false;

        const track = e.target.closest('.carousel-track');
        if (!track) return;

        touchEndX = e.changedTouches[0].screenX;

        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        const areas = currentStaging.areas;
        const areaKeys = Object.keys(areas);
        const area = areas[areaKeys[currentAreaIndex]];
        const photos = area.photos || [];
        const currentPhotoIndex = carouselIndices[currentAreaIndex] || 0;

        if (Math.abs(diff) > swipeThreshold) {{
            if (diff > 0 && currentPhotoIndex < photos.length - 1) {{
                // Swipe left - go to next
                updateCarousel(currentAreaIndex, 1);
            }} else if (diff < 0 && currentPhotoIndex > 0) {{
                // Swipe right - go to previous
                updateCarousel(currentAreaIndex, -1);
            }}
        }}
    }}

    // Show notification toast
    function showNotification(message, type = 'info') {{
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${{type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'}};
            color: white;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {{
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }}, 3000);
    }}

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', loadStagingData);
    """
