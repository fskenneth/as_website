"""
Sign In / Register Page for Astra Staging
"""

from fasthtml.common import *
from page.components import create_page, Circle
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')


def get_signin_styles():
    """CSS styles for signin page"""
    return """
    /* Sign In Page Styles */
    .signin-section {
        min-height: calc(100vh - 200px);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        background: var(--bg-primary);
    }

    .signin-container {
        width: 100%;
        max-width: 420px;
        background: var(--bg-secondary);
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    [data-theme="dark"] .signin-container {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .signin-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .signin-title {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary);
        margin-bottom: 8px;
    }

    .signin-subtitle {
        font-size: 16px;
        color: var(--color-secondary);
    }

    /* Tab switching */
    .signin-tabs {
        display: flex;
        margin-bottom: 30px;
        border-bottom: 1px solid var(--border-color);
    }

    .signin-tab {
        flex: 1;
        padding: 12px;
        text-align: center;
        cursor: pointer;
        color: var(--color-secondary);
        font-weight: 500;
        border: none;
        background: none;
        transition: all 0.3s ease;
        position: relative;
    }

    .signin-tab:hover {
        color: var(--color-primary);
    }

    .signin-tab.active {
        color: var(--color-primary);
    }

    .signin-tab.active::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--color-primary);
    }

    /* Form panels */
    .signin-panel {
        display: none;
    }

    .signin-panel.active {
        display: block;
    }

    /* Google Sign In Button */
    .google-signin-btn {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 14px 20px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-primary);
        color: var(--color-primary);
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 24px;
    }

    .google-signin-btn:hover {
        border-color: var(--border-hover);
        background: var(--bg-secondary);
    }

    .google-signin-btn svg {
        width: 20px;
        height: 20px;
    }

    /* Divider */
    .signin-divider {
        display: flex;
        align-items: center;
        margin: 24px 0;
    }

    .signin-divider::before,
    .signin-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border-color);
    }

    .signin-divider span {
        padding: 0 16px;
        color: var(--color-secondary);
        font-size: 14px;
    }

    /* Form Fields */
    .signin-form {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .form-row {
        display: flex;
        gap: 16px;
    }

    .form-row .form-group {
        flex: 1;
    }

    .form-label {
        font-size: 14px;
        font-weight: 500;
        color: var(--color-primary);
    }

    .form-input {
        width: 100%;
        padding: 14px 16px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-primary);
        color: var(--color-primary);
        font-size: 16px;
        transition: all 0.3s ease;
    }

    .form-input:focus {
        outline: none;
        border-color: var(--border-hover);
    }

    .form-input::placeholder {
        color: var(--color-accent);
    }

    /* Submit Button */
    .signin-submit {
        width: 100%;
        padding: 14px 20px;
        border: none;
        border-radius: 8px;
        background: var(--color-primary);
        color: var(--bg-primary);
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 10px;
    }

    .signin-submit:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    .signin-submit:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    /* Error/Success Messages */
    .signin-message {
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        margin-bottom: 20px;
        display: none;
    }

    .signin-message.error {
        background: rgba(220, 38, 38, 0.1);
        color: #dc2626;
        border: 1px solid rgba(220, 38, 38, 0.3);
        display: block;
    }

    .signin-message.success {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
        display: block;
    }

    /* Password visibility toggle */
    .password-wrapper {
        position: relative;
    }

    .password-toggle {
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        cursor: pointer;
        color: var(--color-secondary);
        padding: 4px;
    }

    .password-toggle:hover {
        color: var(--color-primary);
    }

    /* Mobile adjustments */
    @media (max-width: 480px) {
        .signin-container {
            padding: 30px 24px;
        }

        .signin-title {
            font-size: 24px;
        }

        .form-row {
            flex-direction: column;
            gap: 20px;
        }
    }
    """


