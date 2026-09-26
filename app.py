import google.generativeai as genai
import streamlit as st

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="DasAi - Enterprise Coding Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Professional Look
st.markdown(
    """
    <style>
    .stChatInput {
        max-width: 1000px;
        margin: auto;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1f1f1f;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666666;
        margin-bottom: 25px;
    }
    .stChatMessage {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Sidebar Configuration & Settings
with st.sidebar:
  st.markdown("## ⚙️ DasAi Control Panel")
  st.markdown("---")

  # API Key Management
  api_key = None
  try:
    # Streamlit Secrets se key uthayega (Cloud ke liye)
    api_key = st.secrets.get("GEMINI_API_KEY")
  except Exception:
    pass

  if not api_key:
    api_key = st.text_input(
        "Enter Gemini API Key:", type="password", help="Apni Google AI Studio API Key yahan dalein"
    )

  st.markdown("### 🛠️ Model Settings")
  # Sabse powerful aur advanced model jo aapne manga hai
  selected_model = st.selectbox(
      "Choose Intelligence Model",
      ["gemini-3.1-pro-preview", "gemini-3.8-flash"],
      index=0,
      help="Pro model complex coding architecture ke liye sabse best hai.",
  )

  temperature = st.slider(
      "Creativity / Temperature",
      min_value=0.0,
      max_value=1.0,
      value=0.2,
      step=0.1,
      help="Low temperature code accuracy ke liye behtar hota hai.",
  )

  st.markdown("---")
  if st.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

  st.markdown("### 📊 Status")
  if api_key:
    st.success("API Key Configured ✅")
  else:
    st.warning("API Key Required ⚠️")

  st.markdown("---")
  st.caption("Powered by Google Gemini & Streamlit | Professional Edition")

# 3. Main Header Interface
st.markdown(
    '<p class="main-header">🤖 DasAi Coding Assistant</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Advanced software engineering, debugging, and multi-language system design at your fingertips.</p>',
    unsafe_allow_html=True,
)

# 4. API Configuration & Model Initialization
if api_key:
  try:
    genai.configure(api_key=api_key)

    # System Instructions for Professional Coding AI behavior
    system_prompt = (
        "You are DasAi, an elite Principal Software Engineer and AI Coding Assistant. "
        "Your responses must be extremely accurate, clean, highly optimized, and production-ready. "
        "Always explain complex logic clearly in English/Hinglish as requested, and provide "
        "properly structured markdown code blocks with clear language specifiers (e.g., python, javascript, cpp)."
    )

    # Initialize the Generative Model with configuration
    generation_config = {"temperature": temperature}
    model = genai.GenerativeModel(
        model_name=selected_model,
        system_instruction=system_prompt,
        generation_config=generation_config,
    )
  except Exception as e:
    st.error(f"Failed to initialize model configuration: {e}")
else:
  st.info("👈 Kripya apni API key sidebar mein enter karein taaki coding assistant shuru ho sake.")

# 5. Session State for Chat Memory Management
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display Historical Messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# 6. User Interaction & Chat Loop
if prompt := st.chat_input("Apna coding task, bug, ya system architecture yahan type karein..."):
  if not api_key:
    st.error("Pehle sidebar mein Gemini API Key provide karna zaroori hai!")
  else:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    # Generate Professional AI Response
    with st.chat_message("assistant"):
      with st.spinner("DasAi code analyze kar raha hai aur logic likh raha hai..."):
        try:
          # Format chat history for Gemini multi-turn support
          gemini_history = []
          for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

          # Start chat session and get response
          chat_session = model.start_chat(history=gemini_history)
          response = chat_session.send_message(prompt)
          ai_response = response.text

          # Render response
          st.markdown(ai_response)
          
          # Append Assistant Response to Session History
          st.session_state.messages.append({"role": "assistant", "content": ai_response})

        except Exception as e:
          st.error(f"Execution Error: {e}")
            
