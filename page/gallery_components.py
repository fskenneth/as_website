from fasthtml.common import *
import os
import glob as glob_module
import hashlib
from tools.instagram import get_cached_posts


def get_proxied_image_url(image_url: str) -> str:
    """Generate a proxied URL for an Instagram image"""
    url_hash = hashlib.md5(image_url.encode()).hexdigest()[:16]
    return f"/api/instagram-image/{url_hash}"


def get_portfolio_images():
    """Get all portfolio images dynamically from the static/images folder"""
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    pattern = os.path.join(static_path, 'slide_portfolio_*')
    files = sorted(glob_module.glob(pattern))
    return [f"/static/images/{os.path.basename(f)}" for f in files]


def get_before_after_images():
    """Get all before/after images dynamically from the static/images folder"""
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    pattern = os.path.join(static_path, 'slide_before_after_*')
    files = sorted(glob_module.glob(pattern))
    return [f"/static/images/{os.path.basename(f)}" for f in files]


def get_gallery_carousel_styles():
    """CSS styles for gallery carousels"""
    return """
    /* Gallery Carousel Styles */
    .gallery-carousel-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }

    .gallery-carousel-section.alt-bg {
        background: var(--bg-secondary);
    }

    .gallery-carousel-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(24px, 4vw, 36px);
        font-weight: 700;
        text-align: center;
        margin-bottom: 40px;
        color: var(--color-primary);
    }

    .gallery-carousel-container {
        position: relative;
        width: 100%;
        max-width: 960px;
        margin: 0 auto;
        background: transparent;
        overflow: hidden;
    }

    .gallery-carousel-viewport {
        position: relative;
        width: 100%;
        aspect-ratio: 3 / 2;
        overflow: hidden;
        background: var(--bg-secondary);
        border-radius: 12px;
        touch-action: pan-y;
    }

    /* Before/After carousel needs taller aspect ratio for vertical comparison images */
    #before-after-carousel .gallery-carousel-viewport {
        aspect-ratio: 3 / 4;
    }

    .gallery-carousel-track {
        display: flex;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        touch-action: pan-y;
    }

    .gallery-carousel-slide {
        min-width: 100%;
        width: 100%;
        height: 100%;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-secondary);
    }

    .gallery-carousel-slide img {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        border-radius: 12px;
    }

    .gallery-carousel-nav {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.6);
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        z-index: 10;
        transition: all 0.3s ease;
    }

    .gallery-carousel-nav:hover {
        background: rgba(0, 0, 0, 0.8);
        transform: translateY(-50%) scale(1.1);
    }

    .gallery-carousel-prev {
        left: 15px;
    }

    .gallery-carousel-next {
        right: 15px;
    }

    .gallery-carousel-nav span {
        line-height: 1;
        font-weight: 300;
        color: #fff;
    }

    /* Light theme carousel navigation */
    [data-theme="light"] .gallery-carousel-nav {
        background: rgba(255, 255, 255, 0.9);
        color: #000 !important;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    [data-theme="light"] .gallery-carousel-nav:hover {
        background: rgba(255, 255, 255, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    [data-theme="light"] .gallery-carousel-nav span {
        color: #000 !important;
    }

    /* Carousel indicators */
    .gallery-carousel-indicators {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 20px;
    }

    .gallery-carousel-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        padding: 0;
    }

    .gallery-carousel-indicator.active {
        background: var(--color-primary);
        transform: scale(1.2);
    }

    [data-theme="light"] .gallery-carousel-indicator {
        background: rgba(0, 0, 0, 0.2);
    }

    [data-theme="light"] .gallery-carousel-indicator.active {
        background: var(--color-primary);
    }

    /* Counter display */
    .gallery-carousel-counter {
        text-align: center;
        margin-top: 15px;
        font-size: 14px;
        color: var(--color-secondary);
    }

    /* Mobile responsive */
    @media (max-width: 767px) {
        .gallery-carousel-section {
            padding: 40px 20px;
        }

        .gallery-carousel-title {
            font-size: 24px;
            margin-bottom: 30px;
        }

        .gallery-carousel-viewport {
            border-radius: 8px;
            aspect-ratio: 3 / 2;
        }

        /* Before/After stays taller on mobile too */
        #before-after-carousel .gallery-carousel-viewport {
            aspect-ratio: 3 / 4;
        }

        .gallery-carousel-slide img {
            border-radius: 8px;
        }

        .gallery-carousel-nav {
            width: 40px;
            height: 40px;
            font-size: 22px;
        }

        .gallery-carousel-prev {
            left: 10px;
        }

        .gallery-carousel-next {
            right: 10px;
        }

        .gallery-carousel-indicators {
            gap: 6px;
            margin-top: 15px;
        }

        .gallery-carousel-indicator {
            width: 8px;
            height: 8px;
        }
    }
    """


