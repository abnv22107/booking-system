import streamlit as st
import pandas as pd
from datetime import datetime
from db.database import get_connection

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800&display=swap');
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.75rem;
        border-radius: 24px;
        color: white;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 32px rgba(0, 0, 0, 0.18), 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-family: 'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0.75rem 0 0.5rem 0;
        line-height: 1;
        letter-spacing: -0.03em;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        position: relative;
        z-index: 1;
    }
    
    .metric-label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    div.booking-card,
    .booking-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 20px !important;
        padding: 1.75rem !important;
        margin-bottom: 1.5rem !important;
        margin-top: 0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        display: block !important;
        width: 100% !important;
    }
    
    div.booking-card::before,
    .booking-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 4px !important;
        height: 100% !important;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
        z-index: 1 !important;
    }
    
    div.booking-card:hover,
    .booking-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15), 0 4px 8px rgba(0, 0, 0, 0.08) !important;
        border-color: #667eea !important;
    }
    
    div.booking-time,
    .booking-time {
        font-family: 'Poppins', 'Inter', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.02em !important;
        position: relative !important;
        z-index: 2 !important;
    }
    
    div.booking-detail,
    .booking-detail {
        font-family: 'Inter', sans-serif !important;
        color: #475569 !important;
        margin: 0.5rem 0 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        position: relative !important;
        z-index: 2 !important;
    }
    
    div.booking-detail strong,
    .booking-detail strong {
        color: #1e40af !important;
        font-weight: 600 !important;
        min-width: 100px !important;
        display: inline-block !important;
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    .stDateInput label {
        font-weight: 600;
        color: #1e40af;
    }
    
    .stTextInput label {
        font-weight: 600;
        color: #1e40af;
    }
    </style>
""", unsafe_allow_html=True)


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
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       background-clip: text;
                       font-size: 2.5rem;
                       margin-bottom: 0.5rem;">Admin Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    df = fetch_all_bookings()

    if df.empty:
        st.info("No bookings found.")
        return

    today = datetime.today().strftime("%Y-%m-%d")

    total_bookings = len(df)
    todays_bookings = len(df[df["date"] == today])
    upcoming_bookings = len(df[df["date"] >= today])
    unique_specialties = df["booking_type"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="metric-label">Total Bookings</div>
                <div class="metric-value">{total_bookings}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <div class="metric-label">Today's Bookings</div>
                <div class="metric-value">{todays_bookings}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <div class="metric-label">Upcoming Bookings</div>
                <div class="metric-value">{upcoming_bookings}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <div class="metric-label">Specialties</div>
                <div class="metric-value">{unique_specialties}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📅 Daily Booking Schedule")

    selected_date = st.date_input(
        "Select date",
        value=datetime.today(),
        key="admin_date_picker"
    ).strftime("%Y-%m-%d")

    daily_df = df[df["date"] == selected_date]

    if daily_df.empty:
        st.info("No bookings for the selected date.")
    else:
        daily_df = daily_df.sort_values("time")
        for idx, row in daily_df.iterrows():
            st.markdown(
                f"""
                <div class="booking-card" style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 2px solid #e2e8f0; border-radius: 20px; padding: 1.75rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04); position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);"></div>
                    <div class="booking-time" style="font-family: 'Poppins', 'Inter', sans-serif; font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1rem; letter-spacing: -0.02em; position: relative; z-index: 2;">{row['time']}</div>
                    <div class="booking-detail" style="font-family: 'Inter', sans-serif; color: #475569; margin: 0.5rem 0; font-size: 1rem; line-height: 1.6; position: relative; z-index: 2;"><strong style="color: #1e40af; font-weight: 600; min-width: 100px; display: inline-block;">Specialty:</strong> {row['booking_type']}</div>
                    <div class="booking-detail" style="font-family: 'Inter', sans-serif; color: #475569; margin: 0.5rem 0; font-size: 1rem; line-height: 1.6; position: relative; z-index: 2;"><strong style="color: #1e40af; font-weight: 600; min-width: 100px; display: inline-block;">Patient:</strong> {row['name']}</div>
                    <div class="booking-detail" style="font-family: 'Inter', sans-serif; color: #475569; margin: 0.5rem 0; font-size: 1rem; line-height: 1.6; position: relative; z-index: 2;"><strong style="color: #1e40af; font-weight: 600; min-width: 100px; display: inline-block;">Email:</strong> {row['email']}</div>
                    <div class="booking-detail" style="font-family: 'Inter', sans-serif; color: #475569; margin: 0.5rem 0; font-size: 1rem; line-height: 1.6; position: relative; z-index: 2;"><strong style="color: #1e40af; font-weight: 600; min-width: 100px; display: inline-block;">Phone:</strong> {row['phone']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📊 Booking Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Bookings per Specialty**")
        specialty_counts = (
            df["booking_type"]
            .value_counts()
            .sort_values(ascending=False)
        )
        st.bar_chart(specialty_counts, height=300)

    with col2:
        st.markdown("**Bookings Over Time**")
        bookings_by_date = (
            df.groupby("date")
            .size()
            .sort_index()
        )
        st.line_chart(bookings_by_date, height=300)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🔍 Search and Filter Bookings")

    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_email = st.text_input("Search by email", key="search_email", placeholder="Enter email address...")
    
    with search_col2:
        search_name = st.text_input("Search by name", key="search_name", placeholder="Enter patient name...")

    filtered_df = df.copy()

    if search_email:
        filtered_df = filtered_df[
            filtered_df["email"].str.contains(search_email, case=False, na=False)
        ]

    if search_name:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_name, case=False, na=False)
        ]

    st.markdown("### 📋 All Bookings")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
