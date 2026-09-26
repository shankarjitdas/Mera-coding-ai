import sqlite3
import hashlib
import google.generativeai as genai
import openai
import streamlit as st
import anthropic

# 1. Page Configuration & Enterprise Styling
st.set_page_config(
    page_title="DasAi - Professional AI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Hide Streamlit Default Menu, Footer & Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global Styling for Professional Look */
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #4285F4, #9B72CF, #DB4437);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -20px;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 1rem;
        color: #9aa0a6;
        text-align: center;
        margin-bottom: 25px;
    }
    .stChatMessage {
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        background-color: #1e1f20;
        border: 1px solid #333538;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Database Setup, Auto-Admin & Settings Persistence
def init_db():
    conn = sqlite3.connect("dasai_professional.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            mobile TEXT,
            password TEXT,
            is_admin INTEGER DEFAULT 0
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS platform_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect("dasai_professional.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin = 1 WHERE email = 'shankarjitdas2@gmail.com'")
    conn.commit()
    conn.close()

init_db()

def get_setting(key, default=""):
    try:
        conn = sqlite3.connect("dasai_professional.db")
        c = conn.cursor()
        c.execute("SELECT value FROM platform_settings WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except:
        return default

def save_setting(key, value):
    try:
        conn = sqlite3.connect("dasai_professional.db")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO platform_settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, mobile, password):
    try:
        conn = sqlite3.connect("dasai_professional.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        is_admin_val = 1 if (count == 0 or email == 'shankarjitdas2@gmail.com') else 0

        c.execute("INSERT INTO users (name, email, mobile, password, is_admin) VALUES (?, ?, ?, ?, ?)",
                  (name, email, mobile, hash_password(password), is_admin_val))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def verify_user(email, password):
    conn = sqlite3.connect("dasai_professional.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def log_activity(email, action):
    conn = sqlite3.connect("dasai_professional.db")
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs (email, action) VALUES (?, ?)", (email, action))
    conn.commit()
    conn.close()

# 3. Session State Management with Query Params
if "logged_in" not in st.session_state:
    query_params = st.query_params
    if "user" in query_params and "name" in query_params:
        st.session_state.logged_in = True
        st.session_state.user_email = query_params["user"]
        st.session_state.user_name = query_params["name"]
        st.session_state.is_admin = int(query_params.get("is_admin", 0))
    else:
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.session_state.is_admin = 0

if "current_engine" not in st.session_state:
    st.session_state.current_engine = "Google Gemini Flash / Pro"
if "current_persona" not in st.session_state:
    st.session_state.current_persona = "Master Coding Expert (Full-Stack & Debugging)"

# 4. Authentication Flow
if not st.session_state.logged_in:
    st.markdown('<p class="main-header">⚡ DasAi Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Sign in to access your Enterprise AI Workspace</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio("Portal Mode", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "Login":
            st.subheader("🔐 Account Login")
            with st.form("login_form"):
                login_email = st.text_input("Email Address")
                login_pass = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Access Workspace", use_container_width=True)
                
                if submitted:
                    if login_email and login_pass:
                        conn = sqlite3.connect("dasai_professional.db")
                        c = conn.cursor()
                        c.execute("UPDATE users SET is_admin = 1 WHERE email = 'shankarjitdas2@gmail.com'")
                        conn.commit()
                        conn.close()

                        user = verify_user(login_email, login_pass)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_email = login_email
                            st.session_state.user_name = user[1]
                            st.session_state.is_admin = user[5]
                            
                            st.query_params["user"] = login_email
                            st.query_params["name"] = user[1]
                            st.query_params["is_admin"] = str(user[5])
                            
                            log_activity(login_email, "Logged In Successfully")
                            st.success("Authentication Successful!")
                            st.rerun()
                        else:
                            st.error("Invalid Email or Password!")
                    else:
                        st.warning("Please fill in all fields.")
                    
        else:
            st.subheader("📝 Register New Account")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name")
                reg_email = st.text_input("Email Address")
                reg_mobile = st.text_input("Mobile Number")
                reg_pass = st.text_input("Create Password", type="password")
                reg_submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if reg_submitted:
                    if reg_name and reg_email and reg_mobile and reg_pass:
                        success = register_user(reg_name, reg_email, reg_mobile, reg_pass)
                        if success:
                            st.success("Account created successfully! Switch to Login tab.")
                        else:
                            st.error("Email already registered!")
                    else:
                        st.warning("Please fill out all details.")
    st.stop()

# 5. Sidebar Controls & Customizer
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    st.caption(f"📧 {st.session_state.user_email}")
    
    if st.session_state.is_admin == 1 or st.session_state.user_email == 'shankarjitdas2@gmail.com':
        st.error("👑 ADMIN MODE ACTIVE")
        st.session_state.is_admin = 1
    else:
        st.success("✨ Pro Intelligence Active")
        
    st.markdown("---")
    st.markdown("### ⚙️ Personal AI Customizer")
    
    ai_persona = st.selectbox(
        "Choose AI Mode",
        [
            "Master Coding Expert (Full-Stack & Debugging)",
            "Professional Prompt Engineer (Copy-Ready Prompts)",
            "Enterprise Business Consultant",
            "Creative Content & Copywriter"
        ],
        index=["Master Coding Expert (Full-Stack & Debugging)", "Professional Prompt Engineer (Copy-Ready Prompts)", "Enterprise Business Consultant", "Creative Content & Copywriter"].index(st.session_state.current_persona) if st.session_state.current_persona in ["Master Coding Expert (Full-Stack & Debugging)", "Professional Prompt Engineer (Copy-Ready Prompts)", "Enterprise Business Consultant", "Creative Content & Copywriter"] else 0
    )
    st.session_state.current_persona = ai_persona
    
    ai_engine = st.selectbox(
        "Select Intelligence Engine",
        ["Google Gemini Flash / Pro", "OpenAI ChatGPT-4o", "Anthropic Claude 3.5 Sonnet"],
        index=["Google Gemini Flash / Pro", "OpenAI ChatGPT-4o", "Anthropic Claude 3.5 Sonnet"].index(st.session_state.current_engine) if st.session_state.current_engine in ["Google Gemini Flash / Pro", "OpenAI ChatGPT-4o", "Anthropic Claude 3.5 Sonnet"] else 0
    )
    st.session_state.current_engine = ai_engine

    api_key = ""
    if "Gemini" in ai_engine:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter Gemini API Key:", type="password")
            
    elif "ChatGPT" in ai_engine:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", "")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter OpenAI API Key:", type="password")
            
    elif "Claude" in ai_engine:
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
        if not api_key:
            api_key = st.text_input("Enter Anthropic API Key:", type="password")

    if "Coding" in ai_persona:
        system_prompt = "You are DasAi, an elite Principal Software Engineer. Provide complete, production-ready code with clean syntax, robust error handling, and comments."
    elif "Prompt" in ai_persona:
        system_prompt = "You are DasAi, an expert AI Prompt Engineer. Generate highly optimized, professional, structured, and copy-ready prompts based on user requirements."
    elif "Business" in ai_persona:
        system_prompt = "You are DasAi, an elite Corporate Business Consultant and Strategist. Provide sharp, data-driven, and actionable business strategies."
    else:
        system_prompt = "You are DasAi, an advanced multi-domain AI assistant designed to deliver high-intelligence professional answers."

    saved_upi = get_setting("upi_id", "")
    if saved_upi:
        st.markdown("---")
        st.success(f"💳 Active UPI: `{saved_upi}`")

    st.markdown("---")
    if st.button("🗑️ Clear Chat Workspace", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout Session", use_container_width=True):
        log_activity(st.session_state.user_email, "Logged Out")
        st.query_params.clear()
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.session_state.is_admin = 0
        st.rerun()

    st.markdown("---")
    st.caption("🚀 DasAi Intelligence Core v4.8")

# App Header & Main Views
st.markdown('<p class="main-header">⚡ DasAi</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Mode: <b>{st.session_state.current_persona}</b> | Engine: <b>{st.session_state.current_engine}</b></p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message DasAi or command setting changes (e.g., 'switch to claude', 'set upi id to myname@okaxis')..."):
    cmd_lower = prompt.lower()
    setting_changed = False
    response_msg = ""

    if "claude" in cmd_lower:
        st.session_state.current_engine = "Anthropic Claude 3.5 Sonnet"
        setting_changed = True
        response_msg = "✅ Intelligence Engine successfully switched to **Anthropic Claude 3.5 Sonnet** via chat command!"
    elif "chatgpt" in cmd_lower or "gpt-4o" in cmd_lower:
        st.session_state.current_engine = "OpenAI ChatGPT-4o"
        setting_changed = True
        response_msg = "✅ Intelligence Engine successfully switched to **OpenAI ChatGPT-4o** via chat command!"
    elif "gemini" in cmd_lower:
        st.session_state.current_engine = "Google Gemini Flash / Pro"
        setting_changed = True
        response_msg = "✅ Intelligence Engine successfully switched to **Google Gemini Flash / Pro** via chat command!"

    elif "coding mode" in cmd_lower or "coding expert" in cmd_lower:
        st.session_state.current_persona = "Master Coding Expert (Full-Stack & Debugging)"
        setting_changed = True
        response_msg = "✅ AI Mode successfully switched to **Master Coding Expert** via chat command!"
    elif "prompt mode" in cmd_lower or "prompt engineer" in cmd_lower:
        st.session_state.current_persona = "Professional Prompt Engineer (Copy-Ready Prompts)"
        setting_changed = True
        response_msg = "✅ AI Mode successfully switched to **Professional Prompt Engineer** via chat command!"
    elif "business mode" in cmd_lower or "business consultant" in cmd_lower:
        st.session_state.current_persona = "Enterprise Business Consultant"
        setting_changed = True
        response_msg = "✅ AI Mode successfully switched to **Enterprise Business Consultant** via chat command!"

    elif "upi" in cmd_lower and ("set" in cmd_lower or "to" in cmd_lower):
        words = prompt.split()
        target_upi = next((w for w in words if "@" in w), None)
        if target_upi:
            save_setting("upi_id", target_upi)
            setting_changed = True
            response_msg = f"💳 **UPI Gateway Configured!** Merchant UPI ID successfully saved as: `{target_upi}`"
        else:
            setting_changed = True
            response_msg = "⚠️ Please provide a valid UPI ID format containing '@' (e.g., `set upi id to shankar@okaxis`)."

    elif "pay" in cmd_lower or "payment" in cmd_lower or "qr" in cmd_lower:
        current_upi = get_setting("upi_id", "shankar@okhdfcbank")
        import re
        amounts = re.findall(r'\d+', prompt)
        amount = amounts[0] if amounts else "100"
        
        upi_link = f"upi://pay?pa={current_upi}&pn=DasAi%20Platform&am={amount}&cu=INR"
        setting_changed = True
        response_msg = f"""### 💸 UPI Payment Gateway Link
* **Merchant UPI:** `{current_upi}`
* **Amount:** `₹{amount}`

[👉 Click Here to Pay via UPI App (GPay / PhonePe / Paytm)]({upi_link})

*(Aap apne phone ke UPI scanner se is link ko scan karke ya direct click karke payment kar sakte hain)*"""

    if setting_changed:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response_msg})
        st.rerun()

    if not api_key:
        st.error("Please provide a valid API key in the sidebar to activate the intelligence engine!")
    else:
        log_activity(st.session_state.user_email, f"Queried: {prompt[:25]}...")
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("DasAi is analyzing and generating response..."):
                try:
                    ai_response = ""
                    active_engine = st.session_state.current_engine
                    
                    if "Gemini" in active_engine:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(model_name="gemini-3.8-flash", system_instruction=system_prompt)
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                        ai_response = response.text

                    elif "ChatGPT" in active_engine:
                        client = openai.OpenAI(api_key=api_key)
                        messages_payload = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        response = client.chat.completions.create(model="gpt-4o", messages=messages_payload)
                        ai_response = response.choices[0].message.content

                    elif "Claude" in active_engine:
                        client = anthropic.Anthropic(api_key=api_key)
                        messages_payload = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]} for m in st.session_state.messages]
                        response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=4000, system=system_prompt, messages=messages_payload)
                        ai_response = response.content[0].text

                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    st.error(f"Intelligence Execution Error: {e}")
                    
