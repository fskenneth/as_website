"""
User Portal Page for Astra Staging
Content varies based on user role (customer, admin, manager, stager, mover)
"""

from fasthtml.common import *
from page.components import create_page, Circle, Line, Polyline, SvgPath


def get_portal_styles():
    """CSS styles for portal page"""
    return """
    /* Portal Page Styles */
    .portal-section {
        min-height: calc(100vh - 200px);
        padding: 40px 40px;
        background: var(--bg-primary);
    }

    .portal-container {
        max-width: 1100px;
        margin: 0 auto;
    }

    .portal-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 24px;
        flex-wrap: nowrap;
    }

    .portal-greeting {
        font-size: 18px;
        color: var(--color-secondary);
    }

    .portal-user-name {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
    }

    .portal-signout {
        margin-left: auto;
        padding: 8px 16px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background: transparent;
        color: var(--color-primary);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .portal-signout:hover {
        border-color: var(--border-hover);
        background: var(--bg-secondary);
    }

    /* Tabs */
    .portal-tabs {
        display: flex;
        gap: 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 24px;
    }

    .portal-tab {
        padding: 12px 24px;
        background: none;
        border: none;
        border-bottom: 2px solid transparent;
        color: var(--color-secondary);
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .portal-tab:hover {
        color: var(--color-primary);
    }

    .portal-tab.active {
        color: var(--color-primary);
        border-bottom-color: var(--color-primary);
    }

    /* Tab Content */
    .portal-tab-content {
        display: none;
    }

    .portal-tab-content.active {
        display: block;
    }

    /* Users Table */
    .users-table-container {
        background: var(--bg-secondary);
        border-radius: 12px;
        overflow: hidden;
    }

    .users-table {
        width: 100%;
        border-collapse: collapse;
    }

    .users-table th,
    .users-table td {
        padding: 14px 16px;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
    }

    .users-table th {
        background: var(--bg-primary);
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--color-secondary);
    }

    .users-table tr:last-child td {
        border-bottom: none;
    }

    .users-table tr:hover td {
        background: var(--bg-primary);
    }

    .users-table td {
        font-size: 14px;
        color: var(--color-primary);
    }

    .role-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        text-transform: capitalize;
    }

    .role-badge.admin { background: #fee2e2; color: #dc2626; }
    .role-badge.manager { background: #fef3c7; color: #d97706; }
    .role-badge.stager { background: #dbeafe; color: #2563eb; }
    .role-badge.mover { background: #d1fae5; color: #059669; }
    .role-badge.customer { background: #f3f4f6; color: #6b7280; }

    [data-theme="dark"] .role-badge.admin { background: rgba(220, 38, 38, 0.2); }
    [data-theme="dark"] .role-badge.manager { background: rgba(217, 119, 6, 0.2); }
    [data-theme="dark"] .role-badge.stager { background: rgba(37, 99, 235, 0.2); }
    [data-theme="dark"] .role-badge.mover { background: rgba(5, 150, 105, 0.2); }
    [data-theme="dark"] .role-badge.customer { background: rgba(107, 114, 128, 0.2); }

    .edit-btn {
        padding: 6px 14px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background: transparent;
        color: var(--color-primary);
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .edit-btn:hover {
        background: var(--bg-primary);
        border-color: var(--border-hover);
    }

    /* Modal */
    .modal-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        align-items: center;
        justify-content: center;
    }

    .modal-overlay.active {
        display: flex;
    }

    .modal-content {
        background: var(--bg-primary);
        border-radius: 12px;
        padding: 24px;
        width: 100%;
        max-width: 480px;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }

    .modal-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--color-primary);
    }

    .modal-close {
        background: none;
        border: none;
        font-size: 24px;
        color: var(--color-secondary);
        cursor: pointer;
        padding: 4px;
        line-height: 1;
    }

    .modal-close:hover {
        color: var(--color-primary);
    }

    .modal-form {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .modal-form .form-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .modal-form .form-row {
        display: flex;
        gap: 16px;
    }

    .modal-form .form-row .form-group {
        flex: 1;
    }

    .modal-form label {
        font-size: 13px;
        font-weight: 500;
        color: var(--color-secondary);
    }

    .modal-form input,
    .modal-form select {
        padding: 10px 12px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background: var(--bg-secondary);
        color: var(--color-primary);
        font-size: 14px;
    }

    .modal-form input:focus,
    .modal-form select:focus {
        outline: none;
        border-color: var(--border-hover);
    }

    .modal-actions {
        display: flex;
        gap: 12px;
        justify-content: flex-end;
        margin-top: 8px;
    }

    .modal-btn {
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .modal-btn.cancel {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--color-primary);
    }

    .modal-btn.cancel:hover {
        background: var(--bg-secondary);
    }

    .modal-btn.save {
        background: var(--color-primary);
        border: 1px solid var(--color-primary);
        color: var(--bg-primary);
    }

    .modal-btn.save:hover {
        opacity: 0.9;
    }

    .modal-message {
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        margin-bottom: 16px;
        display: none;
    }

    .modal-message.error {
        display: block;
        background: rgba(220, 38, 38, 0.1);
        color: #dc2626;
    }

    .modal-message.success {
        display: block;
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
    }

    /* Dashboard placeholder */
    .dashboard-placeholder {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 60px 40px;
        text-align: center;
    }

    .dashboard-placeholder-icon {
        width: 60px;
        height: 60px;
        margin: 0 auto 20px;
        color: var(--color-accent);
    }

    .dashboard-placeholder-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 8px;
    }

    .dashboard-placeholder-text {
        font-size: 14px;
        color: var(--color-secondary);
    }

    /* Mobile adjustments */
    @media (max-width: 767px) {
        .portal-section {
            padding: 24px 16px;
        }

        .portal-header {
            gap: 4px;
        }

        .portal-greeting {
            font-size: 14px;
        }

        .portal-user-name {
            font-size: 14px;
        }

        .portal-signout {
            padding: 6px 12px;
            font-size: 12px;
        }

        .portal-tab {
            padding: 10px 16px;
            font-size: 14px;
        }

        .users-table-container {
            overflow-x: auto;
        }

        .users-table {
            min-width: auto;
        }

        /* Hide phone and role columns on mobile */
        .users-table th:nth-child(3),
        .users-table td:nth-child(3),
        .users-table th:nth-child(4),
        .users-table td:nth-child(4) {
            display: none;
        }

        .modal-content {
            margin: 16px;
            padding: 20px;
        }

        .modal-form .form-row {
            flex-direction: column;
        }
    }
    """


