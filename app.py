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
    .google-btn {
        background-color: white;
        color: black;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        width: 100%;
        cursor: pointer;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Database Setup for Users & Activity Tracking
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

def google_login_user(email, name):
    conn = sqlite3.connect("dasai_saas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (name, email, mobile, password) VALUES (?, ?, ?, ?)",
                  (name, email, "N/A", hash_password("GOOGLE_AUTH_PASS")))
        conn.commit()
    conn.close()

def log_activity(email, action):
    conn = sqlite3.connect("dasai_saas.db")
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs (email, action) VALUES (?, ?)", (email, action))
    conn.commit()
    conn.close()

# 3. Session State for Login Tracking
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# 4. Authentication Flow (Login / Signup Screen with Email & Google Option)
if not st.session_state.logged_in:
    st.markdown('<p class="main-header">⚡ DasAi</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Enterprise AI Portal - Login via Email or Google</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Google Login Simulation Button
        if st.button("🌐 Continue with Google Account", use_container_width=True):
            # Simulated Google Quick-Auth for seamless onboarding
            g_email = "user_google@gmail.com"
            g_name = "Google User"
            google_login_user(g_email, g_name)
            st.session_state.logged_in = True
            st.session_state.user_email = g_email
            log_activity(g_email, "Logged In via Google")
            st.success("Google Login Successful!")
            st.rerun()

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

# 5. Main App Dashboard (Accessible Only After Login)
with st.sidebar:
    st.markdown(f"## 👤 Welcome, {st.session_state.user_email}")
    st.markdown("---")
    st.markdown("## ⚙️ DasAi SaaS Control")
    
    ai_provider = st.selectbox(
        "Select AI Provider",
        ["Auto-Select (Smart AI)", "Google Gemini", "OpenAI ChatGPT", "Anthropic Claude"],
    )

    api_key = None
    selected_model = ""

    if ai_provider == "Auto-Select (Smart AI)":
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter Gemini API Key:", type="password")

    elif ai_provider == "Google Gemini":
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter Gemini API Key:", type="password")
        selected_model = st.selectbox("Choose Model", ["gemini-3.1-pro-preview", "gemini-3.8-flash"])

    elif ai_provider == "OpenAI ChatGPT":
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter OpenAI API Key:", type="password")
        selected_model = st.selectbox("Choose Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])

    elif ai_provider == "Anthropic Claude":
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter Anthropic API Key:", type="password")
        selected_model = st.selectbox("Choose Model", ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"])

    st.markdown("---")
    
    # Admin Control Panel Section to view users
    if st.session_state.user_email in ["admin@gmail.com", "root@gmail.com"]: # Apni admin email yahan daal sakte hain
        if st.checkbox("👑 Open Admin Control Panel"):
            st.markdown("### 📊 Active Users & Logs")
            conn = sqlite3.connect("dasai_saas.db")
            c = conn.cursor()
            c.execute("SELECT name, email, mobile FROM users")
            all_users = c.fetchall()
            st.write(f"**Total Registered Users:** {len(all_users)}")
            for u in all_users:
                st.text(f"👤 {u[0]} | 📧 {u[1]} | 📱 {u[2]}")
            conn.close()

    if st.button("🗑️ Clear Workspace", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        log_activity(st.session_state.user_email, "Logged Out")
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

    st.markdown("---")
    st.caption("🚀 DasAi SaaS Platform v3.1")

# Header
st.markdown('<p class="main-header">⚡ DasAi</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Enterprise-grade AI powerhouse with Smart Auto-Routing and Multi-Model support.</p>', unsafe_allow_html=True)

system_instruction = """
You are DasAi, an elite Principal Software Engineer, Enterprise SaaS Architect, and Multi-Domain AI Expert. 
Your core competencies include advanced coding, SaaS scaling, mobile utilities, and business growth.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask DasAi..."):
    if not api_key:
        st.error(f"Kripya pehle sidebar (3-line menu) mein API key provide karein!")
    else:
        active_provider = ai_provider
        active_model = selected_model

        if ai_provider == "Auto-Select (Smart AI)":
            active_provider = "Google Gemini"
            coding_keywords = ["code", "python", "javascript", "error", "bug", "build", "script", "app", "database", "api"]
            is_complex = any(kw in prompt.lower() for kw in coding_keywords) or len(prompt) > 120
            if is_complex:
                active_model = "gemini-3.1-pro-preview"
            else:
                active_model = "gemini-3.8-flash"

        st.info(f"🟢 **Active Engine:** {active_provider} (`{active_model}`)")
        log_activity(st.session_state.user_email, f"Queried: {prompt[:30]}...")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"DasAi is processing via {active_model}..."):
                try:
                    ai_response = ""
                    if active_provider == "Google Gemini":
                        genai.configure(api_key=api_key)
                        gemini_model = genai.GenerativeModel(model_name=active_model, system_instruction=system_instruction)
                        gemini_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat_session = gemini_model.start_chat(history=gemini_history)
                        response = chat_session.send_message(prompt)
                        ai_response = response.text

                    elif active_provider == "OpenAI ChatGPT":
                        client = openai.OpenAI(api_key=api_key)
                        openai_messages = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        response = client.chat.completions.create(model=active_model, messages=openai_messages)
                        ai_response = response.choices[0].message.content

                    elif active_provider == "Anthropic Claude":
                        client = anthropic.Anthropic(api_key=api_key)
                        claude_messages = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]} for m in st.session_state.messages]
                        response = client.messages.create(model=active_model, max_tokens=4000, system=system_instruction, messages=claude_messages)
                        ai_response = response.content[0].text

                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"Execution Error: {e}")
                    
