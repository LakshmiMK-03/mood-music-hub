import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

URL: str = os.environ.get("SUPABASE_URL", "")
KEY: str = os.environ.get("SUPABASE_KEY", "")

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_rest_headers():
    return {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def init_db():
    print("✅ Supabase REST Client initialized.")

def get_user_by_email(email):
    """Retrieve a user by email from Supabase using REST API."""
    try:
        url = f"{URL}/rest/v1/users?email=eq.{email.lower()}"
        response = requests.get(url, headers=get_rest_headers())
        if response.status_code == 200:
            data = response.json()
            return data[0] if len(data) > 0 else None
        else:
            print(f"Fetch Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def create_user(username, password, email, role='user'):
    """Insert a new user into Supabase using REST API."""
    try:
        data = {
            "username": username,
            "password": password,
            "email": email.lower(),
            "role": role,
            "date_joined": datetime.now().isoformat()
        }
        url = f"{URL}/rest/v1/users"
        response = requests.post(url, headers=get_rest_headers(), json=data)
        if response.status_code in (201, 200):
            return response.json()[0] if response.json() else True
        else:
            print(f"Create Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_all_users():
    """Retrieve all users without passwords from Supabase REST API."""
    try:
        url = f"{URL}/rest/v1/users?select=username,email,role"
        response = requests.get(url, headers=get_rest_headers())
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return []

def delete_user(email):
    """Delete a user by email in Supabase REST API."""
    try:
        url = f"{URL}/rest/v1/users?email=eq.{email.lower()}"
        requests.delete(url, headers=get_rest_headers())
    except Exception as e:
        print(f"Error deleting user: {e}")

def update_user_role(email, new_role):
    """Update a user's role in Supabase REST API."""
    try:
        url = f"{URL}/rest/v1/users?email=eq.{email.lower()}"
        response = requests.patch(url, headers=get_rest_headers(), json={"role": new_role})
        if response.status_code in (200, 204):
            return len(response.json()) > 0
        return False
    except Exception as e:
        print(f"Error updating role: {e}")
        return False

if __name__ == "__main__":
    init_db()
