from fasthtml.common import *

# Shared CSS styles for all pages
def get_shared_styles():
    return """
    /* CSS Variables for Themes */
    :root {
        --bg-primary: #000;
        --bg-secondary: #111;
        --bg-overlay: rgba(0, 0, 0, 0);
        --color-primary: #fff;
        --color-secondary: #ccc;
        --color-accent: #666;
        --border-color: #333;
        --border-hover: #fff;
    }

    [data-theme="light"] {
        --bg-primary: #fff;
        --bg-secondary: #f5f5f5;
        --bg-overlay: rgba(255, 255, 255, 0);
        --color-primary: #000;
        --color-secondary: #333;
        --color-accent: #999;
        --border-color: #ddd;
        --border-hover: #000;
    }

    /* Base Styles */
    * { margin: 0; padding: 0; box-sizing: border-box; }

    /* Hide scrollbars globally */
    * {
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* IE and Edge */
    }

    *::-webkit-scrollbar {
        display: none; /* Chrome, Safari, Opera */
    }

    /* Show scrollbars on desktop */
    @media (min-width: 768px) {
        html {
            scrollbar-width: thin; /* Firefox */
            scrollbar-color: rgba(128, 128, 128, 0.5) transparent; /* Firefox */
        }

        html::-webkit-scrollbar {
            display: block;
            width: 12px;
        }

        html::-webkit-scrollbar-track {
            background: transparent;
        }

        html::-webkit-scrollbar-thumb {
            background-color: rgba(128, 128, 128, 0.5);
            border-radius: 6px;
            border: 3px solid transparent;
            background-clip: content-box;
        }

        html::-webkit-scrollbar-thumb:hover {
            background-color: rgba(128, 128, 128, 0.7);
        }
    }

    /* Prevent zooming on entire page */
    html, body {
        touch-action: pan-x pan-y;
        -webkit-touch-callout: none;
        -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
        text-size-adjust: 100%;
    }

    body {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-primary);
        color: var(--color-primary);
        line-height: 1.6;
        overflow-x: hidden;
        transition: background-color 0.3s ease, color 0.3s ease;
        margin: 0;
        padding: 0;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* Main content should grow to push footer down */
    main {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding-top: 59px;  /* Mobile navbar height + top margin */
    }

    /* Desktop main padding */
    @media (min-width: 768px) {
        main {
            padding-top: 76px;  /* Desktop navbar height + top margin */
        }
    }

    /* Navigation Styles - iOS Glass Effect */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 10000;
        padding: 8px 40px;
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
    }
    [data-theme="light"] .navbar {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
    }
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Center navbar content with max-width on desktop */
    @media (min-width: 768px) {
        .nav-container {
            max-width: 960px;
            margin: 0 auto;
        }
    }
    .nav-actions {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    /* Phone number styling - centered between logo and actions */
    .nav-phone {
        margin: 0 auto;
        transition: opacity 0.3s ease;
        color: var(--color-primary);
        text-decoration: none;
        font-weight: 600;
    }
    .nav-phone:hover {
        opacity: 0.7;
    }
    .logo {
        font-size: 24px;
        font-weight: 700;
        color: var(--color-primary);
        text-decoration: none;
        transition: opacity 0.3s ease;
    }

    /* Logo text styling - matches the icon font */
    .logo-text {
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        font-weight: 400;
        letter-spacing: 3px;
        color: #666;
        white-space: nowrap;
        display: flex;
        flex-direction: row;
        gap: 8px;
    }
    .logo-text-line {
        display: inline;
    }
    [data-theme="dark"] .logo-text {
        color: #999;
    }

    /* Theme Toggle Button */
    .theme-toggle {
        background: none;
        border: 1px solid var(--color-primary);
        border-radius: 50%;
        cursor: pointer;
        padding: 8px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    @media (hover: hover) {
        .theme-toggle:hover {
            transform: scale(1.05);
        }
    }
    .theme-icon {
        width: 20px;
        height: 20px;
        transition: all 0.3s ease;
    }
    .theme-icon.sun { display: block; }
    .theme-icon.moon { display: none; }
    [data-theme="light"] .theme-icon.sun { display: none; }
    [data-theme="light"] .theme-icon.moon { display: block; }

    /* Logo theme switching */
    .logo-light { display: block; }
    .logo-dark { display: none !important; }
    [data-theme="light"] .logo-light { display: block; }
    [data-theme="light"] .logo-dark { display: none !important; }
    [data-theme="dark"] .logo-light { display: none !important; }
    [data-theme="dark"] .logo-dark { display: block !important; }

    /* Menu Toggle */
    .menu-toggle {
        background: none;
        border: none;
        cursor: pointer;
        padding: 10px;
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .menu-toggle span {
        display: block;
        width: 25px;
        height: 2px;
        background: var(--color-primary);
        margin: 5px 0;
    }

    /* Navigation Overlay */
    .nav-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: calc(100vh);
        background: var(--bg-primary);
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding-top: 110px;
        z-index: -1;
    }

    @media (max-width: 767px) {
        .nav-overlay {
            top: 0;
            height: calc(100vh);
            padding-top: 70px;
        }
    }

    .nav-overlay.active {
        opacity: 1;
        visibility: visible;
    }

    .nav-menu {
        list-style: none;
        text-align: left;
        width: auto;
        max-width: 300px;
        margin: 0 auto;
        padding: 0;
    }
    .nav-menu li {
        margin: 20px 0;
    }
    .nav-menu a {
        color: var(--color-primary);
        text-decoration: none;
        font-size: 24px;
        font-weight: 300;
        transition: opacity 0.3s ease;
    }
    .nav-menu a:hover {
        opacity: 0.7;
    }

    /* Footer Styles */
    .footer {
        background: var(--bg-secondary);
        padding: 60px 40px 40px;
        margin-top: auto;
        flex-shrink: 0;
    }
    .footer-container {
        max-width: 960px;
        margin: 0 auto;
    }
    .footer-section {
        color: var(--color-secondary);
    }
    .footer-links li {
        margin-bottom: 8px;
    }
    .footer-links a:hover,
    .footer-reservations a:hover {
        opacity: 0.7;
    }
    .footer-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Mobile Footer Styles */
    @media (max-width: 767px) {
        .footer-main-content {
            grid-template-columns: 1fr !important;
            gap: 30px !important;
        }
        .footer-bottom {
            flex-direction: column;
            gap: 20px;
            text-align: center;
        }
    }

    /* Container Utilities */
    .container {
        max-width: 960px;
        margin: 0 auto;
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(24px, 4vw, 36px);
        font-weight: 700;
        margin-bottom: 30px;
        text-align: center;
    }

    /* Welcome Section */
    .welcome-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .welcome-text {
        font-size: 18px;
        line-height: 1.8;
        color: var(--color-secondary);
        text-align: justify;
        max-width: 800px;
        margin: 0 auto;
    }
    @media (max-width: 767px) {
        .welcome-section {
            padding: 40px 20px;
        }
        .welcome-text {
            font-size: 16px;
            line-height: 1.7;
        }
    }

    /* Why Astra Section */
    .why-astra-section {
        padding: 60px 40px;
        background: var(--bg-secondary);
    }
    .why-astra-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(24px, 4vw, 36px);
        font-weight: 700;
        text-align: center;
        margin-bottom: 50px;
        color: var(--color-primary);
        line-height: 1.3;
    }
    .why-astra-title-line {
        display: block;
    }
    .why-astra-features {
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 60px;
        max-width: 960px;
        margin: 0 auto;
    }
    .feature-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        max-width: 280px;
    }
    .feature-icon {
        width: 80px;
        height: 80px;
        margin-bottom: 20px;
        font-size: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--color-primary);
    }
    .feature-description {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        line-height: 1.8;
        color: var(--color-secondary);
    }
    .feature-description p {
        margin: 4px 0;
    }

    /* Mobile: vertical layout */
    @media (max-width: 767px) {
        .why-astra-section {
            padding: 40px 20px;
        }
        .why-astra-title {
            font-size: 24px;
            margin-bottom: 40px;
        }
        .why-astra-features {
            flex-direction: column;
            align-items: flex-start;
            gap: 30px;
            padding-left: 20px;
        }
        .feature-card {
            flex-direction: row;
            align-items: flex-start;
            text-align: left;
            max-width: 100%;
            gap: 20px;
        }
        .feature-icon {
            width: 60px;
            height: 60px;
            flex-shrink: 0;
            margin-bottom: 0;
            font-size: 45px;
        }
        .feature-content {
            flex: 1;
        }
        .feature-title {
            font-size: 18px;
            margin-bottom: 8px;
        }
        .feature-description {
            font-size: 16px;
            line-height: 1.7;
        }
    }

    /* Pricing Section */
    .pricing-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .pricing-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(24px, 4vw, 36px);
        font-weight: 700;
        text-align: center;
        margin-bottom: 50px;
        color: var(--color-primary);
    }
    .pricing-cards {
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 30px;
        max-width: 960px;
        margin: 0 auto;
    }
    .pricing-card {
        flex: 1;
        max-width: 300px;
        background: var(--bg-primary);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 30px 25px;
        transition: all 0.3s ease;
    }
    .pricing-card:hover {
        border-color: var(--border-hover);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    [data-theme="dark"] .pricing-card:hover {
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.05);
    }
    .pricing-card-title {
        font-family: 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: #e75480;
        margin-bottom: 15px;
    }
    .pricing-card-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        color: var(--color-secondary);
        margin-bottom: 20px;
    }
    .pricing-card-cost {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 5px;
    }
    .pricing-card-price {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 15px;
    }
    .pricing-card-list {
        list-style: disc;
        padding-left: 20px;
        margin: 0;
    }
    .pricing-card-list li {
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        color: var(--color-secondary);
        margin-bottom: 8px;
        line-height: 1.5;
    }
    .pricing-service-group {
        margin-bottom: 20px;
    }
    .pricing-service-group:last-child {
        margin-bottom: 0;
    }
    .pricing-service-title {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 10px;
    }

    /* Mobile: vertical layout */
    @media (max-width: 767px) {
        .pricing-section {
            padding: 40px 20px;
        }
        .pricing-title {
            font-size: 24px;
            margin-bottom: 30px;
        }
        .pricing-cards {
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }
        .pricing-card {
            max-width: 100%;
            width: 100%;
        }
    }

    /* Instagram Section */
    .instagram-section {
        padding: 60px 40px;
        background: var(--bg-secondary);
    }
    .instagram-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(24px, 4vw, 36px);
        font-weight: 700;
        text-align: center;
        margin-bottom: 40px;
        color: var(--color-primary);
    }
    .instagram-title a {
        color: inherit;
        text-decoration: none;
        transition: opacity 0.3s ease;
    }
    .instagram-title a:hover {
        opacity: 0.7;
    }
    .instagram-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        max-width: 960px;
        margin: 0 auto 30px;
    }
    .instagram-item {
        position: relative;
        aspect-ratio: 1;
        overflow: hidden;
        border-radius: 8px;
        background: var(--bg-primary);
    }
    .instagram-item a {
        display: block;
        width: 100%;
        height: 100%;
    }
    .instagram-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease, opacity 0.3s ease;
    }
    .instagram-item:hover img {
        transform: scale(1.05);
        opacity: 0.9;
    }
    .instagram-item .video-indicator {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.6);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .instagram-item .video-indicator svg {
        width: 14px;
        height: 14px;
        fill: white;
    }
    .instagram-actions {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    .instagram-follow-btn {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 14px 28px;
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        color: white;
        text-decoration: none;
        border-radius: 30px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    .instagram-follow-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(220, 39, 67, 0.4);
    }
    .instagram-follow-btn svg {
        width: 20px;
        height: 20px;
        fill: white;
    }
    .instagram-error {
        text-align: center;
        padding: 40px;
        color: var(--color-secondary);
    }
    .instagram-error p {
        margin-bottom: 20px;
    }

    /* Mobile: 3 columns */
    @media (max-width: 767px) {
        .instagram-section {
            padding: 40px 20px;
        }
        .instagram-title {
            font-size: 24px;
            margin-bottom: 30px;
        }
        .instagram-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .instagram-item {
            border-radius: 6px;
        }
        .instagram-follow-btn {
            font-size: 14px;
            padding: 12px 24px;
        }
    }

    /* Google Reviews Section */
    .reviews-section {
        padding: 60px 40px;
        background: var(--bg-primary);
    }
    .reviews-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .rating-display {
        font-size: 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }
    .stars {
        letter-spacing: 2px;
        font-size: 16px;
    }
    .rating-number {
        font-weight: 700;
        color: var(--color-primary);
        font-size: 24px;
        border: 2px solid var(--color-primary);
        border-radius: 8px;
        padding: 4px 12px;
        background: var(--bg-primary);
    }
    .google-logo-rating {
        height: 32px;
        width: auto;
        object-fit: contain;
    }
    .total-reviews {
        font-size: 18px;
        color: var(--color-secondary);
    }
    .reviews-grid {
        display: flex;
        flex-direction: column;
        gap: 30px;
    }
    .reviews-row {
        display: flex;
        flex-wrap: wrap;
        gap: 30px;
        align-items: stretch;
    }
    .reviews-row .review-card {
        flex: 1 1 calc(33.333% - 20px);
        max-width: calc(33.333% - 20px);
    }
    .review-card {
        background: var(--bg-secondary);
        padding: 30px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        height: 100%;
        min-height: 280px;
        display: flex;
        align-items: stretch;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    [data-theme="dark"] .review-card {
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.05);
    }
    .review-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    [data-theme="dark"] .review-card:hover {
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.05);
    }
    .review-content {
        display: flex;
        flex-direction: column;
        width: 100%;
        padding: 4px;
    }
    .review-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        flex-wrap: wrap;
        gap: 10px;
    }
    .reviewer-name {
        font-weight: 600;
        font-size: 18px;
        color: var(--color-primary);
    }
    .review-header .stars {
        font-size: 14px;
        letter-spacing: 2px;
    }
    .review-text {
        color: var(--color-secondary);
        line-height: 1.7;
        margin-bottom: 15px;
        font-size: 15px;
        flex-grow: 1;
    }
    .review-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto;
        gap: 10px;
    }
    .read-more-btn {
        color: var(--color-accent);
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        transition: opacity 0.2s ease;
    }
    .read-more-btn:hover {
        opacity: 0.7;
    }
    .review-time {
        font-size: 14px;
        color: var(--color-accent);
        opacity: 0.7;
    }
    .more-reviews-wrapper {
        display: block;
        text-align: right;
        margin-top: 20px;
    }
    .more-reviews-btn {
        color: var(--color-accent);
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        transition: opacity 0.2s ease;
        text-decoration: underline;
    }
    .more-reviews-btn:hover {
        opacity: 0.7;
    }
    .mobile-tablet-hidden {
        display: flex;
    }
    .desktop-hidden {
        display: none;
    }
    .additional-review.desktop-hidden {
        display: none;
    }

    /* Reviews Mobile */
    @media (max-width: 767px) {
        .reviews-section {
            padding: 40px 20px;
        }
        .rating-display {
            font-size: 16px;
            margin-bottom: 5px;
        }
        .stars {
            font-size: 14px;
        }
        .rating-number {
            font-size: 18px;
            padding: 2px 8px;
        }
        .google-logo-rating {
            height: 24px;
        }
        .total-reviews {
            font-size: 16px;
        }
        .reviews-grid {
            gap: 15px;
        }
        .reviews-row {
            gap: 15px;
        }
        .reviews-row .review-card {
            flex: 1 1 100%;
            max-width: 100%;
        }
        .review-card {
            padding: 20px;
            min-height: auto;
        }
        .review-header {
            margin-bottom: 10px;
        }
        .reviewer-name {
            font-size: 16px;
        }
        .review-header .stars {
            font-size: 12px;
        }
        .review-text {
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        .read-more-btn,
        .review-time {
            font-size: 12px;
        }
        .more-reviews-btn {
            font-size: 14px;
        }
        .mobile-tablet-hidden {
            display: none !important;
        }
        .mobile-tablet-hidden.show-mobile {
            display: flex !important;
        }
    }

    /* Back to Top Button - Glass Morphism Style */
    .back-to-top {
        position: fixed;
        bottom: 95px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        color: #fff;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        opacity: 0;
        visibility: hidden;
        z-index: 1000;
        padding: 0;
        line-height: 1;
    }
    .back-to-top span {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        position: relative;
        top: -1px;
        left: 0px;
    }
    [data-theme="light"] .back-to-top {
        color: #000;
        border: 1px solid #000;
    }
    .back-to-top.visible {
        opacity: 1;
        visibility: visible;
    }
    .back-to-top:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    .back-to-top:active {
        transform: translateY(-2px);
    }

    /* WhatsApp Button */
    .whatsapp-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #25d366;
        border: none;
        box-shadow: 0 8px 32px rgba(37, 211, 102, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 1000;
        text-decoration: none;
        opacity: 1;
        visibility: visible;
    }
    .whatsapp-button svg {
        width: 28px;
        height: 28px;
        fill: white;
    }
    .whatsapp-button:hover {
        background: #20ba5a;
        transform: translateY(-5px) scale(1.1);
        box-shadow: 0 12px 40px rgba(37, 211, 102, 0.4);
    }
    .whatsapp-button:active {
        transform: translateY(-2px) scale(1.05);
    }

    /* Floating buttons container */
    .floating-buttons-container {
        position: fixed;
        bottom: 30px;
        left: 20px;
        right: 70px;
        display: flex;
        justify-content: space-between;
        z-index: 999;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
    }
    .floating-buttons-container.visible {
        opacity: 1;
        pointer-events: auto;
    }

    /* Floating button animations */
    @keyframes floating-glow {
        0%, 100% {
            transform: scale(1);
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.35);
            box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        50% {
            transform: scale(1.03);
            background: rgba(255, 255, 255, 0.25);
            border-color: rgba(255, 255, 255, 0.6);
            box-shadow: 0 8px 35px rgba(255, 255, 255, 0.35), 0 16px 70px rgba(255, 255, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.25);
        }
    }
    @keyframes floating-glow-light {
        0%, 100% {
            transform: scale(1);
            background: rgba(0, 0, 0, 0.06);
            border-color: rgba(0, 0, 0, 0.2);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
        50% {
            transform: scale(1.03);
            background: rgba(0, 0, 0, 0.15);
            border-color: rgba(0, 0, 0, 0.4);
            box-shadow: 0 8px 35px rgba(0, 0, 0, 0.2), 0 16px 70px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }
    }

    /* Floating Instant Quote Button */
    .floating-select-dates-btn {
        position: relative;
        bottom: auto;
        left: auto;
        transform: none;
        padding: 0 24px;
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.35);
        border-radius: 30px;
        font-size: 14px;
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
        line-height: 1.2;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        animation: floating-glow 2s ease-in-out infinite;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .floating-select-dates-btn:hover {
        transform: translateY(-3px) scale(1.05) !important;
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.7) !important;
        animation-play-state: paused;
        box-shadow: 0 8px 35px rgba(255, 255, 255, 0.3), 0 16px 70px rgba(255, 255, 255, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    .floating-select-dates-btn:active {
        transform: translateY(-1px) scale(1.02) !important;
        animation-play-state: paused;
    }
    [data-theme="light"] .floating-select-dates-btn {
        background: rgba(0, 0, 0, 0.06);
        color: #000000;
        border: 2px solid rgba(0, 0, 0, 0.2);
        animation: floating-glow-light 2s ease-in-out infinite;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    [data-theme="light"] .floating-select-dates-btn:hover {
        transform: translateY(-3px) scale(1.05) !important;
        background: rgba(0, 0, 0, 0.15) !important;
        border-color: rgba(0, 0, 0, 0.4) !important;
        animation-play-state: paused;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2), 0 16px 60px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    /* Floating Inquiry Button */
    .floating-general-inquiry-btn {
        position: relative;
        bottom: auto;
        left: auto;
        transform: none;
        padding: 0 16px;
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.35);
        border-radius: 30px;
        font-size: 14px;
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
        line-height: 1.2;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15), 0 8px 40px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .floating-general-inquiry-btn:hover {
        transform: translateY(-3px) scale(1.05) !important;
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.7) !important;
        box-shadow: 0 8px 35px rgba(255, 255, 255, 0.3), 0 16px 70px rgba(255, 255, 255, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    .floating-general-inquiry-btn:active {
        transform: translateY(-1px) scale(1.02) !important;
    }
    [data-theme="light"] .floating-general-inquiry-btn {
        background: rgba(0, 0, 0, 0.06);
        color: #000000;
        border: 2px solid rgba(0, 0, 0, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 8px 40px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    [data-theme="light"] .floating-general-inquiry-btn:hover {
        transform: translateY(-3px) scale(1.05) !important;
        background: rgba(0, 0, 0, 0.15) !important;
        border-color: rgba(0, 0, 0, 0.4) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2), 0 16px 60px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    /* Desktop positioning for floating elements */
    @media (min-width: 768px) {
        .back-to-top {
            right: max(30px, calc(50vw - 450px));
        }
        .whatsapp-button {
            right: max(30px, calc(50vw - 450px));
        }
        .floating-buttons-container {
            left: max(30px, calc(50vw - 450px));
            right: max(80px, calc(50vw - 450px + 80px));
            transform: none;
        }
        .floating-select-dates-btn {
            height: 50px;
            font-size: 18px;
            padding: 0 36px;
        }
        .floating-general-inquiry-btn {
            height: 50px;
            font-size: 18px;
            padding: 0 20px;
        }
    }

    /* Mobile adjustments for floating elements */
    @media (max-width: 767px) {
        .back-to-top {
            bottom: 75px;
            right: 20px;
            width: 45px;
            height: 45px;
            font-size: 20px;
        }
        .back-to-top span {
            left: -2px;
        }
        .whatsapp-button {
            bottom: 20px;
            right: 20px;
            width: 45px;
            height: 45px;
        }
        .whatsapp-button svg {
            width: 25px;
            height: 25px;
        }
        .floating-buttons-container {
            left: 10px;
            right: 65px;
            bottom: 20px;
        }
        .floating-select-dates-btn {
            font-size: 12px;
            height: 38px;
            padding: 0 15px;
        }
        .floating-general-inquiry-btn {
            font-size: 12px;
            height: 38px;
            padding: 0 12px;
        }
    }

    /* Extra narrow screens */
    @media (max-width: 380px) {
        .floating-buttons-container {
            left: 8px;
            right: 60px;
        }
        .floating-select-dates-btn {
            font-size: 11px;
            height: 36px;
            padding: 0 12px;
        }
        .floating-general-inquiry-btn {
            font-size: 11px;
            height: 36px;
            padding: 0 10px;
        }
    }

    /* General Inquiry Modal Styles */
    .general-inquiry-popup {
        display: none;
        position: fixed;
        top: 0 !important;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, rgba(13, 27, 42, 0.95), rgba(27, 38, 59, 0.95), rgba(15, 23, 42, 0.98));
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        z-index: 9998;
        overflow-y: auto;
        padding: 0 40px 40px 40px;
    }
    .general-inquiry-popup.active {
        display: block;
    }
    .general-inquiry-popup.active .popup-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 140px;
        max-width: 960px;
        margin: 0 auto;
        width: 100%;
    }
    [data-theme="light"] .general-inquiry-popup {
        background: linear-gradient(to bottom, rgba(248, 250, 252, 0.97), rgba(241, 245, 249, 0.97), rgba(248, 250, 252, 0.99));
    }
    .general-inquiry-popup .popup-header {
        display: none !important;
    }

    /* Inquiry popup close button */
    .general-inquiry-popup-close {
        position: fixed;
        top: 125px;
        right: 40px;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        color: #fff;
        font-size: 28px;
        font-weight: 300;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        opacity: 0;
        visibility: hidden;
        z-index: 9999;
    }
    .general-inquiry-popup-close.visible {
        opacity: 1;
        visibility: visible;
    }
    [data-theme="light"] .general-inquiry-popup-close {
        color: #000;
        border: 1px solid #000;
    }
    .general-inquiry-popup-close:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: scale(1.1);
    }

    /* Inquiry form styling */
    .inquiry-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(24px, 4vw, 36px);
        font-weight: 700;
        color: #fff;
        margin-bottom: 30px;
        text-align: center;
    }
    [data-theme="light"] .inquiry-title {
        color: #000;
    }
    .inquiry-form {
        width: 100%;
        max-width: 500px;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-label {
        display: block;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 8px;
    }
    [data-theme="light"] .form-label {
        color: rgba(0, 0, 0, 0.7);
    }
    .form-input,
    .form-textarea,
    .form-select {
        width: 100%;
        padding: 14px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #fff;
        outline: none;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }
    [data-theme="light"] .form-input,
    [data-theme="light"] .form-textarea,
    [data-theme="light"] .form-select {
        background: rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.15);
        color: #000;
    }
    .form-input:focus,
    .form-textarea:focus,
    .form-select:focus {
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.15);
    }
    [data-theme="light"] .form-input:focus,
    [data-theme="light"] .form-textarea:focus,
    [data-theme="light"] .form-select:focus {
        border-color: rgba(0, 0, 0, 0.3);
        background: rgba(0, 0, 0, 0.08);
    }
    .form-input::placeholder,
    .form-textarea::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    [data-theme="light"] .form-input::placeholder,
    [data-theme="light"] .form-textarea::placeholder {
        color: rgba(0, 0, 0, 0.4);
    }
    .form-textarea {
        min-height: 120px;
        resize: vertical;
    }
    .form-submit-btn {
        width: 100%;
        padding: 16px 32px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 700;
        background: #e75480;
        color: #fff;
        border: none;
        border-radius: 30px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .form-submit-btn:hover {
        background: #d14070;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(231, 84, 128, 0.4);
    }
    .form-submit-btn:active {
        transform: translateY(0);
    }

    @media (min-width: 768px) {
        .general-inquiry-popup {
            padding: 0 60px 40px 60px;
        }
        .general-inquiry-popup.active .popup-content {
            padding-top: 160px;
        }
    }

    @media (max-width: 767px) {
        .general-inquiry-popup {
            padding: 0 20px 20px 20px;
        }
        .general-inquiry-popup.active .popup-content {
            padding-top: 100px;
        }
        .general-inquiry-popup-close {
            top: 80px;
            right: 20px;
            width: 40px;
            height: 40px;
            font-size: 24px;
        }
    }

    /* Hero Section */
    .hero-section {
        display: flex;
        align-items: flex-start;
        justify-content: center;
        text-align: center;
        padding: 40px 0px 60px;
        margin: 0;
        position: relative;
        min-height: 400px;
        height: 400px;
        overflow: visible;
    }

    /* Background image constrained to 960px max-width using pseudo-element */
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 960px;
        height: 100%;
        background-image: var(--hero-bg-image);
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        z-index: 0;
    }

    .hero-section > * { position: relative; z-index: 1; }
    .hero-content {
        width: 100%;
        max-width: 960px;
        margin: 0 auto;
        padding: 0 20px;
        box-sizing: border-box;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
    }

    .hero-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 2px;
        line-height: 1.1;
        margin-top: 35px;
        padding-top: 10px;
        letter-spacing: -0.5px;
        text-transform: uppercase;
        text-align: center;
        width: 100%;
        color: black;
    }
    [data-theme="dark"] .hero-title {
        color: white;
    }
    .hero-title .hero-line {
        display: block !important;
        text-align: center !important;
        width: 100%;
    }

    /* Booking Form - Mobile Base */
    .hero-booking {
        margin-top: 25px;
        margin-bottom: 0;
        margin-left: 20px;
        margin-right: 20px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }

    /* Button glow animations */
    @keyframes dynamic-glow {
        0%, 100% {
            transform: scale(1);
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.35);
            box-shadow:
                0 4px 20px rgba(255, 255, 255, 0.15),
                0 8px 40px rgba(255, 255, 255, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        50% {
            transform: scale(1.03);
            background: rgba(255, 255, 255, 0.25);
            border-color: rgba(255, 255, 255, 0.6);
            box-shadow:
                0 8px 35px rgba(255, 255, 255, 0.35),
                0 16px 70px rgba(255, 255, 255, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.25);
        }
    }

    @keyframes dynamic-glow-light {
        0%, 100% {
            transform: scale(1);
            background: rgba(0, 0, 0, 0.06);
            border-color: rgba(0, 0, 0, 0.2);
            box-shadow:
                0 4px 20px rgba(0, 0, 0, 0.08),
                0 8px 40px rgba(0, 0, 0, 0.04),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
        50% {
            transform: scale(1.03);
            background: rgba(0, 0, 0, 0.15);
            border-color: rgba(0, 0, 0, 0.4);
            box-shadow:
                0 8px 35px rgba(0, 0, 0, 0.2),
                0 16px 70px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }
    }

    .start-search-btn,
    .general-inquiry-btn {
        display: inline-block;
        background: rgba(0, 0, 0, 0.06);
        color: #000000;
        border: 2px solid rgba(0, 0, 0, 0.2);
        padding: 12px 24px;
        border-radius: 30px;
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        white-space: nowrap;
        text-decoration: none;
        text-align: center;
        min-width: 180px;
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        box-shadow:
            0 4px 20px rgba(0, 0, 0, 0.08),
            0 8px 40px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }

    .start-search-btn {
        animation: dynamic-glow-light 2s ease-in-out infinite;
    }

    .general-inquiry-btn {
        margin-bottom: 16px;
    }

    .start-search-btn:hover,
    .general-inquiry-btn:hover {
        transform: translateY(-3px) scale(1.05) !important;
        background: rgba(0, 0, 0, 0.15) !important;
        border-color: rgba(0, 0, 0, 0.4) !important;
        animation: none;
        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.2),
            0 16px 60px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    .start-search-btn:active,
    .general-inquiry-btn:active {
        transform: translateY(-1px) scale(1.02) !important;
        animation: none;
    }

    [data-theme="dark"] .start-search-btn,
    [data-theme="dark"] .general-inquiry-btn {
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.35);
        box-shadow:
            0 4px 20px rgba(255, 255, 255, 0.15),
            0 8px 40px rgba(255, 255, 255, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    [data-theme="dark"] .start-search-btn {
        animation: dynamic-glow 2s ease-in-out infinite;
    }

    [data-theme="dark"] .start-search-btn:hover,
    [data-theme="dark"] .general-inquiry-btn:hover {
        transform: translateY(-3px) scale(1.05) !important;
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.7) !important;
        animation: none;
        box-shadow:
            0 8px 35px rgba(255, 255, 255, 0.3),
            0 16px 70px rgba(255, 255, 255, 0.18),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    [data-theme="dark"] .start-search-btn:active,
    [data-theme="dark"] .general-inquiry-btn:active {
        transform: translateY(-1px) scale(1.02) !important;
        animation: none;
    }

    /* Mobile hero adjustments */
    @media (max-width: 767px) {
        .hero-section {
            min-height: 300px;
            height: 300px;
            padding: 20px 0px 40px;
        }
        .hero-title {
            font-size: 24px;
            margin-top: 20px;
        }
        .hero-booking {
            margin-left: 0;
            margin-right: 0;
        }
        .start-search-btn,
        .general-inquiry-btn {
            font-size: 14px;
            padding: 10px 20px;
            min-width: 150px;
        }
    }

    /* Mobile styles - 767px and below */
    @media (max-width: 767px) {
        .navbar {
            top: 0;
            left: 0;
            right: 0;
            padding: 6px 15px;
            min-height: 50px;
        }
        .nav-container {
            gap: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            min-height: 47px;
        }
        .logo {
            flex: 0 0 auto;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            gap: 6px !important;
        }
        .logo img {
            height: 40px !important;
        }
        .logo-text {
            font-size: 11px;
            letter-spacing: 1.5px;
            flex-direction: column;
            gap: 0;
            line-height: 1.3;
        }
        .nav-phone {
            font-size: 14px !important;
            flex: 0;
            text-align: center;
            white-space: nowrap;
            display: flex;
            justify-content: center;
            padding-left: 0;
            margin: 0 auto;
        }
        .phone-prefix {
            display: none;
        }
        .nav-actions {
            gap: 8px;
            flex: 0 0 auto;
            display: flex;
            justify-content: flex-end;
        }
        .theme-toggle {
            width: 32px;
            height: 32px;
            padding: 6px;
        }
        .theme-icon {
            width: 18px;
            height: 18px;
        }
        .menu-toggle {
            padding: 8px;
        }
        .menu-toggle span {
            width: 22px;
            height: 2px;
            margin: 4px 0;
        }
        .footer { padding: 40px 20px 30px; }
    }

    /* Extra small screens - below 384px */
    @media (max-width: 384px) {
        .nav-container {
            gap: 4px;
        }
        .logo img {
            height: 35px !important;
        }
        .nav-phone {
            font-size: 14px !important;
            margin: 0 auto;
            flex: 1;
            text-align: center;
            white-space: nowrap;
        }
        .theme-toggle {
            width: 28px !important;
            height: 28px !important;
            padding: 4px !important;
        }
        .menu-toggle {
            width: 28px !important;
            height: 28px !important;
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .menu-toggle span {
            width: 16px !important;
            height: 2px !important;
            margin: 2px 0 !important;
        }
    }

    /* Extra extra small screens - below 320px */
    @media (max-width: 320px) {
        .nav-phone {
            font-size: 12px !important;
            letter-spacing: -0.5px;
        }
        .logo img {
            height: 30px !important;
        }
        .theme-toggle {
            width: 26px !important;
            height: 26px !important;
            padding: 3px !important;
        }
        .menu-toggle {
            width: 26px !important;
            height: 26px !important;
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .menu-toggle span {
            width: 14px !important;
            height: 2px !important;
            margin: 2px 0 !important;
        }
    }
    """


