import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date
from pathlib import Path
import io

# ============================================================
# MASAR INTELLIGENCE OS
# ============================================================

APP_NAME = "MASAR Intelligence OS"
COMPANY_NAME = "MASAR for Consultancy and Business Development"

NAVY = "#0B1E36"
BLUE = "#38BDF8"
SLATE = "#64748B"
SLATE_BLUE = "#1E3A8A"
BG = "#F4F7FA"

DB_PATH = "masar.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def init_database():

    conn = get_db()

    cursor = conn.cursor()

    cursor.executescript("""

    CREATE TABLE IF NOT EXISTS companies (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        industry TEXT,

        website TEXT,

        phone TEXT,

        email TEXT,

        status TEXT DEFAULT 'Prospect',

        priority TEXT DEFAULT 'Medium',

        notes TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP

    );


    CREATE TABLE IF NOT EXISTS opportunities (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_id INTEGER,

        title TEXT NOT NULL,

        stage TEXT DEFAULT 'Lead',

        value REAL DEFAULT 0,

        probability REAL DEFAULT 0,

        next_action TEXT,

        next_date TEXT,

        notes TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(company_id)

        REFERENCES companies(id)

    );


    CREATE TABLE IF NOT EXISTS followups (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_id INTEGER,

        title TEXT NOT NULL,

        due_date TEXT,

        status TEXT DEFAULT 'Open',

        priority TEXT DEFAULT 'Medium',

        notes TEXT,

        FOREIGN KEY(company_id)

        REFERENCES companies(id)

    );


    CREATE TABLE IF NOT EXISTS governance (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        item_type TEXT NOT NULL,

        title TEXT NOT NULL,

        owner TEXT,

        approval_date TEXT,

        review_date TEXT,

        status TEXT DEFAULT 'Active',

        notes TEXT

    );

    """)

    conn.commit()

    conn.close()


def fetch(query, params=()):

    conn = get_db()

    df = pd.read_sql_query(

        query,

        conn,

        params=params

    )

    conn.close()

    return df


def execute(query, params=()):

    conn = get_db()

    conn.execute(query, params)

    conn.commit()

    conn.close()


# ============================================================
# UI
# ============================================================

def inject_css():

    st.markdown(

        f"""

        <style>

        .stApp {{

            background: {BG};

        }}


        [data-testid="stSidebar"] {{

            background: {NAVY};

        }}


        [data-testid="stSidebar"] * {{

            color: white !important;

        }}


        .masar-hero {{

            background:

            linear-gradient(

                135deg,

                {NAVY},

                #16365c

            );

            padding: 32px;

            border-radius: 22px;

            color: white;

            margin-bottom: 25px;

        }}


        .masar-hero h1 {{

            font-size: 36px;

            margin: 0;

            font-weight: 800;

        }}


        .masar-hero p {{

            color: #cbd5e1;

            margin-top: 8px;

        }}


        .metric-card {{

            background: white;

            border-radius: 18px;

            padding: 22px;

            border: 1px solid #e5e7eb;

            box-shadow:

            0 8px 30px rgba(15,23,42,0.06);

        }}


        .metric-label {{

            color: {SLATE};

            font-size: 12px;

            text-transform: uppercase;

            letter-spacing: 1px;

        }}


        .metric-value {{

            color: {NAVY};

            font-size: 30px;

            font-weight: 800;

            margin-top: 5px;

        }}


        .section-title {{

            color: {NAVY};

            font-size: 21px;

            font-weight: 800;

            margin-top: 30px;

            margin-bottom: 12px;

        }}


        div.stButton > button {{

            border-radius: 10px;

            font-weight: 700;

        }}

        </style>

        """,

        unsafe_allow_html=True

    )


