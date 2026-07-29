import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Xpense Tracker Pro", page_icon="⚡", layout="centered"
)

# --- SECURE CREDENTIALS SETUP ---
SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL", "https://bqnmzwqayxetuhlygjim.supabase.co"
)
SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxbm16d3FheXhldHVobHlnamltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUyODY1MjQsImV4cCI6MjEwMDg2MjUyNH0.Xkfbl2puPZxOhRMkmyQWbhIJnbUiNh5Isf5GynUnWNM",
)

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- CLEAN & MODERN STYLING ---
st.markdown(
    """
    <style>
        /* Main Background */
        .stApp {
            background-color: #F8F9FA;
        }
        
        /* Headers formatting */
        h1, h2, h3 {
            color: #1A1A1A !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Input fields styling */
        [data-testid="stTextInput"] input {
            background-color: #FFFFFF;
            color: #1A1A1A;
            border: 1px solid #CED4DA;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Primary Action Buttons (Yellow Theme) */
        .stButton>button {
            width: 100%;
            border-radius: 25px;
            font-weight: bold;
            background-color: #FFC107;
            color: #1A1A1A;
            border: none;
            padding: 10px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        }
        .stButton>button:hover {
            background-color: #E0A800;
            color: #000000;
        }
        
        /* Card container look */
        .auth-container {
            background: #FFFFFF;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        }
    </style>
""",
    unsafe_allow_html=True,
)

if "user" not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION SCREEN ---
if not st.session_state.user:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 28px;'>⚡ Xpense Tracker</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6C757D; margin-bottom: 30px;'>Manage your money smartly</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                login_email = st.text_input("Email")
                login_pass = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login")

                if login_btn:
                    try:
                        res = supabase.auth.sign_in_with_password({
                            "email": login_email,
                            "password": login_pass,
                        })
                        st.session_state.user = res.user
                        st.success("Login Successful!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form"):
                signup_email = st.text_input("Email Address")
                signup_pass = st.text_input(
                    "Create Password (min 6 chars)", type="password"
                )
                signup_btn = st.form_submit_button("Sign Up")

                if signup_btn:
                    try:
                        res = supabase.auth.sign_up({
                            "email": signup_email,
                            "password": signup_pass,
                        })
                        st.success(
                            "Account created! Check your email to verify or try logging in."
                        )
                    except Exception as e:
                        st.error(f"Signup failed: {e}")

else:
    current_user = st.session_state.user
    
    # Fetch profile data from database
    try:
        profile_res = (
            supabase.table("user_profiles")
            .select("*")
            .eq("user_id", current_user.id)
            .execute()
        )
        if profile_res.data:
            user_profile = profile_res.data[0]
            monthly_budget = user_profile.get("monthly_budget", 25000)
            savings_goal = user_profile.get("savings_goal", 5000)
        else:
            monthly_budget = 25000
            savings_goal = 5000
    except:
        monthly_budget = 25000
        savings_goal = 5000

    # Top Bar with Welcome Greeting
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"<h2>Welcome back! 👋</h2>", unsafe_allow_html=True)
        st.caption(f"Logged in as: {current_user.email}")
    with col_h2:
        if st.button("🚪 Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    # Fetch expenses
    try:
        response = (
            supabase.table("expenses")
            .select("*")
            .eq("user_id", current_user.id)
            .execute()
        )
        expenses_data = response.data
    except:
        expenses_data = []

    df = pd.DataFrame(expenses_data)
    total_spent = int(df["amount"].sum()) if not df.empty and "amount" in df else 0
    remaining_budget = monthly_budget - total_spent

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Budget", f"₹ {monthly_budget:,}")
    m2.metric("Total Spent", f"₹ {total_spent:,}")
    m3.metric("Remaining Balance", f"₹ {remaining_budget:,}")
    m4.metric("Savings Goal 🎯", f"₹ {savings_goal:,}")

    st.markdown("---")

    # Sidebar
    st.sidebar.markdown("### ➕ Log New Expense")
    with st.sidebar.form("expense_logger", clear_on_submit=True):
        date = st.date_input("Date")
        category = st.selectbox(
            "Category",
            [
                "Food & Dining",
                "Study / Education",
                "Transport",
                "Entertainment",
                "Utilities",
                "Shopping",
                "Others",
            ],
        )
        description = st.text_input("Description / Notes")
        amount = st.number_input(
            "Amount (₹)", min_value=0, value=100, step=10, format="%d"
        )
        payment_method = st.selectbox(
            "Payment Mode", ["UPI", "Credit Card", "Net Banking", "Cash"]
        )

        submitted = st.form_submit_button("Record Spend")
        if submitted:
            if amount > 0:
                try:
                    supabase.table("expenses").insert({
                        "user_id": current_user.id,
                        "date": str(date),
                        "category": category,
                        "description": description,
                        "amount": int(amount),
                        "payment_method": payment_method,
                    }).execute()
                    st.sidebar.success("Saved!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
            else:
                st.sidebar.error("Amount must be > 0")

    # Main Body Layout
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown("### 📋 Transactions")
        if not df.empty and "amount" in df:
            display_df = df[
                ["id", "date", "category", "description", "amount", "payment_method"]
            ].rename(
                columns={
                    "id": "ID",
                    "date": "Date",
                    "category": "Category",
                    "description": "Description",
                    "amount": "Amount (₹)",
                    "payment_method": "Payment Method",
                }
            )
            with st.container(height=300):
                st.dataframe(display_df.drop(columns=["ID"]), use_container_width=True)
        else:
            st.info("No expenses added yet.")

    with col_right:
        st.markdown("### 📊 Analytics")
        if not df.empty and "amount" in df:
            cat_summary = df.groupby("category")["amount"].sum().reset_index()
            cat_summary.columns = ["Category", "Amount"]

            fig = px.pie(
                cat_summary,
                names="Category",
                values="Amount",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Sunset,
            )
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Chart will show up after adding expenses.")
