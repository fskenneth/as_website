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

    .portal-header-actions {
        margin-left: auto;
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .portal-edit-btn {
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

    .portal-edit-btn:hover {
        border-color: var(--border-hover);
        background: var(--bg-secondary);
    }

    .portal-signout {
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

    .modal-form input.input-error {
        border-color: #dc2626;
    }

    .modal-form input.input-error:focus {
        border-color: #dc2626;
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

    /* Staging Tab Styles */
    .staging-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .staging-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }

    .staging-card:hover {
        border-color: var(--border-hover);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .staging-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
        gap: 12px;
    }

    .staging-address {
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
        line-height: 1.3;
    }

    .staging-address.staging-address-pending {
        color: var(--color-secondary);
        font-style: italic;
    }

    .staging-status {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        flex-shrink: 0;
    }

    .staging-status.quote {
        background: #fef3c7;
        color: #d97706;
    }

    .staging-status.confirmed {
        background: #d1fae5;
        color: #059669;
    }

    [data-theme="dark"] .staging-status.quote {
        background: rgba(217, 119, 6, 0.2);
    }

    [data-theme="dark"] .staging-status.confirmed {
        background: rgba(5, 150, 105, 0.2);
    }

    .staging-card-body {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }

    .staging-detail {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .staging-detail.full-width {
        grid-column: 1 / -1;
    }

    .staging-detail-label {
        font-size: 12px;
        font-weight: 500;
        color: var(--color-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .staging-detail-value {
        font-size: 14px;
        color: var(--color-primary);
    }

    .staging-total {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .staging-total-label {
        font-size: 14px;
        font-weight: 500;
        color: var(--color-secondary);
    }

    .staging-total-value {
        font-size: 20px;
        font-weight: 700;
        color: #4CAF50;
    }

    .staging-actions {
        margin-top: 16px;
        display: flex;
        gap: 12px;
    }

    .staging-action-btn {
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .staging-action-btn.primary {
        background: #4CAF50;
        color: white;
        border: none;
    }

    .staging-action-btn.primary:hover {
        background: #45a049;
    }

    .staging-action-btn.secondary {
        background: transparent;
        color: var(--color-primary);
        border: 1px solid var(--border-color);
    }

    .staging-action-btn.secondary:hover {
        border-color: var(--border-hover);
        background: var(--bg-primary);
    }

    .staging-empty {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 60px 40px;
        text-align: center;
    }

    .staging-empty-icon {
        width: 60px;
        height: 60px;
        margin: 0 auto 20px;
        color: var(--color-accent);
    }

    .staging-empty-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 8px;
    }

    .staging-empty-text {
        font-size: 14px;
        color: var(--color-secondary);
        margin-bottom: 20px;
    }

    .staging-empty-btn {
        display: inline-block;
        padding: 12px 24px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .staging-empty-btn:hover {
        background: #45a049;
    }

    .staging-areas-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }

    .staging-area-tag {
        display: inline-block;
        padding: 3px 8px;
        background: rgba(76, 175, 80, 0.1);
        color: #4CAF50;
        border-radius: 4px;
        font-size: 12px;
    }

    [data-theme="dark"] .staging-area-tag {
        background: rgba(76, 175, 80, 0.2);
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

        .portal-header-actions {
            gap: 8px;
        }

        .portal-edit-btn,
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

        .staging-address {
            font-size: 16px;
        }

        .staging-action-btn {
            flex: 1;
            text-align: center;
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

        // Validate email
        const emailField = document.getElementById('edit-email');
        const email = emailField.value.toLowerCase().trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
            showModalMessage('Please enter a valid email address', 'error');
            emailField.classList.add('input-error');
            emailField.focus();
            return;
        }
        emailField.classList.remove('input-error');

        // Validate phone (must have 10 digits)
        const phoneField = document.getElementById('edit-phone');
        const phoneDigits = phoneField.value.replace(/\D/g, '');
        if (!phoneDigits || phoneDigits.length < 10) {
            showModalMessage('Please enter a valid 10-digit phone number', 'error');
            phoneField.classList.add('input-error');
            phoneField.focus();
            return;
        }
        phoneField.classList.remove('input-error');

        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        hideModalMessage();

        const data = {
            id: parseInt(document.getElementById('edit-user-id').value),
            first_name: document.getElementById('edit-first-name').value,
            last_name: document.getElementById('edit-last-name').value,
            email: email,
            phone: phoneField.value || null,
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

        // Load staging data
        if (document.getElementById('staging-container')) {
            loadStagingData();
        }
    });

    // Session storage keys
    const STAGING_SESSION_KEY = 'astra_staging_data';
    const RESERVE_SESSION_KEY = 'astra_reserve_data';

    // Area display names
    const areaDisplayNames = {
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
    };

    // Load staging data from server and merge with local storage
    async function loadStagingData() {
        const container = document.getElementById('staging-container');
        if (!container) return;

        const stagingItems = [];

        // First, try to load from server
        try {
            const response = await fetch('/api/stagings');
            const result = await response.json();
            if (result.success && result.stagings) {
                result.stagings.forEach(staging => {
                    stagingItems.push({
                        id: staging.id,
                        propertyAddress: staging.property_address,
                        propertyType: staging.property_type,
                        propertySize: staging.property_size,
                        selectedAreas: staging.selected_areas ? JSON.parse(staging.selected_areas) : [],
                        selectedItems: staging.selected_items ? JSON.parse(staging.selected_items) : {},
                        totalFee: staging.total_fee,
                        stagingDate: staging.staging_date,
                        stagingDateDisplay: staging.staging_date,
                        addons: staging.addons ? JSON.parse(staging.addons) : [],
                        status: staging.status,
                        fromServer: true
                    });
                });
            }
        } catch (e) {
            console.warn('Error loading stagings from server:', e);
        }

        // Load local session storage data
        let stagingInfo = {};
        let reserveInfo = {};
        try {
            const stagingData = sessionStorage.getItem(STAGING_SESSION_KEY);
            if (stagingData) stagingInfo = JSON.parse(stagingData);
        } catch (e) {}
        try {
            const reserveData = sessionStorage.getItem(RESERVE_SESSION_KEY);
            if (reserveData) reserveInfo = JSON.parse(reserveData);
        } catch (e) {}

        // Check if we have local quote data not yet synced
        const hasPropertyType = stagingInfo.propertyType || reserveInfo.propertyType;
        const hasPropertySize = stagingInfo.propertySize || reserveInfo.propertySize;
        const hasSelectedAreas = (stagingInfo.selectedAreas && stagingInfo.selectedAreas.length > 0);

        if (hasPropertyType || hasPropertySize || hasSelectedAreas) {
            const localData = { ...stagingInfo, ...reserveInfo, status: 'quote' };

            // Check if this local data already exists on server (by property address or similar data)
            const existsOnServer = stagingItems.some(item =>
                item.propertyAddress && localData.propertyAddress &&
                item.propertyAddress === localData.propertyAddress
            );

            if (!existsOnServer) {
                // Sync local data to server
                await syncLocalToServer(localData);
                // Reload to get the synced data
                return loadStagingData();
            }
        }

        renderStagingItems(container, stagingItems);
    }

    // Sync local storage data to server
    async function syncLocalToServer(localData, existingStagingId = null) {
        try {
            // First, check if there's an existing unpaid quote on server
            let stagingId = existingStagingId;
            if (!stagingId) {
                const checkResponse = await fetch('/api/stagings?status=quote');
                const checkResult = await checkResponse.json();
                if (checkResult.success && checkResult.stagings && checkResult.stagings.length > 0) {
                    stagingId = checkResult.stagings[0].id;
                }
            }

            const serverData = {
                status: 'quote',
                property_address: localData.propertyAddress || '',
                property_type: localData.propertyType || '',
                property_size: localData.propertySize || '',
                selected_areas: JSON.stringify(localData.selectedAreas || []),
                selected_items: JSON.stringify(localData.selectedItems || localData.areaItemsData || {}),
                area_photos: JSON.stringify(localData.areaPhotos || {}),
                total_fee: localData.totalFee || '',
                staging_date: localData.stagingDateDisplay || localData.stagingDate || '',
                addons: JSON.stringify(localData.addons || []),
                property_status: localData.propertyStatus || '',
                user_type: localData.userType || '',
                pets_status: localData.petsStatus || '',
                referral_source: localData.referralSource || '',
                guest_first_name: localData.guestFirstName || '',
                guest_last_name: localData.guestLastName || '',
                guest_email: localData.guestEmail || '',
                guest_phone: localData.guestPhone || '',
                special_requests: localData.specialRequests || ''
            };

            // Include staging ID if updating existing quote
            if (stagingId) {
                serverData.id = stagingId;
            }

            const response = await fetch('/api/stagings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(serverData)
            });

            const result = await response.json();
            if (result.success) {
                // Clear local storage after successful sync
                sessionStorage.removeItem(STAGING_SESSION_KEY);
                sessionStorage.removeItem(RESERVE_SESSION_KEY);
                console.log('Local quote synced to server, staging_id:', result.staging_id);
            }
        } catch (e) {
            console.warn('Error syncing to server:', e);
        }
    }

    // Render staging items
    function renderStagingItems(container, items) {
        if (items.length === 0) {
            container.innerHTML = `
                <div class="staging-empty">
                    <svg class="staging-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="9" y1="3" x2="9" y2="21"></line>
                    </svg>
                    <h3 class="staging-empty-title">No Staging Quotes</h3>
                    <p class="staging-empty-text">You haven't created any staging quotes yet. Get started by getting an instant quote for your property.</p>
                    <a href="/staging-inquiry/" class="staging-empty-btn">Get Instant Quote</a>
                </div>
            `;
            return;
        }

        container.innerHTML = items.map(item => renderStagingCard(item)).join('');
    }

    // Render a single staging card
    function renderStagingCard(item) {
        const statusClass = item.status === 'confirmed' ? 'confirmed' : 'quote';
        const statusText = item.status === 'confirmed' ? 'Confirmed' : 'Quote';

        // Format property type
        const propType = item.propertyType ?
            item.propertyType.charAt(0).toUpperCase() + item.propertyType.slice(1) :
            '-';

        // Format property size
        const propSize = item.propertySize ? item.propertySize + ' sq ft' : '-';

        // Format selected areas
        let areasHtml = '-';
        if (item.selectedAreas && item.selectedAreas.length > 0) {
            areasHtml = `<div class="staging-areas-list">
                ${item.selectedAreas.map(area =>
                    `<span class="staging-area-tag">${areaDisplayNames[area] || area}</span>`
                ).join('')}
            </div>`;
        }

        // Format total fee
        let totalFee = '$0.00';
        if (item.totalFee) {
            if (typeof item.totalFee === 'string') {
                totalFee = item.totalFee.startsWith('$') ? item.totalFee : '$' + item.totalFee;
            } else {
                totalFee = '$' + item.totalFee.toLocaleString('en-CA', { minimumFractionDigits: 2 });
            }
        }

        // Format date
        let stagingDate = '-';
        if (item.stagingDateDisplay) {
            stagingDate = item.stagingDateDisplay;
        } else if (item.stagingDate) {
            stagingDate = item.stagingDate;
        }

        // Format addons
        let addonsText = '-';
        if (item.addons && item.addons.length > 0) {
            const addonNames = {
                'photos': 'Photography',
                'consultation': 'Consultation',
                'furniture-move': 'Furniture Move'
            };
            addonsText = item.addons.map(a => addonNames[a] || a).join(', ');
        }

        // Action buttons
        let actionsHtml = '';
        if (item.status === 'quote') {
            actionsHtml = `
                <div class="staging-actions">
                    <a href="/staging-inquiry/" class="staging-action-btn secondary">Edit Quote</a>
                    <a href="/reserve/" class="staging-action-btn primary">Complete Booking</a>
                </div>
            `;
        }

        // Address display
        const addressDisplay = item.propertyAddress || 'Property Address Not Set';
        const addressClass = item.propertyAddress ? '' : 'staging-address-pending';

        return `
            <div class="staging-card">
                <div class="staging-card-header">
                    <div class="staging-address ${addressClass}">${addressDisplay}</div>
                    <span class="staging-status ${statusClass}">${statusText}</span>
                </div>
                <div class="staging-card-body">
                    <div class="staging-detail">
                        <span class="staging-detail-label">Property Type</span>
                        <span class="staging-detail-value">${propType}</span>
                    </div>
                    <div class="staging-detail">
                        <span class="staging-detail-label">Property Size</span>
                        <span class="staging-detail-value">${propSize}</span>
                    </div>
                    <div class="staging-detail">
                        <span class="staging-detail-label">Staging Date</span>
                        <span class="staging-detail-value">${stagingDate}</span>
                    </div>
                    <div class="staging-detail">
                        <span class="staging-detail-label">Add-ons</span>
                        <span class="staging-detail-value">${addonsText}</span>
                    </div>
                    <div class="staging-detail full-width">
                        <span class="staging-detail-label">Selected Areas</span>
                        <div class="staging-detail-value">${areasHtml}</div>
                    </div>
                </div>
                <div class="staging-total">
                    <span class="staging-total-label">Total Staging Fee</span>
                    <span class="staging-total-value">${totalFee}</span>
                </div>
                ${actionsHtml}
            </div>
        `;
    }

    // Clear quote from session storage and server
    async function clearQuote(stagingId) {
        if (!confirm('Are you sure you want to remove this quote?')) return;

        // Clear local storage
        sessionStorage.removeItem(STAGING_SESSION_KEY);
        sessionStorage.removeItem(RESERVE_SESSION_KEY);

        // Delete from server if we have a staging ID
        if (stagingId) {
            try {
                await fetch('/api/stagings/' + stagingId, { method: 'DELETE' });
            } catch (e) {
                console.warn('Error deleting staging from server:', e);
            }
        }

        loadStagingData();
    }

    // Profile modal functions
    function openProfileModal() {
        // Fetch current user data
        fetch('/api/auth/check')
            .then(response => response.json())
            .then(data => {
                if (data.authenticated && data.user) {
                    document.getElementById('profile-first-name').value = data.user.first_name || '';
                    document.getElementById('profile-last-name').value = data.user.last_name || '';
                    document.getElementById('profile-email').value = data.user.email || '';
                    document.getElementById('profile-phone').value = data.user.phone || '';
                    document.getElementById('profile-password').value = '';
                    hideProfileModalMessage();
                    document.getElementById('profile-modal').classList.add('active');
                }
            })
            .catch(error => {
                console.error('Failed to load user data:', error);
            });
    }

    function closeProfileModal() {
        document.getElementById('profile-modal').classList.remove('active');
    }

    function showProfileModalMessage(message, type) {
        const msgEl = document.getElementById('profile-modal-message');
        msgEl.textContent = message;
        msgEl.className = 'modal-message ' + type;
    }

    function hideProfileModalMessage() {
        const msgEl = document.getElementById('profile-modal-message');
        msgEl.className = 'modal-message';
    }

    async function saveProfile(event) {
        event.preventDefault();
        const form = event.target;
        const saveBtn = form.querySelector('.modal-btn.save');
        const originalText = saveBtn.textContent;

        // Validate email
        const emailField = document.getElementById('profile-email');
        const email = emailField.value.toLowerCase().trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
            showProfileModalMessage('Please enter a valid email address', 'error');
            emailField.classList.add('input-error');
            emailField.focus();
            return;
        }
        emailField.classList.remove('input-error');

        // Validate phone (must have 10 digits)
        const phoneField = document.getElementById('profile-phone');
        const phoneDigits = phoneField.value.replace(/\D/g, '');
        if (!phoneDigits || phoneDigits.length < 10) {
            showProfileModalMessage('Please enter a valid 10-digit phone number', 'error');
            phoneField.classList.add('input-error');
            phoneField.focus();
            return;
        }
        phoneField.classList.remove('input-error');

        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        hideProfileModalMessage();

        const data = {
            first_name: document.getElementById('profile-first-name').value,
            last_name: document.getElementById('profile-last-name').value,
            email: email,
            phone: phoneField.value || null,
            password: document.getElementById('profile-password').value || null
        };

        try {
            const response = await fetch('/api/profile/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showProfileModalMessage('Profile updated successfully', 'success');
                // Update the displayed name
                const nameEl = document.querySelector('.portal-user-name');
                if (nameEl) {
                    nameEl.textContent = (data.first_name + ' ' + data.last_name).trim();
                }
                setTimeout(() => {
                    closeProfileModal();
                }, 1000);
            } else {
                showProfileModalMessage(result.error || 'Failed to update profile', 'error');
            }
        } catch (error) {
            showProfileModalMessage('An error occurred', 'error');
        }

        saveBtn.disabled = false;
        saveBtn.textContent = originalText;
    }

    // Format phone number as (XXX) XXX-XXXX
    function formatPhoneNumber(value) {
        // Remove all non-digit characters
        const digits = value.replace(/\D/g, '');

        // Limit to 10 digits
        const limited = digits.substring(0, 10);

        // Format based on length
        if (limited.length === 0) return '';
        if (limited.length <= 3) return `(${limited}`;
        if (limited.length <= 6) return `(${limited.substring(0, 3)}) ${limited.substring(3)}`;
        return `(${limited.substring(0, 3)}) ${limited.substring(3, 6)}-${limited.substring(6)}`;
    }

    // Format and validate email (lowercase and trim)
    function formatEmail(value) {
        return value.toLowerCase().trim();
    }

    // Validate email format
    function validateEmail(input) {
        const value = input.value.toLowerCase().trim();
        input.value = value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailRegex.test(value)) {
            input.setCustomValidity('Please enter a valid email address');
            input.classList.add('input-error');
        } else {
            input.setCustomValidity('');
            input.classList.remove('input-error');
        }
    }

    // Close profile modal on overlay click and initialize formatters
    document.addEventListener('DOMContentLoaded', function() {
        const profileModal = document.getElementById('profile-modal');
        if (profileModal) {
            profileModal.addEventListener('click', function(e) {
                if (e.target === profileModal) {
                    closeProfileModal();
                }
            });
        }

        // Add phone formatting to profile phone field
        const profilePhone = document.getElementById('profile-phone');
        if (profilePhone) {
            profilePhone.addEventListener('input', function(e) {
                const cursorPos = e.target.selectionStart;
                const oldLength = e.target.value.length;
                e.target.value = formatPhoneNumber(e.target.value);
                const newLength = e.target.value.length;
                const newCursorPos = cursorPos + (newLength - oldLength);
                e.target.setSelectionRange(newCursorPos, newCursorPos);
            });
        }

        // Add email validation to profile email field
        const profileEmail = document.getElementById('profile-email');
        if (profileEmail) {
            profileEmail.addEventListener('blur', function(e) {
                validateEmail(e.target);
            });
        }

        // Add phone formatting to admin edit phone field
        const editPhone = document.getElementById('edit-phone');
        if (editPhone) {
            editPhone.addEventListener('input', function(e) {
                const cursorPos = e.target.selectionStart;
                const oldLength = e.target.value.length;
                e.target.value = formatPhoneNumber(e.target.value);
                const newLength = e.target.value.length;
                const newCursorPos = cursorPos + (newLength - oldLength);
                e.target.setSelectionRange(newCursorPos, newCursorPos);
            });
        }

        // Add email validation to admin edit email field
        const editEmail = document.getElementById('edit-email');
        if (editEmail) {
            editEmail.addEventListener('blur', function(e) {
                validateEmail(e.target);
            });
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
        ("staging", "Staging"),
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

    # Staging tab content (now the default active tab)
    staging_content = Div(
        Div(
            id="staging-container",
            cls="staging-container"
        ),
        id="tab-staging",
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

    # Profile edit modal (for all users to edit their own profile)
    profile_modal = Div(
        Div(
            Div(
                H3("Edit Profile", cls="modal-title"),
                Button("×", cls="modal-close", onclick="closeProfileModal()"),
                cls="modal-header"
            ),
            Div(id="profile-modal-message", cls="modal-message"),
            Form(
                Div(
                    Div(
                        Label("First Name", **{"for": "profile-first-name"}),
                        Input(type="text", id="profile-first-name", required=True),
                        cls="form-group"
                    ),
                    Div(
                        Label("Last Name", **{"for": "profile-last-name"}),
                        Input(type="text", id="profile-last-name", required=True),
                        cls="form-group"
                    ),
                    cls="form-row"
                ),
                Div(
                    Label("Email", **{"for": "profile-email"}),
                    Input(type="email", id="profile-email", required=True),
                    cls="form-group"
                ),
                Div(
                    Label("Phone", **{"for": "profile-phone"}),
                    Input(type="tel", id="profile-phone", required=True),
                    cls="form-group"
                ),
                Div(
                    Label("New Password (leave blank to keep current)", **{"for": "profile-password"}),
                    Input(type="password", id="profile-password", placeholder="Enter new password"),
                    cls="form-group"
                ),
                Div(
                    Button("Cancel", type="button", cls="modal-btn cancel", onclick="closeProfileModal()"),
                    Button("Save Changes", type="submit", cls="modal-btn save"),
                    cls="modal-actions"
                ),
                cls="modal-form",
                onsubmit="saveProfile(event)"
            ),
            cls="modal-content"
        ),
        id="profile-modal",
        cls="modal-overlay"
    )

    content = Div(
        Section(
            Div(
                # Header
                Div(
                    Span("Welcome back, ", cls="portal-greeting"),
                    Span(full_name, cls="portal-user-name"),
                    Div(
                        Button("Edit", cls="portal-edit-btn", onclick="openProfileModal()"),
                        Button("Sign Out", cls="portal-signout", onclick="handleSignOut()"),
                        cls="portal-header-actions"
                    ),
                    cls="portal-header"
                ),

                # Tabs
                Div(*tab_buttons, cls="portal-tabs"),

                # Tab contents
                staging_content,
                users_content,

                cls="portal-container"
            ),
            cls="portal-section"
        ),
        edit_modal,
        profile_modal,
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
