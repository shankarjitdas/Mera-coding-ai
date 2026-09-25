import google.generativeai as genai
import streamlit as st

st.set_page_config(
    page_title="DasAi - Coding Assistant", page_icon="🤖", layout="centered"
)

st.title("🤖 DasAi - Coding Assistant")
st.write(
    "Aapka apna AI assistant, jo bina kisi memory limit ke fast chalega!"
)

try:
  api_key = st.secrets["GEMINI_API_KEY"]
  genai.configure(api_key=api_key)
except Exception as e:
  st.error("Kripya Streamlit Secrets mein 'GEMINI_API_KEY' add karein.")

if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

if prompt := st.chat_input("Ask DasAi... (Coding related sawal puchein)"):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    try:
      # Yeh loop aapki key ke hisab se jo bhi model available hoga use dhoond lega
      available_model = None
      for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
          available_model = m.name
          break

      if not available_model:
        available_model = "gemini-pro"

      model = genai.GenerativeModel(available_model)
      response = model.generate_content(prompt)
      assistant_response = response.text

      st.markdown(assistant_response)
      st.session_state.messages.append(
          {"role": "assistant", "content": assistant_response}
      )

    except Exception as e:
      st.error(f"Kuch error aa gayi: {e}")
        
