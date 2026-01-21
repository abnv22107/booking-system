from db.database import get_connection
import smtplib
import streamlit as st
from email.message import EmailMessage


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