def get_shared_scripts():
    return """
    // Theme Management
    const ThemeManager = {
        MANUAL_OVERRIDE_DURATION: 3600000, // 1 hour in milliseconds

        init() {
            this.themeToggle = document.getElementById('theme-toggle');
            this.prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

            // Determine and apply the appropriate theme
            const theme = this.determineTheme();
            this.setTheme(theme);

            // Listen for system theme changes
            this.prefersDark.addListener((e) => {
                if (!this.hasRecentManualOverride()) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });

            // Listen for theme changes in other tabs
            window.addEventListener('storage', (e) => {
                if (e.key === 'theme' && e.newValue) {
                    this.setTheme(e.newValue);
                } else if (e.key === 'themeOverrideTime') {
                    if (!this.hasRecentManualOverride()) {
                        const theme = this.determineTheme();
                        this.setTheme(theme);
                    }
                }
            });

            // Theme toggle button
            if (this.themeToggle) {
                this.themeToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                    this.setTheme(newTheme);
                    localStorage.setItem('theme', newTheme);
                    localStorage.setItem('themeOverrideTime', Date.now().toString());
                });
            }

            // Check periodically if manual override has expired
            setInterval(() => {
                if (!this.hasRecentManualOverride()) {
                    const currentTheme = document.documentElement.getAttribute('data-theme');
                    const expectedTheme = this.getSystemOrTimeBasedTheme();
                    if (currentTheme !== expectedTheme) {
                        this.setTheme(expectedTheme);
                    }
                }
            }, 60000);
        },

        determineTheme() {
            if (this.hasRecentManualOverride()) {
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme) {
                    return savedTheme;
                }
            }
            return this.getSystemOrTimeBasedTheme();
        },

        hasRecentManualOverride() {
            const overrideTime = localStorage.getItem('themeOverrideTime');
            if (!overrideTime) return false;
            const timeSinceOverride = Date.now() - parseInt(overrideTime);
            return timeSinceOverride < this.MANUAL_OVERRIDE_DURATION;
        },

        getSystemOrTimeBasedTheme() {
            if (window.matchMedia) {
                try {
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
                    if (prefersDark.matches !== undefined) {
                        return prefersDark.matches ? 'dark' : 'light';
                    }
                } catch (e) {}
            }
            const hour = new Date().getHours();
            return (hour >= 19 || hour < 7) ? 'dark' : 'light';
        },

        setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            document.body.setAttribute('data-theme', theme);
        },

        toggle() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            this.setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
            localStorage.setItem('themeOverrideTime', Date.now().toString());
        }
    };

    // Initialize on DOM load
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize theme
        ThemeManager.init();

        // Mobile menu
        const menuToggle = document.getElementById('menu-toggle');
        const navOverlay = document.getElementById('nav-overlay');

        if (menuToggle && navOverlay) {
            menuToggle.addEventListener('click', function() {
                menuToggle.classList.toggle('active');
                navOverlay.classList.toggle('active');
                document.body.style.overflow = navOverlay.classList.contains('active') ? 'hidden' : '';
            });

            navOverlay.addEventListener('click', function(e) {
                if (e.target === navOverlay || e.target.tagName === 'A') {
                    menuToggle.classList.remove('active');
                    navOverlay.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        }
    });
    """


