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
  genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
  st.error("Kripya Streamlit Secrets mein 'GEMINI_API_KEY' add karein.")

if "gemini_model" not in st.session_state:
  st.session_state["gemini_model"] = "gemini-pro"
    

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
      model = genai.GenerativeModel(
          model_name=st.session_state["gemini_model"],
          system_instruction=(
              "You are DasAi, an expert coding assistant. Help the user with"
              " clean code, debugging, and programming explanations."
          ),
      )

      response = model.generate_content(prompt)
      assistant_response = response.text

      st.markdown(assistant_response)
      st.session_state.messages.append(
          {"role": "assistant", "content": assistant_response}
      )

    except Exception as e:
      st.error(f"Kuch error aa gayi: {e}")
        
