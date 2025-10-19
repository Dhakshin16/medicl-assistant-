import streamlit as st
import base64
import os
import time
from groq import Groq
from pinecone import Pinecone
from PyPDF2 import PdfReader
import docx
from io import BytesIO
import json
from datetime import datetime
import pickle


# --- Page Configuration ---
st.set_page_config(
    page_title="ARORA - Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Professional CSS Styling (ChatGPT-like) ---
st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d0d0d !important;
        color: #ececf1 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #10a37f !important;
        background: linear-gradient(180deg, #0d9e73 0%, #0a6a50 100%) !important;
    }
    
    [data-testid="stSidebarContent"] {
        background-color: transparent !important;
    }
    
    .main {
        background-color: #0d0d0d !important;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        background: #0d0d0d;
    }
    
    .header-title {
        font-size: 20px;
        font-weight: 600;
        color: #ececf1;
    }
    
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background: #0d0d0d;
    }
    
    .messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 40px 60px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        background: #0d0d0d;
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
    }
    
    .empty-title {
        font-size: 32px;
        font-weight: 600;
        color: #ececf1;
        margin-bottom: 16px;
    }
    
    .empty-subtitle {
        color: rgba(236, 207, 241, 0.6);
        font-size: 16px;
        margin-bottom: 32px;
        max-width: 500px;
    }
    
    .message-row {
        display: flex;
        margin-bottom: 16px;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-row {
        justify-content: flex-end;
    }
    
    .assistant-row {
        justify-content: flex-start;
    }
    
    .message-bubble {
        max-width: 60%;
        padding: 12px 16px;
        border-radius: 12px;
        line-height: 1.5;
        word-wrap: break-word;
    }
    
    .user-bubble {
        background: #10a37f;
        color: white;
        border-radius: 18px;
    }
    
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ececf1;
    }
    
    .input-area {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px 60px 30px;
        background: #0d0d0d;
    }
    
    .stChatInput {
        border-radius: 12px !important;
    }
    
    .stChatInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        padding: 12px 16px !important;
    }
    
    .stChatInput input:focus {
        border: 1px solid #10a37f !important;
        box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
    }
    
    .sidebar-header {
        padding: 12px;
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
    }
    
    .btn-new-chat {
        flex: 1;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.1);
        color: white;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .btn-new-chat:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    
    .sidebar-section {
        padding: 12px;
        margin-bottom: 12px;
    }
    
    .section-title {
        font-size: 13px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .file-box {
        border: 2px dashed rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        background: rgba(255, 255, 255, 0.05);
        margin-bottom: 12px;
    }
    
    .file-list {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 12px;
    }
    
    .file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        margin-bottom: 6px;
        font-size: 13px;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .file-item:last-child {
        margin-bottom: 0;
    }
    
    .chat-history-item {
        padding: 10px;
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.05);
        cursor: pointer;
        transition: all 0.2s;
        font-size: 13px;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        position: relative;
    }
    
    .chat-history-item:hover {
        background: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.9);
    }
    
    .chat-history-active {
        background: rgba(255, 255, 255, 0.15) !important;
        border-left: 3px solid #10a37f;
    }
    
    .delete-btn {
        float: right;
        color: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        font-size: 12px;
        padding: 2px 6px;
        border-radius: 3px;
        background: rgba(255, 0, 0, 0.2);
    }
    
    .delete-btn:hover {
        background: rgba(255, 0, 0, 0.4);
        color: white;
    }
    
    .stButton button {
        width: 100% !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .stButton:first-child button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    .stButton:first-child button:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }
    
    .stFileUploader {
        color: white !important;
    }
    
    .stFileUploader label {
        color: rgba(236, 207, 241, 0.8) !important;
        font-size: 13px !important;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)


# --- Chat History Management Functions ---
CHAT_HISTORY_FILE = "chat_history.json"

