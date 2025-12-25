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

    # Create indexes for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')

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


# Initialize database on module load
init_db()