def get_signin_scripts():
    """JavaScript for signin page functionality"""
    return f"""
    // Tab switching
    function switchTab(tabName) {{
        // Update tabs
        document.querySelectorAll('.signin-tab').forEach(tab => {{
            tab.classList.remove('active');
        }});
        document.querySelector(`[data-tab="${{tabName}}"]`).classList.add('active');

        // Update panels
        document.querySelectorAll('.signin-panel').forEach(panel => {{
            panel.classList.remove('active');
        }});
        document.getElementById(`${{tabName}}-panel`).classList.add('active');

        // Clear messages
        hideMessage();
    }}

    // Show/hide message
    function showMessage(message, type) {{
        const msgEl = document.getElementById('signin-message');
        msgEl.textContent = message;
        msgEl.className = 'signin-message ' + type;
    }}

    function hideMessage() {{
        const msgEl = document.getElementById('signin-message');
        msgEl.className = 'signin-message';
        msgEl.textContent = '';
    }}

    // Toggle password visibility
    function togglePassword(inputId) {{
        const input = document.getElementById(inputId);
        const btn = input.parentElement.querySelector('.password-toggle');
        if (input.type === 'password') {{
            input.type = 'text';
            btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
        }} else {{
            input.type = 'password';
            btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
        }}
    }}

    // Handle Sign In
    async function handleSignIn(event) {{
        event.preventDefault();
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Signing in...';
        hideMessage();

        const data = {{
            email: form.querySelector('#signin-email').value,
            password: form.querySelector('#signin-password').value
        }};

        try {{
            const response = await fetch('/api/auth/signin', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }});

            const result = await response.json();

            if (result.success) {{
                showMessage('Sign in successful! Redirecting...', 'success');
                setTimeout(() => {{
                    window.location.href = '/portal';
                }}, 1000);
            }} else {{
                showMessage(result.error || 'Sign in failed', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }}
        }} catch (error) {{
            showMessage('An error occurred. Please try again.', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }}
    }}

    // Handle Register
    async function handleRegister(event) {{
        event.preventDefault();
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';
        hideMessage();

        const password = form.querySelector('#register-password').value;
        const confirmPassword = form.querySelector('#register-confirm-password').value;

        if (password !== confirmPassword) {{
            showMessage('Passwords do not match', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            return;
        }}

        if (password.length < 8) {{
            showMessage('Password must be at least 8 characters', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            return;
        }}

        const data = {{
            first_name: form.querySelector('#register-first-name').value,
            last_name: form.querySelector('#register-last-name').value,
            email: form.querySelector('#register-email').value,
            phone: form.querySelector('#register-phone').value,
            password: password
        }};

        try {{
            const response = await fetch('/api/auth/register', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }});

            const result = await response.json();

            if (result.success) {{
                showMessage('Account created! Redirecting...', 'success');
                setTimeout(() => {{
                    window.location.href = '/portal';
                }}, 1000);
            }} else {{
                showMessage(result.error || 'Registration failed', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }}
        }} catch (error) {{
            showMessage('An error occurred. Please try again.', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }}
    }}

    // Google Sign In
    function handleGoogleCredentialResponse(response) {{
        fetch('/api/auth/google', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ credential: response.credential }})
        }})
        .then(res => res.json())
        .then(result => {{
            if (result.success) {{
                showMessage('Sign in successful! Redirecting...', 'success');
                setTimeout(() => {{
                    window.location.href = '/portal';
                }}, 1000);
            }} else {{
                showMessage(result.error || 'Google sign in failed', 'error');
            }}
        }})
        .catch(error => {{
            showMessage('An error occurred. Please try again.', 'error');
        }});
    }}

    // Initialize Google Sign In
    document.addEventListener('DOMContentLoaded', function() {{
        // Initialize Google Identity Services if client ID is available
        const googleClientId = '{GOOGLE_CLIENT_ID}';
        if (googleClientId && typeof google !== 'undefined') {{
            google.accounts.id.initialize({{
                client_id: googleClientId,
                callback: handleGoogleCredentialResponse
            }});

            // Render custom Google button
            document.querySelectorAll('.google-signin-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    google.accounts.id.prompt();
                }});
            }});
        }}
    }});
    """