def get_gallery_carousel_scripts():
    """JavaScript for gallery carousels"""
    return """
    // Gallery Carousel Management
    const galleryCarouselStates = {};

    function initializeGalleryCarousel(carouselId, images) {
        const container = document.getElementById(carouselId);
        if (!container) return;

        const track = container.querySelector('.gallery-carousel-track');
        const indicatorsContainer = container.querySelector('.gallery-carousel-indicators');
        const counter = container.querySelector('.gallery-carousel-counter');

        if (!track) return;

        // Initialize state
        galleryCarouselStates[carouselId] = {
            currentIndex: 0,
            totalSlides: images.length,
            isTransitioning: false
        };

        // Clear existing content
        track.innerHTML = '';
        if (indicatorsContainer) indicatorsContainer.innerHTML = '';

        // Create slides
        images.forEach((imageSrc, index) => {
            const slide = document.createElement('div');
            slide.className = 'gallery-carousel-slide';
            slide.innerHTML = `<img src="${imageSrc}" alt="Gallery Image ${index + 1}" loading="${index === 0 ? 'eager' : 'lazy'}">`;
            track.appendChild(slide);

            // Create indicator
            if (indicatorsContainer && images.length <= 20) {
                const indicator = document.createElement('button');
                indicator.className = 'gallery-carousel-indicator' + (index === 0 ? ' active' : '');
                indicator.onclick = () => goToGallerySlide(carouselId, index);
                indicatorsContainer.appendChild(indicator);
            }
        });

        // Update counter
        if (counter) {
            counter.textContent = `1 / ${images.length}`;
        }

        // Set up infinite carousel if more than 1 image
        if (images.length > 1) {
            const firstSlide = track.firstElementChild.cloneNode(true);
            const lastSlide = track.lastElementChild.cloneNode(true);
            firstSlide.classList.add('clone');
            lastSlide.classList.add('clone');
            track.appendChild(firstSlide);
            track.insertBefore(lastSlide, track.firstElementChild);

            // Position at first real slide
            track.style.transition = 'none';
            track.style.transform = 'translateX(-100%)';
            track.offsetHeight;
            requestAnimationFrame(() => {
                track.style.transition = '';
            });

            // Enable touch handlers
            initializeGalleryCarouselTouchHandlers(carouselId, track);
        }
    }

    function navigateGalleryCarousel(carouselId, direction) {
        const state = galleryCarouselStates[carouselId];
        if (!state || state.isTransitioning) return;

        const container = document.getElementById(carouselId);
        if (!container) return;

        const track = container.querySelector('.gallery-carousel-track');
        if (!track) return;

        const hasClones = track.querySelector('.clone') !== null;
        state.isTransitioning = true;

        if (direction === 'next') {
            state.currentIndex++;
        } else {
            state.currentIndex--;
        }

        updateGalleryCarouselPosition(carouselId);

        setTimeout(() => {
            state.isTransitioning = false;
        }, 550);
    }

    function goToGallerySlide(carouselId, index) {
        const state = galleryCarouselStates[carouselId];
        if (!state || state.isTransitioning || index === state.currentIndex) return;

        state.currentIndex = index;
        updateGalleryCarouselPosition(carouselId);
    }

    function updateGalleryCarouselPosition(carouselId) {
        const state = galleryCarouselStates[carouselId];
        if (!state) return;

        const container = document.getElementById(carouselId);
        if (!container) return;

        const track = container.querySelector('.gallery-carousel-track');
        const indicatorsContainer = container.querySelector('.gallery-carousel-indicators');
        const counter = container.querySelector('.gallery-carousel-counter');
        if (!track) return;

        const slides = track.querySelectorAll('.gallery-carousel-slide:not(.clone)');
        const hasClones = track.querySelector('.clone') !== null;

        let offset;
        if (hasClones) {
            offset = (state.currentIndex + 1) * -100;

            if (state.currentIndex >= slides.length) {
                track.style.transform = `translateX(${offset}%)`;
                setTimeout(() => {
                    track.style.transition = 'none';
                    state.currentIndex = 0;
                    track.style.transform = 'translateX(-100%)';
                    setTimeout(() => { track.style.transition = ''; }, 50);
                    updateGalleryIndicators(carouselId, indicatorsContainer, counter, slides.length);
                }, 500);
            } else if (state.currentIndex < 0) {
                track.style.transform = `translateX(${offset}%)`;
                setTimeout(() => {
                    track.style.transition = 'none';
                    state.currentIndex = slides.length - 1;
                    track.style.transform = `translateX(${-100 * slides.length}%)`;
                    setTimeout(() => { track.style.transition = ''; }, 50);
                    updateGalleryIndicators(carouselId, indicatorsContainer, counter, slides.length);
                }, 500);
            } else {
                track.style.transform = `translateX(${offset}%)`;
            }
        } else {
            offset = state.currentIndex * -100;
            track.style.transform = `translateX(${offset}%)`;
        }

        updateGalleryIndicators(carouselId, indicatorsContainer, counter, slides.length);
    }

    function updateGalleryIndicators(carouselId, indicatorsContainer, counter, totalSlides) {
        const state = galleryCarouselStates[carouselId];
        if (!state) return;

        const displayIndex = ((state.currentIndex % totalSlides) + totalSlides) % totalSlides;

        if (indicatorsContainer) {
            const indicators = indicatorsContainer.querySelectorAll('.gallery-carousel-indicator');
            indicators.forEach((ind, idx) => {
                ind.classList.toggle('active', idx === displayIndex);
            });
        }

        if (counter) {
            counter.textContent = `${displayIndex + 1} / ${totalSlides}`;
        }
    }

    function initializeGalleryCarouselTouchHandlers(carouselId, track) {
        if (!track) return;

        let touchStartX = 0;
        let touchCurrentX = 0;
        let isDragging = false;
        let startTransform = 0;

        function handleTouchStart(e) {
            const state = galleryCarouselStates[carouselId];
            if (!state || state.isTransitioning) return;

            touchStartX = e.touches[0].clientX;
            touchCurrentX = touchStartX;
            isDragging = true;

            const hasClones = track.querySelector('.clone') !== null;
            if (hasClones) {
                startTransform = -(state.currentIndex + 1) * 100;
            } else {
                startTransform = -state.currentIndex * 100;
            }

            track.style.transition = 'none';
        }

        function handleTouchMove(e) {
            if (!isDragging) return;

            touchCurrentX = e.touches[0].clientX;
            const diff = touchCurrentX - touchStartX;
            const trackWidth = track.offsetWidth;
            const percentMove = (diff / trackWidth) * 100;

            const newTransform = startTransform + percentMove;
            track.style.transform = `translateX(${newTransform}%)`;
        }

        function handleTouchEnd(e) {
            if (!isDragging) return;

            isDragging = false;
            const diff = touchCurrentX - touchStartX;
            const threshold = 50;

            track.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';

            if (Math.abs(diff) > threshold) {
                if (diff > 0) {
                    navigateGalleryCarousel(carouselId, 'prev');
                } else {
                    navigateGalleryCarousel(carouselId, 'next');
                }
            } else {
                updateGalleryCarouselPosition(carouselId);
            }
        }

        track.addEventListener('touchstart', handleTouchStart, { passive: true });
        track.addEventListener('touchmove', handleTouchMove, { passive: true });
        track.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
    """


