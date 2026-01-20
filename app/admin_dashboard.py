import pandas as pd
import streamlit as st
from db.database import get_connection


def fetch_all_bookings():
    conn = get_connection()
    query = """
    SELECT 
        b.id AS booking_id,
        c.name,
        c.email,
        c.phone,
        b.booking_type,
        b.date,
        b.time,
        b.status,
        b.created_at
    FROM bookings b
    JOIN customers c ON b.customer_id = c.customer_id
    ORDER BY b.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def render_admin_dashboard():
    st.subheader("🛠 Admin Dashboard — Bookings")

    df = fetch_all_bookings()

    if df.empty:
        st.info("No bookings found.")
        return

    # Filters
    search_email = st.text_input("Search by email (optional)")
    search_name = st.text_input("Search by name (optional)")

    if search_email:
        df = df[df["email"].str.contains(search_email, case=False)]

    if search_name:
        df = df[df["name"].str.contains(search_name, case=False)]

    st.dataframe(df, use_container_width=True)
