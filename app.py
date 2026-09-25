"""
DasAI - Coding Assistant
A Streamlit-based AI chat application powered by Qwen2.5-Coder-1.5B-Instruct
via the Hugging Face Inference API.
"""

import streamlit as st
from huggingface_hub import InferenceClient

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct""

SYSTEM_PROMPT = (
    "You are an expert AI programming assistant with deep knowledge of "
    "software engineering, multiple programming languages, debugging, and "
    "industry best practices. When answering:\n"
    "- Explain your reasoning clearly and concisely.\n"
    "- Always format code in proper markdown code blocks with the correct "
    "language tag.\n"
    "- Identify bugs and explain why they occur, not just how to fix them.\n"
    "- Suggest improvements and best practices where relevant.\n"
    "- If a request is ambiguous, ask a short clarifying question instead "
    "of guessing."
)

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="DasAI - Coding Assistant",
    page_icon="🤖",
    layout="centered",
)

# ------------------------------------------------------------------
# CLIENT SETUP
# The API token is read securely from Streamlit Secrets.
# It must never be hardcoded in this file.
# ------------------------------------------------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]

client = InferenceClient(
    model=MODEL_NAME,
    token=HF_TOKEN,
)

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.title("🤖 DasAI — Coding Assistant")
st.caption("Your personal AI assistant for writing, debugging, and explaining code.")

# ------------------------------------------------------------------
# CHAT HISTORY (persists for the duration of the browser session)
# ------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Render past messages (system prompt stays hidden from the UI)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ------------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------------
prompt = st.chat_input("Ask DasAI anything about your code...")

if prompt:
    # Save and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display the assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            response = client.chat_completion(
                messages=st.session_state.messages,
                max_tokens=800,
                temperature=0.3,
            )
            reply = response.choices[0].message.content
            message_placeholder.markdown(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

        except Exception as e:
            error_message = (
                f"⚠️ Something went wrong: {e}\n\n"
                "Please check that your Hugging Face token is valid and has "
                "the correct permissions."
            )
            message_placeholder.markdown(error_message)

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ About")
    st.markdown(
        f"""
        **Model:** `{MODEL_NAME}`

        **License:** Apache 2.0 — free for commercial and personal use.

        DasAI is designed to help you write, debug, explain, and improve
        code faster — all powered by a free, open-source model.
        """
    )

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()