def portfolio_carousel_section(title="Portfolio", alt_bg=False):
    """Create a portfolio carousel section - dynamically loads images"""
    images = get_portfolio_images()
    carousel_id = "portfolio-carousel"

    # Generate JavaScript data for images
    images_js = "[" + ",".join([f'"{img}"' for img in images]) + "]"

    section_class = "gallery-carousel-section"
    if alt_bg:
        section_class += " alt-bg"

    return Section(
        Div(
            H2(title, cls="gallery-carousel-title"),
            Div(
                Div(
                    Button(
                        Span("‹"),
                        cls="gallery-carousel-nav gallery-carousel-prev",
                        onclick=f"navigateGalleryCarousel('{carousel_id}', 'prev')",
                        **{"aria-label": "Previous slide"}
                    ),
                    Button(
                        Span("›"),
                        cls="gallery-carousel-nav gallery-carousel-next",
                        onclick=f"navigateGalleryCarousel('{carousel_id}', 'next')",
                        **{"aria-label": "Next slide"}
                    ),
                    Div(cls="gallery-carousel-track"),
                    cls="gallery-carousel-viewport"
                ),
                Div(cls="gallery-carousel-counter"),
                cls="gallery-carousel-container",
                id=carousel_id
            ),
            cls="container"
        ),
        Script(f"document.addEventListener('DOMContentLoaded', function() {{ initializeGalleryCarousel('{carousel_id}', {images_js}); }});"),
        cls=section_class
    )


