import streamlit as st
import re
from datetime import datetime

from tools import save_booking, send_confirmation_email
from tools import is_slot_available, suggest_nearby_slots


REQUIRED_FIELDS = [
    "name",
    "email",
    "phone",
    "doctor_or_specialty",
    "date",
    "time",
]

FIELD_QUESTIONS = {
    "name": "May I have your full name?",
    "email": "Please provide your email address.",
    "phone": "What is your phone number?",
    "doctor_or_specialty": "Which doctor or specialty would you like to consult?",
    "date": "What date would you prefer for the appointment? (YYYY-MM-DD)",
    "time": "What time would you prefer? (e.g., 10:30 AM)",
}


# ---------------- VALIDATION HELPERS ----------------

def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def is_valid_phone(phone: str) -> bool:
    return phone.isdigit() and len(phone) >= 8


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(time_str: str) -> bool:
    return bool(re.match(r"^\d{1,2}:\d{2}\s?(AM|PM)?$", time_str, re.IGNORECASE))


# ---------------- STATE INITIALIZATION ----------------

def initialize_booking_state():
    if "booking_state" not in st.session_state:
        st.session_state.booking_state = {
            "active": True,
            "name": None,
            "email": None,
            "phone": None,
            "doctor_or_specialty": None,
            "date": None,
            "time": None,
            "confirmed": False,

            # slot validation
            "slot_conflict": False,
            "suggested_slots": [],
            "current_field": None,
        }


def get_next_missing_field():
    for field in REQUIRED_FIELDS:
        if not st.session_state.booking_state.get(field):
            return field
    return None


# ---------------- UPDATE BOOKING STATE ----------------

def update_booking_state(user_message: str):
    state = st.session_state.booking_state
    field = state.get("current_field")

    if not field:
        return None

    value = user_message.strip()

    # ---------- VALIDATIONS ----------
    if field == "email" and not is_valid_email(value):
        return "❌ Please enter a valid email address."

    if field == "phone" and not is_valid_phone(value):
        return "❌ Please enter a valid phone number (digits only)."

    if field == "date" and not is_valid_date(value):
        return "❌ Please enter date in YYYY-MM-DD format."

    if field == "time":
        if not is_valid_time(value):
            return "❌ Please enter a valid time (e.g., 10:30 AM)."

        date = state.get("date")
        specialty = state.get("doctor_or_specialty")

        # -------- SLOT CHECK --------
        if not is_slot_available(date, value, specialty):
            state["slot_conflict"] = True
            state["suggested_slots"] = suggest_nearby_slots(
                date, value, specialty
            )

            suggestion_text = ""
            if state["suggested_slots"]:
                suggestion_text = (
                    "\n\n🕒 **Available nearby slots:** "
                    + ", ".join(state["suggested_slots"])
                )

            return (
                "⚠️ The selected time slot is already booked for this specialty.\n\n"
                "Would you like to continue anyway?\n"
                "Reply **Yes** to continue or **No** to choose another time."
                + suggestion_text
            )

    # ---------- SAVE FIELD ----------
    state[field] = value
    state["current_field"] = None
    return None


def summarize_booking():
    b = st.session_state.booking_state
    return (
        "📝 **Please confirm your appointment details:**\n\n"
        f"- **Name:** {b['name']}\n"
        f"- **Email:** {b['email']}\n"
        f"- **Phone:** {b['phone']}\n"
        f"- **Doctor/Specialty:** {b['doctor_or_specialty']}\n"
        f"- **Date:** {b['date']}\n"
        f"- **Time:** {b['time']}\n\n"
        "✅ Please reply with **Yes** to confirm or **No** to cancel."
    )


# ---------------- MAIN BOOKING HANDLER ----------------

def handle_booking_intent(user_message: str) -> str:
    initialize_booking_state()
    state = st.session_state.booking_state

    # ---------- SLOT CONFLICT DECISION ----------
    if state.get("slot_conflict"):
        if user_message.lower() in ["yes", "y"]:
            state["slot_conflict"] = False
            state["suggested_slots"] = []
            return summarize_booking()

        elif user_message.lower() in ["no", "n"]:
            state["slot_conflict"] = False
            state["time"] = None
            state["current_field"] = "time"
            return FIELD_QUESTIONS["time"]

        else:
            return (
                "Please reply **Yes** to continue with the same time "
                "or **No** to choose a different slot."
            )

    # ---------- CONFIRMATION ----------
    if all(state.get(f) for f in REQUIRED_FIELDS):
        if not state["confirmed"]:
            if user_message.lower() in ["yes", "y", "confirm"]:
                state["confirmed"] = True

                booking_data = state.copy()
                booking_id = save_booking(booking_data)

                email_body = (
                    f"Hello {booking_data['name']},\n\n"
                    f"Your doctor appointment has been confirmed.\n\n"
                    f"Booking ID: {booking_id}\n"
                    f"Doctor/Specialty: {booking_data['doctor_or_specialty']}\n"
                    f"Date: {booking_data['date']}\n"
                    f"Time: {booking_data['time']}\n\n"
                    f"Thank you for using our service."
                )

                email_sent = send_confirmation_email(
                    booking_data["email"],
                    "Doctor Appointment Confirmation",
                    email_body
                )

                del st.session_state.booking_state

                if email_sent:
                    return (
                        "✅ Your appointment is confirmed!\n\n"
                        f"📌 **Booking ID:** {booking_id}\n\n"
                        "📧 A confirmation email has been sent."
                    )
                else:
                    return (
                        "✅ Your appointment is confirmed!\n\n"
                        f"📌 **Booking ID:** {booking_id}\n\n"
                        "⚠️ Email could not be sent, but your booking was saved."
                    )

            elif user_message.lower() in ["no", "n", "cancel"]:
                del st.session_state.booking_state
                return "❌ Booking cancelled. Let me know if you'd like to start again."

            else:
                return summarize_booking()

    # ---------- STORE ANSWER ----------
    if state.get("current_field"):
        error = update_booking_state(user_message)
        if error:
            return error

    # ---------- ASK NEXT ----------
    next_field = get_next_missing_field()
    if next_field:
        state["current_field"] = next_field
        return FIELD_QUESTIONS[next_field]

    return summarize_booking()