def metric_card(label, value):

    st.markdown(

        f"""

        <div class="metric-card">

            <div class="metric-label">

                {label}

            </div>

            <div class="metric-value">

                {value}

            </div>

        </div>

        """,

        unsafe_allow_html=True

    )


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    st.markdown(

        """

        <div class="masar-hero">

            <h1>MASAR Executive Command Center</h1>

            <p>

            Business Development • Government Affairs • Public Relations

            </p>

        </div>

        """,

        unsafe_allow_html=True

    )


    companies = fetch(

        "SELECT COUNT(*) AS count FROM companies"

    ).iloc[0]["count"]


    active_opportunities = fetch(

        """

        SELECT COUNT(*) AS count

        FROM opportunities

        WHERE stage NOT IN ('Won','Lost')

        """

    ).iloc[0]["count"]


    pipeline = fetch(

        """

        SELECT

        COALESCE(SUM(value),0) AS value

        FROM opportunities

        WHERE stage != 'Lost'

        """

    ).iloc[0]["value"]


    weighted_pipeline = fetch(

        """

        SELECT

        COALESCE(

            SUM(value * probability / 100),

            0

        ) AS value

        FROM opportunities

        WHERE stage != 'Lost'

        """

    ).iloc[0]["value"]


    followups = fetch(

        """

        SELECT COUNT(*) AS count

        FROM followups

        WHERE status = 'Open'

        """

    ).iloc[0]["count"]


    cols = st.columns(5)


    values = [

        ("Companies", companies),

        ("Active Opportunities", active_opportunities),

        ("Pipeline Value", f"EGP {pipeline:,.0f}"),

        ("Weighted Pipeline", f"EGP {weighted_pipeline:,.0f}"),

        ("Open Follow-ups", followups),

    ]


    for col, (label, value) in zip(cols, values):

        with col:

            metric_card(label, value)


    st.markdown(

        '<div class="section-title">Opportunity Funnel</div>',

        unsafe_allow_html=True

    )


    funnel = fetch(

        """

        SELECT

            stage,

            COUNT(*) AS opportunities,

            COALESCE(SUM(value),0) AS value

        FROM opportunities

        GROUP BY stage

        """

    )


    if not funnel.empty:

        c1, c2 = st.columns(2)


        with c1:

            fig = px.bar(

                funnel,

                x="stage",

                y="opportunities",

                text="opportunities",

                template="plotly_white",

                title="Opportunities by Stage"

            )

            st.plotly_chart(

                fig,

                use_container_width=True

            )


        with c2:

            fig = px.bar(

                funnel,

                x="stage",

                y="value",

                text="value",

                template="plotly_white",

                title="Pipeline Value by Stage"

            )

            st.plotly_chart(

                fig,

                use_container_width=True

            )


    st.markdown(

        '<div class="section-title">Top Opportunities</div>',

        unsafe_allow_html=True

    )


    top = fetch(

        """

        SELECT

            companies.name AS Company,

            opportunities.title AS Opportunity,

            opportunities.stage AS Stage,

            opportunities.value AS Value,

            opportunities.probability AS Probability,

            ROUND(

                opportunities.value *

                opportunities.probability / 100

            ) AS Weighted_Value,

            opportunities.next_action AS Next_Action

        FROM opportunities

        LEFT JOIN companies

        ON companies.id = opportunities.company_id

        ORDER BY Weighted_Value DESC

        LIMIT 10

        """

    )


    st.dataframe(

        top,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# CRM
# ============================================================

def crm():

    st.title("🏢 CRM & Companies")


    with st.expander("＋ Add New Company"):

        with st.form("company_form"):

            col1, col2 = st.columns(2)

            name = col1.text_input(

                "Company Name *"

            )

            industry = col2.text_input(

                "Industry"

            )

            website = col1.text_input(

                "Website"

            )

            phone = col2.text_input(

                "Phone"

            )

            email = col1.text_input(

                "Email"

            )

            status = col2.selectbox(

                "Status",

                [

                    "Prospect",

                    "Contacted",

                    "Meeting",

                    "Proposal",

                    "Negotiation",

                    "Won",

                    "Lost",

                    "On Hold"

                ]

            )

            priority = col1.selectbox(

                "Priority",

                ["High","Medium","Low"]

            )

            notes = st.text_area(

                "Notes"

            )


            submit = st.form_submit_button(

                "Save Company"

            )


            if submit:

                if not name.strip():

                    st.error(

                        "Company Name is required."

                    )

                else:

                    execute(

                        """

                        INSERT INTO companies

                        (

                            name,

                            industry,

                            website,

                            phone,

                            email,

                            status,

                            priority,

                            notes

                        )

                        VALUES (?,?,?,?,?,?,?,?)

                        """,

                        (

                            name,

                            industry,

                            website,

                            phone,

                            email,

                            status,

                            priority,

                            notes

                        )

                    )

                    st.success(

                        "Company added successfully."

                    )

                    st.rerun()


    search = st.text_input(

        "🔎 Search companies"

    )


    companies = fetch(

        """

        SELECT *

        FROM companies

        WHERE name LIKE ?

        ORDER BY id DESC

        """,

        (f"%{search}%",)

    )


    st.dataframe(

        companies,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# PIPELINE
# ============================================================

def pipeline():

    st.title("🎯 Business Development Pipeline")


    companies = fetch(

        "SELECT id,name FROM companies ORDER BY name"

    )


    if companies.empty:

        st.info(

            "Add companies in CRM first."

        )

        return


    company_map = dict(

        zip(

            companies["name"],

            companies["id"]

        )

    )


    with st.expander("＋ Add Opportunity"):

        with st.form("opportunity_form"):

            c1, c2 = st.columns(2)


            company = c1.selectbox(

                "Company",

                list(company_map.keys())

            )


            title = c2.text_input(

                "Opportunity Title *"

            )


            stage = c1.selectbox(

                "Stage",

                [

                    "Lead",

                    "Contacted",

                    "Meeting",

                    "Proposal",

                    "Negotiation",

                    "Won",

                    "Lost"

                ]

            )


            value = c2.number_input(

                "Opportunity Value (EGP)",

                min_value=0.0,

                step=1000.0

            )


            probability = c1.slider(

                "Probability %",

                0,

                100,

                50

            )


            next_date = c2.date_input(

                "Next Action Date"

            )


            next_action = c1.text_input(

                "Next Action"

            )


            notes = st.text_area(

                "Notes"

            )


            submit = st.form_submit_button(

                "Save Opportunity"

            )


            if submit:

                if not title.strip():

                    st.error(

                        "Opportunity title is required."

                    )

                else:

                    execute(

                        """

                        INSERT INTO opportunities

                        (

                            company_id,

                            title,

                            stage,

                            value,

                            probability,

                            next_action,

                            next_date,

                            notes

                        )

                        VALUES (?,?,?,?,?,?,?,?)

                        """,

                        (

                            company_map[company],

                            title,

                            stage,

                            value,

                            probability,

                            next_action,

                            str(next_date),

                            notes

                        )

                    )


                    st.success(

                        "Opportunity created."

                    )

                    st.rerun()


    data = fetch(

        """

        SELECT

            opportunities.id,

            companies.name AS Company,

            opportunities.title AS Opportunity,

            opportunities.stage AS Stage,

            opportunities.value AS Value,

            opportunities.probability AS Probability,

            ROUND(

                opportunities.value *

                opportunities.probability / 100

            ) AS Weighted_Value,

            opportunities.next_action AS Next_Action,

            opportunities.next_date AS Next_Date

        FROM opportunities

        LEFT JOIN companies

        ON companies.id = opportunities.company_id

        ORDER BY Weighted_Value DESC

        """

    )


    st.dataframe(

        data,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# FOLLOW UPS
# ============================================================

def followups():

    st.title("📞 Follow-ups & Tasks")


    companies = fetch(

        "SELECT id,name FROM companies ORDER BY name"

    )


    if not companies.empty:

        company_map = dict(

            zip(

                companies["name"],

                companies["id"]

            )

        )


        with st.expander("＋ Add Follow-up"):

            with st.form("followup_form"):

                company = st.selectbox(

                    "Company",

                    list(company_map.keys())

                )


                title = st.text_input(

                    "Task / Follow-up *"

                )


                due = st.date_input(

                    "Due Date"

                )


                priority = st.selectbox(

                    "Priority",

                    [

                        "High",

                        "Medium",

                        "Low"

                    ]

                )


                notes = st.text_area(

                    "Notes"

                )


                submit = st.form_submit_button(

                    "Save Follow-up"

                )


                if submit:

                    execute(

                        """

                        INSERT INTO followups

                        (

                            company_id,

                            title,

                            due_date,

                            priority,

                            notes

                        )

                        VALUES (?,?,?,?,?)

                        """,

                        (

                            company_map[company],

                            title,

                            str(due),

                            priority,

                            notes

                        )

                    )


                    st.success(

                        "Follow-up added."

                    )

                    st.rerun()


    data = fetch(

        """

        SELECT

            followups.id,

            companies.name AS Company,

            followups.title AS Task,

            followups.due_date AS Due_Date,

            followups.status AS Status,

            followups.priority AS Priority,

            followups.notes AS Notes

        FROM followups

        LEFT JOIN companies

        ON companies.id = followups.company_id

        ORDER BY followups.due_date

        """

    )


    st.dataframe(

        data,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# INTELLIGENCE CENTER
# ============================================================

def intelligence():

    st.title("🧠 Intelligence Center")


    st.markdown(

        """

        ### Company Intelligence Workspace

        Use this area to prepare a structured research brief

        before meetings and business development activities.

        """

    )


    company = st.text_input(

        "Company Name"

    )


    website = st.text_input(

        "Website"

    )


    if st.button(

        "🚀 Run Intelligence Analysis",

        type="primary"

    ):

        if not company and not website:

            st.warning(

                "Enter a company name or website."

            )

        else:

            st.session_state["intel_company"] = (

                company or website

            )

            st.session_state["intel_website"] = website

            st.success(

                "Intelligence workspace created."

            )


    if "intel_company" in st.session_state:

        company = st.session_state["intel_company"]

        website = st.session_state["intel_website"]


        st.divider()


        st.subheader(

            f"🎯 {company}"

        )


        tabs = st.tabs(

            [

                "Company Snapshot",

                "Services",

                "Market Position",

                "MASAR Opportunities",

                "Risks",

                "Meeting Brief"

            ]

        )


        with tabs[0]:

            st.text_area(

                "Company Overview",

                height=180,

                placeholder=

                "Paste verified company information here..."

            )


        with tabs[1]:

            st.text_area(

                "Services / Capabilities",

                height=180

            )


        with tabs[2]:

            st.text_area(

                "Market Position / Competitors",

                height=180

            )


        with tabs[3]:

            st.markdown(

                "### MASAR Opportunity Map"

            )


            a,b,c,d = st.columns(4)


            with a:

                st.checkbox(

                    "Government Affairs"

                )


            with b:

                st.checkbox(

                    "Public Relations"

                )


            with c:

                st.checkbox(

                    "Business Development"

                )


            with d:

                st.checkbox(

                    "Stakeholder Management"

                )


            st.text_area(

                "Opportunity Rationale",

                height=160

            )


        with tabs[4]:

            st.text_area(

                "Risks / Red Flags",

                height=160

            )


        with tabs[5]:

            st.text_area(

                "Meeting Objectives",

                height=120

            )


            st.text_area(

                "Key Questions",

                height=160

            )


            st.text_area(

                "Recommended Talking Points",

                height=160

            )


# ============================================================
# GOVERNANCE
# ============================================================

def governance():

    st.title("⚖️ Governance")


    with st.expander("＋ Add Governance Item"):

        with st.form("governance_form"):

            c1,c2 = st.columns(2)


            item_type = c1.selectbox(

                "Type",

                [

                    "Job Description",

                    "Procedure",

                    "Policy"

                ]

            )


            title = c2.text_input(

                "Title *"

            )


            owner = c1.text_input(

                "Owner"

            )


            approval = c2.date_input(

                "Approval Date"

            )


            review = c1.date_input(

                "Next Review Date"

            )


            status = c2.selectbox(

                "Status",

                [

                    "Active",

                    "Draft",

                    "Under Review",

                    "Archived"

                ]

            )


            notes = st.text_area(

                "Notes"

            )


            submit = st.form_submit_button(

                "Save"

            )


            if submit:

                execute(

                    """

                    INSERT INTO governance

                    (

                        item_type,

                        title,

                        owner,

                        approval_date,

                        review_date,

                        status,

                        notes

                    )

                    VALUES (?,?,?,?,?,?,?)

                    """,

                    (

                        item_type,

                        title,

                        owner,

                        str(approval),

                        str(review),

                        status,

                        notes

                    )

                )


                st.success(

                    "Governance item saved."

                )

                st.rerun()


    data = fetch(

        """

        SELECT *

        FROM governance

        ORDER BY review_date

        """

    )


    st.dataframe(

        data,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# APP
# ============================================================

init_database()

inject_css()


with st.sidebar:

    st.markdown(

        """

        <h1 style="letter-spacing:3px;">

        MASAR

        </h1>

        <small>

        INTELLIGENCE OS

        </small>

        """,

        unsafe_allow_html=True

    )


    st.divider()


    page = st.radio(

        "Navigation",

        [

            "Executive Dashboard",

            "CRM & Companies",

            "Pipeline",

            "Follow-ups",

            "Intelligence Center",

            "Governance"

        ]

    )


    st.divider()


    st.caption(

        "FOR CONSULTANCY AND BUSINESS DEVELOPMENT"

    )


if page == "Executive Dashboard":

    dashboard()

elif page == "CRM & Companies":

    crm()

elif page == "Pipeline":

    pipeline()

elif page == "Follow-ups":

    followups()

elif page == "Intelligence Center":

    intelligence()

elif page == "Governance":

    governance()