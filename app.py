import google.generativeai as genai
import requests
import streamlit as st

# 1. Page Configuration & Professional Layout
st.set_page_config(
    page_title="DasAi - Universal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Code Block Copy Buttons & UI Cleanliness
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

# 2. Sidebar Settings & Tools Panel
with st.sidebar:
  st.markdown("## ⚙️ DasAi Control Center")
  st.markdown("---")

  # API Key Setup
  api_key = None
  try:
    api_key = st.secrets.get("GEMINI_API_KEY")
  except Exception:
    pass

  if not api_key:
    api_key = st.text_input(
        "Enter Gemini API Key:",
        type="password",
        help="Google AI Studio se li gayi key yahan dalein",
    )

  st.markdown("### 🧠 Intelligence Model")
  selected_model = st.selectbox(
      "Choose Model",
      ["gemini-3.1-pro-preview", "gemini-3.8-flash"],
      index=0,
      help="Pro model complex coding aur reasoning ke liye best hai.",
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

  st.caption("🚀 Powered by Gemini & Streamlit")

# 3. Main Header Interface
st.markdown(
    '<p class="main-header">🤖 DasAi Universal AI Assistant</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Advanced Software Engineering, Device/App Guidance, Digital Business, Travel, Healthcare Info, and Real-time Utilities.</p>',
    unsafe_allow_html=True,
)

# 4. Master Universal System Prompt & Model Initialization
if api_key:
  try:
    genai.configure(api_key=api_key)

    # Master Universal Prompt integrating all required domains
    system_instruction = """
        You are DasAi, an elite, highly intelligent, and multi-disciplinary Universal AI Assistant 
        and Principal System Architect. You possess expert-level knowledge across a massive range of domains:

        1. Software Engineering, Coding & Tech: Python, JavaScript, HTML/CSS, Database management, API integration, debugging, app/website creation, and system architecture.
        2. Mobile & Device Utilities: Smartphone settings, phone diagnostics, contacts, SMS, calling, WhatsApp, Telegram, email, calendar, alarm, calculator, notes, camera, gallery, file manager, PDF reader, document scanner, and screen recording.
        3. Travel, Logistics & Transport: Maps, GPS navigation, nearby places, train search/timetable/PNR/ticket booking info, bus search/booking, flight search/booking, airport info, cab/taxi/auto booking, metro info, travel planning, and hotel booking.
        4. Healthcare & Medical Guidance: Vellore hospital search, Christian Medical College (CMC) Vellore information, medical appointment details, pharmacy information, blood bank info, doctors, ambulance, and emergency services.
        5. Local & Regional Knowledge: Hailakandi information, Silchar information, Assam info, India info, and Indian government services (Aadhaar, PAN, Passport, Driving licence, RTO, electricity, water, gas).
        6. Finance, Business & Digital Services: Banking info, UPI, digital payments, currency conversion, stock market, cryptocurrency, shopping, product/price comparison, grocery delivery, online education, job search, resume creation, business research, Amazon KDP, SEO, marketing, analytics, and customer support.
        7. Digital Content & Growth: YouTube research, Instagram tools, Facebook tools & monetization, LinkedIn tools, content writing, blog/ebook creation, AI image/video generation, translation, OCR, and workflow automation.

        Guidelines for your responses:
        - Provide precise, highly structured, clean, and production-ready answers.
        - Always format code blocks clearly with proper language specifiers (e.g., python, javascript) so users can easily copy snippets using native markdown copy tools.
        - Maintain a professional yet helpful tone. Answer accurately in English or Hinglish based on the user's preference.
        """

    model = genai.GenerativeModel(
        model_name=selected_model, system_instruction=system_instruction
    )
  except Exception as e:
    st.error(f"Model config error: {e}")
else:
  st.warning("⚠️ Kripya sidebar mein apni Gemini API Key enter karein.")

# 5. Session Chat Management
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Prompt Input Loop
if prompt := st.chat_input(
    "Apna sawal, coding task, travel query, ya device guidance yahan type"
    " karein..."
):
  if not api_key:
    st.error("Pehle API key provide karein!")
  else:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("DasAi process kar raha hai..."):
        try:
          gemini_history = []
          for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

          chat_session = model.start_chat(history=gemini_history)
          response = chat_session.send_message(prompt)
          ai_response = response.text

          # Render Markdown (Streamlit automatically provides native code copy buttons on code blocks)
          st.markdown(ai_response)
          st.session_state.messages.append(
              {"role": "assistant", "content": ai_response}
          )
        except Exception as e:
          st.error(f"Error: {e}")
            
