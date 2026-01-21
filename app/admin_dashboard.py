import streamlit as st
import pandas as pd
from datetime import datetime
from db.database import get_connection


# ---------------- DATA FETCH ----------------

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
    ORDER BY b.date, b.time
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ---------------- ADMIN DASHBOARD ----------------

def render_admin_dashboard():
    st.title("Admin Dashboard")

    df = fetch_all_bookings()

    if df.empty:
        st.info("No bookings found.")
        return

    # ---------- KPI METRICS ----------
    today = datetime.today().strftime("%Y-%m-%d")

    total_bookings = len(df)
    todays_bookings = len(df[df["date"] == today])
    upcoming_bookings = len(df[df["date"] >= today])
    unique_specialties = df["booking_type"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bookings", total_bookings)
    col2.metric("Today's Bookings", todays_bookings)
    col3.metric("Upcoming Bookings", upcoming_bookings)
    col4.metric("Specialties", unique_specialties)

    st.divider()

    # ---------- DAILY CALENDAR VIEW ----------
    st.subheader("Daily Booking Schedule")

    selected_date = st.date_input(
        "Select date",
        value=datetime.today()
    ).strftime("%Y-%m-%d")

    daily_df = df[df["date"] == selected_date]

    if daily_df.empty:
        st.info("No bookings for the selected date.")
    else:
        daily_df = daily_df.sort_values("time")
        for _, row in daily_df.iterrows():
            st.markdown(
                f"""
                Time: {row['time']}  
                Specialty: {row['booking_type']}  
                Patient: {row['name']}  
                Email: {row['email']}  
                ---
                """
            )

    st.divider()

    # ---------- ANALYTICS ----------
    st.subheader("Booking Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("Bookings per Specialty")
        specialty_counts = (
            df["booking_type"]
            .value_counts()
            .sort_values(ascending=False)
        )
        st.bar_chart(specialty_counts)

    with col2:
        st.markdown("Bookings Over Time")
        bookings_by_date = (
            df.groupby("date")
            .size()
            .sort_index()
        )
        st.line_chart(bookings_by_date)

    st.divider()

    # ---------- FILTERS ----------
    st.subheader("Search and Filter Bookings")

    search_email = st.text_input("Search by email (optional)")
    search_name = st.text_input("Search by name (optional)")

    filtered_df = df.copy()

    if search_email:
        filtered_df = filtered_df[
            filtered_df["email"].str.contains(search_email, case=False, na=False)
        ]

    if search_name:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_name, case=False, na=False)
        ]

    st.subheader("All Bookings")
    st.dataframe(filtered_df, use_container_width=True)
