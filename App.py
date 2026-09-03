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
        padding-bottom: 6px;
        margin-bottom: 15px;
    }
    .sub-header {
        font-size: 16px;
        color: #555555;
        margin-bottom: 20px;
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
    conn = sqlite3.connect("masar_comprehensive_v5.db")
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
    
    # CRM Deals & Clients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            deal_title TEXT,
            status TEXT,
            deal_value REAL,
            last_contact_date TEXT,
            notes TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM crm_deals")
    if cursor.fetchone()[0] == 0:
        default_deals = [
            ('Acme Corp', 'Enterprise Tech Expansion', 'Open', 150000.0, '2026-08-10', 'Awaiting final board approval on contract terms.'),
            ('Global Logistics', 'Supply Chain Consulting', 'Pending', 85000.0, '2026-06-15', 'Initial meetings concluded. Follow-up required.'),
            ('Al-Rehab Hub', 'Local Operations Upgrade', 'Closed-Won', 200000.0, '2026-09-01', 'Contract successfully executed and implemented.')
        ]
        cursor.executemany("INSERT INTO crm_deals (client_name, deal_title, status, deal_value, last_contact_date, notes) VALUES (?, ?, ?, ?, ?, ?)", default_deals)

    # Master Uploaded Database Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_master_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_name TEXT,
            category TEXT,
            details TEXT,
            entry_date TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM uploaded_master_db")
    if cursor.fetchone()[0] == 0:
        default_master = [
            ('Strategic Partner Alpha', 'Partnership', 'Primary regional coordinator', '2026-01-10'),
            ('Government Liaison Unit', 'Government', 'Compliance and licensing division', '2026-02-15')
        ]
        cursor.executemany("INSERT INTO uploaded_master_db (record_name, category, details, entry_date) VALUES (?, ?, ?, ?)", default_master)

    # Accounting Ledger (SGA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounting_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT,
            description TEXT,
            category TEXT,
            amount REAL,
            entry_type TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM accounting_ledger")
    if cursor.fetchone()[0] == 0:
        default_ledger = [
            ('2026-09-01', 'Initial Advisory Retainer - Acme Corp', 'Revenue', 50000.0, 'Credit'),
            ('2026-09-02', 'Software Subscriptions & Cloud Infra', 'Expense', 12000.0, 'Debit')
        ]
        cursor.executemany("INSERT INTO accounting_ledger (transaction_date, description, category, amount, entry_type) VALUES (?, ?, ?, ?, ?)", default_ledger)

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
    st.markdown('<div class="sub-header">Enterprise Management Suite - Secure Authentication Portal</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        with st.form("login_form"):
            st.markdown("### Executive Login")
            role_choice = st.selectbox("Select Role Designation", ["Founder", "CEO", "AMOM", "SSA", "GAA", "SGA", "SPM"])
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Authenticate Access")
            
            if submit_btn:
                conn = sqlite3.connect("masar_comprehensive_v5.db")
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
                    st.error("Authentication Failed: Incorrect username, password, or role match.")
                    
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
    cairo_tz = pytz.timezone('Africa/Cairo')
    current_time = datetime.now(cairo_tz)
    
    st.sidebar.markdown("### MASAR ENTERPRISE")
    st.sidebar.markdown("**Consultancy & Business Development**")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Date:** {current_time.strftime('%Y-%m-%d')}")
    st.sidebar.markdown(f"**Time:** {current_time.strftime('%H:%M:%S')} (EET)")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Executive:** {st.session_state.full_name}")
    st.sidebar.markdown(f"**Clearance:** {st.session_state.role_code}")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Navigation Menu", ["Executive Dashboard", "CRM & Deal Pipeline", "Master Database & File Uploader", "Accounting Ledger (SGA)", "Task Management", "Smart Assistant", "Management Control", "Profile"])
    
    if st.sidebar.button("Sign Out"):
        st.session_state.authenticated = False
        st.rerun()
        
    if page == "Executive Dashboard":
        st.markdown(f'<div class="main-header">Executive Dashboard - {st.session_state.full_name}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Real-time enterprise metrics, active workflows, and corporate indicators.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_comprehensive_v5.db")
        df_crm = pd.read_sql_query("SELECT * FROM crm_deals", conn)
        df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
        df_ledger = pd.read_sql_query("SELECT * FROM accounting_ledger", conn)
        conn.close()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="Active CRM Deals", value=len(df_crm))
        with c2:
            st.metric(label="Pending Operations Tasks", value=len(df_tasks))
        with c3:
            total_rev = df_ledger[df_ledger['entry_type'] == 'Credit']['amount'].sum()
            st.metric(label="Total Recorded Revenues", value=f"{total_rev:,.2f} EGP")
            
        st.markdown("---")
        st.subheader("Periodic Summary & System Status")
        st.success("All systems operating under strict corporate compliance. CRM data streams directly to internal data sheets.")

    elif page == "CRM & Deal Pipeline":
        st.markdown('<div class="main-header">CRM & Deal Pipeline Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Manage client relationships, track opportunity statuses, and review automated CRM notifications.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_comprehensive_v5.db")
        crm_df = pd.read_sql_query("SELECT * FROM crm_deals", conn)
        conn.close()
        
        # Smart Alerts Analysis for CRM
        st.markdown("### Automated CRM Smart Alerts & Actionable Insights")
        today_date = datetime.now(cairo_tz).date()
        alert_count = 0
        
        for index, row in crm_df.iterrows():
            last_dt = datetime.strptime(row['last_contact_date'], "%Y-%m-%d").date()
            delta_days = (today_date - last_dt).days
            
            if row['status'] == 'Open' and delta_days > 20:
                st.warning(f"Attention Required: Deal '{row['deal_title']}' with client '{row['client_name']}' has been Open with NO intervention for {delta_days} days!")
                alert_count += 1
            elif row['status'] == 'Pending':
                st.info(f"Pending Status Notice: Deal '{row['deal_title']}' with '{row['client_name']}' is awaiting review (Last contact: {row['last_contact_date']}).")
                alert_count += 1
                
        if alert_count == 0:
            st.success("All active CRM deals are up to date with recent client interventions.")
            
        st.markdown("---")
        st.subheader("Live CRM Database Sheet")
        st.dataframe(crm_df, use_container_width=True)
        
        # Export option to Excel/CSV format
        csv_data = crm_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CRM Data Sheet (CSV/Excel Compatible)",
            data=csv_data,
            file_name='masar_crm_export.csv',
            mime='text/csv',
        )
        
        st.markdown("---")
        st.subheader("Add / Update CRM Deal & Interaction")
        with st.form("crm_form"):
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("Client Name")
                d_title = st.text_input("Deal / Opportunity Title")
                d_status = st.selectbox("Deal Status", ["Open", "Pending", "Closed-Won", "Closed-Lost"])
            with col2:
                d_val = st.number_input("Deal Value (EGP)", min_value=0.0, step=1000.0)
                l_date = st.text_input("Last Contact Date (YYYY-MM-DD)", value=str(today_date))
            d_notes = st.text_area("Deal Notes & Summary")
            d_submit = st.form_submit_button("Commit CRM Record to Sheet")
            
            if d_submit and c_name:
                conn = sqlite3.connect("masar_comprehensive_v5.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO crm_deals (client_name, deal_title, status, deal_value, last_contact_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
                               (c_name, d_title, d_status, d_val, l_date, d_notes))
                conn.commit()
                conn.close()
                st.success("CRM record successfully added and synced to sheet.")
                st.rerun()

    elif page == "Master Database & File Uploader":
        st.markdown('<div class="main-header">Master Database & File Uploader</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Upload custom files (Excel/CSV), search instantly, and add entries that sync on the fly.</div>', unsafe_allow_html=True)
        
        # File Uploader Section
        st.markdown("### Upload External File / Database Sheet")
        uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    temp_df = pd.read_csv(uploaded_file)
                else:
                    temp_df = pd.read_excel(uploaded_file)
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                st.dataframe(temp_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error reading file: {e}")

        st.markdown("---")
        st.subheader("Instant Searchable Database")
        
        conn = sqlite3.connect("masar_comprehensive_v5.db")
        master_df = pd.read_sql_query("SELECT * FROM uploaded_master_db", conn)
        conn.close()
        
        search_query = st.text_input("Search Database (Enter name, category, or details):")
        if search_query:
            filtered_df = master_df[
                master_df['record_name'].str.contains(search_query, case=False, na=False) |
                master_df['category'].str.contains(search_query, case=False, na=False) |
                master_df['details'].str.contains(search_query, case=False, na=False)
            ]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(master_df, use_container_width=True)
            
        st.markdown("---")
        st.subheader("Add New Entity / Name Directly")
        with st.form("master_add_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_name = st.text_input("Entity / Name")
                m_cat = st.text_input("Category / Type")
            with col2:
                m_date = st.text_input("Date (YYYY-MM-DD)", value=str(datetime.now(cairo_tz).date()))
            m_details = st.text_area("Details & Notes")
            m_submit = st.form_submit_button("Add and Save to Database")
            
            if m_submit and m_name:
                conn = sqlite3.connect("masar_comprehensive_v5.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO uploaded_master_db (record_name, category, details, entry_date) VALUES (?, ?, ?, ?)",
                               (m_name, m_cat, m_details, m_date))
                conn.commit()
                conn.close()
                st.success("Name/Entity successfully added and updated in the system!")
                st.rerun()

    elif page == "Accounting Ledger (SGA)":
        st.markdown('<div class="main-header">Senior General Accountant Ledger (SGA)</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Complete corporate financial tracking, revenues, expenses, and periodic summaries.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_comprehensive_v5.db")
        ledger_df = pd.read_sql_query("SELECT * FROM accounting_ledger", conn)
        conn.close()
        
        st.dataframe(ledger_df, use_container_width=True)
        
        if st.session_state.role_code in ["Founder", "CEO", "SGA"]:
            st.markdown("---")
            st.subheader("Record Financial Transaction")
            with st.form("ledger_form"):
                col1, col2 = st.columns(2)
                with col1:
                    t_date = st.text_input("Transaction Date (YYYY-MM-DD)", value=str(datetime.now(cairo_tz).date()))
                    t_desc = st.text_input("Transaction Description")
                with col2:
                    t_cat = st.selectbox("Category", ["Revenue", "Expense", "Consultancy Fee", "Operational Cost"])
                    t_amount = st.number_input("Amount (EGP)", min_value=0.0, step=100.0)
                    t_type = st.selectbox("Entry Type", ["Credit", "Debit"])
                t_submit = st.form_submit_button("Save Financial Entry")
                
                if t_submit and t_desc:
                    conn = sqlite3.connect("masar_comprehensive_v5.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO accounting_ledger (transaction_date, description, category, amount, entry_type) VALUES (?, ?, ?, ?, ?)",
                                   (t_date, t_desc, t_cat, t_amount, t_type))
                    conn.commit()
                    conn.close()
                    st.success("Transaction successfully posted to the SGA ledger.")
                    st.rerun()
        else:
            st.info("Financial entry rights are restricted to SGA, Founder, and CEO designations.")

    elif page == "Task Management":
        st.markdown('<div class="main-header">Task & Operations Manager</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Delegate, monitor, and track department deliverables.</div>', unsafe_allow_html=True)
        
        conn = sqlite3.connect("masar_comprehensive_v5.db")
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
                conn = sqlite3.connect("masar_comprehensive_v5.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tasks (task_title, assigned_to, priority, status, deadline) VALUES (?, ?, ?, ?, ?)",
                               (t_title, t_assignee, t_priority, "Pending", t_deadline))
                conn.commit()
                conn.close()
                st.success("Task successfully dispatched.")
                st.rerun()

    elif page == "Smart Assistant":
        st.markdown('<div class="main-header">MASAR AI Smart Assistant</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Advanced corporate query engine for operational guidelines, CRM analysis, and financial briefs.</div>', unsafe_allow_html=True)
        
        query = st.text_input("Ask the Assistant about deals, financial accounts, or corporate procedures:")
        if st.button("Query Assistant"):
            if query:
                q_lower = query.lower()
                conn = sqlite3.connect("masar_comprehensive_v5.db")
                if "crm" in q_lower or "deal" in q_lower or "client" in q_lower:
                    df_c = pd.read_sql_query("SELECT client_name, deal_title, status FROM crm_deals", conn)
                    st.success("Assistant Analysis on CRM Pipeline:")
                    st.dataframe(df_c, use_container_width=True)
                elif "account" in q_lower or "financial" in q_lower or "revenue" in q_lower:
                    df_l = pd.read_sql_query("SELECT * FROM accounting_ledger", conn)
                    st.success("Assistant Analysis on Financial Ledger:")
                    st.dataframe(df_l, use_container_width=True)
                else:
                    st.info(f"Assistant Report regarding '{query}': MASAR for Consultancy and Business Development maintains high structural integrity across all departments, including active CRM tracking, SGA financial oversight, and file upload capabilities.")
                conn.close()
            else:
                st.warning("Please enter a valid query string.")

    elif page == "Management Control":
        if st.session_state.role_code in ["Founder", "CEO"]:
            st.markdown('<div class="main-header">Executive Administration Control Panel</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-header">Manage corporate directory and user clearance levels.</div>', unsafe_allow_html=True)
            
            conn = sqlite3.connect("masar_comprehensive_v5.db")
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
