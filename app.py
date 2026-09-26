import google.generativeai as genai
import openai
import streamlit as st
import anthropic

# 1. Page Configuration & Enterprise Styling
st.set_page_config(
    page_title="DasAi - Professional SaaS AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End SaaS UI Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .stChatMessage {
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stSidebar {
        background-color: #F9FAFB;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Sidebar Control Center (Clean Professional Layout)
with st.sidebar:
  st.markdown("## ⚙️ DasAi SaaS Control")
  st.markdown("---")

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
    selected_model = st.selectbox(
        "Choose Model", ["gemini-3.1-pro-preview", "gemini-3.8-flash"]
    )

  elif ai_provider == "OpenAI ChatGPT":
    try:
      api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
      pass
    if not api_key:
      api_key = st.text_input("Enter OpenAI API Key:", type="password")
    selected_model = st.selectbox(
        "Choose Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    )

  elif ai_provider == "Anthropic Claude":
    try:
      api_key = st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
      pass
    if not api_key:
      api_key = st.text_input("Enter Anthropic API Key:", type="password")
    selected_model = st.selectbox(
        "Choose Model",
        [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ],
    )

  st.markdown("---")
  st.markdown("### 🤖 DasAi Workspace")
  st.markdown("- **Status:** Online & Secure")
  st.markdown("- **Mode:** Enterprise Ready")

  if st.button("🗑️ Clear Workspace", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

  st.markdown("---")
  st.caption("🚀 DasAi SaaS Platform v2.0")

# 3. Main SaaS Header
st.markdown(
    '<p class="main-header">⚡ DasAi Professional SaaS Agent</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Your Enterprise-grade AI powerhouse with Smart Auto-Routing and Multi-Model support.</p>',
    unsafe_allow_html=True,
)

# 4. Master SaaS System Prompt
system_instruction = """
You are DasAi, an elite Principal Software Engineer, Enterprise SaaS Architect, and Multi-Domain AI Expert. 
Your core competencies include:
1. Advanced Coding & Full-Stack Development: Python, JavaScript, React, Streamlit, HTML/CSS, SQL databases, API integrations, debugging, and secure system design.
2. SaaS Scaling & Monetization: Subscription models, payment gateways (Stripe/Razorpay), user management, and digital product strategies.
3. Mobile & Daily Utilities: Device settings, diagnostics, document handling, and live information processing.
4. Business & Content Growth: YouTube optimization, Facebook monetization, SEO, marketing automation, and Amazon KDP workflows.

Response Guidelines:
- Write clean, highly optimized, production-ready code with clear language markdown specifiers (e.g., python, javascript) so users can instantly use the built-in copy features.
- Maintain an expert yet supportive tone. Communicate fluently in English or Hinglish according to user preference.
"""

# 5. Session State Initialization
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# 6. Main Interaction Loop with Active Model Indicator & Smart Routing
if prompt := st.chat_input(
    "Apna coding task, bug fix, SaaS architecture, ya query yahan type karein..."
):
  if not api_key:
    st.error(f"Kripya pehle sidebar mein API key provide karein!")
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

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner(f"DasAi is processing via {active_model}..."):
        try:
          ai_response = ""

          if active_provider == "Google Gemini":
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel(
                model_name=active_model, system_instruction=system_instruction
            )
            gemini_history = []
            for msg in st.session_state.messages[:-1]:
              role = "user" if msg["role"] == "user" else "model"
              gemini_history.append({"role": role, "parts": [msg["content"]]})
            chat_session = gemini_model.start_chat(history=gemini_history)
            response = chat_session.send_message(prompt)
            ai_response = response.text

          elif active_provider == "OpenAI ChatGPT":
            client = openai.OpenAI(api_key=api_key)
            openai_messages = [
                {"role": "system", "content": system_instruction}
            ]
            for msg in st.session_state.messages:
              openai_messages.append(
                  {"role": msg["role"], "content": msg["content"]}
              )
            response = client.chat.completions.create(
                model=active_model, messages=openai_messages
            )
            ai_response = response.choices[0].message.content

          elif active_provider == "Anthropic Claude":
            client = anthropic.Anthropic(api_key=api_key)
            claude_messages = []
            for msg in st.session_state.messages:
              role = "user" if msg["role"] == "user" else "assistant"
              claude_messages.append({"role": role, "content": msg["content"]})
            response = client.messages.create(
                model=active_model,
                max_tokens=4000,
                system=system_instruction,
                messages=claude_messages,
            )
            ai_response = response.content[0].text

          st.markdown(ai_response)
          st.session_state.messages.append(
              {"role": "assistant", "content": ai_response}
          )

        except Exception as e:
          st.error(f"Execution Error: {e}")
            
