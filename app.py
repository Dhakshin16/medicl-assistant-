import streamlit as st
import streamlit as st
import base64
import os
import time
from groq import Groq
from pinecone import Pinecone, ServerlessSpec
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch


# Load the tokenizer and model

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small", legacy=False)
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")
    
def generate_response(input_text):
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def display_typing_effect(text, role="assistant"):
    message_placeholder = st.empty()  # Create an empty placeholder for messages
    current_text = ""
    for char in text:
        current_text += char
        message_placeholder.markdown(f"**{role}:** {current_text}")  # Update placeholder content
        time.sleep(0.005)  # Simulate typing delay
    return current_text



conversation_history = ""

def generate_response_with_context(user_input):
    global conversation_history
    conversation_history += f"User: {user_input}\n"
    response = generate_response(conversation_history)
    conversation_history += f"Bot: {response}\n"
    return response


st.markdown("""
    <style>
    .glowing-box {
        border-radius: 10px;
        padding: 10px;
        background-color: #1E1E1E;
        color: grey;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.6), 0 0 30px rgba(255, 255, 255, 0.4), 0 0 40px rgba(255, 0, 255, 0.3);
        transition: box-shadow 0.3s ease-in-out;
    }

    .glowing-box:hover {
        box-shadow: 0 0 40px rgba(255, 255, 255, 0.8), 0 0 60px rgba(255, 0, 255, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

client = Groq(
    # This is the default and can be omitted
    api_key="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",
)
pc = Pinecone("52eb674a-0527-4ccb-80b5-baacd6e6a1e7")
index = pc.Index("quickstart")
st.session_state.api_key = "pcsk_6zRJ7k_P1uocGbprKwXWb8YJSVHFVQasaJbs4aa69p73Th8akHtHLPFjsXoTeQ5FfYUzy9"


# Only show the API key input if the key is not already set
if not st.session_state.api_key:
    # Ask the user's API key if it doesn't exist
    api_key = st.text_input("Enter API Key", type="password")
    
    # Store the API key in the session state once provided
    if api_key:
        st.session_state.api_key = api_key
        st.rerun()  # Refresh the app once the key is entered to remove the input field
else:
    # If the API key exists, show the chat app
    # Center the title using HTML and Markdown
    
    st.markdown("""
    <style>
    @keyframes flyIn {
        0% {
            transform: translateX(-100%);
            opacity: 0;
        }
        100% {
            transform: translateX(0%);
            opacity: 1;
        }
    }

    .fly-in-title {
        animation: flyIn 2s ease-out;
        color: #808080;
        text-align: center;
        font-size: 2.5em;
    }
    </style>

    <h1 class="fly-in-title">AI ASSISTANT</h1>
    """, unsafe_allow_html=True)

    # Initialize the chat message list in session state if it doesn't exist
    if "chat_messages" not in st.session_state:
        st.session_state.groq_chat_messages = [{"role": "system", "content": "You are an AI assistance. You are a medical assistance. You can able to answer all kind of questions related to users medical related doubts.You will help the users in all aspects by giving them kind and polite reply and clarrifing all their doubts."}]
        st.session_state.chat_messages = []
        
    # Display previous chat messages
    for messages in st.session_state.chat_messages:
        if messages["role"] in ["user", "assistant"]:
            with st.chat_message(messages["role"]):
                st.markdown(messages["content"])
    
    # Define a function to simulate chat interaction (you would replace this with an actual API call)
    def get_chat():
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[st.session_state.chat_messages[-1]["content"]],
            parameters={
                "input_type": "query"
            }
        )
        results = index.query(
            namespace="ns1",
            vector=embedding[0].values,
            top_k=3,
            include_values=False,
            include_metadata=True
        )
        context = ""
        for result in results.matches:
            if result['score'] > 0.8:
                context += result['metadata']['text']
            
        st.session_state.groq_chat_messages[-1]["content"] = f"User Query: {st.session_state.chat_messages[-1]['content']} \n Retrieved Content (optional): {context}"
        chat_completion = client.chat.completions.create(
            messages=st.session_state.groq_chat_messages,
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content

    # Handle user input
    if prompt := st.chat_input("Any queries?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.groq_chat_messages.append({"role": "user", "content": prompt})
        # Get the assistant's response (in this case, it's just echoing the prompt)
        with st.spinner("Aurora is working on it.."):
            response = get_chat()
        with st.chat_message("Aurora"):
            final_response = display_typing_effect(response)
         # Add user message and assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.session_state.groq_chat_messages.append({"role": "assistant", "content": response})

        

     