def save_chat_history():
    """Save all chat sessions to a JSON file"""
    try:
        history_data = {
            "sessions": st.session_state.chat_sessions,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

def load_chat_history():
    """Load chat sessions from JSON file"""
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                return history_data.get("sessions", [])
        return []
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return []

def auto_save_current_session():
    """Automatically save or update the current session"""
    if st.session_state.chat_messages:
        # Create session title from first user message
        session_title = "New Chat"
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                session_title = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break
        
        # Create session object
        session = {
            "id": st.session_state.current_session_id or datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "title": session_title,
            "messages": st.session_state.chat_messages.copy(),
            "document_context": st.session_state.document_context,
            "source_files": st.session_state.source_files.copy(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Update current session ID if not set
        if not st.session_state.current_session_id:
            st.session_state.current_session_id = session["id"]
        
        # Check if session already exists and update it
        session_exists = False
        for idx, existing_session in enumerate(st.session_state.chat_sessions):
            if existing_session["id"] == session["id"]:
                st.session_state.chat_sessions[idx] = session
                session_exists = True
                break
        
        # If session doesn't exist, add it
        if not session_exists:
            st.session_state.chat_sessions.insert(0, session)
        
        # Save to file
        save_chat_history()

def create_new_session():
    """Start a new chat session"""
    # Auto-save current session before creating new one
    auto_save_current_session()
    
    # Clear current chat
    st.session_state.chat_messages = []
    st.session_state.document_context = ""
    st.session_state.source_files = []
    st.session_state.current_session_id = None

def load_session(session_id):
    """Load a specific chat session"""
    for session in st.session_state.chat_sessions:
        if session["id"] == session_id:
            st.session_state.chat_messages = session["messages"].copy()
            st.session_state.document_context = session.get("document_context", "")
            st.session_state.source_files = session.get("source_files", [])
            st.session_state.current_session_id = session_id
            break

def delete_session(session_id):
    """Delete a chat session"""
    st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s["id"] != session_id]
    save_chat_history()
    
    # If deleted session was active, clear current chat
    if st.session_state.get("current_session_id") == session_id:
        st.session_state.chat_messages = []
        st.session_state.document_context = ""
        st.session_state.source_files = []
        st.session_state.current_session_id = None


# --- Initialize Session State ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "document_context" not in st.session_state:
    st.session_state.document_context = ""

if "source_files" not in st.session_state:
    st.session_state.source_files = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chat_history()

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None


# --- API Setup ---
try:
    client = enter api")
    pc = Pinecone("52eb674a-0527-4ccb-80b5-baacd6e6a1e7")
    index = pc.Index("quickstart")
except Exception as e:
    st.error(f"API Configuration Error: {str(e)}")


# --- File Processing Functions ---
def read_pdf_file(uploaded_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def read_docx_file(uploaded_file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"


def read_text_file(uploaded_file):
    """Extract text from TXT file"""
    try:
        text = uploaded_file.read().decode("utf-8")
        return text
    except Exception as e:
        return f"Error reading TXT: {str(e)}"


def process_uploaded_file(uploaded_file):
    """Process different file types"""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return read_pdf_file(uploaded_file)
    elif file_extension == 'docx':
        return read_docx_file(uploaded_file)
    elif file_extension == 'txt':
        return read_text_file(uploaded_file)
    else:
        return f"Unsupported file type: {file_extension}"


# --- Get AI Response ---
def get_arora_response(user_message, document_context=""):
    """Get response from ARORA with medical focus"""
    try:
        # Build the context with medical emphasis
        medical_context = ""
        if document_context:
            medical_context = f"MEDICAL DOCUMENT CONTENT:\n{document_context[:3000]}\n\n"
        
        # System message with medical focus
        system_prompt = """You are ARORA, a professional medical AI assistant specializing in healthcare support.

IMPORTANT GUIDELINES:
1. MEDICAL EXPERTISE: You have deep knowledge of medical conditions, treatments, medications, and health management.
2. EMPATHY: Show compassion and understanding when discussing health concerns.
3. ACCURACY: Provide evidence-based medical information.
4. SAFETY: Always recommend consulting healthcare professionals for serious conditions.
5. CLARITY: Explain medical concepts in understandable language.
6. RESPONSIBILITY: Never replace professional medical advice.

When answering medical questions:
- Provide detailed, accurate information
- Cite reliable sources when possible
- Suggest professional consultation for serious issues
- Give practical health advice when appropriate
- Consider patient safety in all responses

If someone asks non-medical questions, politely redirect to medical topics while remaining helpful."""

        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add conversation history (last 4 messages for context)
        for msg in st.session_state.chat_messages[-4:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message with context
        messages.append({
            "role": "user",
            "content": f"{medical_context}User Query: {user_message}"
        })

        # Get response from Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1500,
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"I encountered an error processing your request: {str(e)}. Please try again or contact support."


# --- Sidebar ---
with st.sidebar:
    # Header buttons
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("✏️ New Chat", key="new_chat", use_container_width=True):
            create_new_session()
            st.rerun()
    
    with col2:
        if st.button("⚙️", key="settings", use_container_width=True):
            st.session_state.show_settings = not st.session_state.get("show_settings", False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Document Upload Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Document Upload</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="file-box">
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">
                <strong>PDF, DOCX, or TXT</strong><br>
                <small>Max 200MB per file</small>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload medical documents",
        type=['pdf', 'docx', 'txt'],
        label_visibility="collapsed",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        if st.button("📥 Process Document", use_container_width=True, key="process_btn"):
            with st.spinner("📖 Processing document..."):
                extracted_text = process_uploaded_file(uploaded_file)
                
                if "Error" not in extracted_text and len(extracted_text) > 20:
                    st.session_state.document_context = extracted_text
                    if uploaded_file.name not in [f["name"] for f in st.session_state.source_files]:
                        st.session_state.source_files.append({
                            "name": uploaded_file.name,
                            "size": len(extracted_text),
                            "uploaded": datetime.now().strftime("%H:%M")
                        })
                    st.success("✓ Document loaded successfully!")
                else:
                    st.error(f"Failed to extract text from file: {extracted_text[:100]}")
    
    # Display loaded files
    if st.session_state.source_files:
        st.markdown('<div class="file-list">', unsafe_allow_html=True)
        for file_info in st.session_state.source_files:
            st.markdown(f"""
                <div class="file-item">
                    <span>📎 {file_info['name']}</span>
                    <span style="font-size: 11px; color: rgba(255, 255, 255, 0.5);">{file_info['uploaded']}</span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Files", use_container_width=True, key="clear_files"):
            st.session_state.document_context = ""
            st.session_state.source_files = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chat History Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 Chat History</div>', unsafe_allow_html=True)
    
    # Display saved sessions
    if st.session_state.chat_sessions:
        st.markdown(f"<small style='color: rgba(255, 255, 255, 0.5);'>{len(st.session_state.chat_sessions)} saved chats</small>", unsafe_allow_html=True)
        
        # Group by date
        sessions_by_date = {}
        for session in st.session_state.chat_sessions:
            date = session.get("date", "Unknown")
            if date not in sessions_by_date:
                sessions_by_date[date] = []
            sessions_by_date[date].append(session)
        
        # Display sessions grouped by date
        for date, sessions in sorted(sessions_by_date.items(), reverse=True):
            # Show date header for recent dates
            if date == datetime.now().strftime("%Y-%m-%d"):
                st.markdown("<small style='color: rgba(255, 255, 255, 0.6); margin-top: 8px;'>📅 Today</small>", unsafe_allow_html=True)
            elif date == (datetime.now().replace(day=datetime.now().day-1)).strftime("%Y-%m-%d"):
                st.markdown("<small style='color: rgba(255, 255, 255, 0.6); margin-top: 8px;'>📅 Yesterday</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small style='color: rgba(255, 255, 255, 0.6); margin-top: 8px;'>📅 {date}</small>", unsafe_allow_html=True)
            
            for session in sessions:
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    is_active = st.session_state.current_session_id == session["id"]
                    active_class = "chat-history-active" if is_active else ""
                    
                    if st.button(
                        f"💬 {session['title']}", 
                        key=f"load_{session['id']}",
                        use_container_width=True
                    ):
                        load_session(session["id"])
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{session['id']}", use_container_width=True):
                        delete_session(session["id"])
                        st.rerun()
        
        # Clear all history button
        if st.button("🗑️ Clear All History", use_container_width=True, key="clear_all_history"):
            st.session_state.chat_sessions = []
            save_chat_history()
            if os.path.exists(CHAT_HISTORY_FILE):
                os.remove(CHAT_HISTORY_FILE)
            st.rerun()
    else:
        st.markdown("<small style='color: rgba(255, 255, 255, 0.5);'>No saved chats yet</small>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- Main Chat Area ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <div class="header-title">🏥 ARORA - Medical Assistant</div>
    </div>
""", unsafe_allow_html=True)

# Messages Display
st.markdown('<div class="messages-area">', unsafe_allow_html=True)

if not st.session_state.chat_messages:
    st.markdown("""
        <div class="empty-state">
            <div class="empty-title">How can I help you?</div>
            <div class="empty-subtitle">
                I'm ARORA, your professional medical AI assistant. Ask me anything about health, medications, symptoms, treatments, and medical conditions.
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.markdown(f"""
                <div class="message-row user-row">
                    <div class="message-bubble user-bubble">
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f"""
                <div class="message-row assistant-row">
                    <div class="message-bubble assistant-bubble">
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input Area
st.markdown('<div class="input-area">', unsafe_allow_html=True)

prompt = st.chat_input("Message ARORA about your health...", key="main_input")

if prompt:
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Show user message
    st.markdown(f"""
        <div class="message-row user-row">
            <div class="message-bubble user-bubble">
                {prompt}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Get response
    with st.spinner("🔄 ARORA is analyzing..."):
        response = get_arora_response(prompt, st.session_state.document_context)
    
    # Add assistant message
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Auto-save the chat after each exchange
    auto_save_current_session()
    
    # Show assistant message
    st.markdown(f"""
        <div class="message-row assistant-row">
            <div class="message-bubble assistant-bubble">
                {response}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)