def get_portal_scripts():
    """JavaScript for portal page"""
    return """
    // Handle sign out
    async function handleSignOut() {
        try {
            const response = await fetch('/api/auth/signout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            window.location.href = '/signin';
        } catch (error) {
            window.location.href = '/signin';
        }
    }

    // Tab switching
    function switchPortalTab(tabName) {
        document.querySelectorAll('.portal-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        document.querySelectorAll('.portal-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`tab-${tabName}`).classList.add('active');
    }

    // Load users for admin
    async function loadUsers() {
        try {
            const response = await fetch('/api/admin/users');
            const data = await response.json();
            if (data.users) {
                renderUsersTable(data.users);
            }
        } catch (error) {
            console.error('Failed to load users:', error);
        }
    }

    function renderUsersTable(users) {
        const tbody = document.getElementById('users-tbody');
        if (!tbody) return;

        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.first_name} ${user.last_name}</td>
                <td>${user.email}</td>
                <td>${user.phone || '-'}</td>
                <td><span class="role-badge ${user.user_role}">${user.user_role}</span></td>
                <td>
                    <button class="edit-btn" onclick="openEditModal(${user.id})">Edit</button>
                </td>
            </tr>
        `).join('');

        // Store users data for editing
        window.usersData = users;
    }

    // Modal functions
    function openEditModal(userId) {
        const user = window.usersData.find(u => u.id === userId);
        if (!user) return;

        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-first-name').value = user.first_name;
        document.getElementById('edit-last-name').value = user.last_name;
        document.getElementById('edit-email').value = user.email;
        document.getElementById('edit-phone').value = user.phone || '';
        document.getElementById('edit-role').value = user.user_role;
        document.getElementById('edit-password').value = '';

        hideModalMessage();
        document.getElementById('edit-modal').classList.add('active');
    }

    function closeEditModal() {
        document.getElementById('edit-modal').classList.remove('active');
    }

    function showModalMessage(message, type) {
        const msgEl = document.getElementById('modal-message');
        msgEl.textContent = message;
        msgEl.className = 'modal-message ' + type;
    }

    function hideModalMessage() {
        const msgEl = document.getElementById('modal-message');
        msgEl.className = 'modal-message';
    }

    async function saveUser(event) {
        event.preventDefault();
        const form = event.target;
        const saveBtn = form.querySelector('.modal-btn.save');
        const originalText = saveBtn.textContent;

        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        hideModalMessage();

        const data = {
            id: parseInt(document.getElementById('edit-user-id').value),
            first_name: document.getElementById('edit-first-name').value,
            last_name: document.getElementById('edit-last-name').value,
            email: document.getElementById('edit-email').value,
            phone: document.getElementById('edit-phone').value || null,
            user_role: document.getElementById('edit-role').value,
            password: document.getElementById('edit-password').value || null
        };

        try {
            const response = await fetch('/api/admin/users/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showModalMessage('User updated successfully', 'success');
                setTimeout(() => {
                    closeEditModal();
                    loadUsers();
                }, 1000);
            } else {
                showModalMessage(result.error || 'Failed to update user', 'error');
            }
        } catch (error) {
            showModalMessage('An error occurred', 'error');
        }

        saveBtn.disabled = false;
        saveBtn.textContent = originalText;
    }

    // Close modal on overlay click
    document.addEventListener('DOMContentLoaded', function() {
        const modal = document.getElementById('edit-modal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeEditModal();
                }
            });
        }

        // Load users if admin
        if (document.getElementById('users-tbody')) {
            loadUsers();
        }
    });
    """


