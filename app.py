import google.generativeai as genai
import openai
import requests
import streamlit as st
import anthropic

# 1. Page Configuration & Professional Layout
st.set_page_config(
    page_title="DasAi - Multi-AI Universal Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for UI Cleanliness
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #ff4b4b;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666666;
        margin-bottom: 20px;
    }
    .stChatMessage {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Sidebar Settings & Multi-AI Control Panel
with st.sidebar:
  st.markdown("## ⚙️ DasAi Multi-AI Panel")
  st.markdown("---")

  # Model Provider Selection
  ai_provider = st.selectbox(
      "Select AI Provider",
      ["Google Gemini", "OpenAI ChatGPT", "Anthropic Claude"],
  )

  # Dynamic API Key inputs based on selected provider
  api_key = None
  selected_model = ""

  if ai_provider == "Google Gemini":
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
  st.markdown("### 🌤️ Live Weather Tool")
  city_input = st.text_input("Check City Weather:", "Delhi")
  if st.button("Fetch Live Weather"):
    try:
      geo_url = f"https://nominatim.openstreetmap.org/search?q={city_input}&format=json&limit=1"
      headers = {"User-Agent": "DasAiApp/1.0"}
      geo_res = requests.get(geo_url, headers=headers).json()
      if geo_res:
        lat, lon = float(geo_res[0]["lat"]), float(geo_res[0]["lon"])
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        w_res = requests.get(weather_url).json()
        curr = w_res["current"]
        st.success(
            f"📍 **{city_input.capitalize()}**\n\n- Temp: **{curr['temperature_2m']}°C**\n- Humidity:"
            f" **{curr['relative_humidity_2m']}%**\n- Wind:"
            f" **{curr['wind_speed_10m']} km/h**"
        )
      else:
        st.error("City nahi mili!")
    except Exception as e:
      st.error(f"Weather fetch karne mein error: {e}")

  st.markdown("---")
  if st.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

  st.caption("🚀 Multi-AI Powered by Streamlit")

# 3. Main Header Interface
st.markdown(
    '<p class="main-header">🤖 DasAi Multi-AI Assistant</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Switch between Gemini, ChatGPT, and Claude models seamlessly in one unified interface.</p>',
    unsafe_allow_html=True,
)

# 4. Master Universal System Prompt Instruction
system_instruction = """
You are DasAi, an elite, highly intelligent, and multi-disciplinary Universal AI Assistant 
and Principal System Architect. You possess expert-level knowledge across a massive range of domains:
1. Software Engineering & Coding (Python, JS, Web Dev, DB, Architecture).
2. Mobile/Device Utilities, Travel, Healthcare (CMC Vellore), and Government Services.
3. Digital Content Creation, YouTube/Facebook Monetization, and Business Strategy.
Provide clean, structured responses and proper markdown code blocks with copy features. Answer accurately in English or Hinglish.
"""

# 5. Session Chat Management
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Prompt Input Loop
if prompt := st.chat_input("Apna sawal ya coding task yahan type karein..."):
  if not api_key:
    st.error(
        f"Pehle sidebar mein {ai_provider} ki API Key provide karna zaroori hai!"
    )
  else:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner(f"Connecting to {ai_provider} ({selected_model})..."):
        try:
          ai_response = ""

          # --- GEMINI EXECUTION ---
          if ai_provider == "Google Gemini":
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel(
                model_name=selected_model, system_instruction=system_instruction
            )
            gemini_history = []
            for msg in st.session_state.messages[:-1]:
              role = "user" if msg["role"] == "user" else "model"
              gemini_history.append({"role": role, "parts": [msg["content"]]})
            chat_session = gemini_model.start_chat(history=gemini_history)
            response = chat_session.send_message(prompt)
            ai_response = response.text

          # --- OPENAI CHATGPT EXECUTION ---
          elif ai_provider == "OpenAI ChatGPT":
            client = openai.OpenAI(api_key=api_key)
            openai_messages = [
                {"role": "system", "content": system_instruction}
            ]
            for msg in st.session_state.messages:
              openai_messages.append(
                  {"role": msg["role"], "content": msg["content"]}
              )
            response = client.chat.completions.create(
                model=selected_model, messages=openai_messages
            )
            ai_response = response.choices[0].message.content

          # --- ANTHROPIC CLAUDE EXECUTION ---
          elif ai_provider == "Anthropic Claude":
            client = anthropic.Anthropic(api_key=api_key)
            claude_messages = []
            for msg in st.session_state.messages:
              role = "user" if msg["role"] == "user" else "assistant"
              claude_messages.append({"role": role, "content": msg["content"]})
            response = client.messages.create(
                model=selected_model,
                max_tokens=4000,
                system=system_instruction,
                messages=claude_messages,
            )
            ai_response = response.content[0].text

          # Render Response
          st.markdown(ai_response)
          st.session_state.messages.append(
              {"role": "assistant", "content": ai_response}
          )

        except Exception as e:
          st.error(f"Execution Error with {ai_provider}: {e}")
            
