import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Xpense Tracker | Premium", page_icon="💎", layout="wide"
)

# Custom Premium Glassmorphism & Dark/Clean Theme Styling
st.markdown(
    """
    <style>
        .main {
            background-color: #0e1117;
        }
        .hero-title {
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #6EE7B7 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .hero-subtitle {
            color: #9CA3AF;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .stMetric {
            background-color: #1F2937;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #374151;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    '<p class="hero-title">💎 Xpense Tracker</p>', unsafe_allow_html=True
)
st.markdown(
    '<p class="hero-subtitle">The ultimate zero-friction financial companion'
    " for you and your circle.</p>",
    unsafe_allow_html=True,
)

# Initialize session state for storing expenses
if "expenses" not in st.session_state:
  st.session_state.expenses = pd.DataFrame(
      columns=["Date", "Category", "Description", "Amount (₹)", "Payment Method"]
  )

# --- SIDEBAR: CONTROL PANEL ---
st.sidebar.markdown("## ⚙️ Control Center")

# Monthly Budget Input
monthly_budget = st.sidebar.number_input(
    "Monthly Budget Limit (₹)", min_value=0.0, value=20000.0, step=1000.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Add Expense")

with st.sidebar.form("expense_form", clear_on_submit=True):
  date = st.date_input("Date")

  category_list = [
      "Food & Dining",
      "Utilities",
      "Transport",
      "Shopping",
      "Entertainment",
      "Other (Custom)",
  ]
  selected_category = st.selectbox("Category", category_list)

  custom_category = ""
  if selected_category == "Other (Custom)":
    custom_category = st.text_input("Custom Category (e.g., Bike Repair)")

  description = st.text_input("Description (optional)")
  amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
  payment_method = st.selectbox(
      "Payment Method", ["UPI", "Credit Card", "Net Banking", "Cash"]
  )

  submitted = st.form_submit_button("Record Transaction")
  if submitted:
    final_category = (
        custom_category.strip()
        if selected_category == "Other (Custom)" and custom_category.strip()
        else selected_category
    )

    if amount > 0:
      new_data = pd.DataFrame(
          {
              "Date": [str(date)],
              "Category": [final_category],
              "Description": [description],
              "Amount (₹)": [amount],
              "Payment Method": [payment_method],
          }
      )
      st.session_state.expenses = pd.concat(
          [st.session_state.expenses, new_data], ignore_index=True
      )
      st.sidebar.success("Transaction recorded!")
    else:
      st.sidebar.error("Amount must be greater than 0.")

# --- SIDEBAR: UTILITIES ---
st.sidebar.markdown("---")
with st.sidebar.expander("🧮 Quick Calculator"):
  calc_expr = st.text_input("Expression:", key="calc_box")
  if calc_expr:
    try:
      res = eval(calc_expr, {"__builtins__": None}, {})
      st.info(f"Ans: {res}")
    except:
      st.error("Invalid")

# --- MAIN DASHBOARD ---
if not st.session_state.expenses.empty:
  total_spent = st.session_state.expenses["Amount (₹)"].sum()
  remaining_budget = monthly_budget - total_spent

  # Metrics
  col1, col2, col3 = st.columns(3)
  col1.metric("Total Budget", f"₹ {monthly_budget:,.2f}")
  col2.metric("Total Spent", f"₹ {total_spent:,.2f}")
  col3.metric("Remaining", f"₹ {remaining_budget:,.2f}")

  if total_spent > monthly_budget:
    st.warning("⚠️ Budget limit exceeded! Time to cut back.")

  st.markdown("---")

  # Layout: Table & Chart
  c1, c2 = st.columns([1.5, 1])

  with c1:
    st.markdown("### 📋 Transaction History")
    st.dataframe(st.session_state.expenses, use_container_width=True)

    if st.button("🗑️ Reset All Data"):
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

  with c2:
    st.markdown("### 📊 Spend Analysis")
    cat_summary = (
        st.session_state.expenses.groupby("Category")["Amount (₹)"]
        .sum()
        .reset_index()
    )
    st.bar_chart(cat_summary, x="Category", y="Amount (₹)", color="#6EE7B7")

  # Download Report
  st.markdown("---")
  csv_data = st.session_state.expenses.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Export Financial Report (CSV)",
      data=csv_data,
      file_name="Xpense_Report.csv",
      mime="text/csv",
  )

else:
  st.info(
      "👋 Welcome to Xpense Tracker! Start adding your transactions using the"
      " sidebar control panel to unlock your dashboard."
  )