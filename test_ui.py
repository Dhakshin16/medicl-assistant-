import streamlit as st

st.set_page_config(page_title="UI Test", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
        }
        h1 {
            color: white;
            text-align: center;
            font-family: 'Poppins', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 If you see a pink gradient background, CSS injection works!")
