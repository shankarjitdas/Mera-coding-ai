"""
Coding AI Assistant - Streamlit App
Model: Qwen/Qwen2.5-Coder-1.5B-Instruct (Hugging Face, free & open)

Ye app ek chatbox interface deta hai jisme user coding sawaal pooch sakta hai
aur AI expert programming assistant ki tarah jawaab deta hai.
"""

import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
from threading import Thread

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

SYSTEM_PROMPT = (
    "You are an expert AI programming assistant with deep knowledge of software "
    "engineering, multiple programming languages, debugging, and best practices. "
    "You write clean, correct, well-explained code. When answering:\n"
    "- Explain your reasoning clearly and simply.\n"
    "- Always format code in proper markdown code blocks with the correct language tag.\n"
    "- Point out bugs and explain WHY they happen, not just how to fix them.\n"
    "- Suggest best practices and improvements when relevant.\n"
    "- If a request is unclear, ask a short clarifying question instead of guessing.\n"
    "- Be concise but thorough — don't pad answers with unnecessary text."
)

# ------------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------------
st.set_page_config(page_title="Coding AI Assistant", page_icon="💻", layout="wide")


# ------------------------------------------------------------------
# LOAD MODEL (cached so it only loads once, not on every message)
# ------------------------------------------------------------------
@st.cache_resource(show_spinner="Model load ho raha hai... (pehli baar 1-2 minute lag sakte hain)")
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,   # CPU-friendly. Agar GPU hai toh torch.float16 use kar sakte ho.
        device_map="cpu",
    )
    return tokenizer, model


tokenizer, model = load_model()

# ------------------------------------------------------------------
# UI HEADER
# ------------------------------------------------------------------
st.title("💻 Coding AI Assistant")
st.caption("Powered by Qwen2.5-Coder-1.5B-Instruct (free & open-source)")

# ------------------------------------------------------------------
# CHAT HISTORY (session_state = jab tak browser tab khula hai, yaad rehta hai)
# ------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Purane messages screen par dikhana (system prompt hide rakhte hain)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ------------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------------
user_input = st.chat_input("Apna coding sawaal poochho...")

if user_input:
    # User ka message save aur dikhana
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI ka jawaab generate karna
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # Chat template apply karna (model ko conversation format samjhata hai)
        prompt = tokenizer.apply_chat_template(
            st.session_state.messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer(prompt, return_tensors="pt")

        # Streaming setup - jawaab word-by-word screen par aayega (jaise ChatGPT)
        streamer = TextIteratorStreamer(
            tokenizer, skip_prompt=True, skip_special_tokens=True
        )
        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1,
        )

        # Generation ko alag thread mein chalate hain taaki streaming kaam kare
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            full_response += new_text
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown(
        "**Model:** Qwen2.5-Coder-1.5B-Instruct\n\n"
        "**License:** Apache 2.0 (free, commercial use allowed)"
    )
    if st.button("🗑️ Chat clear karo"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
