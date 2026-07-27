import pandas as pd
import streamlit as st
from supabase import create_client

# Page Configuration
st.set_page_config(
    page_title="Xpense Tracker Pro", page_icon="⚡", layout="wide"
)

# --- SECURE CREDENTIALS SETUP ---
SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL", "https://vryxhpolhefvuqxshxsq.supabase.co"
)
SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY", "sb_publishable_-yQnaJJeKHq0XEm1-4-AQw_HTBUynKk"
)


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
        .motivation-banner { background: linear-gradient(135deg, #1f2937 0%, #111827 100%); padding: 15px 20px; border-radius: 10px; border-left: 5px solid #4facfe; margin-bottom: 20px; font-size: 16px; color: #e5e7eb; }
        .tip-box { background: rgba(79, 172, 254, 0.08); padding: 10px 15px; border-radius: 8px; border: 1px dashed #4facfe; margin-bottom: 15px; font-size: 14px; color: #4facfe; }
    </style>
""",
    unsafe_allow_html=True,
)

if "user" not in st.session_state:
  st.session_state.user = None

# --- AUTHENTICATION SCREEN ---
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

  st.markdown(
      """
        <div style='text-align: center; max-width: 600px; margin: 20px auto; padding: 15px; background: rgba(79, 172, 254, 0.1); border-radius: 10px; border: 1px solid rgba(79, 172, 254, 0.2);'>
            <p style='color: #4facfe; font-size: 18px; font-weight: 600; margin: 0;'>💡 "Financial freedom isn't about having a lot of money; it's about having control over your choices."</p>
            <p style='color: #9ca3af; font-size: 13px; margin-top: 5px;'>Track smart today, secure your tomorrow! 🚀</p>
        </div>
    """,
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
  current_user = st.session_state.user

  # Fetch profile data from database (Default: 25000 budget, 5000 goal)
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
    st.markdown(
        f"<h1>😊 Welcome back, friend! <span style='font-size:16px;"
        f" color:#4facfe;'>({current_user.email})</span></h1>",
        unsafe_allow_html=True,
    )
  with col_h2:
    if st.button("🚪 Logout"):
      supabase.auth.sign_out()
      st.session_state.user = None
      st.rerun()

  st.markdown(
      """
        <div class="motivation-banner">
            ✨ <b>Financial Tip of the Day:</b> "Don't save what is left after spending, but spend what is left after saving." Let's make every penny count today! 🎯
        </div>
    """,
      unsafe_allow_html=True,
  )

  # Subtle guide tip
  st.markdown(
      """
        <div class="tip-box">
            👉 <b>Quick Tip:</b> Daily expenses add karne ke liye <b>left sidebar (Control Center)</b> ka use karein. Wahan se aap apna budget bhi change kar sakte hain!
        </div>
    """,
      unsafe_allow_html=True,
  )

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

  # --- SIDEBAR: CONTROL CENTER ---
  st.sidebar.markdown("## 🕹️ Control Center")
  st.sidebar.markdown(f"**Logged in as:** {current_user.email}")
  st.sidebar.markdown("---")

  st.sidebar.markdown("### ⚙️ Update Targets")
  new_b = st.sidebar.number_input(
      "Monthly Budget (₹)", min_value=1000, value=int(monthly_budget), step=500
  )
  new_g = st.sidebar.number_input(
      "Savings Goal (₹)", min_value=0, value=int(savings_goal), step=500
  )

  if st.sidebar.button("Update Targets in Cloud"):
    try:
      supabase.table("user_profiles").upsert({
          "user_id": current_user.id,
          "monthly_budget": new_b,
          "savings_goal": new_g,
      }).execute()
      st.sidebar.success("Updated!")
      st.rerun()
    except Exception as e:
      st.sidebar.error(f"Error: {e}")

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
          st.sidebar.success("Saved to Cloud!")
          st.rerun()
        except Exception as e:
          st.sidebar.error(f"Error saving: {e}")
      else:
        st.sidebar.error("Amount must be > 0")

  # --- MAIN BODY ---
  col_left, col_right = st.columns([1.6, 1])

  with col_left:
    st.markdown("### 📋 Your Personal Transactions")
    if not df.empty and "amount" in df:
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
          "No expenses recorded yet. Use the left sidebar to add your first"
          " spend!"
      )

  with col_right:
    st.markdown("### 📊 Spend Analytics")
    if not df.empty and "amount" in df:
      cat_summary = df.groupby("category")["amount"].sum().reset_index()
      cat_summary.columns = ["Category", "Amount (₹)"]
      st.bar_chart(cat_summary, x="Category", y="Amount (₹)", color="#4facfe")
    else:
      st.warning("Analytics will appear once you add expenses.")
