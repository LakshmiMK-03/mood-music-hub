import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

URL: str = os.environ.get("SUPABASE_URL")
KEY: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(URL, KEY)

def get_db_connection():
    """Returns the supabase client instance."""
    return supabase

def init_db():
    """
    Supabase tables are usually created in the dashboard.
    For this project, we'll assume they are created via the SQL Editor 
    or the migration script.
    """
    print("✅ Supabase Client initialized.")

def get_user_by_email(email):
    """Retrieve a user by email from Supabase."""
    try:
        response = supabase.table('users').select('*').eq('email', email.lower()).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def create_user(username, password, email, role='user'):
    """Insert a new user into Supabase."""
    try:
        data = {
            "username": username,
            "password": password,
            "email": email.lower(),
            "role": role,
            "date_joined": datetime.now().isoformat()
        }
        supabase.table('users').insert(data).execute()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_all_users():
    """Retrieve all users without passwords from Supabase."""
    try:
        response = supabase.table('users').select('username, email, role').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return []

def delete_user(email):
    """Delete a user by email in Supabase."""
    try:
        supabase.table('users').delete().eq('email', email.lower()).execute()
    except Exception as e:
        print(f"Error deleting user: {e}")

def update_user_role(email, new_role):
    """Update a user's role in Supabase."""
    try:
        response = supabase.table('users').update({"role": new_role}).eq('email', email.lower()).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating role: {e}")
        return False

if __name__ == "__main__":
    init_db()
