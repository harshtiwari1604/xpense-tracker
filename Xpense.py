import pandas as pd
import streamlit as st
from supabase import create_client

# Page Configuration
st.set_page_config(
    page_title="Xpense Tracker Cloud", page_icon="⚡", layout="wide"
)

# --- SUPABASE CONNECTION CONFIG ---
# Yahan apni Supabase URL aur Anon Key daalein jo aapne Step 3 mein copy ki thi
SUPABASE_URL = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyeGhwb2xoZWZ2dXF4dHNoeHNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUxNzQ1MDcsImV4cCI6MjEwMDc1MDUwN30.AyjGwbN-jIKOHhxVbuJWbg3Y8juNTGGGn1LWsAFa_0k"
SUPABASE_KEY = "https://vrxhpolhefvuqxtshxsq.supabase.co"

@st.cache_resource
def init_supabase():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

# --- PREMIUM STYLING ---
st.markdown(
    """
    <style>
        .main { background-color: #0b0f19; color: #ffffff; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: black; border: none; }
        .stButton>button:hover { opacity: 0.9; }
        .auth-card { background-color: #111827; padding: 30px; border-radius: 12px; border: 1px solid #1F2937; max-width: 400px; margin: auto; margin-top: 10vh; }
    </style>
""",
    unsafe_allow_html=True,
)

# Session state for user auth
if "user" not in st.session_state:
  st.session_state.user = None

# --- AUTHENTICATION SCREEN (LOGIN / SIGNUP) ---
if not st.session_state.user:
  st.markdown(
      "<h1 style='text-align: center; color: #4facfe;'>⚡ Xpense Tracker"
      " Pro</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: gray;'>Secure Multi-User Financial"
      " Ecosystem</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1.2, 1])
  with col2:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
      st.markdown("### Welcome Back")
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
      st.markdown("### Create Account")
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
                "Account created! Check your email to verify or try logging"
                " in."
            )
          except Exception as e:
            st.error(f"Signup failed: {e}")

else:
  # --- MAIN DASHBOARD (AFTER LOGIN) ---
  current_user = st.session_state.user

  col_h1, col_h2 = st.columns([3, 1])
  with col_h1:
    st.markdown(
        f"<h1>⚡ Xpense Tracker <span style='font-size:16px;"
        f" color:#4facfe;'>({current_user.email})</span></h1>",
        unsafe_allow_html=True,
    )
  with col_h2:
    if st.button("🚪 Logout"):
      supabase.auth.sign_out()
      st.session_state.user = None
      st.rerun()

  # Fetch data specific to this logged-in user from Supabase
  try:
    response = (
        supabase.table("expenses")
        .select("*")
        .eq("user_id", current_user.id)
        .execute()
    )
    expenses_data = response.data
  except Exception as e:
    expenses_data = []
    st.error(f"Error fetching data: {e}")

  df = pd.DataFrame(expenses_data)

  monthly_budget = 25000  # Default budget limit
  total_spent = int(df["amount"].sum()) if not df.empty else 0
  remaining_budget = monthly_budget - total_spent

  # Metrics Row
  m1, m2, m3 = st.columns(3)
  m1.metric("Total Budget", f"₹ {monthly_budget:,}")
  m2.metric("Total Spent", f"₹ {total_spent:,}")
  m3.metric("Remaining", f"₹ {remaining_budget:,}")

  st.markdown("---")

  # --- SIDEBAR: ADD EXPENSE ---
  st.sidebar.markdown("## 🕹️ Control Center")
  st.sidebar.markdown(f"**Logged in as:** {current_user.email}")
  st.sidebar.markdown("---")

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
          st.sidebar.success("Saved to Cloud!")
          st.rerun()
        except Exception as e:
          st.sidebar.error(f"Error saving: {e}")
      else:
        st.sidebar.error("Amount must be > 0")

  # --- MAIN BODY: TRANSACTIONS & ANALYTICS ---
  col_left, col_right = st.columns([1.6, 1])

  with col_left:
    st.markdown("### 📋 Your Personal Transactions")
    if not df.empty:
      display_df = df[
          ["date", "category", "description", "amount", "payment_method"]
      ].rename(
          columns={
              "date": "Date",
              "category": "Category",
              "description": "Description",
              "amount": "Amount (₹)",
              "payment_method": "Payment Method",
          }
      )
      st.dataframe(display_df, use_container_width=True)
    else:
      st.info(
          "No expenses recorded yet. Add your first spend from the sidebar!"
      )

  with col_right:
    st.markdown("### 📊 Spend Analytics")
    if not df.empty:
      cat_summary = df.groupby("category")["amount"].sum().reset_index()
      cat_summary.columns = ["Category", "Amount (₹)"]
      st.bar_chart(cat_summary, x="Category", y="Amount (₹)", color="#4facfe")
    else:
      st.warning("Analytics will appear once you add expenses.")