def signin_page():
    """Sign in / Register page"""

    # Google Sign In script
    google_script = Script(src="https://accounts.google.com/gsi/client", async_=True) if GOOGLE_CLIENT_ID else ""

    content = Div(
        Section(
            Div(
                # Header
                Div(
                    H1("Welcome", cls="signin-title"),
                    P("Sign in to access your account", cls="signin-subtitle"),
                    cls="signin-header"
                ),

                # Message area
                Div(id="signin-message", cls="signin-message"),

                # Tab buttons
                Div(
                    Button("Sign In", cls="signin-tab active", **{"data-tab": "signin"}, onclick="switchTab('signin')"),
                    Button("Register", cls="signin-tab", **{"data-tab": "register"}, onclick="switchTab('register')"),
                    cls="signin-tabs"
                ),

                # Sign In Panel
                Div(
                    # Google Sign In
                    Button(
                        Svg(
                            Path(d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z", fill="#4285F4"),
                            Path(d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z", fill="#34A853"),
                            Path(d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z", fill="#FBBC05"),
                            Path(d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z", fill="#EA4335"),
                            viewBox="0 0 24 24"
                        ),
                        "Continue with Google",
                        type="button",
                        cls="google-signin-btn"
                    ) if GOOGLE_CLIENT_ID else "",

                    # Divider
                    Div(
                        Span("or"),
                        cls="signin-divider"
                    ) if GOOGLE_CLIENT_ID else "",

                    # Sign In Form
                    Form(
                        Div(
                            Label("Email", cls="form-label", **{"for": "signin-email"}),
                            Input(type="email", id="signin-email", cls="form-input", placeholder="Enter your email", required=True),
                            cls="form-group"
                        ),
                        Div(
                            Label("Password", cls="form-label", **{"for": "signin-password"}),
                            Div(
                                Input(type="password", id="signin-password", cls="form-input", placeholder="Enter your password", required=True),
                                Button(
                                    Svg(
                                        Path(d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"),
                                        Circle(cx="12", cy="12", r="3"),
                                        viewBox="0 0 24 24",
                                        fill="none",
                                        stroke="currentColor",
                                        stroke_width="2"
                                    ),
                                    type="button",
                                    cls="password-toggle",
                                    onclick="togglePassword('signin-password')"
                                ),
                                cls="password-wrapper"
                            ),
                            cls="form-group"
                        ),
                        Button("Sign In", type="submit", cls="signin-submit"),
                        cls="signin-form",
                        onsubmit="handleSignIn(event)"
                    ),
                    id="signin-panel",
                    cls="signin-panel active"
                ),

                # Register Panel
                Div(
                    # Google Sign In
                    Button(
                        Svg(
                            Path(d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z", fill="#4285F4"),
                            Path(d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z", fill="#34A853"),
                            Path(d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z", fill="#FBBC05"),
                            Path(d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z", fill="#EA4335"),
                            viewBox="0 0 24 24"
                        ),
                        "Continue with Google",
                        type="button",
                        cls="google-signin-btn"
                    ) if GOOGLE_CLIENT_ID else "",

                    # Divider
                    Div(
                        Span("or"),
                        cls="signin-divider"
                    ) if GOOGLE_CLIENT_ID else "",

                    # Register Form
                    Form(
                        Div(
                            Div(
                                Label("First Name", cls="form-label", **{"for": "register-first-name"}),
                                Input(type="text", id="register-first-name", cls="form-input", placeholder="First name", required=True),
                                cls="form-group"
                            ),
                            Div(
                                Label("Last Name", cls="form-label", **{"for": "register-last-name"}),
                                Input(type="text", id="register-last-name", cls="form-input", placeholder="Last name", required=True),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Label("Email", cls="form-label", **{"for": "register-email"}),
                            Input(type="email", id="register-email", cls="form-input", placeholder="Enter your email", required=True),
                            cls="form-group"
                        ),
                        Div(
                            Label("Phone (optional)", cls="form-label", **{"for": "register-phone"}),
                            Input(type="tel", id="register-phone", cls="form-input", placeholder="Enter your phone number"),
                            cls="form-group"
                        ),
                        Div(
                            Label("Password", cls="form-label", **{"for": "register-password"}),
                            Div(
                                Input(type="password", id="register-password", cls="form-input", placeholder="Create a password (min 8 characters)", required=True, minlength="8"),
                                Button(
                                    Svg(
                                        Path(d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"),
                                        Circle(cx="12", cy="12", r="3"),
                                        viewBox="0 0 24 24",
                                        fill="none",
                                        stroke="currentColor",
                                        stroke_width="2"
                                    ),
                                    type="button",
                                    cls="password-toggle",
                                    onclick="togglePassword('register-password')"
                                ),
                                cls="password-wrapper"
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Confirm Password", cls="form-label", **{"for": "register-confirm-password"}),
                            Div(
                                Input(type="password", id="register-confirm-password", cls="form-input", placeholder="Confirm your password", required=True),
                                Button(
                                    Svg(
                                        Path(d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"),
                                        Circle(cx="12", cy="12", r="3"),
                                        viewBox="0 0 24 24",
                                        fill="none",
                                        stroke="currentColor",
                                        stroke_width="2"
                                    ),
                                    type="button",
                                    cls="password-toggle",
                                    onclick="togglePassword('register-confirm-password')"
                                ),
                                cls="password-wrapper"
                            ),
                            cls="form-group"
                        ),
                        Button("Create Account", type="submit", cls="signin-submit"),
                        cls="signin-form",
                        onsubmit="handleRegister(event)"
                    ),
                    id="register-panel",
                    cls="signin-panel"
                ),

                cls="signin-container"
            ),
            cls="signin-section"
        ),
        google_script,
        cls="signin-content"
    )

    return create_page(
        "Sign In | Astra Staging",
        content,
        additional_styles=get_signin_styles(),
        additional_scripts=get_signin_scripts(),
        description="Sign in or create an account to access Astra Staging customer portal.",
        keywords="sign in, login, register, account, astra staging",
        hide_floating_buttons=True
    )
