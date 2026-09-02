import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(
    page_title="MASAR | Enterprise Management Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Professional UI Styling (Times New Roman, Executive Palette, Card Layouts)
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif;
    }
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #0F2C59;
        border-bottom: 2px solid #0F2C59;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    .sub-header {
        font-size: 17px;
        color: #333333;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 15px;
        text-align: center;
    }
    .stButton>button {
        background-color: #0F2C59;
        color: white;
        font-family: 'Times New Roman', Times, serif;
        border-radius: 4px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect("masar_enterprise_v2.db")
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            username TEXT UNIQUE, 
            password TEXT, 
            role_code TEXT, 
            full_name TEXT, 
            email TEXT, 
            phone TEXT, 
            department TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            (1, 'founder_admin', 'MasarFnd2026!', 'Founder', 'Founder & Managing Director', 'founder@masar-consultancy.com', '+20 100 000 0001', 'Executive Management'),
            (2, 'ceo_user', 'MasarCEO#88', 'CEO', 'Chief Executive Officer', 'ceo@masar-consultancy.com', '+20 100 000 0002', 'Executive Management'),
            (3, 'amom_user', 'AmomOffice@2026', 'AMOM', 'Admin Manager and Office Manager', 'amom@masar-consultancy.com', '+20 100 000 0003', 'Administration'),
            (4, 'ssa_user', 'SSA_Support*99', 'SSA', 'Sales Support Advisor', 'ssa@masar-consultancy.com', '+20 100 000 0004', 'Sales & Support'),
            (5, 'gaa_user', 'GAA_Gov#55', 'GAA', 'Government Affairs Advisor', 'gaa@masar-consultancy.com', '+20 100 000 0005', 'Government Relations'),
            (6, 'sga_user', 'SGA_Acc#33', 'SGA', 'Senior General Accountant', 'sga@masar-consultancy.com', '+20 100 000 0006', 'Finance & Accounting'),
            (7, 'spm_user', 'SPM_Proj*77', 'SPM', 'Special Projects Manager', 'spm@masar-consultancy.com', '+20 100 000 0007', 'Projects')
        ]
        cursor.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", default_users)
    
    # Master Database Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_database (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            category TEXT, 
            status TEXT, 
            contact_info TEXT, 
            notes TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM master_database")
    if cursor.fetchone()[0] == 0:
        default_records = [
            ('Acme Corp', 'Client', 'Active', 'contact@acmecorp.com', 'Strategic partnership in technology'),
            ('Global Logistics', 'Vendor', 'Pending', 'info@globallogistics.com', 'Supply chain consultancy provider'),
            ('Al-Rehab Hub', 'Partner', 'Active', 'hub@rehab.com', 'Local operational development')
        ]
        cursor.executemany("INSERT INTO master_database (name, category, status, contact_info, notes) VALUES (?, ?, ?, ?, ?)", default_records)

    # Tasks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_title TEXT,
            assigned_to TEXT,
            priority TEXT,
            status TEXT,
            deadline TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role_code = ""
    st.session_state.full_name = ""

