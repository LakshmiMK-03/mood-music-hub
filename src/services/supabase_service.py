import requests
from datetime import datetime
from src.core.config import Config
from src.core.exceptions import DatabaseError
from src.utils.logger import setup_logging

logger = setup_logging("supabase_service")

class SupabaseService:
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        if not self.url or not self.key:
            logger.error("Supabase credentials missing in Config")

    def _get_headers(self, prefer="return=representation"):
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": prefer
        }

    def _handle_response(self, response, error_msg="Database operation failed"):
        if response.status_code not in (200, 201, 204):
            logger.error(f"{error_msg}: {response.text}")
            raise DatabaseError(f"{error_msg}: {response.reason}")
        
        # DELETE/PATCH might return empty if no results
        try:
            return response.json()
        except Exception:
            return None

    # --- User Operations ---

    def get_user_by_email(self, email):
        url = f"{self.url}/rest/v1/users?email=eq.{email.lower()}"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            data = self._handle_response(resp, f"Error fetching user by email {email}")
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Supabase network error (get_user_by_email): {e}")
            return None

    def get_user_by_username(self, username):
        url = f"{self.url}/rest/v1/users?username=eq.{username}"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            data = self._handle_response(resp, f"Error fetching user by username {username}")
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Supabase network error (get_user_by_username): {e}")
            return None

    def create_user(self, username, password_hash, email, role='user'):
        data = {
            "username": username,
            "password": password_hash,
            "email": email.lower(),
            "role": role,
            "date_joined": datetime.now().isoformat()
        }
        try:
            url = f"{self.url}/rest/v1/users"
            resp = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            result = self._handle_response(resp, f"Error creating user {email}")
            return result[0] if result else True
        except Exception as e:
            logger.error(f"Supabase network error (create_user): {e}")
            raise DatabaseError(f"Connection to database failed: {e}")

    def get_all_users(self):
        url = f"{self.url}/rest/v1/users?select=id,username,email,role,date_joined"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            return self._handle_response(resp, "Error fetching all users") or []
        except Exception as e:
            logger.error(f"Supabase network error (get_all_users): {e}")
            return []

    def delete_user(self, email):
        url = f"{self.url}/rest/v1/users?email=eq.{email.lower()}"
        try:
            resp = requests.delete(url, headers=self._get_headers(), timeout=10)
            self._handle_response(resp, f"Error deleting user {email}")
        except Exception as e:
            logger.error(f"Supabase delete error for {email}: {e}")

    def update_user_role(self, email, new_role):
        url = f"{self.url}/rest/v1/users?email=eq.{email.lower()}"
        try:
            resp = requests.patch(url, headers=self._get_headers(), json={"role": new_role}, timeout=10)
            data = self._handle_response(resp, f"Error updating role for {email}")
            return len(data) > 0 if data else False
        except Exception as e:
            logger.error(f"Supabase update error for {email}: {e}")
            return False

    # --- History / Analytics Operations ---

    def log_analysis(self, user_id, source, text, emotion, stress_level, confidence, stress_score):
        text_preview = (text[:50] + '...') if text and len(text) > 50 else text
        data = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "text_preview": text_preview,
            "emotion": emotion,
            "stress_level": stress_level,
            "stress_score": float(stress_score),
            "confidence": float(confidence)
        }
        url = f"{self.url}/rest/v1/history"
        try:
            resp = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            self._handle_response(resp, f"Error logging analysis for user {user_id}")
        except Exception as e:
            logger.error(f"Database logging failed for user {user_id}: {e}")

    def log_feedback(self, name, email, message):
        data = {
            "name": name,
            "email": email.lower(),
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        url = f"{self.url}/rest/v1/feedback"
        try:
            resp = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            self._handle_response(resp, f"Error saving feedback from {email}")
            return True
        except Exception as e:
            logger.error(f"Feedback saving failed: {e}")
            return False

    def get_stats(self):
        try:
            url_history = f"{self.url}/rest/v1/history"
            resp = requests.get(url_history, headers=self._get_headers(), timeout=10)
            history_data = self._handle_response(resp, "Error fetching history for stats") or []
            
            total = len(history_data)
            emotions = ['Happy', 'Sad', 'Angry', 'Neutral', 'Fearful']
            emotion_dist = {e: 0 for e in emotions}
            stresses = ['Low', 'Medium', 'High']
            stress_dist = {s: 0 for s in stresses}
            
            for item in history_data:
                em = item.get('emotion')
                sl = item.get('stress_level')
                if em in emotion_dist: emotion_dist[em] += 1
                if sl in stress_dist: stress_dist[sl] += 1
                    
            # Recent Activity
            url_recent = f"{url_history}?order=id.desc&limit=5"
            resp_recent = requests.get(url_recent, headers=self._get_headers(), timeout=10)
            recent = self._handle_response(resp_recent, "Error fetching recent activity") or []
            
            # User Counts
            url_users = f"{self.url}/rest/v1/users?select=role"
            resp_users = requests.get(url_users, headers=self._get_headers(), timeout=10)
            users_data = self._handle_response(resp_users, "Error fetching user counts") or []
            
            total_users = len(users_data)
            admin_users = sum(1 for u in users_data if u.get('role') == 'admin')

            return {
                'total_analyses': total,
                'emotion_dist': emotion_dist,
                'stress_dist': stress_dist,
                'recent_activity': recent,
                'user_counts': {
                    'total': total_users,
                    'admins': admin_users,
                    'users': total_users - admin_users
                }
            }
        except Exception as e:
            logger.error(f"Supabase stats error: {e}")
            return {
                'total_analyses': 0, 'emotion_dist': {}, 'stress_dist': {}, 
                'recent_activity': [], 'user_counts': {'total':0, 'admins':0, 'users':0}
            }

    def get_latest_emotion(self, user_id):
        url = f"{self.url}/rest/v1/history?user_id=eq.{user_id}&order=timestamp.desc&limit=1"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            data = self._handle_response(resp, f"Error fetching latest emotion for user {user_id}")
            return data[0]['emotion'] if data else None
        except Exception as e:
            logger.error(f"Supabase emotion fetch error for user {user_id}: {e}")
            return None
