from db.database import get_connection



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


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st


def send_confirmation_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = st.secrets["SMTP_EMAIL"]
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(
            st.secrets["SMTP_SERVER"],
            st.secrets["SMTP_PORT"]
        )
        server.starttls()
        server.login(
            st.secrets["SMTP_EMAIL"],
            st.secrets["SMTP_PASSWORD"]
        )
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print("Email error:", e)
        return False

