import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

def ensure_data_dir():
    """Ensure the data directory exists."""
    data_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    ensure_data_dir()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database with tables and default admin user."""
    ensure_data_dir()
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_address TEXT NOT NULL,
                video_link TEXT,
                description TEXT,
                remarks TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')

        conn.commit()

# ============== User Operations ==============

def get_user_by_username(username):
    """Get a user by username."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_user_by_id(user_id):
    """Get a user by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_all_users():
    """Get all users."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]

def create_user(username, hashed_password, is_admin=0):
    """Create a new user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                (username, hashed_password, is_admin)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def update_user_password(user_id, hashed_password):
    """Update a user's password."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (hashed_password, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_user(user_id):
    """Delete a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0

# ============== Entry Operations ==============

def get_all_entries():
    """Get all entries."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, u.username as creator_name
            FROM entries e
            LEFT JOIN users u ON e.created_by = u.id
            ORDER BY e.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_entry_by_id(entry_id):
    """Get an entry by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def create_entry(website_address, video_link, description, remarks, created_by):
    """Create a new entry."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (website_address, video_link, description, remarks, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (website_address, video_link, description, remarks, created_by))
        conn.commit()
        return cursor.lastrowid

def update_entry(entry_id, website_address, video_link, description, remarks):
    """Update an existing entry."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE entries
            SET website_address = ?, video_link = ?, description = ?, remarks = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (website_address, video_link, description, remarks, entry_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_entry(entry_id):
    """Delete an entry."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        conn.commit()
        return cursor.rowcount > 0
