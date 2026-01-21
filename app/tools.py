from db.database import get_connection
import smtplib
import streamlit as st
from email.message import EmailMessage
from datetime import datetime, timedelta
import re


# -----------------------------
# DATABASE: Save Booking
# -----------------------------
def save_booking(booking_data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert customer
    cursor.execute("""
        INSERT INTO customers (name, email, phone)
        VALUES (?, ?, ?)
    """, (
        booking_data["name"],
        booking_data["email"],
        booking_data["phone"],
    ))

    customer_id = cursor.lastrowid

    # Insert booking
    cursor.execute("""
        INSERT INTO bookings (customer_id, booking_type, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        customer_id,
        booking_data["doctor_or_specialty"],
        booking_data["date"],
        booking_data["time"],
        "CONFIRMED",
    ))

    booking_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return booking_id


def safe_save_booking(booking_data: dict):
    """
    Final safety check before saving booking.
    Prevents double-booking for the same
    date, time, and specialty.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Re-check slot availability at DB level
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE date = ?
        AND time = ?
        AND booking_type = ?
    """, (
        booking_data["date"],
        booking_data["time"],
        booking_data["doctor_or_specialty"],
    ))

    conflict_count = cursor.fetchone()[0]

    if conflict_count > 0:
        conn.close()
        return None  # Slot already taken

    # Insert customer
    cursor.execute("""
        INSERT INTO customers (name, email, phone)
        VALUES (?, ?, ?)
    """, (
        booking_data["name"],
        booking_data["email"],
        booking_data["phone"],
    ))

    customer_id = cursor.lastrowid

    # Insert booking
    cursor.execute("""
        INSERT INTO bookings (customer_id, booking_type, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        customer_id,
        booking_data["doctor_or_specialty"],
        booking_data["date"],
        booking_data["time"],
        "CONFIRMED",
    ))

    booking_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return booking_id



# EMAIL: Send Confirmation

def send_confirmation_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends a confirmation email using SMTP credentials
    stored in Streamlit secrets.
    """

    try:
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = st.secrets["SMTP_PORT"]
        smtp_email = st.secrets["SMTP_EMAIL"]
        smtp_password = st.secrets["SMTP_PASSWORD"]

        msg = EmailMessage()
        msg["From"] = smtp_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        return True

    except Exception as e:
        # Important: never crash the app due to email failure
        print("Email error:", e)
        return False
    

# TIME & SLOT UTILITIES


SLOT_DURATION_MINUTES = 30


def normalize_time_to_minutes(time_str: str) -> int | None:
    """
    Converts time string like:
    - '10:30'
    - '10:30 AM'
    - '22:00'
    into minutes since midnight.
    """
    try:
        time_str = time_str.strip().upper()

        # Handle AM/PM format
        if "AM" in time_str or "PM" in time_str:
            dt = datetime.strptime(time_str, "%I:%M %p")
        else:
            dt = datetime.strptime(time_str, "%H:%M")

        return dt.hour * 60 + dt.minute

    except Exception:
        return None


def minutes_to_time_str(minutes: int) -> str:
    """
    Converts minutes since midnight back to HH:MM format.
    """
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def is_slot_available(
    date: str,
    time_str: str,
    doctor_or_specialty: str
) -> bool:
    """
    Returns False if a booking already exists
    for the same date, time slot, and specialty.
    """

    requested_minutes = normalize_time_to_minutes(time_str)
    if requested_minutes is None:
        return True  # Let validation handle bad formats elsewhere

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT time
        FROM bookings
        WHERE date = ?
        AND booking_type = ?
    """, (date, doctor_or_specialty))

    existing_times = cursor.fetchall()
    conn.close()

    for (existing_time,) in existing_times:
        existing_minutes = normalize_time_to_minutes(existing_time)
        if existing_minutes is None:
            continue

        # Check overlap (30 min slot)
        if abs(existing_minutes - requested_minutes) < SLOT_DURATION_MINUTES:
            return False

    return True

def suggest_nearby_slots(
    date: str,
    time_str: str,
    doctor_or_specialty: str,
    max_suggestions: int = 2
) -> list[str]:
    """
    Suggests nearby available time slots
    (±30 minutes) for the same date and specialty.
    """

    base_minutes = normalize_time_to_minutes(time_str)
    if base_minutes is None:
        return []

    suggestions = []
    offsets = [-SLOT_DURATION_MINUTES, SLOT_DURATION_MINUTES]

    for offset in offsets:
        candidate = base_minutes + offset

        # Working hours safety (00:00 - 23:30)
        if candidate < 0 or candidate > (23 * 60 + 30):
            continue

        candidate_time = minutes_to_time_str(candidate)

        if is_slot_available(date, candidate_time, doctor_or_specialty):
            suggestions.append(candidate_time)

        if len(suggestions) >= max_suggestions:
            break

    return suggestions
