"""
User Database Module for Astra Staging
SQLite database for user management with authentication support
"""

import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def get_db_connection():
    """Get a connection to the SQLite database"""
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT,
            user_role TEXT NOT NULL DEFAULT 'customer',
            google_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # Sessions table for managing login sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Stagings table - stores both quotes (unpaid) and confirmed stagings (paid)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stagings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'quote',
            property_address TEXT,
            property_type TEXT,
            property_size TEXT,
            selected_areas TEXT,
            selected_items TEXT,
            total_fee TEXT,
            staging_date TEXT,
            addons TEXT,
            property_status TEXT,
            user_type TEXT,
            pets_status TEXT,
            referral_source TEXT,
            referral_other TEXT,
            guest_first_name TEXT,
            guest_last_name TEXT,
            guest_email TEXT,
            guest_phone TEXT,
            special_requests TEXT,
            stripe_payment_id TEXT,
            stripe_customer_id TEXT,
            area_photos TEXT,
            area_selected_items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Migration: Add area_photos column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE stagings ADD COLUMN area_photos TEXT')
    except:
        pass  # Column already exists

    # Migration: Add area_selected_items column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE stagings ADD COLUMN area_selected_items TEXT')
    except:
        pass  # Column already exists

    # Design models table - stores 3D model placement state for staging designs
    # Supports multiple instances of same model via instance_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS design_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staging_id INTEGER,
            background_image TEXT NOT NULL,
            model_url TEXT NOT NULL,
            instance_id INTEGER DEFAULT 0,
            position_x REAL DEFAULT 0,
            position_y REAL DEFAULT 0,
            position_z REAL DEFAULT 0,
            scale REAL DEFAULT 1,
            rotation_y REAL DEFAULT 0,
            tilt REAL DEFAULT 0.1745,
            brightness REAL DEFAULT 2.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staging_id) REFERENCES stagings (id),
            UNIQUE(background_image, model_url, instance_id)
        )
    ''')

    # Migration: Add instance_id column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE design_models ADD COLUMN instance_id INTEGER DEFAULT 0')
    except:
        pass  # Column already exists

    # Migration: Add item_name and image_url columns if they don't exist
    try:
        cursor.execute('ALTER TABLE design_models ADD COLUMN item_name TEXT')
    except:
        pass  # Column already exists

    try:
        cursor.execute('ALTER TABLE design_models ADD COLUMN image_url TEXT')
    except:
        pass  # Column already exists

    # Drop old unique constraint and add new one with instance_id
    # SQLite doesn't support DROP CONSTRAINT, so we need to recreate the table
    # For now, just ensure the new table structure is used for new installations

    # Create indexes for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stagings_user_id ON stagings(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stagings_status ON stagings(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_design_models_background ON design_models(background_image)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_design_models_staging ON design_models(staging_id)')

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash"""
    if not stored_hash or ':' not in stored_hash:
        return False
    salt, hash_value = stored_hash.split(':', 1)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash == hash_value


def create_user(first_name: str, last_name: str, email: str,
                password: str = None, phone: str = None,
                user_role: str = 'customer', google_id: str = None) -> dict:
    """
    Create a new user
    Returns: dict with 'success' and 'user' or 'error'
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
        if cursor.fetchone():
            return {'success': False, 'error': 'Email already registered'}

        # Check if google_id already exists (if provided)
        if google_id:
            cursor.execute('SELECT id FROM users WHERE google_id = ?', (google_id,))
            if cursor.fetchone():
                return {'success': False, 'error': 'Google account already linked'}

        # Hash password if provided
        password_hash = hash_password(password) if password else None

        cursor.execute('''
            INSERT INTO users (first_name, last_name, email, phone, password_hash, user_role, google_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email.lower(), phone, password_hash, user_role, google_id))

        user_id = cursor.lastrowid
        conn.commit()

        return {
            'success': True,
            'user': {
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email.lower(),
                'phone': phone,
                'user_role': user_role
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> dict:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_user_by_google_id(google_id: str) -> dict:
    """Get user by Google ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticate user with email and password
    Returns: dict with 'success' and 'user' or 'error'
    """
    user = get_user_by_email(email)

    if not user:
        return {'success': False, 'error': 'Invalid email or password'}

    if not user.get('password_hash'):
        return {'success': False, 'error': 'Please sign in with Google'}

    if not verify_password(password, user['password_hash']):
        return {'success': False, 'error': 'Invalid email or password'}

    if not user.get('is_active', True):
        return {'success': False, 'error': 'Account is deactivated'}

    # Update last login
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                   (datetime.now(), user['id']))
    conn.commit()
    conn.close()

    return {
        'success': True,
        'user': {
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'phone': user['phone'],
            'user_role': user['user_role']
        }
    }


def create_session(user_id: int, days_valid: int = 7) -> str:
    """Create a new session for a user and return the session token"""
    conn = get_db_connection()
    cursor = conn.cursor()

    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=days_valid)

    cursor.execute('''
        INSERT INTO sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, session_token, expires_at))

    conn.commit()
    conn.close()

    return session_token


def get_user_by_session(session_token: str) -> dict:
    """Get user by session token (validates expiration)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.* FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > ?
    ''', (session_token, datetime.now()))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def delete_session(session_token: str) -> bool:
    """Delete a session (logout)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


def cleanup_expired_sessions():
    """Remove expired sessions from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now(),))

    conn.commit()
    conn.close()


