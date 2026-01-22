import sys
from pathlib import Path
import uuid
from utils.faiss_store import delete_faiss_index
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd

from chat_logic import (
    initialize_chat_state,
    add_message,
    get_chat_history,
    detect_intent,
)

from booking_flow import handle_booking_intent
from rag_pipeline import ingest_pdfs, rag_query
from admin_dashboard import render_admin_dashboard
from db.models import create_tables
from db.database import get_connection

st.set_page_config(
    page_title="AI Doctor Booking Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    .stMarkdown {
        line-height: 1.7;
    }
    
    h1 {
        color: #1e3a8a;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem;
    }
    
    h2, h3 {
        color: #1e40af;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.25);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stFileUploader {
        border: none;
        border-radius: 16px;
        padding: 0;
        background: transparent;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px dashed rgba(148, 163, 184, 0.5);
        border-radius: 18px;
        padding: 1.25rem;
        transition: all 0.25s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(102, 126, 234, 0.75);
        background: rgba(255, 255, 255, 0.06);
        transform: translateY(-1px);
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: rgba(226, 232, 240, 0.95);
    }
    
    .stChatMessage {
        padding: 1.25rem;
        border-radius: 16px;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stChatMessage[data-testid="assistant"] {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        border: 1px solid #e2e8f0;
    }
    
    .stChatMessage p {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    
    .stChatMessage p:last-child {
        margin-bottom: 0;
    }
    
    .stSelectbox label {
        font-weight: 600;
        color: #1e40af;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stSpinner {
        color: #667eea;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: white;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] .stSelectbox select {
        background: rgba(255, 255, 255, 0.95);
        color: #1e3a8a;
        border-radius: 10px;
        border: none;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stSidebar"] .stSelectbox select:hover {
        background: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="stSidebar"] * {
        color: white;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }
    
    .sidebar-stat-card {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .sidebar-stat-label {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.95);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .sidebar-stat-value {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar-calendar {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        padding: 1.25rem;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
    }
    
    .sidebar-date-display {
        font-size: 1rem;
        color: #ffffff;
        margin-bottom: 0.75rem;
        text-align: center;
        font-weight: 600;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    .stChatInput {
        border-radius: 16px;
        border: 2px solid #e2e8f0;
    }
    
    .stChatInput:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    </style>
""", unsafe_allow_html=True)
# Getting the session ID 
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# Initialize DB tables
create_tables()

def get_booking_stats():
    try:
        conn = get_connection()
        query = """
        SELECT 
            b.date
        FROM bookings b
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {"today_bookings": 0}
        
        today = datetime.today().strftime("%Y-%m-%d")
        today_bookings = len(df[df["date"] == today])
        
        return {"today_bookings": today_bookings}
    except:
        return {"today_bookings": 0}

st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   background-clip: text;
                   font-size: 3rem;
                   margin-bottom: 0.5rem;">AI Doctor Booking Assistant</h1>
        <p style="color: #64748b; font-size: 1.1rem; margin-top: 0;">Your intelligent booking Assistant</p>
    </div>
""", unsafe_allow_html=True)

mode = st.sidebar.selectbox(
    "Select Mode",
    ["User", "Admin"],
    key="mode_selector"
)

st.sidebar.markdown("---")

stats = get_booking_stats()

st.sidebar.markdown("""
    <div class="sidebar-stat-card">
        <div class="sidebar-stat-label">Today's Date</div>
        <div class="sidebar-date-display">{}</div>
    </div>
""".format(datetime.today().strftime("%B %d, %Y")), unsafe_allow_html=True)

st.sidebar.markdown("""
    <div class="sidebar-stat-card">
        <div class="sidebar-stat-label">Today's Bookings</div>
        <div class="sidebar-stat-value">{}</div>
    </div>
""".format(stats["today_bookings"]), unsafe_allow_html=True)

st.sidebar.markdown("---")

today = datetime.today()
cal = calendar.monthcalendar(today.year, today.month)

st.sidebar.markdown("""
    <div class="sidebar-calendar">
        <div class="sidebar-date-display">{}</div>
    </div>
""".format(today.strftime("%B %Y")), unsafe_allow_html=True)

calendar_html = '<div style="display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 4px; width: 100%; box-sizing: border-box;">'
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
for day in weekdays:
    calendar_html += f'<div style="text-align: center; padding: 0.3rem 0; color: rgba(255, 255, 255, 0.9); font-weight: 700; font-size: 0.7rem; min-width: 0;">{day}</div>'

for week in cal:
    for day in week:
        if day == 0:
            calendar_html += '<div style="padding: 0.45rem 0; min-width: 0;"></div>'
        else:
            is_today = day == today.day
            if is_today:
                style = 'background: rgba(255, 255, 255, 0.35); border-radius: 6px; font-weight: 800; color: #ffffff; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);'
            else:
                style = 'color: rgba(255, 255, 255, 0.95); font-weight: 600;'
            calendar_html += f'<div style="text-align: center; padding: 0.45rem 0; min-width: 0; {style}">{day}</div>'

calendar_html += '</div>'

st.sidebar.markdown(f"""
    <div class="sidebar-calendar">
        {calendar_html}
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# ADMIN MODE 

if mode == "Admin":
    render_admin_dashboard()
    st.stop()   

# USER MODE


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📄 Upload Documents for Q&A")

uploaded_pdfs = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload medical documents or guides to ask questions about them"
)

if uploaded_pdfs:
    with st.spinner("Processing documents..."):
        vector_store = ingest_pdfs(uploaded_pdfs)
        if vector_store:
            st.session_state.vector_store = vector_store
            st.success("Documents processed successfully!")
        else:
            st.error("Could not extract text from the uploaded PDFs.")


initialize_chat_state()

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Clear Chat", use_container_width=True):
        delete_faiss_index(st.session_state.session_id)
        st.session_state.clear()
        st.rerun()


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 💬 Chat")

for msg in get_chat_history():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a question or book an appointment...")


if user_input:
    # Show user message
    add_message("user", user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    # ROUTING LOGIC
    if (
        "booking_state" in st.session_state
        and st.session_state.booking_state.get("active")
    ):
        assistant_reply = handle_booking_intent(user_input)
    else:
        intent = detect_intent(user_input)
        if intent == "booking":
            assistant_reply = handle_booking_intent(user_input)
        else:
            assistant_reply = rag_query(user_input)

    # Show assistant response
    add_message("assistant", assistant_reply)
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)
