import streamlit as st
from huggingface_hub import InferenceClient
import os

# Page configuration
st.set_page_config(page_title="DasAi", page_icon="🤖")

st.title("🤖 DasAi - Coding Assistant")
st.write("Aapka apna AI assistant, jo bina kisi memory limit ke fast chalega!")

HF_TOKEN = "aiqcpWLhRPTvlSDvllYlmBAtcoTzQrFBWb"

# Client setup
os.environ["HF_TOKEN"] = HF_TOKEN
client = InferenceClient(model="Qwen/Qwen2.5-Coder-1.5B-Instruct")

# Chat history initialize karo
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani messages screen par dikhao
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User ka input lo
if prompt := st.chat_input("Ask DasAi..."):
    # User message add karo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI ka response generate karo
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = client.chat_completion(
                messages=st.session_state.messages,
                max_tokens=500,
                temperature=0.7
            )
            bot_reply = response.choices[0].message.content
            message_placeholder.markdown(bot_reply)
            
            # Assistant response add karo
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            error_msg = f"Error: {e}. Kripya apna token check karein."
            message_placeholder.markdown(error_msg)
            
