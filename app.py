import google.generativeai as genai
import streamlit as st

# Page Configuration & Layout
st.set_page_config(
    page_title="DasAi - Professional AI Assistant",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styling for Professional Look
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Professional Header Section
st.markdown('<p class="main-title">⚡ DasAi Intelligence</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Your high-performance universal assistant for'
    " software development, research, and general problem solving.</p>",
    unsafe_allow_html=True,
)

# Configure Gemini API securely via Streamlit Secrets
try:
  if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
  else:
    st.error(
        "⚠️ Configuration Error: 'GEMINI_API_KEY' is missing from your"
        " Streamlit Secrets."
    )
    st.stop()
except Exception as e:
  st.error(f"⚠️ Initialization Error: {e}")
  st.stop()

# Initialize Chat Session History
if "messages" not in st.session_state:
  st.session_state.messages = []

# Render Prior Chat Messages from History
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Capture User Input
if prompt := st.chat_input(
    "Type your message, code query, or question here..."
):
  # Append and display user message
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Generate Assistant Response
  with st.chat_message("assistant"):
    with st.spinner("Processing request..."):
      try:
        # Initialize Gemini Model
        model = genai.GenerativeModel("gemini-3.8-flash")

        # Professional System Instructions for Universal Capabilities
        system_prompt = (
            "You are DasAi, an advanced, highly competent, and professional"
            " AI assistant. You excel across multiple domains including"
            " software engineering, technical analysis, general knowledge,"
            " factual inquiries, and creative tasks. Always deliver accurate,"
            " well-structured, clear, and professional responses in English."
            f"\n\nUser Query: {prompt}"
        )

        # Generate Content
        response = model.generate_content(system_prompt)
        assistant_response = response.text

        # Display and Store Assistant Response
        st.markdown(assistant_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response}
        )

      except Exception as e:
        st.error(
            "⚠️ An error occurred while generating the response. Please check"
            f" your API configuration or network connection. Details: {e}"
        )
          
