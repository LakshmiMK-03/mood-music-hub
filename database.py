import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'hub.db')

def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            date_joined TEXT,
            last_login TEXT
        )
    ''')
    
    # History table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT,
            text_preview TEXT,
            emotion TEXT,
            stress_level TEXT,
            stress_score REAL,
            confidence REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def migrate_data():
    """Migrate legacy JSON data to SQLite."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Migrate Users
    users_file = os.path.join(os.path.dirname(__file__), 'users.json')
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
                for uname, udata in users.items():
                    cursor.execute('''
                        INSERT OR IGNORE INTO users (username, password, email, role, date_joined)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (uname, udata['password'], udata.get('email'), udata.get('role', 'user'), datetime.now().isoformat()))
            print(f"✅ Migrated {len(users)} users from users.json")
        except Exception as e:
            print(f"❌ Error migrating users: {e}")
            
    # 2. Migrate History
    history_file = os.path.join(os.path.dirname(__file__), 'history.json')
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
                for event in history:
                    cursor.execute('''
                        INSERT INTO history (timestamp, source, text_preview, emotion, stress_level, stress_score, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event.get('timestamp'),
                        event.get('source'),
                        event.get('text_Preview') or event.get('text_preview'), # Handle potential case diff
                        event.get('emotion'),
                        event.get('stress_level'),
                        event.get('stress_score', 0.0),
                        event.get('confidence', 0.0)
                    ))
            print(f"✅ Migrated {len(history)} events from history.json")
        except Exception as e:
            print(f"❌ Error migrating history: {e}")
            
    conn.commit()
    conn.close()

def get_user_by_email(email):
    """Retrieve a user by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, password, email, role='user'):
    """Insert a new user into the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, email, role, date_joined)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password, email.lower(), role, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_users():
    """Retrieve all users without passwords."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, role FROM users')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def delete_user(email):
    """Delete a user by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE email = ?', (email.lower(),))
    conn.commit()
    conn.close()

def update_user_role(email, new_role):
    """Update a user's role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
    if not cursor.fetchone():
        conn.close()
        return False
    cursor.execute('UPDATE users SET role = ? WHERE email = ?', (new_role, email.lower()))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    migrate_data()
