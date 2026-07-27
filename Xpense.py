import sqlite3
import time
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Xpense Tracker Pro", page_icon="⚡", layout="wide"
)

# --- DATABASE SETUP (Permanent Local Storage) ---
def init_db():
  conn = sqlite3.connect("xpense_data.db", check_same_thread=False)
  cursor = conn.cursor()
  # Expenses Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount INTEGER,
            payment_method TEXT
        )
    """)
  # User Config Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
  conn.commit()
  return conn, cursor

conn, cursor = init_db()

# --- PREMIUM STYLING ---
st.markdown(
    """
    <style>
        .main { background-color: #0b0f19; color: #ffffff; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: black; border: none; }
        .stButton>button:hover { opacity: 0.9; }
        .splash-title { font-size: 50px; font-weight: 900; background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-top: 20vh; }
        .splash-sub { text-align: center; color: #9CA3AF; font-size: 18px; }
    </style>
""",
    unsafe_allow_html=True,
)

# Check if setup exists in DB
cursor.execute("SELECT value FROM config WHERE key='initialized'")
row = cursor.fetchone()
is_initialized = True if row and row[0] == "True" else False

if "splash_done" not in st.session_state:
  st.session_state.splash_done = False

if "custom_categories" not in st.session_state:
  st.session_state.custom_categories = [
      "Food & Dining",
      "Study / Education",
      "Transport",
      "Entertainment",
      "Utilities",
      "Shopping",
  ]

# --- 1. SPLASH SCREEN (2 SECONDS) ---
if not st.session_state.splash_done:
  placeholder = st.empty()
  with placeholder.container():
    st.markdown(
        '<p class="splash-title">⚡ Xpense Tracker</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="splash-sub">Initializing your persistent financial database...</p>',
        unsafe_allow_html=True,
    )
    time.sleep(2.0)
  st.session_state.splash_done = True
  st.rerun()

# --- 2. ONBOARDING SETUP WIZARD ---
if not is_initialized:
  st.markdown(
      "<h2 style='text-align: center;'>🎯 Welcome to Your Personal Finance"
      " Setup</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: gray;'>Let's personalize your"
      " experience. Your settings will be permanently saved.</p>",
      unsafe_allow_html=True,
  )

  with st.form("onboarding_form"):
    st.subheader("1. Monthly Budget & Savings Goal")
    monthly_budget = st.number_input(
        "What is your total monthly budget? (₹)",
        min_value=1000,
        value=25000,
        step=500,
        format="%d",
    )

    submit_setup = st.form_submit_button("Launch Dashboard 🚀")
    if submit_setup:
      cursor.execute(
          "INSERT OR REPLACE INTO config (key, value) VALUES ('initialized',"
          " 'True')"
      )
      cursor.execute(
          "INSERT OR REPLACE INTO config (key, value) VALUES ('budget', ?)",
          (str(int(monthly_budget)),),
      )
      conn.commit()
      st.rerun()

else:
  # Fetch budget from DB
  cursor.execute("SELECT value FROM config WHERE key='budget'")
  b_row = cursor.fetchone()
  monthly_budget = int(b_row[0]) if b_row else 25000

  # --- 3. MAIN DASHBOARD INTERFACE ---
  col_h1, col_h2 = st.columns([3, 1])
  with col_h1:
    st.markdown(
        "<h1>⚡ Xpense Tracker <span style='font-size:16px; color:#4facfe;'>(Pro"
        " + Persistent)</span></h1>",
        unsafe_allow_html=True,
    )
  with col_h2:
    if st.button("🔄 Reset Setup / Budget"):
      cursor.execute("DELETE FROM config")
      conn.commit()
      st.rerun()

  # Fetch expenses from database into Pandas DataFrame
  expenses_df = pd.read_sql_query(
      "SELECT date, category, description, amount, payment_method FROM expenses",
      conn,
  )

  if not expenses_df.empty:
    total_spent = int(expenses_df["amount"].sum())
  else:
    total_spent = 0

  remaining_budget = monthly_budget - total_spent
  estimated_saved = monthly_budget - total_spent

  # Metrics Row
  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Total Budget", f"₹ {monthly_budget:,}")
  m2.metric("Total Spent", f"₹ {total_spent:,}")
  m3.metric("Remaining", f"₹ {remaining_budget:,}")
  m4.metric("Est. Savings Streak", f"₹ {max(0, estimated_saved):,}")

  st.markdown("---")

  # --- SIDEBAR: TRANSACTION LOGGER & CALCULATOR ---
  st.sidebar.markdown("## 🕹️ Control Center")

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
    amount = st.number_input(
        "Amount (₹)", min_value=0, value=100, step=10, format="%d"
    )
    payment_method = st.selectbox(
        "Payment Mode", ["UPI", "Credit Card", "Net Banking", "Cash"]
    )

    submitted = st.form_submit_button("Record Spend")
    if submitted:
      if amount > 0:
        cursor.execute(
            """
                    INSERT INTO expenses (date, category, description, amount, payment_method)
                    VALUES (?, ?, ?, ?, ?)
                """,
            (
                str(date),
                category,
                description,
                int(amount),
                payment_method,
            ),
        )
        conn.commit()
        st.sidebar.success("Recorded and Saved Permanently!")
        st.rerun()
      else:
        st.sidebar.error("Amount must be > 0")

  st.sidebar.markdown("---")
  st.sidebar.markdown("### 🧮 Quick Calculator")
  calc_input = st.sidebar.text_input(
      "Calculate expression:", placeholder="e.g. 450 + 200"
  )
  if calc_input:
    try:
      res = int(eval(calc_input, {"__builtins__": None}, {}))
      st.sidebar.info(f"Result: {res}")
    except:
      st.sidebar.error("Invalid expression")

  # --- MAIN BODY LAYOUT ---
  col_left, col_right = st.columns([1.6, 1])

  with col_left:
    st.markdown("### 📋 Recent Transactions (Saved)")
    if not expenses_df.empty:
      # Rename columns for clean UI view
      display_df = expenses_df.rename(
          columns={
              "date": "Date",
              "category": "Category",
              "description": "Description",
              "amount": "Amount (₹)",
              "payment_method": "Payment Method",
          }
      )
      st.dataframe(display_df, use_container_width=True)

      if st.button("🗑️ Clear All Transactions"):
        cursor.execute("DELETE FROM expenses")
        conn.commit()
        st.rerun()
    else:
      st.info(
          "No transactions recorded yet. Data entered here will persist across"
          " refreshes!"
      )

  with col_right:
    st.markdown("### 📊 Spend Analytics")
    if not expenses_df.empty:
      cat_summary = (
          expenses_df.groupby("category")["amount"].sum().reset_index()
      )
      cat_summary.columns = ["Category", "Amount (₹)"]
      st.bar_chart(cat_summary, x="Category", y="Amount (₹)", color="#4facfe")
    else:
      st.warning("Analytics will appear once you add expenses.")

  st.markdown("---")
  if not expenses_df.empty:
    csv_data = expenses_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Financial Report (CSV)",
        data=csv_data,
        file_name="Xpense_Tracker_Persistent_Report.csv",
        mime="text/csv",
    )
