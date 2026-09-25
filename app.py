import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="DasAi - Professional Coding Assistant",
    page_icon="💻",
    layout="centered",
)

# Professional Header & Description
st.title("💻 DasAi: Advanced AI Coding Assistant")
st.markdown(
    "*Your reliable AI pair programmer for multi-language software development,"
    " debugging, and optimization.*"
)

# Configure Gemini API
try:
  api_key = st.secrets["GEMINI_API_KEY"]
  genai.configure(api_key=api_key)
except Exception as e:
  st.error(
      "Configuration Error: Please add your 'GEMINI_API_KEY' to Streamlit"
      " Secrets."
  )

# Initialize Chat History
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display Prior Chat Messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Input Handling
if prompt := st.chat_input("Ask any programming or software engineering question..."
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    try:
      # Initialize Model
      model = genai.GenerativeModel("gemini-3.8-flash")

      # Professional Developer System Instructions & Context
      system_prompt = (
          "You are DasAi, an expert AI software engineer and coding"
          " assistant. Your objective is to provide clean, production-ready,"
          " and well-commented code solutions accompanied by clear, concise"
          " technical explanations.\n\nUser Inquiry: "
          f"{prompt}"
      )

      # Generate Response
      response = model.generate_content(system_prompt)
      assistant_response = response.text

      st.markdown(assistant_response)
      st.session_state.messages.append(
          {"role": "assistant", "content": assistant_response}
      )

    except Exception as e:
      st.error(f"An error occurred: {e}")
        
