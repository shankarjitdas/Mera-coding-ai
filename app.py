import google.generativeai as genai
import streamlit as st

st.set_page_config(
    page_title="DasAi - Coding Assistant", page_icon="🤖", layout="centered"
)

st.title("🤖 DasAi - Coding Assistant")
st.write(
    "Aapka apna AI assistant, jo bina kisi memory limit ke fast chalega!"
)

# API Key configure karna
try:
  api_key = st.secrets["GEMINI_API_KEY"]
  genai.configure(api_key=api_key)
except Exception as e:
  st.error("Kripya Streamlit Secrets mein 'GEMINI_API_KEY' add karein.")

# Chat history initialize karna
if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User input lena
if prompt := st.chat_input("Ask DasAi... (Coding related sawal puchein)"):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    try:
      # Sahi aur updated model name yahan set kiya gaya hai
      model = genai.GenerativeModel("gemini-1.5-flash")

      response = model.generate_content(prompt)
      assistant_response = response.text

      st.markdown(assistant_response)
      st.session_state.messages.append(
          {"role": "assistant", "content": assistant_response}
      )

    except Exception as e:
      st.error(f"Kuch error aa gayi: {e}")
        
