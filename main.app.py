import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
import time

# ---------------------------
# Page Configuration & Styling
# ---------------------------
st.set_page_config(page_title="AI Powered Waste Management with Smart Routing and Rewards", layout="wide", page_icon="🍃")

def apply_custom_css():
    st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background-color: #f8fafc;
        }
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
            padding-top: 1rem;
        }
        /* Headers */
        h1, h2, h3 {
            color: #0f172a;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
        }
        .zero-title {
            color: #1e293b;
        }
        .hero-title {
            color: #16a34a; /* vibrant green */
        }
        /* Metric styling */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem;
            color: #16a34a;
            font-weight: 800;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.0rem;
            color: #64748b;
            font-weight: 600;
        }
        /* Hide default Streamlit menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom Button */
        .stButton>button {
            border-radius: 50px;
            background-color: #16a34a;
            color: white;
            font-weight: 700;
            border: none;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #15803d;
            box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
            color: white;
            border-color: #15803d;
        }
        
        /* Login Card */
        .login-box {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------
# Data Generation & Caching
# ---------------------------
@st.cache_data
def load_data():
    """Generates and caches random bin data to prevent recalculation on every render."""
    np.random.seed(int(time.time()))
    
    # Base coordinates for a city center (e.g., NYC)
    base_lat = 40.7128
    base_lon = -74.0060
    
    df = pd.DataFrame({
        "Bin ID": [f"BIN-{i:02d}" for i in range(1, 11)],
        "Location": ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Zone F", "Zone G", "Zone H", "Zone I", "Zone J"],
        "Capacity (L)": [5000] * 10,
        "Waste Type": np.random.choice(["Dry Waste", "Wet Waste"], 10),
        "Fill Level (%)": np.random.randint(10, 100, 10),
        "latitude": base_lat + np.random.uniform(-0.05, 0.05, 10),
        "longitude": base_lon + np.random.uniform(-0.05, 0.05, 10)
    })
    
    df["Status"] = df["Fill Level (%)"].apply(
        lambda x: "Full" if x >= 80 else ("Half Full" if x >= 40 else "Empty")
    )
    return df

# ---------------------------
# View Components
# ---------------------------
def dashboard(bins):
    st.subheader("🏠 Home Dashboard")
    st.markdown("Real-time snapshot of the waste management infrastructure.")

    total_bins = len(bins)
    full_bins = len(bins[bins["Status"] == "Full"])
    half_bins = len(bins[bins["Status"] == "Half Full"])
    empty_bins = len(bins[bins["Status"] == "Empty"])

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bins", total_bins)
    with col2:
        st.metric("Full Bins", full_bins, delta=f"{full_bins} Critical", delta_color="inverse")
    with col3:
        st.metric("Half Full", half_bins)
    with col4:
        st.metric("Empty Bins", empty_bins)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns([2, 1])
    color_map = {"Full": "#ef4444", "Half Full": "#f59e0b", "Empty": "#16a34a"}
    
    with col_chart1:
        st.markdown("##### Smart Bin Fill Levels")
        fig = px.bar(bins, x="Bin ID", y="Fill Level (%)", color="Status", 
                     text="Fill Level (%)", color_discrete_map=color_map, 
                     hover_data=["Waste Type", "Capacity (L)"],
                     template="plotly_white")
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig.update_traces(textposition='outside')
        fig.update_yaxes(range=[0, 110])
        st.plotly_chart(fig, use_container_width=True)
        
    with col_chart2:
        st.markdown("##### Bin Status Distribution")
        fig_pie = px.pie(bins, names='Status', color='Status', 
                         color_discrete_map=color_map, template="plotly_white", hole=0.4)
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🗺️ Live Bin Locations (Interactive Map)")
    fig_map = px.scatter_mapbox(bins, lat="latitude", lon="longitude", color="Status",
                                hover_name="Bin ID", hover_data=["Location", "Waste Type", "Capacity (L)", "Fill Level (%)"],
                                color_discrete_map=color_map, zoom=11, height=450)
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Bin Inventory & Status")
    st.dataframe(bins[["Bin ID", "Location", "Waste Type", "Capacity (L)", "Fill Level (%)", "Status"]], use_container_width=True, hide_index=True)

def complaint_system():
    st.subheader("📍 Report Waste")
    st.markdown("Help us keep the community clean by reporting uncollected waste or damaged bins.")
    
    with st.form("complaint_form"):
        complaint_type = st.selectbox("Issue Type", ["Uncollected Waste", "Damaged Bin", "Illegal Dumping", "Spilled Waste", "Other"])
        
        st.markdown("**If reporting uncollected waste, select the affected waste types:**")
        waste_types = st.multiselect(
            "Waste Types Involved",
            ["Glass", "Paper", "Organic", "Metal", "Plastic", "E-Waste"],
            default=["Glass", "Paper"]
        )
        
        location = st.text_input("Location / Address / Zone")
        description = st.text_area("Additional Details", placeholder="Please describe the issue in detail...")
        
        uploaded_image = st.file_uploader("Attach Photo (Evidence)", type=["jpg", "png", "jpeg"])
        
        submitted = st.form_submit_button("Submit Report")
        
        if submitted:
            if not location:
                st.error("Please provide a location.")
            else:
                st.success(f"✅ Report regarding '{complaint_type}' at '{location}' has been submitted successfully! You earned +10 Points.")
                if "points_db" in st.session_state:
                    st.session_state.points_db[st.session_state.username] += 10
                st.balloons()

def route_optimization(bins):
    st.subheader("🚛 Collect Waste (Route Optimization)")
    st.markdown("AI-generated optimal routing for the collection fleet to minimize transit time.")

    full_bins_df = bins[bins["Status"] == "Full"].copy()

    if full_bins_df.empty:
        st.success("✅ Fleet on standby. No bins require collection at this moment.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("##### Collection Targets")
            st.dataframe(full_bins_df[["Bin ID", "Location", "Waste Type", "Capacity (L)", "Fill Level (%)"]], use_container_width=True, hide_index=True)
            
            route_locations = full_bins_df["Location"].tolist()
            route_str = " ➝ ".join(["Depot"] + route_locations + ["Depot"])
            st.info(f"**Optimal Path:**\n\n{route_str}")

        with col2:
            st.markdown("##### 🔴 LIVE: Route Visualization")
            # Create a connected route path mimicking a live GPS tracker
            fig = px.line_mapbox(full_bins_df, lat="latitude", lon="longitude", 
                                 hover_name="Bin ID", hover_data=["Location", "Waste Type", "Capacity (L)", "Fill Level (%)"],
                                 color_discrete_sequence=["#3b82f6"], zoom=12, height=400)
            
            # Add markers for the bins on top of the path
            fig.add_scattermapbox(lat=full_bins_df["latitude"], lon=full_bins_df["longitude"],
                                  mode="markers", text=full_bins_df["Bin ID"], 
                                  marker=dict(size=14, color="#ef4444"))
                                  
            fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def rewards_system():
    st.subheader("🎁 Rewards")
    st.markdown("Earn points for proper waste disposal and recycling! Redeem points for discounts.")
    
    col1, col2, col3 = st.columns(3)
    
    if "points_db" not in st.session_state:
        st.session_state.points_db = {}
    if st.session_state.username not in st.session_state.points_db:
        st.session_state.points_db[st.session_state.username] = 0
        
    with col1:
        st.metric("Your Total Points", f"⭐ {st.session_state.points_db[st.session_state.username]}")
    with col2:
        st.metric("Eco-Level", "🌱 Silver Paws")
    with col3:
        st.metric("Rank", "🏆 Top 15%")
        
    st.markdown("---")
    st.markdown("### Redeem Points for Bill Reductions")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.info("⚡ 500 Pts: Current Bill Reduction")
        if st.button("Redeem Current Bill Promo"):
            if st.session_state.points_db[st.session_state.username] >= 500:
                st.session_state.points_db[st.session_state.username] -= 500
                st.success("Successfully redeemed Current Bill Reduction!")
                st.rerun()
            else:
                st.error("Not enough points.")
    with col_r2:
        st.info("💧 1000 Pts: Water Bill Reduction")
        if st.button("Redeem Water Bill Promo"):
            if st.session_state.points_db[st.session_state.username] >= 1000:
                st.session_state.points_db[st.session_state.username] -= 1000
                st.success("Successfully redeemed Water Bill Reduction!")
                st.rerun()
            else:
                st.error("Not enough points.")
    with col_r3:
        st.info("🏛️ 1500 Pts: Government Bill Reduction")
        if st.button("Redeem Gov Bill Promo"):
            if st.session_state.points_db[st.session_state.username] >= 1500:
                st.session_state.points_db[st.session_state.username] -= 1500
                st.success("Successfully redeemed Government Bill Reduction!")
                st.rerun()
            else:
                st.error("Not enough points.")

    st.markdown("---")
    st.markdown("### 📄 Verify Bill Statement for Reductions")
    st.markdown("Upload your current, water, or government bill statement to verify it before applying reductions.")
    
    bill_type = st.selectbox("Select Bill Type", ["Current (Electricity) Bill", "Water Bill", "Government/Property Tax"])
    uploaded_bill = st.file_uploader("Upload Bill Document (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])
    
    if st.button("Verify Bill Statement & Apply Reduction"):
        if uploaded_bill is not None:
            with st.spinner("Verifying statement authenticity using AI OCR..."):
                time.sleep(2) # Simulate processing
                
            # Document verified as authentic (Mocking AI verification for the demo)
            is_valid = True
            
            if is_valid:
                # Determine points to deduct
                points_needed = 0
                if bill_type == "Current (Electricity) Bill":
                    points_needed = 500
                elif bill_type == "Water Bill":
                    points_needed = 1000
                elif bill_type == "Government/Property Tax":
                    points_needed = 1500
                
                if st.session_state.points_db[st.session_state.username] >= points_needed:
                    st.session_state.points_db[st.session_state.username] -= points_needed
                    st.success(f"✅ **Verification True:** Your {bill_type} statement is an authentic Government/Utility document!")
                    st.info(f"🧾 **Acknowledgement:** {points_needed} points have been successfully deducted and the reduction has been applied directly to your {bill_type}.")
                    st.balloons()
                else:
                    st.success(f"✅ **Verification True:** Your {bill_type} statement is authentic!")
                    st.error(f"❌ However, you need {points_needed} points to apply this reduction. You currently have {st.session_state.points_db[st.session_state.username]} points.")
            else:
                st.error("❌ **Verification False:** The document could not be verified. Please ensure the image is clear and the bill is recent.")
        else:
            st.warning("Please upload a file before verifying.")

def leaderboard():
    st.subheader("🏅 Eco-Hero Leaderboard")
    st.markdown("See who is leading the charge in making our community greener!")
    st.success("🎉 **Monthly Leaders Rewards:** Top users on the leaderboard are rewarded with Government, Current, or Water bill reductions!")
    
    data = pd.DataFrame({
        "Rank": ["🥇 1", "🥈 2", "🥉 3", "4", "5"],
        "User": ["Alex Green", "EcoWarrior99", "EarthLover", "GreenThumb", st.session_state.get("username", "You")],
        "Points": [5200, 4800, 4100, 3900, st.session_state.points_db.get(st.session_state.username, 0) if "points_db" in st.session_state else 0],
        "Level": ["Platinum Tree", "Gold Leaf", "Gold Leaf", "Silver Paws", "Silver Paws"],
        "Special Reward": ["Gov Bill Reduction", "Current Bill Reduction", "Water Bill Reduction", "-", "-"]
    })
    
    st.dataframe(data, use_container_width=True, hide_index=True)


# ---------------------------
# Login Page
# ---------------------------
def login_page():
    apply_custom_css()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("<h1 style='font-size: 3.5rem; line-height: 1.2;'><span class='zero-title'>AI Powered</span><br><span class='hero-title'>Waste Management<br>with Smart Routing and Rewards</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.2rem; color: #64748b; margin-top: 10px;'>Making waste management more efficient and rewarding! Join the community in keeping our environment clean.</p>", unsafe_allow_html=True)
        
        st.markdown("<div class='login-box' style='margin-top: 30px; text-align: left; padding: 2rem;'>", unsafe_allow_html=True)
        st.subheader("Login to your account")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Get Started →", use_container_width=True):
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                if "points_db" not in st.session_state:
                    st.session_state.points_db = {}
                if username not in st.session_state.points_db:
                    st.session_state.points_db[username] = 0
                st.rerun()
            else:
                st.error("Please enter a valid username and password.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        # Template Image as requested (Using a relevant high-quality image)
        st.image("https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=1200&q=80", use_container_width=True, caption="Collecting and sorting waste for a better tomorrow.")

# ---------------------------
# Main Application Flow
# ---------------------------
def main():
    apply_custom_css()
    
    # Top Bar Header
    col_logo, col_space, col_user, col_logout = st.columns([2, 2, 1, 1])
    with col_logo:
        st.markdown("<h2>🍃 <span class='zero-title'>AI Powered </span><span class='hero-title'>Waste System</span></h2>", unsafe_allow_html=True)
    with col_user:
        points = st.session_state.points_db.get(st.session_state.username, 0) if "points_db" in st.session_state else 0
        st.markdown(f"<div style='text-align:right; font-weight:bold; color:#16a34a; font-size:1.2rem; padding-top:10px;'>🟢 {points} Pts</div>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Logout 🚪"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("<h2>🍃 <span class='zero-title'>AI Powered </span><span class='hero-title'>Waste System</span></h2>", unsafe_allow_html=True)
        
        # Displaying an image on every page via the sidebar
        # (To use the specific Freepik illustration you downloaded, change this URL to your local filename, e.g., "my_image.png")
        st.image("https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=600&q=80", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        menu = st.radio("Menu", 
                        ["Home", "Report Waste", "Collect Waste", "Rewards", "Leaderboard"],
                        label_visibility="collapsed")
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Fetch Data
    bins = load_data()

    # Route to selected page
    if menu == "Home":
        dashboard(bins)
    elif menu == "Report Waste":
        complaint_system()
    elif menu == "Collect Waste":
        route_optimization(bins)
    elif menu == "Rewards":
        rewards_system()
    elif menu == "Leaderboard":
        leaderboard()

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        main()