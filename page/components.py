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
                Img(src="/static/images/as_logo.png", alt="Astra Staging", cls="logo-light", style="height: 60px; width: auto;"),
                Img(src="/static/images/as_logo.png", alt="Astra Staging", cls="logo-dark", style="height: 60px; width: auto; display: none;"),
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


def create_page(title, content, additional_styles="", additional_scripts="",
                description="Astra Staging - Professional Home Staging Services",
                keywords="home staging, furniture staging, real estate staging"):
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
            Script(get_shared_scripts() + (str(additional_scripts) if additional_scripts else "")),
            cls="page-wrapper"
        )
    )
