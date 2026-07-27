import time
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Xpense Tracker Pro", page_icon="⚡", layout="wide"
)

# --- PREMIUM STYLING ---
st.markdown(
    """
    <style>
        .main { background-color: #0b0f19; color: #ffffff; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: black; border: none; }
        .stButton>button:hover { opacity: 0.9; }
        .splash-title { font-size: 50px; font-weight: 900; background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-top: 20vh; }
        .splash-sub { text-align: center; color: #9CA3AF; font-size: 18px; }
        .metric-card { background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1F2937; text-align: center; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SESSION STATE INITIALIZATION ---
if "initialized" not in st.session_state:
  st.session_state.initialized = False
if "splash_done" not in st.session_state:
  st.session_state.splash_done = False
if "expenses" not in st.session_state:
  st.session_state.expenses = pd.DataFrame(
      columns=["Date", "Category", "Description", "Amount (₹)", "Payment Method"]
  )
if "custom_categories" not in st.session_state:
  st.session_state.custom_categories = [
      "Food & Dining",
      "Study / Education",
      "Transport",
      "Entertainment",
      "Utilities",
      "Shopping",
  ]
if "user_config" not in st.session_state:
  st.session_state.user_config = {}

# --- 1. SPLASH SCREEN (2 SECONDS) ---
if not st.session_state.splash_done:
  placeholder = st.empty()
  with placeholder.container():
    st.markdown(
        '<p class="splash-title">⚡ Xpense Tracker</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="splash-sub">Initializing your smart financial ecosystem...</p>',
        unsafe_allow_html=True,
    )
    time.sleep(2.0)
  st.session_state.splash_done = True
  st.rerun()

# --- 2. ONBOARDING SETUP WIZARD (If not set up) ---
if not st.session_state.initialized:
  st.markdown(
      "<h2 style='text-align: center;'>🎯 Welcome to Your Personal Finance"
      " Setup</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: gray;'>Let's personalize your"
      " experience based on your habits.</p>",
      unsafe_allow_html=True,
  )

  with st.form("onboarding_form"):
    st.subheader("1. Monthly Budget & Savings Goal")
    monthly_budget = st.number_input(
        "What is your total monthly budget? (₹)",
        min_value=1000.0,
        value=25000.0,
        step=500.0,
    )
    target_savings = st.number_input(
        "How much do you aim to save this month? (₹)",
        min_value=0.0,
        value=5000.0,
        step=500.0,
    )

    st.subheader("2. Estimated Habit Breakdown (Where does your money go?)")
    col1, col2 = st.columns(2)
    with col1:
      est_food = st.number_input("Food & Dining (₹)", value=5000.0, step=100.0)
      est_study = st.number_input("Study / Education (₹)", value=2000.0, step=100.0)
    with col2:
      est_transport = st.number_input("Transport (₹)", value=1500.0, step=100.0)
      est_entertainment = st.number_input("Entertainment (₹)", value=2000.0, step=100.0)

    submit_setup = st.form_submit_button("Launch Dashboard 🚀")
    if submit_setup:
      st.session_state.user_config = {
          "budget": monthly_budget,
          "target_savings": target_savings,
          "est_food": est_food,
          "est_study": est_study,
          "est_transport": est_transport,
          "est_entertainment": est_entertainment,
      }
      st.session_state.initialized = True
      st.rerun()

else:
  # --- 3. MAIN DASHBOARD INTERFACE ---
  config = st.session_state.user_config
  monthly_budget = config.get("budget", 25000.0)
  target_savings = config.get("target_savings", 5000.0)

  # Top Branding Header
  col_h1, col_h2 = st.columns([3, 1])
  with col_h1:
    st.markdown(
        "<h1>⚡ Xpense Tracker <span style='font-size:16px; color:#4facfe;'>(Pro"
        " Edition)</span></h1>",
        unsafe_allow_html=True,
    )
  with col_h2:
    if st.button("🔄 Reset Setup / Budget"):
      st.session_state.initialized = False
      st.rerun()

  # Calculate metrics
  if not st.session_state.expenses.empty:
    total_spent = st.session_state.expenses["Amount (₹)"].sum()
  else:
    total_spent = 0.0

  remaining_budget = monthly_budget - total_spent
  estimated_saved = monthly_budget - total_spent  # Simplified calculation

  # Metrics Row
  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Total Budget", f"₹ {monthly_budget:,.2f}")
  m2.metric("Total Spent", f"₹ {total_spent:,.2f}")
  m3.metric("Remaining", f"₹ {remaining_budget:,.2f}")
  m4.metric("Est. Savings Streak", f"₹ {max(0, estimated_saved):,.2f}")

  st.markdown("---")

  # --- SIDEBAR: TRANSACTION LOGGER & CALCULATOR & CATEGORY BUILDER ---
  st.sidebar.markdown("## 🕹️ Control Center")

  # Popup / Section to Add Custom Category dynamically
  with st.sidebar.expander("🛠️ Manage Custom Categories"):
    new_cat_input = st.text_input("Add new category (e.g., Bike Repair)")
    if st.button("Add Category"):
      if (
          new_cat_input
          and new_cat_input not in st.session_state.custom_categories
      ):
        st.session_state.custom_categories.append(new_cat_input)
        st.success(f"Added '{new_cat_input}' successfully!")
        st.rerun()

  st.sidebar.markdown("### ➕ Log New Expense")
  with st.sidebar.form("expense_logger", clear_on_submit=True):
    date = st.date_input("Date")
    category = st.selectbox("Category", st.session_state.custom_categories)
    description = st.text_input("Description / Notes")
    amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
    payment_method = st.selectbox(
        "Payment Mode", ["UPI", "Credit Card", "Net Banking", "Cash"]
    )

    submitted = st.form_submit_button("Record Spend")
    if submitted:
      if amount > 0:
        new_row = pd.DataFrame({
            "Date": [str(date)],
            "Category": [category],
            "Description": [description],
            "Amount (₹)": [amount],
            "Payment Method": [payment_method],
        })
        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, new_row], ignore_index=True
        )
        st.sidebar.success("Recorded!")
        st.rerun()
      else:
        st.sidebar.error("Amount must be > 0")

  # Quick Calculator inside Sidebar
  st.sidebar.markdown("---")
  st.sidebar.markdown("### 🧮 Quick Calculator")
  calc_input = st.sidebar.text_input(
      "Calculate expression:", placeholder="e.g. 450 + 200"
  )
  if calc_input:
    try:
      res = eval(calc_input, {"__builtins__": None}, {})
      st.sidebar.info(f"Result: {res}")
    except:
      st.sidebar.error("Invalid expression")

  # --- MAIN BODY LAYOUT ---
  col_left, col_right = st.columns([1.6, 1])

  with col_left:
    st.markdown("### 📋 Recent Transactions")
    if not st.session_state.expenses.empty:
      st.dataframe(st.session_state.expenses, use_container_width=True)
      if st.button("🗑️ Clear All Transactions"):
        st.session_state.expenses = pd.DataFrame(
            columns=[
                "Date",
                "Category",
                "Description",
                "Amount (₹)",
                "Payment Method",
            ]
        )
        st.rerun()
    else:
      st.info(
          "No transactions recorded yet. Use the sidebar to log your first"
          " spend!"
      )

  with col_right:
    st.markdown("### 📊 Spend Analytics")
    if not st.session_state.expenses.empty:
      cat_summary = (
          st.session_state.expenses.groupby("Category")["Amount (₹)"]
          .sum()
          .reset_index()
      )
      st.bar_chart(cat_summary, x="Category", y="Amount (₹)", color="#4facfe")
    else:
      st.warning("Analytics will appear once you add expenses.")

  # Export Data Report
  st.markdown("---")
  if not st.session_state.expenses.empty:
    csv_data = st.session_state.expenses.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Financial Report (CSV)",
        data=csv_data,
        file_name="Xpense_Tracker_Pro_Report.csv",
        mime="text/csv",
    )