def navigation():
    """Navigation bar with logo, phone, theme toggle, and menu"""
    return Nav(
        Div(
            A(
                Img(src="/static/images/logo_astra.png", alt="Astra Staging", cls="logo-light", style="height: 60px; width: auto;"),
                Img(src="/static/images/logo_astra.png", alt="Astra Staging", cls="logo-dark", style="height: 60px; width: auto; display: none;"),
                Span(
                    Span("ASTRA", cls="logo-text-line"),
                    Span("STAGING", cls="logo-text-line"),
                    cls="logo-text"
                ),
                href="/",
                cls="logo",
                style="display: flex; align-items: center; text-decoration: none; gap: 10px;"
            ),
            # Phone number - different display for mobile and desktop
            A(
                Span(
                    NotStr('''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>'''),
                    style="display: inline-flex; align-items: center;"
                ),
                Span("1-", cls="phone-prefix"),
                Span("888-744-4078", cls="phone-number"),
                href="tel:18887444078",
                cls="nav-phone",
                style="color: var(--color-primary); text-decoration: none; font-size: 22px; font-weight: 600; display: flex; align-items: center;"
            ),
            Div(
                Button(
                    Svg(
                        Path(d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"),
                        viewBox="0 0 24 24",
                        fill="none",
                        stroke="currentColor",
                        stroke_width="2",
                        stroke_linecap="round",
                        stroke_linejoin="round",
                        cls="theme-icon sun"
                    ),
                    Svg(
                        Path(d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"),
                        viewBox="0 0 24 24",
                        fill="none",
                        stroke="currentColor",
                        stroke_width="2",
                        stroke_linecap="round",
                        stroke_linejoin="round",
                        cls="theme-icon moon"
                    ),
                    type="button",
                    cls="theme-toggle",
                    id="theme-toggle",
                    **{"aria-label": "Toggle theme"}
                ),
                Button(
                    Span(),
                    Span(),
                    Span(),
                    cls="menu-toggle",
                    id="menu-toggle"
                ),
                cls="nav-actions"
            ),
            cls="nav-container"
        ),
        Div(
            Ul(
                Li(A("Home", href="/")),
                Li(A("About", href="/about")),
                Li(A("Services", href="/services")),
                Li(A("Contact", href="/contact")),
                cls="nav-menu"
            ),
            cls="nav-overlay",
            id="nav-overlay"
        ),
        cls="navbar"
    )


def footer():
    """Reusable footer component"""
    return Footer(
        Div(
            Div(
                P("© 2026 Astra Staging. All rights reserved.", style="color: var(--color-secondary); margin: 0;"),
                cls="footer-bottom"
            ),
            cls="footer-container"
        ),
        cls="footer"
    )


def back_to_top_button():
    """Back to top button with glass morphism style"""
    return Button(
        Span("›", style="font-size: 40px; line-height: 1; font-weight: 300; transform: rotate(-90deg); display: inline-block; margin: 0; padding: 0;"),
        cls="back-to-top",
        id="back-to-top",
        onclick="window.scrollTo({top: 0, behavior: 'smooth'})",
        **{"aria-label": "Back to top"}
    )


def whatsapp_button():
    """WhatsApp floating button"""
    return A(
        NotStr('''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>'''),
        href="https://api.whatsapp.com/send?phone=16475585677",
        target="_blank",
        cls="whatsapp-button",
        **{"aria-label": "Contact us on WhatsApp"}
    )


def floating_buttons():
    """Floating inquiry and instant quote buttons"""
    return Div(
        Button(
            "General Inquiry",
            cls="floating-general-inquiry-btn",
            onclick="showGeneralInquiryForm()"
        ),
        A(
            "Instant Quote",
            href="/quote",
            cls="floating-select-dates-btn"
        ),
        cls="floating-buttons-container",
        id="floating-buttons"
    )


def general_inquiry_modal():
    """General inquiry popup modal"""
    return Div(
        Button(
            "×",
            cls="general-inquiry-popup-close",
            id="general-inquiry-close",
            onclick="closeGeneralInquiryForm()"
        ),
        Div(
            H2("General Inquiry", cls="inquiry-title"),
            Form(
                Div(
                    Label("Name *", cls="form-label", **{"for": "inquiry-name"}),
                    Input(type="text", id="inquiry-name", name="name", cls="form-input", placeholder="Your name", required=True),
                    cls="form-group"
                ),
                Div(
                    Label("Email *", cls="form-label", **{"for": "inquiry-email"}),
                    Input(type="email", id="inquiry-email", name="email", cls="form-input", placeholder="Your email", required=True),
                    cls="form-group"
                ),
                Div(
                    Label("Phone", cls="form-label", **{"for": "inquiry-phone"}),
                    Input(type="tel", id="inquiry-phone", name="phone", cls="form-input", placeholder="Your phone number"),
                    cls="form-group"
                ),
                Div(
                    Label("Property Address", cls="form-label", **{"for": "inquiry-address"}),
                    Input(type="text", id="inquiry-address", name="address", cls="form-input", placeholder="Property address"),
                    cls="form-group"
                ),
                Div(
                    Label("Message *", cls="form-label", **{"for": "inquiry-message"}),
                    Textarea(id="inquiry-message", name="message", cls="form-textarea form-input", placeholder="Tell us about your staging needs...", required=True),
                    cls="form-group"
                ),
                Button("Send Inquiry", type="submit", cls="form-submit-btn"),
                cls="inquiry-form",
                id="general-inquiry-form"
            ),
            cls="popup-content"
        ),
        cls="general-inquiry-popup",
        id="general-inquiry-popup"
    )


def get_floating_elements_script():
    """JavaScript for floating elements - back to top, modal, scroll behavior"""
    return """
    // Back to top button visibility
    function updateBackToTopVisibility() {
        const backToTop = document.getElementById('back-to-top');
        if (backToTop) {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        }
    }

    // General inquiry modal functions
    function showGeneralInquiryForm() {
        const popup = document.getElementById('general-inquiry-popup');
        const closeBtn = document.getElementById('general-inquiry-close');
        if (popup) {
            popup.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        if (closeBtn) {
            closeBtn.classList.add('visible');
        }
    }

    function closeGeneralInquiryForm() {
        const popup = document.getElementById('general-inquiry-popup');
        const closeBtn = document.getElementById('general-inquiry-close');
        if (popup) {
            popup.classList.remove('active');
            document.body.style.overflow = '';
        }
        if (closeBtn) {
            closeBtn.classList.remove('visible');
        }
    }

    // Close modal on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeGeneralInquiryForm();
        }
    });

    // Close modal when clicking outside
    document.addEventListener('click', function(e) {
        const popup = document.getElementById('general-inquiry-popup');
        if (popup && popup.classList.contains('active')) {
            if (e.target === popup) {
                closeGeneralInquiryForm();
            }
        }
    });

    // Initialize scroll listener
    window.addEventListener('scroll', function() {
        updateBackToTopVisibility();
    });

    // Initial check
    document.addEventListener('DOMContentLoaded', function() {
        updateBackToTopVisibility();
    });
    """


def create_page(title, content, additional_styles="", additional_scripts="",
                description="Astra Staging - Professional Home Staging Services",
                keywords="home staging, furniture staging, real estate staging",
                is_homepage=False):
    """Create a page with the shared layout and styles"""

    # Inline script to prevent theme flash - runs immediately
    theme_init_script = """
    <script>
    (function() {
        const MANUAL_OVERRIDE_DURATION = 3600000;

        function hasRecentManualOverride() {
            const overrideTime = localStorage.getItem('themeOverrideTime');
            if (!overrideTime) return false;
            const timeSinceOverride = Date.now() - parseInt(overrideTime);
            return timeSinceOverride < MANUAL_OVERRIDE_DURATION;
        }

        function getSystemOrTimeBasedTheme() {
            if (window.matchMedia) {
                try {
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
                    if (prefersDark.matches !== undefined) {
                        return prefersDark.matches ? 'dark' : 'light';
                    }
                } catch (e) {}
            }
            const hour = new Date().getHours();
            return (hour >= 19 || hour < 7) ? 'dark' : 'light';
        }

        let theme = 'light';

        if (hasRecentManualOverride()) {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) theme = savedTheme;
        } else {
            theme = getSystemOrTimeBasedTheme();
        }

        document.documentElement.setAttribute('data-theme', theme);
    })();
    </script>
    """

    # Homepage scroll script for floating buttons (only show when banner is scrolled out of view)
    homepage_scroll_script = """
    // Homepage-specific scroll behavior for floating buttons
    function updateFloatingButtonsVisibility() {
        const floatingButtons = document.getElementById('floating-buttons');
        const heroSection = document.querySelector('.hero-section');

        if (floatingButtons && heroSection) {
            const heroBottom = heroSection.getBoundingClientRect().bottom;
            if (heroBottom <= 0) {
                floatingButtons.classList.add('visible');
            } else {
                floatingButtons.classList.remove('visible');
            }
        }
    }

    window.addEventListener('scroll', function() {
        updateFloatingButtonsVisibility();
    });

    document.addEventListener('DOMContentLoaded', function() {
        updateFloatingButtonsVisibility();
    });
    """ if is_homepage else """
    // Non-homepage: always show floating buttons
    document.addEventListener('DOMContentLoaded', function() {
        const floatingButtons = document.getElementById('floating-buttons');
        if (floatingButtons) {
            floatingButtons.classList.add('visible');
        }
    });
    """

    # Combine all scripts
    all_scripts = get_shared_scripts() + get_floating_elements_script() + homepage_scroll_script + (str(additional_scripts) if additional_scripts else "")

    return Html(
        Head(
            Title(title),
            Meta(charset='UTF-8'),
            Meta(name='viewport', content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'),
            Meta(name='description', content=description),
            Meta(name='keywords', content=keywords),
            Link(href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@300;400;500&family=Barlow+Condensed:wght@400;500;600;700&display=swap', rel='stylesheet'),
            Link(rel='icon', type='image/x-icon', href='/static/favicon.ico'),
            Style(get_shared_styles() + additional_styles),
            NotStr(theme_init_script)
        ),
        Body(
            navigation(),
            Main(content),
            footer(),
            # Floating elements - always present on all pages
            back_to_top_button(),
            whatsapp_button(),
            floating_buttons(),
            general_inquiry_modal(),
            Script(all_scripts),
            cls="page-wrapper"
        )
    )
