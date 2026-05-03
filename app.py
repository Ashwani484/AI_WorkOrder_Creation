import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Cadent Industrial AI Ops",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Premium Look) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    .sidebar-status {
        padding: 15px;
        border-radius: 10px;
        background-color: #f1f3f5;
        border: 1px solid #dee2e6;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Global Data Fetching ---
def fetch_history():
    try:
        response = requests.get("http://localhost:8000/v1/work-order/history", timeout=5)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        return pd.DataFrame()
    return pd.DataFrame()

df = fetch_history()

# --- Sidebar: Branding & AI System Status ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092130.png", width=80)
    st.title("Cadent AI Ops")
    st.markdown("---")
    
    # 1. AI System Status in Sidebar [Requirement 1]
    st.header("🌐 AI System Status")
    with st.container():
        st.markdown("""
            <div class="sidebar-status">
                <p>🧠 <b>Orchestrator:</b> Active ✅</p>
                <p>🔌 <b>SAP Mock:</b> Connected ✅</p>
                <p>📂 <b>Database:</b> JSON Local ✅</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("Connected Systems with AI Agent and Mock SAP S/4HANA OData simulation")

# --- Main Body Header ---
st.title("🛡️ Enterprise Work Order Control Center")
st.caption("Industrial GenAI Work Order Management System")

# --- Tabbed Interface ---
tab1, tab2, tab3 = st.tabs(["📊 WorkOrder Creation", "🛠️ Statistics", "📜 Historical Logs"])

with tab2: # Assuming Analytics is in Tab 1 based on previous updates
    st.subheader("📊 WorkOrder Analytics Insight")
    if not df.empty:
        # 1. Summary Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Tickets", len(df))
        m2.metric("Critical (High)", len(df[df['severity'] == 'high']))
        m3.metric("Medium Issues", len(df[df['severity'] == 'medium']))
        m4.metric("Minor (Low)", len(df[df['severity'] == 'low']))
        
        st.markdown("---")
        
        # 2. Refined Plotly Logic for Thin Bars & Labels
        counts = df['severity'].value_counts().reset_index()
        counts.columns = ['severity_level', 'total']
        
        fig = px.bar(
            counts, 
            x='severity_level', 
            y='total', 
            text='total',  # Adds labels to the bars
            color='severity_level',
            color_discrete_map={'high': '#d9534f', 'medium': '#f0ad4e', 'low': '#5cb85c'},
            title="Work Order Volume by Severity",
            template="plotly_white")
        
        
        # 3. Trace Updates for "Thin" Look and Label Positioning
        fig.update_traces(
            width=0.3,  # Adjusts bar thickness (0.1 to 1.0)[cite: 5]
            textposition='outside',  # Places labels above the bars
            textfont_size=12,
            cliponaxis=False  # Ensures labels aren't cut off at the top
        )
        
        # 4. Layout Polish
        fig.update_layout(
            xaxis_title="Severity Category",
            yaxis_title="Total Work Orders",
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to display statistics.")

with tab1:
    st.subheader("✍️ Create New Work Order")
    # Creation Section
    user_query = st.text_area(
        "Describe the issue (e.g., LAN issue at ODC-9, Priority-2, location-India):",
        height=150,
        placeholder="Type your infrastructure or IT problem here..."
    )
    
    if st.button("🚀 Create Work Order"):
        if user_query:
            with st.spinner("Agent interpreting query & calling SAP..."):
                response = requests.post(
                    "http://localhost:8000/v1/work-order/create",
                    json={"query": user_query}
                )
                if response.status_code == 200:
                    
                    st.markdown(response.json()['response']) # Shows ID, Status, Category[cite: 3, 4]
                else:
                    st.error("Submission failed. Check backend connectivity.")
        else:
            st.warning("Please enter a query before processing.")

    st.markdown("---")

    # 2. Global Search below text box [Requirement 2]
    st.subheader("🔍 Historical Search WrokOrder")
    search_col_1, search_col_2 = st.columns([4, 1])
    
    with search_col_1:
        search_id = st.text_input("Enter Work Order ID to view historical schema data:", placeholder="e.g. WO1234")
    
    with search_col_2:
        st.write("##") # Spacer
        view_button = st.button("👁️ View Record")

    if view_button and search_id:
        with st.spinner("Fetching historical data..."):
            res = requests.get(f"http://localhost:8000/v1/work-order/{search_id}")
            if res.status_code == 200:
            
                # Display historical workorder with schema[cite: 5]
                data=res.json()
                st.success(f"Historical Record Found: {data.get('order_id')}")
                
                # Create a structured card view using container and columns
                with st.container():
                    st.markdown("### 📄 Work Order Details")
                    
                    # Row 1: Primary Identifiers
                    
                    st.markdown(f"**Intent:**\n{data.get('intent')}")
                    st.markdown(f"**System Status:**\n`{data.get('sap_status')}`")
                    st.markdown(f"**Problem Area:**\n{data.get('problem_area')}")
                    
                
                    # Apply color coding to severity
                    sev = data.get('severity', '').lower()
                    color = "#d9534f" if sev == "high" else "#f0ad4e" if sev == "medium" else "#5cb85c"
                    
                    st.markdown(f"**Severity:** <span style='color:; font-weight:bold;'>{sev.upper()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Location ID:**\n{data.get('Location id')}")
                    
                    
                    # Row 3: Full Summary
                    st.markdown(f"**Issue Summary:**")
                    st.info(data.get('summary'))
            else:
                st.error(f"Work Order ID '{search_id}' not found in archive[cite: 5].")

with tab3:
    st.subheader("Historical Audit Trail")
    if not df.empty:
        # Refresh and Export[cite: 5]
        col_ref, col_dl = st.columns([6, 1])
        if col_ref.button("🔄 Refresh Logs"):
            st.rerun()
        
        csv = df.to_csv(index=False).encode('utf-8')
        col_dl.download_button("📥 Export CSV", data=csv, file_name="cadent_audit.csv", mime='text/csv')
        
        # Display Audit Log with new schema fields[cite: 2]
        cols_to_show = ["order_id", "sap_status", "problem_area", "severity", "Location id", "summary"]
        available_cols = [c for c in cols_to_show if c in df.columns]
        st.dataframe(df[available_cols], width='stretch', hide_index=True)
    else:
        st.warning("Historical database is currently empty.")