def before_after_carousel_section(title="Before and After", alt_bg=True):
    """Create a before/after carousel section - dynamically loads images"""
    images = get_before_after_images()
    carousel_id = "before-after-carousel"

    # Generate JavaScript data for images
    images_js = "[" + ",".join([f'"{img}"' for img in images]) + "]"

    section_class = "gallery-carousel-section"
    if alt_bg:
        section_class += " alt-bg"

    return Section(
        Div(
            H2(title, cls="gallery-carousel-title"),
            Div(
                Div(
                    Button(
                        Span("‹"),
                        cls="gallery-carousel-nav gallery-carousel-prev",
                        onclick=f"navigateGalleryCarousel('{carousel_id}', 'prev')",
                        **{"aria-label": "Previous slide"}
                    ),
                    Button(
                        Span("›"),
                        cls="gallery-carousel-nav gallery-carousel-next",
                        onclick=f"navigateGalleryCarousel('{carousel_id}', 'next')",
                        **{"aria-label": "Next slide"}
                    ),
                    Div(cls="gallery-carousel-track"),
                    cls="gallery-carousel-viewport"
                ),
                Div(cls="gallery-carousel-counter"),
                cls="gallery-carousel-container",
                id=carousel_id
            ),
            cls="container"
        ),
        Script(f"document.addEventListener('DOMContentLoaded', function() {{ initializeGalleryCarousel('{carousel_id}', {images_js}); }});"),
        cls=section_class
    )


def instagram_section(alt_bg=False):
    """Instagram feed section showing latest posts - reusable module"""
    INSTAGRAM_USERNAME = "astra_home_staging_gta"
    INSTAGRAM_URL = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/"

    # Get cached posts (refreshes every hour)
    posts = get_cached_posts(max_age_seconds=3600)

    # Instagram icon SVG
    instagram_icon = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
    </svg>'''

    # Video play icon SVG
    video_icon = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 5v14l11-7z"/>
    </svg>'''

    section_class = "instagram-section"
    if alt_bg:
        section_class += " alt-bg"

    if posts:
        # Create grid items for each post
        grid_items = []
        for post in posts[:12]:  # Show up to 12 posts
            # Use proxied image URL to avoid CORS issues
            image_url = post.get('image_url', '')
            proxied_url = get_proxied_image_url(image_url) if image_url else ''

            item_content = [
                A(
                    Img(
                        src=proxied_url,
                        alt=post.get('caption', 'Instagram post')[:100] if post.get('caption') else 'Instagram post',
                        loading="lazy"
                    ),
                    href=post.get('url', INSTAGRAM_URL),
                    target="_blank",
                    rel="noopener noreferrer"
                )
            ]

            # Add video indicator if it's a video/reel
            if post.get('is_video'):
                item_content.append(
                    Div(
                        NotStr(video_icon),
                        cls="video-indicator"
                    )
                )

            grid_items.append(Div(*item_content, cls="instagram-item"))

        content = Div(
            H2(
                A("Check Our Instagram", href=INSTAGRAM_URL, target="_blank"),
                cls="instagram-title"
            ),
            Div(*grid_items, cls="instagram-grid"),
            Div(
                A(
                    NotStr(instagram_icon),
                    "Follow @astra_home_staging_gta",
                    href=INSTAGRAM_URL,
                    target="_blank",
                    rel="noopener noreferrer",
                    cls="instagram-follow-btn"
                ),
                cls="instagram-actions"
            ),
            cls="container"
        )
    else:
        # Fallback if posts couldn't be loaded
        content = Div(
            H2(
                A("Check Our Instagram", href=INSTAGRAM_URL, target="_blank"),
                cls="instagram-title"
            ),
            Div(
                P("Follow us on Instagram to see our latest staging projects!"),
                A(
                    NotStr(instagram_icon),
                    "Follow @astra_home_staging_gta",
                    href=INSTAGRAM_URL,
                    target="_blank",
                    rel="noopener noreferrer",
                    cls="instagram-follow-btn"
                ),
                cls="instagram-error"
            ),
            cls="container"
        )

    return Section(content, cls=section_class)
