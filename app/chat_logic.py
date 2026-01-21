import streamlit as st

MAX_HISTORY = 25


def initialize_chat_state():
    """Initialize chat history in session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_message(role: str, content: str):
    """Add a message to chat history with size limit."""
    st.session_state.messages.append(
        {"role": role, "content": content}
    )

    # Keep only last MAX_HISTORY (25) messages
    if len(st.session_state.messages) > MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]


def get_chat_history():
    """Return current chat history."""
    return st.session_state.messages

def detect_intent(user_message: str) -> str:
    """
    Detect user intent.
    Returns: 'booking' or 'general'
    """

    booking_keywords = [
        "book", "appointment", "schedule", "consult",
        "doctor", "visit", "checkup"
    ]

    message_lower = user_message.lower()

    for keyword in booking_keywords:
        if keyword in message_lower:
            return "booking"

    return "general"