def get_all_users() -> list:
    """Get all users for admin management"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, first_name, last_name, email, phone, user_role,
               created_at, last_login, is_active
        FROM users
        ORDER BY created_at DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_user(user_id: int, **kwargs) -> dict:
    """Update user fields"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Handle password separately
        password = kwargs.pop('password', None)
        if password:
            password_hash = hash_password(password)
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                           (password_hash, user_id))

        # Handle email separately (check for uniqueness)
        email = kwargs.pop('email', None)
        if email:
            cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?',
                           (email.lower(), user_id))
            if cursor.fetchone():
                return {'success': False, 'error': 'Email already in use'}
            cursor.execute('UPDATE users SET email = ? WHERE id = ?',
                           (email.lower(), user_id))

        # Handle other allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'user_role', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if updates:
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', values)

        # Update timestamp
        cursor.execute('UPDATE users SET updated_at = ? WHERE id = ?',
                       (datetime.now(), user_id))

        conn.commit()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def link_google_account(user_id: int, google_id: str) -> dict:
    """Link a Google account to an existing user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE users SET google_id = ?, updated_at = ? WHERE id = ?',
                       (google_id, datetime.now(), user_id))
        conn.commit()
        return {'success': True}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'Google account already linked to another user'}
    finally:
        conn.close()


def get_or_create_google_user(google_id: str, email: str, first_name: str, last_name: str) -> dict:
    """Get existing Google user or create new one"""
    # Check if user exists by Google ID
    user = get_user_by_google_id(google_id)
    if user:
        return {'success': True, 'user': user, 'is_new': False}

    # Check if email exists (user registered with email, now signing in with Google)
    user = get_user_by_email(email)
    if user:
        # Link Google account to existing user
        link_result = link_google_account(user['id'], google_id)
        if link_result['success']:
            user['google_id'] = google_id
            return {'success': True, 'user': user, 'is_new': False}
        return link_result

    # Create new user
    result = create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        google_id=google_id,
        user_role='customer'
    )

    if result['success']:
        result['is_new'] = True

    return result


# ============== Staging Functions ==============

def save_staging(user_id: int, staging_data: dict) -> dict:
    """
    Save or update a staging for a user.
    If staging_id is provided in staging_data, updates existing; otherwise creates new.
    Returns: dict with 'success' and 'staging_id' or 'error'
    """
    print(f"[save_staging] user_id={user_id}, staging_data={staging_data}")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        staging_id = staging_data.get('id') or staging_data.get('staging_id')
        print(f"[save_staging] staging_id={staging_id}")

        if staging_id:
            # Update existing staging
            cursor.execute('''
                UPDATE stagings SET
                    status = ?,
                    property_address = ?,
                    property_type = ?,
                    property_size = ?,
                    selected_areas = ?,
                    selected_items = ?,
                    total_fee = ?,
                    staging_date = ?,
                    addons = ?,
                    property_status = ?,
                    user_type = ?,
                    pets_status = ?,
                    referral_source = ?,
                    referral_other = ?,
                    guest_first_name = ?,
                    guest_last_name = ?,
                    guest_email = ?,
                    guest_phone = ?,
                    special_requests = ?,
                    stripe_payment_id = ?,
                    stripe_customer_id = ?,
                    area_photos = ?,
                    area_selected_items = ?,
                    updated_at = ?
                WHERE id = ? AND user_id = ?
            ''', (
                staging_data.get('status', 'quote'),
                staging_data.get('property_address'),
                staging_data.get('property_type'),
                staging_data.get('property_size'),
                staging_data.get('selected_areas'),
                staging_data.get('selected_items'),
                staging_data.get('total_fee'),
                staging_data.get('staging_date'),
                staging_data.get('addons'),
                staging_data.get('property_status'),
                staging_data.get('user_type'),
                staging_data.get('pets_status'),
                staging_data.get('referral_source'),
                staging_data.get('referral_other'),
                staging_data.get('guest_first_name'),
                staging_data.get('guest_last_name'),
                staging_data.get('guest_email'),
                staging_data.get('guest_phone'),
                staging_data.get('special_requests'),
                staging_data.get('stripe_payment_id'),
                staging_data.get('stripe_customer_id'),
                staging_data.get('area_photos'),
                staging_data.get('area_selected_items'),
                datetime.now(),
                staging_id,
                user_id
            ))
        else:
            # Create new staging
            cursor.execute('''
                INSERT INTO stagings (
                    user_id, status, property_address, property_type, property_size,
                    selected_areas, selected_items, total_fee, staging_date, addons,
                    property_status, user_type, pets_status, referral_source, referral_other,
                    guest_first_name, guest_last_name, guest_email, guest_phone,
                    special_requests, stripe_payment_id, stripe_customer_id, area_photos,
                    area_selected_items
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                staging_data.get('status', 'quote'),
                staging_data.get('property_address'),
                staging_data.get('property_type'),
                staging_data.get('property_size'),
                staging_data.get('selected_areas'),
                staging_data.get('selected_items'),
                staging_data.get('total_fee'),
                staging_data.get('staging_date'),
                staging_data.get('addons'),
                staging_data.get('property_status'),
                staging_data.get('user_type'),
                staging_data.get('pets_status'),
                staging_data.get('referral_source'),
                staging_data.get('referral_other'),
                staging_data.get('guest_first_name'),
                staging_data.get('guest_last_name'),
                staging_data.get('guest_email'),
                staging_data.get('guest_phone'),
                staging_data.get('special_requests'),
                staging_data.get('stripe_payment_id'),
                staging_data.get('stripe_customer_id'),
                staging_data.get('area_photos'),
                staging_data.get('area_selected_items')
            ))
            staging_id = cursor.lastrowid
            print(f"[save_staging] Created new staging with id={staging_id}")

        conn.commit()
        print(f"[save_staging] Committed successfully, returning staging_id={staging_id}")
        return {'success': True, 'staging_id': staging_id}
    except Exception as e:
        print(f"[save_staging] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def get_user_stagings(user_id: int, status: str = None) -> list:
    """
    Get all stagings for a user, optionally filtered by status.
    Status can be 'quote' (unpaid) or 'confirmed' (paid).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute('''
            SELECT * FROM stagings
            WHERE user_id = ? AND status = ?
            ORDER BY updated_at DESC
        ''', (user_id, status))
    else:
        cursor.execute('''
            SELECT * FROM stagings
            WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_staging_by_id(staging_id: int, user_id: int = None) -> dict:
    """Get a staging by ID, optionally verifying user ownership"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute('SELECT * FROM stagings WHERE id = ? AND user_id = ?',
                       (staging_id, user_id))
    else:
        cursor.execute('SELECT * FROM stagings WHERE id = ?', (staging_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def delete_staging(staging_id: int, user_id: int) -> dict:
    """Delete a staging (only if owned by user)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM stagings WHERE id = ? AND user_id = ?',
                       (staging_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        return {'success': deleted, 'error': None if deleted else 'Staging not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def update_staging_status(staging_id: int, status: str,
                          stripe_payment_id: str = None,
                          stripe_customer_id: str = None) -> dict:
    """Update staging status (e.g., from 'quote' to 'confirmed' after payment)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if stripe_payment_id or stripe_customer_id:
            cursor.execute('''
                UPDATE stagings SET
                    status = ?,
                    stripe_payment_id = COALESCE(?, stripe_payment_id),
                    stripe_customer_id = COALESCE(?, stripe_customer_id),
                    updated_at = ?
                WHERE id = ?
            ''', (status, stripe_payment_id, stripe_customer_id, datetime.now(), staging_id))
        else:
            cursor.execute('''
                UPDATE stagings SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status, datetime.now(), staging_id))

        conn.commit()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


