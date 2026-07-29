import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client
from PIL import Image # Profile photo upload ke liye PIL zaroori hai
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Xpense Tracker Pro", page_icon="⚡", layout="centered" # Centered layout mobile feel ke liye behtar hai
)

# --- SECURE CREDENTIALS SETUP (Replace with your correct credentials) ---
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

# --- PREMIUM STYLING (INSPIRED BY Image 4 & 6) ---
st.markdown(
    """
    <style>
        /* General App Background (Clean White) */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Headers (Black) */
        h1, h2, h3 {
            color: #121212;
            font-family: sans-serif;
        }
        
        /* Profile Upload Box (Light Beige/Gray) */
        .profile-upload {
            border: 2px dashed #E0E0E0;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            background-color: #FBF8F5; /* Waisa hi cream color */
            margin-bottom: 20px;
        }
        
        /* Input Fields (Clean White) */
        [data-testid="stTextInput"] > div > div > input {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Yellow "Next/Action" Button (INSPIRED BY YELLOW HEADER) */
        .stButton>button {
            width: 100%;
            border-radius: 30px; /* Gol button */
            font-weight: bold;
            background-color: #FFD700; /* Solid Yellow */
            color: #121212; /* Black text */
            border: none;
            padding: 12px;
            margin-top: 20px;
        }
        .stButton>button:hover {
            background-color: #E6C200; /* Thoda dark yellow hover par */
        }

        /* Tabs Styling (To match the sleek yellow/black top bar feel) */
        [data-testid="stTabs"] button {
             font-weight: bold;
             color: #666666;
        }
        [data-testid="stTabs"] button[data-baseweb="tab"]:aria-selected="true" {
            color: #FFD700; /* Active tab yellow */
            border-bottom-color: #FFD700 !important;
        }
        
    </style>
""",
    unsafe_allow_html=True,
)

if "user" not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION SCREEN (MODIFIED TO MATCH IMAGE 4) ---
if not st.session_state.user:
    
    # Spacer to push content down slightly
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Title: "What's your name?" (INSPIRED BY IMAGE 4)
    st.markdown(
        "<h1 style='text-align: center;'>What's your name?</h1>",
        unsafe_allow_html=True,
    )
    
    # Profile Photo Upload Placeholder (INSPIRED BY IMAGE 4)
    col_space, col_photo, col_space2 = st.columns([1, 2, 1])
    with col_photo:
        st.markdown('<div class="profile-upload">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file is not None:
            # Display uploaded image (circular crop would need more advanced CSS)
            image = Image.open(uploaded_file)
            st.image(image, width=150) 
        else:
             # Placeholder icon/text
            st.markdown("<br><p style='color:gray; font-size:50px;'>📷</p><p style='color:gray;'>Upload photo</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Columns for layout control
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        # Name Input (INSPIRED BY IMAGE 4)
        user_full_name = st.text_input("", placeholder="e.g., Harsh Tiwari", label_visibility="collapsed")
        
        # Login/Signup Tabs (Sleek addition to onboarding)
        sub_tab1, sub_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with sub_tab1:
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

        with sub_tab2:
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
    # --- MAIN DASHBOARD (WILL BE MODIFIED NEXT TO MATCH IMAGE 6 & 7) ---
    # For now, we'll just keep it simple and load the existing dashboard logic.
    # We will replace this whole "else" block in the next step to match the yellow header.
    
    current_user = st.session_state.user
    st.write(f"Logged in as: {current_user.email}")
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()
    
    # (The rest of your original dashboard code would go here for now)
    # st.write("Dashboard under construction to match new UI...")
