import streamlit as st
from openai import OpenAI

# ----------------- CONFIG -----------------
st.set_page_config(page_title="ChatGPT Clone", page_icon="🤖", layout="centered")
st.title("🤖 Chat with GPT")

# Initialize OpenAI client
client = OpenAI(api_key="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")

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- CHAT DISPLAY -----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------- USER INPUT -----------------
if prompt := st.chat_input("Type your message..."):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # you can use gpt-4o or gpt-3.5-turbo
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content

    # Store assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)
