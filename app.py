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

# 3. Session State for Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# 4. Authentication Flow
if not st.session_state.logged_in:
    st.markdown('<p class="main-header">⚡ DasAi</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Enterprise AI Portal - Login</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio("Choose Action", ["Login", "Register"], horizontal=True)
        
        if auth_mode == "Login":
            st.subheader("🔐 Account Login")
            with st.form("login_form"):
                login_email = st.text_input("Email Address")
                login_pass = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login to DasAi", use_container_width=True)
                
                if submitted:
                    if login_email and login_pass:
                        user = verify_user(login_email, login_pass)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_email = login_email
                            st.session_state.user_name = user[1]
                            log_activity(login_email, "Logged In via Email")
                            st.success("Login Successful!")
                            st.rerun()
                        else:
                            st.error("Invalid Email or Password!")
                    else:
                        st.warning("Please fill in both Email and Password fields.")
                    
        else:
            st.subheader("📝 Create New Account")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name")
                reg_email = st.text_input("Email Address")
                reg_mobile = st.text_input("Mobile Number")
                reg_pass = st.text_input("Choose Password", type="password")
                reg_submitted = st.form_submit_button("Register Account", use_container_width=True)
                
                if reg_submitted:
                    if reg_name and reg_email and reg_mobile and reg_pass:
                        success = register_user(reg_name, reg_email, reg_mobile, reg_pass)
                        if success:
                            st.success("Account created successfully! Please switch to the Login tab.")
                        else:
                            st.error("Email already exists!")
                    else:
                        st.warning("Please fill in all required details.")
    st.stop()

# 5. Main App Dashboard (Accessible Only After Login)
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.user_name or 'User'}")
    st.caption(f"📧 {st.session_state.user_email}")
    st.success("✨ Unlimited Access Active")
        
    st.markdown("---")
    st.markdown("## ⚙️ Personal AI Settings")
    
    ai_persona = st.selectbox(
        "Choose AI Mode / Persona",
        [
            "Master Coding Expert (Programming Focus)",
            "Professional Prompt Generator",
            "General Enterprise Assistant",
            "Creative Content Writer"
        ]
    )
    
    if ai_persona == "Master Coding Expert (Programming Focus)":
        custom_system_instruction = "You are DasAi, an elite Master Coding Expert. Provide accurate, clean, optimized code snippets with detailed explanations in every response."
    elif ai_persona == "Professional Prompt Generator":
        custom_system_instruction = "You are DasAi, an expert AI Prompt Engineer. Your primary task is to generate high-quality, professional, copy-ready prompts for users based on their requests."
    elif ai_persona == "Creative Content Writer":
        custom_system_instruction = "You are DasAi, a creative writer specializing in engaging blogs, copywriting, and marketing text."
    else:
        custom_system_instruction = "You are DasAi, a helpful enterprise AI assistant built to help with all tasks."

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None
        
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key:", type="password")

    st.markdown("---")
    
    if st.button("🗑️ Clear Workspace", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        log_activity(st.session_state.user_email, "Logged Out")
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.rerun()

    st.markdown("---")
    st.caption("🚀 DasAi Platform v3.4")

# Header
st.markdown('<p class="main-header">⚡ DasAi</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Current Mode: <b>{ai_persona}</b></p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask DasAi..."):
    if not api_key:
        st.error("Please provide your API key in the sidebar to proceed!")
    else:
        log_activity(st.session_state.user_email, f"Queried: {prompt[:30]}...")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("DasAi is thinking..."):
                try:
                    genai.configure(api_key=api_key)
                    gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=custom_system_instruction)
                    
                    gemini_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat_session = gemini_model.start_chat(history=gemini_history)
                    response = chat_session.send_message(prompt)
                    ai_response = response.text

                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"Execution Error: {e}")
