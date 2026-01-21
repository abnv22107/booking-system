import sys
from pathlib import Path
import uuid
from utils.faiss_store import delete_faiss_index
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st

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

# Setting up basic streamlit page 
st.set_page_config(
    page_title="AI Doctor Booking Assistant",
    page_icon="🩺",
    layout="wide"
)
# Getting the session ID 
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# Initialize DB tables
create_tables()

# App Title & Mode Selection

st.title("AI Doctor Booking Assistant")

mode = st.sidebar.selectbox(
    "Select Mode",
    ["User", "Admin"]
)

# ADMIN MODE 

if mode == "Admin":
    render_admin_dashboard()
    st.stop()   

# USER MODE


# PDF upload 
st.subheader("Upload Documents for Q&A")

uploaded_pdfs = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
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

# Clear chat button logic
if st.button("Clear Chat"):
    delete_faiss_index(st.session_state.session_id)

    st.session_state.clear()
    st.rerun()


# For displaying previous messages
for msg in get_chat_history():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
user_input = st.chat_input("Ask a question or book an appointment…")


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
