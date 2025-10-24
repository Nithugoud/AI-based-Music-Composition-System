import sqlite3
import hashlib
import streamlit as st
from datetime import datetime, timedelta
import secrets
import os

class AuthManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create user sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create music history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS music_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                mood_input TEXT NOT NULL,
                mood_category TEXT,
                energy_level INTEGER,
                sentiment TEXT,
                music_params TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password, password_hash, salt):
        """Verify password against hash"""
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == password_hash
    
    def register_user(self, username, email, password):
        """Register a new user"""
        try:
            # Validate input
            if len(username) < 3:
                return False, "Username must be at least 3 characters long"
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters long"
            
            if "@" not in email:
                return False, "Please enter a valid email address"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Username or email already exists"
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, salt))
            
            conn.commit()
            conn.close()
            
            return True, "User registered successfully"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password):
        """Authenticate user and create session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, is_active 
                FROM users WHERE username = ?
            ''', (username,))
            
            user_data = cursor.fetchone()
            
            if not user_data:
                conn.close()
                return False, "Invalid username or password", None
            
            user_id, username, email, stored_hash, salt, is_active = user_data
            
            if not is_active:
                conn.close()
                return False, "Account is disabled", None
            
            # Verify password
            if not self.verify_password(password, stored_hash, salt):
                conn.close()
                return False, "Invalid username or password", None
            
            # Create session token
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            # Store session
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            user_info = {
                'id': user_id,
                'username': username,
                'email': email,
                'session_token': session_token
            }
            
            return True, "Login successful", user_info
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None
    
    def verify_session(self, session_token):
        """Verify if session token is valid"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, u.username, u.email, s.expires_at
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1 AND u.is_active = 1
            ''', (session_token,))
            
            session_data = cursor.fetchone()
            conn.close()
            
            if not session_data:
                return False, None
            
            user_id, username, email, expires_at = session_data
            expires_at = datetime.fromisoformat(expires_at)
            
            if datetime.now() > expires_at:
                self.logout_user(session_token)
                return False, None
            
            user_info = {
                'id': user_id,
                'username': username,
                'email': email
            }
            
            return True, user_info
            
        except Exception as e:
            return False, None
    
    def logout_user(self, session_token):
        """Logout user by deactivating session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions SET is_active = 0 
                WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            return False
    
    def save_music_generation(self, user_id, mood_input, mood_category, energy_level, sentiment, music_params, file_path):
        """Save music generation to user history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO music_history 
                (user_id, mood_input, mood_category, energy_level, sentiment, music_params, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, mood_input, mood_category, energy_level, sentiment, str(music_params), file_path))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            return False
    
    def get_user_music_history(self, user_id, limit=10):
        """Get user's music generation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mood_input, mood_category, energy_level, sentiment, 
                       music_params, file_path, created_at
                FROM music_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            history = cursor.fetchall()
            conn.close()
            
            return history
            
        except Exception as e:
            return []

# Streamlit integration functions
def init_session_state():
    """Initialize session state for authentication"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

def check_authentication():
    """Check if user is authenticated"""
    if st.session_state.session_token:
        is_valid, user_info = st.session_state.auth_manager.verify_session(st.session_state.session_token)
        if is_valid:
            st.session_state.authenticated = True
            st.session_state.user_info = user_info
            return True
        else:
            # Session expired or invalid
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.session_token = None
    
    return False

def show_login_form():
    """Display login form"""
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                success, message, user_info = st.session_state.auth_manager.login_user(username, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.session_state.session_token = user_info['session_token']
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in all fields")

def show_register_form():
    """Display registration form"""
    st.subheader("📝 Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = st.session_state.auth_manager.register_user(username, email, password)
                    
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials")
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all fields")

def show_user_profile():
    """Display user profile and options"""
    if st.session_state.user_info:
        st.sidebar.markdown(f"👤 **{st.session_state.user_info['username']}**")
        st.sidebar.markdown(f"📧 {st.session_state.user_info['email']}")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.auth_manager.logout_user(st.session_state.session_token)
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.session_token = None
            st.rerun()

def require_authentication(func):
    """Decorator to require authentication for functions"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            st.warning("Please login to access this feature")
            return None
        return func(*args, **kwargs)
    return wrapper