# ============== Design Model State Functions ==============

def save_model_state(background_image: str, model_url: str, state: dict, staging_id: int = None, instance_id: int = 0) -> dict:
    """
    Save or update a 3D model's placement state.
    Uses INSERT OR REPLACE to upsert based on background_image + model_url + instance_id unique constraint.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO design_models (
                staging_id, background_image, model_url, instance_id,
                position_x, position_y, position_z,
                scale, rotation_y, tilt, brightness,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(background_image, model_url, instance_id) DO UPDATE SET
                staging_id = excluded.staging_id,
                position_x = excluded.position_x,
                position_y = excluded.position_y,
                position_z = excluded.position_z,
                scale = excluded.scale,
                rotation_y = excluded.rotation_y,
                tilt = excluded.tilt,
                brightness = excluded.brightness,
                updated_at = excluded.updated_at
        ''', (
            staging_id,
            background_image,
            model_url,
            instance_id,
            state.get('position_x', 0),
            state.get('position_y', 0),
            state.get('position_z', 0),
            state.get('scale', 1),
            state.get('rotation_y', 0),
            state.get('tilt', 0.1745),
            state.get('brightness', 2.5),
            datetime.now()
        ))

        conn.commit()
        return {'success': True, 'id': cursor.lastrowid}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def save_all_model_states(background_image: str, model_url: str, models: list, staging_id: int = None) -> dict:
    """
    Save all model instances for a background image.
    Deletes existing models first, then saves all current models.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Delete existing models for this background/model_url combination
        cursor.execute('''
            DELETE FROM design_models
            WHERE background_image = ? AND model_url = ?
        ''', (background_image, model_url))

        # Insert all models with their instance_id
        for idx, model_state in enumerate(models):
            cursor.execute('''
                INSERT INTO design_models (
                    staging_id, background_image, model_url, instance_id,
                    position_x, position_y, position_z,
                    scale, rotation_y, tilt, brightness,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                staging_id,
                background_image,
                model_url,
                idx,
                model_state.get('position_x', 0),
                model_state.get('position_y', 0),
                model_state.get('position_z', 0),
                model_state.get('scale', 1),
                model_state.get('rotation_y', 0),
                model_state.get('tilt', 0.1745),
                model_state.get('brightness', 2.5),
                datetime.now()
            ))

        conn.commit()
        return {'success': True, 'count': len(models)}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def get_model_state(background_image: str, model_url: str) -> dict:
    """Get the saved state for a specific model on a background image."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT position_x, position_y, position_z, scale, rotation_y, tilt, brightness
        FROM design_models
        WHERE background_image = ? AND model_url = ?
    ''', (background_image, model_url))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_all_models_for_background(background_image: str) -> list:
    """Get all saved models for a specific background image, ordered by instance_id."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT model_url, instance_id, position_x, position_y, position_z, scale, rotation_y, tilt, brightness
        FROM design_models
        WHERE background_image = ?
        ORDER BY model_url, instance_id
    ''', (background_image,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def delete_model_state(background_image: str, model_url: str) -> dict:
    """Delete a saved model state."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            DELETE FROM design_models
            WHERE background_image = ? AND model_url = ?
        ''', (background_image, model_url))

        deleted = cursor.rowcount > 0
        conn.commit()
        return {'success': deleted, 'error': None if deleted else 'Model state not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def delete_all_models_for_background(background_image: str) -> dict:
    """Delete all saved model states for a background image."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM design_models WHERE background_image = ?', (background_image,))
        deleted_count = cursor.rowcount
        conn.commit()
        return {'success': True, 'deleted_count': deleted_count}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


# Initialize database on module load
init_db()