def portal_page(user: dict = None):
    """
    Portal page - content varies by user role
    User dict should contain: first_name, last_name, email, user_role
    """

    if not user:
        first_name = "Guest"
        last_name = ""
        user_role = "customer"
    else:
        first_name = user.get('first_name', 'User')
        last_name = user.get('last_name', '')
        user_role = user.get('user_role', 'customer')

    full_name = f"{first_name} {last_name}".strip()
    is_admin = user_role == 'admin'

    # Build tabs based on role
    tabs = [
        ("dashboard", "Dashboard"),
    ]
    if is_admin:
        tabs.append(("users", "Users"))

    # Tab buttons
    tab_buttons = [
        Button(
            label,
            cls=f"portal-tab {'active' if i == 0 else ''}",
            **{"data-tab": tab_id},
            onclick=f"switchPortalTab('{tab_id}')"
        )
        for i, (tab_id, label) in enumerate(tabs)
    ]

    # Dashboard tab content
    dashboard_content = Div(
        Div(
            Svg(
                Circle(cx="12", cy="12", r="10"),
                SvgPath(d="M12 6v6l4 2"),
                viewBox="0 0 24 24",
                fill="none",
                stroke="currentColor",
                **{"stroke-width": "2", "stroke-linecap": "round", "stroke-linejoin": "round"},
                cls="dashboard-placeholder-icon"
            ),
            H2("Dashboard Coming Soon", cls="dashboard-placeholder-title"),
            P("Your personalized dashboard is being set up.", cls="dashboard-placeholder-text"),
            cls="dashboard-placeholder"
        ),
        id="tab-dashboard",
        cls="portal-tab-content active"
    )

    # Users tab content (admin only)
    users_content = Div(
        Div(
            Table(
                Thead(
                    Tr(
                        Th("Name"),
                        Th("Email"),
                        Th("Phone"),
                        Th("Role"),
                        Th("Actions"),
                    )
                ),
                Tbody(id="users-tbody"),
                cls="users-table"
            ),
            cls="users-table-container"
        ),
        id="tab-users",
        cls="portal-tab-content"
    ) if is_admin else ""

    # Edit user modal
    edit_modal = Div(
        Div(
            Div(
                H3("Edit User", cls="modal-title"),
                Button("×", cls="modal-close", onclick="closeEditModal()"),
                cls="modal-header"
            ),
            Div(id="modal-message", cls="modal-message"),
            Form(
                Input(type="hidden", id="edit-user-id"),
                Div(
                    Div(
                        Label("First Name", **{"for": "edit-first-name"}),
                        Input(type="text", id="edit-first-name", required=True),
                        cls="form-group"
                    ),
                    Div(
                        Label("Last Name", **{"for": "edit-last-name"}),
                        Input(type="text", id="edit-last-name", required=True),
                        cls="form-group"
                    ),
                    cls="form-row"
                ),
                Div(
                    Label("Email", **{"for": "edit-email"}),
                    Input(type="email", id="edit-email", required=True),
                    cls="form-group"
                ),
                Div(
                    Label("Phone", **{"for": "edit-phone"}),
                    Input(type="tel", id="edit-phone"),
                    cls="form-group"
                ),
                Div(
                    Label("Role", **{"for": "edit-role"}),
                    Select(
                        Option("Customer", value="customer"),
                        Option("Admin", value="admin"),
                        Option("Manager", value="manager"),
                        Option("Stager", value="stager"),
                        Option("Mover", value="mover"),
                        id="edit-role"
                    ),
                    cls="form-group"
                ),
                Div(
                    Label("New Password (leave blank to keep current)", **{"for": "edit-password"}),
                    Input(type="password", id="edit-password", placeholder="Enter new password"),
                    cls="form-group"
                ),
                Div(
                    Button("Cancel", type="button", cls="modal-btn cancel", onclick="closeEditModal()"),
                    Button("Save Changes", type="submit", cls="modal-btn save"),
                    cls="modal-actions"
                ),
                cls="modal-form",
                onsubmit="saveUser(event)"
            ),
            cls="modal-content"
        ),
        id="edit-modal",
        cls="modal-overlay"
    ) if is_admin else ""

    content = Div(
        Section(
            Div(
                # Header
                Div(
                    Span("Welcome back, ", cls="portal-greeting"),
                    Span(full_name, cls="portal-user-name"),
                    Button("Sign Out", cls="portal-signout", onclick="handleSignOut()"),
                    cls="portal-header"
                ),

                # Tabs
                Div(*tab_buttons, cls="portal-tabs"),

                # Tab contents
                dashboard_content,
                users_content,

                cls="portal-container"
            ),
            cls="portal-section"
        ),
        edit_modal,
        cls="portal-page"
    )

    return create_page(
        "Portal | Astra Staging",
        content,
        additional_styles=get_portal_styles(),
        additional_scripts=get_portal_scripts(),
        description="Access your Astra Staging customer portal.",
        keywords="portal, dashboard, account, astra staging",
        hide_floating_buttons=True
    )
