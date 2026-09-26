import sqlite3
import hashlib
import google.generativeai as genai
import openai
import streamlit as st
import anthropic

# 1. Page Configuration & Enterprise Styling
st.set_page_config(
    page_title="DasAi - Professional SaaS AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @keyframes rgbGlow {
        0% { color: #EF4444; }     /* Red */
        33% { color: #3B82F6; }    /* Blue */
        66% { color: #10B981; }    /* Green */
        100% { color: #EF4444; }   /* Red */
    }
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        animation: rgbGlow 6s infinite;
        margin-top: -10px;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 30px;
    }
    .stChatMessage {
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #3B82F6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Database Setup
def init_db():
    conn = sqlite3.connect("dasai_saas.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            mobile TEXT,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, mobile, password):
    try:
        conn = sqlite3.connect("dasai_saas.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, mobile, password) VALUES (?, ?, ?, ?)",
                  (name, email, mobile, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def verify_user(email, password):
    conn = sqlite3.connect("dasai_saas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def log_activity(email, action):
    conn = sqlite3.connect("dasai_saas.db")
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs (email, action) VALUES (?, ?)", (email, action))
    conn.commit()
    conn.close()

# 3. Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# 4. Authentication Flow
if not st.session_state.logged_in:
    st.markdown('<p class="main-header">⚡ DasAi</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Enterprise AI Portal - Login via Email or Google</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Proper Google OAuth Integration using Streamlit secrets / input credentials
        from streamlit_google_auth import GoogleAuth
        
        # Streamlit secrets mein client_id aur client_secret set karna hoga
        # ya aap yahan direct credentials daal sakte hain
        client_id = st.secrets.get("GOOGLE_CLIENT_ID", "Aapka_Google_Client_ID")
        client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "Aapka_Google_Client_Secret")
        redirect_uri = st.secrets.get("GOOGLE_REDIRECT_URI", "http://localhost:8501")

        if client_id != "Aapka_Google_Client_ID":
            google_auth = GoogleAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, server_metadata_url="https://accounts.google.com/.well-known/openid-configuration")
            logged_in_google = google_auth.login()
            
            if logged_in_google:
                user_info = google_auth.get_user_info()
                g_email = user_info.get("email")
                g_name = user_info.get("name", "Google User")
                
                st.session_state.logged_in = True
                st.session_state.user_email = g_email
                log_activity(g_email, "Logged In via Google OAuth")
                st.rerun()
        else:
            # Agar credentials configured nahi hain toh warning dikhayein
            st.warning("Google OAuth ke liye Streamlit secrets mein `GOOGLE_CLIENT_ID` aur `GOOGLE_CLIENT_SECRET` configure karein.")

        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        auth_mode = st.radio("Choose Action", ["Login", "Register"], horizontal=True)
        
        if auth_mode == "Login":
            st.subheader("🔐 Email Login")
            login_email = st.text_input("Email Address")
            login_pass = st.text_input("Password", type="password")
            if st.button("Login to DasAi", use_container_width=True):
                user = verify_user(login_email, login_pass)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    log_activity(login_email, "Logged In via Email")
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Email or Password!")
                    
        else:
            st.subheader("📝 Create New Account")
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address")
            reg_mobile = st.text_input("Mobile Number")
            reg_pass = st.text_input("Choose Password", type="password")
            
            if st.button("Register Account", use_container_width=True):
                if reg_name and reg_email and reg_mobile and reg_pass:
                    success = register_user(reg_name, reg_email, reg_mobile, reg_pass)
                    if success:
                        st.success("Account created successfully! Please switch to Login.")
                    else:
                        st.error("Email already exists!")
                else:
                    st.warning("Please fill all the details!")
    st.stop()

# 5. Main App Dashboard (Baaki ka code same rahega)