if not st.session_state.authenticated:
    st.markdown('<div class="main-header">MASAR for Consultancy and Business Development</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Executive Management & Operations Suite - Secure Authentication</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        with st.form("login_form"):
            st.markdown("### Portal Login")
            role_choice = st.selectbox("Select Role Designation", ["Founder", "CEO", "AMOM", "SSA", "GAA", "SGA", "SPM"])
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Authenticate Access")
            
            if submit_btn:
                conn = sqlite3.connect("masar_enterprise_v2.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, role_code, full_name FROM users WHERE role_code = ? AND username = ? AND password = ?", (role_choice, username_input, password_input))
                user_res = cursor.fetchone()
                conn.close()
                
                if user_res:
                    st.session_state.authenticated = True
                    st.session_state.username = user_res[0]
                    st.session_state.role_code = user_res[1]
                    st.session_state.full_name = user_res[2]
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid credentials for selected role.")
                    
    with col2:
        st.markdown("### System Credentials Reference")
        st.markdown("""
        * **Founder:** `founder_admin` | `MasarFnd2026!`
        * **CEO:** `ceo_user` | `MasarCEO#88`
        * **AMOM:** `amom_user` | `AmomOffice@2026`
        * **SSA:** `ssa_user` | `SSA_Support*99`
        * **GAA:** `gaa_user` | `GAA_Gov#55`
        * **SGA:** `sga_user` | `SGA_Acc#33`
        * **SPM:** `spm_user` | `SPM_Proj*77`
        """)
else:
    st.sidebar.markdown("### MASAR Enterprise")
    st.sidebar.markdown(f"**Executive:** {st.session_state.full_name}")
    st.sidebar.markdown(f"**Designation:** {st.session_state.role_code}")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Navigation Menu", ["Executive Dashboard", "Master Database", "Task Management", "Management Control", "Profile"])
    
    if st.sidebar.button("Terminate Session"):
        st.session_state.authenticated = False
        st.rerun()
        
    if page == "Executive Dashboard":
        st.markdown(f'<div class="main-header">Welcome, {st.session_state.full_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Overview of corporate metrics and operational standing.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_enterprise_v2.db")
        df_clients = pd.read_sql_query("SELECT * FROM master_database", conn)
        df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
        conn.close()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Database Records", value=len(df_clients))
        with col2:
            st.metric(label="Active Operations Tasks", value=len(df_tasks))
        with col3:
            st.metric(label="Security Clearance", value=st.session_state.role_code)
            
        st.markdown("---")
        st.subheader("System Activity & Quick Notice")
        st.info("The corporate suite is running under high-security encryption on Streamlit Cloud infrastructure.")

    elif page == "Master Database":
        st.markdown('<div class="main-header">Master Database Hub</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Centralized directory for clients, corporate vendors, and strategic partners.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_enterprise_v2.db")
        df = pd.read_sql_query("SELECT * FROM master_database", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)
        
        if st.session_state.role_code in ["Founder", "CEO", "AMOM"]:
            st.markdown("---")
            st.subheader("Register New Entity Record")
            with st.form("add_record_form"):
                c1, c2 = st.columns(2)
                with c1:
                    n_name = st.text_input("Entity / Organization Name")
                    n_category = st.selectbox("Category", ["Client", "Vendor", "Partner", "Government Entity"])
                with c2:
                    n_status = st.selectbox("Status", ["Active", "Pending", "Archived"])
                    n_contact = st.text_input("Contact Email / Phone")
                n_notes = st.text_area("Executive Notes & Overview")
                submitted = st.form_submit_button("Commit New Record")
                
                if submitted and n_name:
                    conn = sqlite3.connect("masar_enterprise_v2.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO master_database (name, category, status, contact_info, notes) VALUES (?, ?, ?, ?, ?)", 
                                   (n_name, n_category, n_status, n_contact, n_notes))
                    conn.commit()
                    conn.close()
                    st.success("Record successfully integrated into Master Database.")
                    st.rerun()

    elif page == "Task Management":
        st.markdown('<div class="main-header">Task & Operations Management</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Delegate, monitor, and track department deliverables.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_enterprise_v2.db")
        tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
        conn.close()
        
        if not tasks_df.empty:
            st.dataframe(tasks_df, use_container_width=True)
        else:
            st.info("No active operational tasks recorded.")
            
        st.markdown("---")
        st.subheader("Create & Delegate Task")
        with st.form("task_form"):
            t1, t2 = st.columns(2)
            with t1:
                t_title = st.text_input("Task Description / Objective")
                t_assignee = st.selectbox("Assign To Role", ["Founder", "CEO", "AMOM", "SSA", "GAA", "SGA", "SPM"])
            with t2:
                t_priority = st.selectbox("Priority Level", ["Normal", "High", "Critical"])
                t_deadline = st.text_input("Deadline Target (YYYY-MM-DD)")
            t_submit = st.form_submit_button("Authorize Task Assignment")
            
            if t_submit and t_title:
                conn = sqlite3.connect("masar_enterprise_v2.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tasks (task_title, assigned_to, priority, status, deadline) VALUES (?, ?, ?, ?, ?)",
                               (t_title, t_assignee, t_priority, "Pending", t_deadline))
                conn.commit()
                conn.close()
                st.success("Task successfully dispatched.")
                st.rerun()

    elif page == "Management Control":
        if st.session_state.role_code in ["Founder", "CEO"]:
            st.markdown('<div class="main-header">Executive Administration Control Panel</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-header">Manage corporate directory and user clearance levels.</div>', unsafe_allow_html=True)
            
            conn = sqlite3.connect("masar_enterprise_v2.db")
            users_df = pd.read_sql_query("SELECT role_code AS 'Role Code', username AS 'Username', full_name AS 'Full Name', department AS 'Department', email AS 'Email' FROM users", conn)
            conn.close()
            st.dataframe(users_df, use_container_width=True)
        else:
            st.error("Access Denied: Executive-level clearance (Founder / CEO) required for Management Control.")

    elif page == "Profile":
        st.markdown('<div class="main-header">Executive Profile Details</div>', unsafe_allow_html=True)
        st.markdown(f"**Username:** `{st.session_state.username}`")
        st.markdown(f"**Full Name:** {st.session_state.full_name}")
        st.markdown(f"**Designation / Role Code:** {st.session_state.role_code}")
        st.markdown(f"**Access Status:** Fully Authenticated & Operational")
