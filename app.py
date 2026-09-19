import io
import os
import zipfile

import mysql.connector
import numpy as np
import pandas as pd
import streamlit as st

from sklearn.ensemble import RandomForestClassifier


# ============================================================
# PAGE CONFIGURATION & SOLID DARK BLUE STYLING (NO GRADIENTS)
# ============================================================

st.set_page_config(
    page_title="EduGuard-AI | UET Mardan",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1320px; }

    /* Completely hide default sidebar */
    [data-testid="stSidebar"] { display: none; }

    /* Solid Dark Navy Blue University Header (No Gradient) */
    .uni-header {
        background-color: #0b132b;
        padding: 1.75rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid #1c2541;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
    }
    .uni-header h1 { color: #ffffff; font-weight: 700; font-size: 2rem; margin-bottom: 0.25rem; }
    .uni-header p { color: #cbd5e1; font-size: 0.95rem; margin: 0; }

    /* Clean Corporate Cards */
    .saas-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 1.75rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .saas-card h3 { color: #0b132b; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.75rem; }
    .saas-card p { color: #475569; font-size: 0.95rem; line-height: 1.5; }

    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    div[data-testid="stMetric"] label { color: #475569 !important; font-weight: 500 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #0b132b; font-weight: 700; font-size: 1.6rem; }

    /* Solid Dark Blue Buttons (No Gradient) */
    .stButton button {
        background-color: #0b132b !important;
        background-image: none !important;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
        border: 1px solid #1c2541;
        transition: background-color 0.2s;
    }
    .stButton button:hover {
        background-color: #1c2541 !important;
        border-color: #3a506b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE & DYNAMIC DATABASE MIGRATION
# ============================================================

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

REQUIRED_COLS = ["quiz1", "quiz2", "assignment1", "assignment2", "midterm"]

def get_db_connection():
    db_config = st.secrets["mysql"]
    return mysql.connector.connect(
        host=db_config["host"],
        port=db_config.get("port", 3306),
        database=db_config["database"],
        user=db_config["username"],
        password=db_config["password"]
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            batch_name VARCHAR(255),
            student_id VARCHAR(100),
            subject VARCHAR(255),
            quiz1 FLOAT DEFAULT 0,
            quiz2 FLOAT DEFAULT 0,
            assignment1 FLOAT DEFAULT 0,
            assignment2 FLOAT DEFAULT 0,
            midterm FLOAT DEFAULT 0,
            risk_status VARCHAR(50),
            probability FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute("SHOW COLUMNS FROM evaluations")
    existing_columns = [col[0] for col in cursor.fetchall()]
    
    for col_name in ["final", "total_score", "gpa"]:
        if col_name not in existing_columns:
            cursor.execute(f"ALTER TABLE evaluations ADD COLUMN {col_name} FLOAT DEFAULT 0")

    conn.commit()
    cursor.close()
    conn.close()

init_db()


# ============================================================
# ML MODEL & HELPERS
# ============================================================

@st.cache_resource
def get_trained_model():
    data = {
        "quiz1": [10, 5, 8, 9, 3, 2, 7, 10, 4, 6],
        "quiz2": [10, 4, 7, 8, 2, 3, 6, 9, 5, 6],
        "assignment1": [15, 6, 12, 14, 5, 4, 11, 15, 7, 10],
        "assignment2": [15, 5, 13, 14, 4, 5, 12, 14, 6, 9],
        "midterm": [40, 18, 30, 35, 12, 15, 28, 38, 20, 25],
    }
    df_train = pd.DataFrame(data)
    df_train["total"] = df_train.sum(axis=1)
    y_train = (df_train["total"] < 37.5).astype(int)

    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    model.fit(df_train[REQUIRED_COLS], y_train)
    return model

model = get_trained_model()

def load_multi_subject_file(uploaded_file):
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file, header=None)
    elif filename.endswith((".xlsx", ".xls")):
        excel_file = pd.ExcelFile(uploaded_file)
        raw_df = pd.read_excel(uploaded_file, sheet_name=excel_file.sheet_names[0], header=None)
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.lower().endswith(".csv") and not f.endswith("/")]
            if not csv_files:
                raise ValueError("No CSV files found inside ZIP.")
            with zip_ref.open(csv_files[0]) as f:
                raw_df = pd.read_csv(f, header=None)
    else:
        raise ValueError("Unsupported file format.")

    row_zero = raw_df.iloc[0].values
    has_subjects = any(pd.notna(val) for val in row_zero[5:]) if len(row_zero) > 5 else False

    if has_subjects:
        row_assessments = raw_df.iloc[1].values
        subject_map = {}
        current_subject = None

        for col_idx in range(5, raw_df.shape[1]):
            subj_val = row_zero[col_idx]
            if pd.notna(subj_val):
                current_subject = str(subj_val).strip()
            
            assess_val = row_assessments[col_idx]
            if pd.notna(assess_val) and current_subject:
                assess_lower = str(assess_val).strip().lower()
                subject_map.setdefault(current_subject, {})[assess_lower] = col_idx

        parsed_subjects_data = {}
        data_subset = raw_df.iloc[2:].dropna(subset=[1]).copy()

        for subj, cols in subject_map.items():
            sub_df = pd.DataFrame()
            sub_df["Student_ID"] = data_subset.iloc[:, 1].values
            sub_df["Student_Name"] = data_subset.iloc[:, 2].values if data_subset.shape[1] > 2 else ""

            q1_idx = next((idx for key, idx in cols.items() if "quiz 1" in key or "q1" in key), None)
            q2_idx = next((idx for key, idx in cols.items() if "quiz 2" in key or "q2" in key), None)
            asg_idx = next((idx for key, idx in cols.items() if "assignment" in key or "presentation" in key or "a1" in key), None)
            mid_idx = next((idx for key, idx in cols.items() if "midterm" in key or "mid" in key), None)
            final_idx = next((idx for key, idx in cols.items() if "final" in key or "terminal" in key), None)

            sub_df["quiz1"] = pd.to_numeric(pd.Series(data_subset.iloc[:, q1_idx].values if q1_idx is not None else 0), errors="coerce").fillna(0)
            sub_df["quiz2"] = pd.to_numeric(pd.Series(data_subset.iloc[:, q2_idx].values if q2_idx is not None else 0), errors="coerce").fillna(0)
            
            val_asg = pd.to_numeric(pd.Series(data_subset.iloc[:, asg_idx].values if asg_idx is not None else 0), errors="coerce").fillna(0)
            sub_df["assignment1"] = val_asg / 2.0
            sub_df["assignment2"] = val_asg / 2.0

            sub_df["midterm"] = pd.to_numeric(pd.Series(data_subset.iloc[:, mid_idx].values if mid_idx is not None else 0), errors="coerce").fillna(0)
            
            if final_idx is not None:
                sub_df["final"] = pd.to_numeric(pd.Series(data_subset.iloc[:, final_idx].values), errors="coerce").fillna(0)
            else:
                sub_df["final"] = 0.0
            
            parsed_subjects_data[subj] = sub_df

        return parsed_subjects_data, "multi_subject"
    else:
        df = pd.read_csv(uploaded_file) if filename.endswith(".csv") else pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        if "final" not in df.columns and "terminal" in df.columns:
            df["final"] = df["terminal"]
        elif "final" not in df.columns:
            df["final"] = 0.0
        else:
            df["final"] = pd.to_numeric(df["final"], errors="coerce").fillna(0.0)

        return {"General Course": df}, "flat"

def save_batch_to_database(df, subject_name, batch_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO evaluations (batch_name, student_id, subject, quiz1, quiz2, assignment1, assignment2, midterm, final, risk_status, probability)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                batch_name, 
                str(row.get("Student_ID", row.get("student_id", "Unknown"))), 
                subject_name, 
                float(row.get("quiz1", 0)), 
                float(row.get("quiz2", 0)), 
                float(row.get("assignment1", 0)), 
                float(row.get("assignment2", 0)), 
                float(row.get("midterm", 0)), 
                float(row.get("final", 0)), 
                str(row.get("Evaluation", row.get("risk_status", row.get("Overall_Status", "No Risk")))), 
                float(row.get("Risk_Probability", row.get("probability", 0.0)))
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()

def marks_to_gpa(total_marks, max_possible=75.0):
    percentage = (total_marks / max_possible) * 100
    if percentage >= 85: return 4.0, "A+"
    elif percentage >= 80: return 4.0, "A"
    elif percentage >= 75: return 3.7, "B+"
    elif percentage >= 70: return 3.3, "B"
    elif percentage >= 65: return 3.0, "C+"
    elif percentage >= 60: return 2.7, "C"
    elif percentage >= 50: return 2.0, "D"
    else: return 0.0, "F"

def color_risk_cells(val):
    """Applies red styling for At Risk / F grades and green for No Risk / Passing grades."""
    if isinstance(val, str):
        val_lower = val.lower()
        if "at risk" in val_lower or val == "F":
            return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
        elif "no risk" in val_lower or "pass" in val_lower or val in ["A+", "A", "B+", "B", "C+", "C", "D"]:
            return "background-color: #dcfce7; color: #166534; font-weight: bold;"
    return ""

def render_styled_dataframe(df):
    try:
        styled_df = df.style.map(color_risk_cells)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    except Exception:
        st.dataframe(df, use_container_width=True, hide_index=True)

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Evaluation_Results")
    return output.getvalue()


# ============================================================
# SOLID DARK BLUE HEADER & NAVIGATION BAR
# ============================================================

st.markdown(
    """
    <div class="uni-header">
        <h1>EduGuard-AI Academic Evaluation System</h1>
        <p>University of Engineering and Technology (UET) Mardan — Faculty Decision Support & Analytics Portal</p>
    </div>
    """,
    unsafe_allow_html=True,
)

pages = ["Home", "Dashboard", "Batch Evaluation & CGPA", "Single Student", "Database Logs & Batches"]

cols = st.columns(len(pages))
for i, p_name in enumerate(pages):
    with cols[i]:
        is_active = st.session_state.selected_page == p_name
        btn_type = "primary" if is_active else "secondary"
        if st.button(p_name, use_container_width=True, type=btn_type):
            st.session_state.selected_page = p_name
            st.rerun()

page = st.session_state.selected_page
st.divider()


# ============================================================
# PAGE ROUTING & VIEWS
# ============================================================

if page == "Home":
    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        st.markdown(
            """
            <div class="saas-card">
                <h3>🏛️ Departmental Academic Management</h3>
                <p>EduGuard-AI provides automated student performance monitoring, machine learning-driven risk evaluation, 
                and comprehensive multi-course semester CGPA calculations for faculty members.</p>
                <hr style="margin: 1.25rem 0; border: none; border-top: 1px solid #cbd5e1;">
                <ul style="color: #334155; padding-left: 1.25rem; line-height: 1.6;">
                    <li><b>Automated Risk Assessment:</b> Instantly classifies students at academic risk based on continuous assessments.</li>
                    <li><b>Flexible File Parsing:</b> Supports standard department Excel/CSV grade sheets and batch ZIP archives.</li>
                    <li><b>Institutional Reporting:</b> Securely logs all evaluation results directly to the institutional MySQL database.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="saas-card" style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
                <h3>Quick Actions</h3>
                <p style="margin-bottom: 1.5rem; color: #475569;">Begin batch evaluation or inspect logs.</p>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Batch Evaluation", use_container_width=True):
            st.session_state.selected_page = "Batch Evaluation & CGPA"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Dashboard":
    st.subheader("📊 Department Executive Analytics")
    conn = get_db_connection()
    logs_df = pd.read_sql_query("SELECT * FROM evaluations ORDER BY timestamp DESC", conn)
    conn.close()

    total_evaluations = len(logs_df)
    at_risk = int((logs_df["risk_status"] == "At Risk").sum()) if total_evaluations > 0 else 0
    safe = int((logs_df["risk_status"] == "No Risk").sum()) if total_evaluations > 0 else 0
    risk_pct = (at_risk / total_evaluations * 100) if total_evaluations > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Evaluations", total_evaluations)
    with col2: st.metric("Students At Risk", at_risk)
    with col3: st.metric("Passing Students", safe)
    with col4: st.metric("At-Risk Ratio", f"{risk_pct:.1f}%")

    if not logs_df.empty:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Risk Status Breakdown**")
            st.bar_chart(logs_df["risk_status"].value_counts())
        with col2:
            st.markdown("**Evaluations by Batch**")
            st.bar_chart(logs_df["batch_name"].value_counts())

        st.divider()
        st.markdown("**Recent Database Activity Logs**")
        render_styled_dataframe(logs_df.head(25))
        
        excel_data = convert_df_to_excel(logs_df)
        st.download_button(
            label="📥 Download Full Logs as Excel",
            data=excel_data,
            file_name="EduGuard_AI_All_Logs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No evaluation logs found in the database. Upload a batch to populate data.")

elif page == "Batch Evaluation & CGPA":
    st.subheader("📂 Batch Semester Student Evaluation & CGPA Calculator")
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1: batch_name = st.text_input("Batch Tag / ID", "Fall-2026-CS-4")
    with col_b2: uploaded_file = st.file_uploader("Upload Course Grades Dataset (CSV, Excel, or ZIP)", type=["csv", "xlsx", "xls", "zip"])

    if uploaded_file is not None:
        try:
            subjects_data, file_type = load_multi_subject_file(uploaded_file)
            st.success(f"Successfully loaded dataset. Detected courses: {len(subjects_data)}")

            eval_mode = st.radio("Evaluation Mode", ["Single Course Evaluation", "Overall CGPA & Multi-Course"], horizontal=True)

            if eval_mode == "Single Course Evaluation":
                selected_subject = st.selectbox("Select Course", list(subjects_data.keys()))
                input_df = subjects_data[selected_subject]
                if "Student_ID" not in input_df.columns:
                    input_df["Student_ID"] = [f"STUDENT-{i+1:03d}" for i in range(len(input_df))]

                st.markdown(f"**Course Preview: {selected_subject} ({len(input_df)} Students)**")
                render_styled_dataframe(input_df.head(10))

                if st.button(f"Run AI Evaluation for {selected_subject}"):
                    features = input_df[REQUIRED_COLS]
                    preds = model.predict(features)
                    probs = model.predict_proba(features)[:, 1]

                    input_df["Evaluation"] = ["At Risk" if p == 1 else "No Risk" for p in preds]
                    input_df["Risk_Probability"] = (probs * 100).round(1)
                    
                    has_final = "final" in input_df.columns and (input_df["final"] > 0).any()
                    final_vals = input_df["final"] if "final" in input_df.columns else 0.0
                    input_df["Total_Score"] = input_df[REQUIRED_COLS].sum(axis=1) + final_vals
                    
                    max_scale = 125.0 if has_final else 75.0
                    gpa_l, grade_l = [], []
                    for _, r in input_df.iterrows():
                        g, gr = marks_to_gpa(r["Total_Score"], max_possible=max_scale)
                        gpa_l.append(g); grade_l.append(gr)
                    input_df["GPA"] = gpa_l
                    input_df["Grade"] = grade_l

                    # Mark At Risk if GPA < 2.0 or model triggered
                    input_df.loc[input_df["GPA"] < 2.0, "Evaluation"] = "At Risk"

                    save_batch_to_database(input_df, selected_subject, batch_name)
                    st.success("Evaluation completed and results saved to database.")
                    render_styled_dataframe(input_df)

                    excel_bytes = convert_df_to_excel(input_df)
                    st.download_button(
                        label=f"📥 Download {selected_subject} Results (Excel)",
                        data=excel_bytes,
                        file_name=f"{batch_name}_{selected_subject}_Evaluation.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            else:
                st.markdown("**Overall Semester CGPA Calculation**")
                selected_courses = st.multiselect("Select Courses for CGPA Calculation", list(subjects_data.keys()), default=list(subjects_data.keys()))
                credit_hours = st.number_input("Credit Hours per Course", 1, 4, 3)

                if selected_courses and st.button("Calculate Semester CGPA"):
                    base_students = subjects_data[selected_courses[0]][["Student_ID", "Student_Name"]].copy()
                    cgpa_records = []
                    
                    for _, student in base_students.iterrows():
                        sid, sname = student["Student_ID"], student["Student_Name"]
                        total_qp, total_cr = 0.0, 0.0
                        c_breakdown, risk_flag = {}, False

                        for course in selected_courses:
                            cdf = subjects_data[course]
                            srow = cdf[cdf["Student_ID"] == sid]
                            if not srow.empty:
                                r = srow.iloc[0]
                                final_val = r.get("final", 0.0)
                                t_score = r["quiz1"] + r["quiz2"] + r["assignment1"] + r["assignment2"] + r["midterm"] + final_val
                                
                                sample = pd.DataFrame([[r["quiz1"], r["quiz2"], r["assignment1"], r["assignment2"], r["midterm"]]], columns=REQUIRED_COLS)
                                if model.predict(sample)[0] == 1: risk_flag = True
                                
                                max_scale = 125.0 if final_val > 0 else 75.0
                                gp, grade = marks_to_gpa(t_score, max_possible=max_scale)
                                total_qp += gp * credit_hours
                                total_cr += credit_hours
                                c_breakdown[f"{course} (Grade)"] = grade

                        cgpa = round(total_qp / total_cr, 2) if total_cr > 0 else 0.0
                        # Mark At Risk if overall CGPA < 2.0 or model risk flag triggered
                        overall_status = "At Risk" if risk_flag or cgpa < 2.0 else "No Risk"
                        
                        rec = {"Student_ID": sid, "Student_Name": sname, "CGPA": cgpa, "Overall_Status": overall_status}
                        rec.update(c_breakdown)
                        cgpa_records.append(rec)

                    cgpa_df = pd.DataFrame(cgpa_records)
                    st.success("CGPA computation completed successfully.")
                    render_styled_dataframe(cgpa_df)

                    excel_bytes = convert_df_to_excel(cgpa_df)
                    st.download_button(
                        label="📥 Download Semester CGPA Report (Excel)",
                        data=excel_bytes,
                        file_name=f"{batch_name}_Semester_CGPA_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        except Exception as e:
            st.error(f"Error processing dataset: {e}")

elif page == "Single Student":
    st.subheader("🔍 Individual Student Assessment")
    col1, col2 = st.columns(2)
    with col1:
        batch_name = st.text_input("Batch Tag", "Fall-2026-CS-4")
        student_id = st.text_input("Student ID", "UET-2026-001")
        subject = st.text_input("Subject Name", "Artificial Intelligence")
        quiz1 = st.number_input("Quiz 1 (Max: 10)", 0.0, 10.0, 7.0)
        quiz2 = st.number_input("Quiz 2 (Max: 10)", 0.0, 10.0, 8.0)
    with col2:
        assignment1 = st.number_input("Assignment 1 (Max: 7.5)", 0.0, 15.0, 6.0)
        assignment2 = st.number_input("Assignment 2 (Max: 7.5)", 0.0, 15.0, 6.5)
        midterm = st.number_input("Midterm Examination (Max: 40)", 0.0, 40.0, 28.0)
        final = st.number_input("Final Term Examination (Optional - Max: 50)", 0.0, 50.0, 0.0)

    if st.button("Evaluate Student Profile"):
        sample = pd.DataFrame([[quiz1, quiz2, assignment1, assignment2, midterm]], columns=REQUIRED_COLS)
        pred = model.predict(sample)[0]
        prob = model.predict_proba(sample)[0][1] * 100
        
        max_scale = 125.0 if final > 0 else 75.0
        total = quiz1 + quiz2 + assignment1 + assignment2 + midterm + final
        gpa, grade = marks_to_gpa(total, max_possible=max_scale)
        
        status = "At Risk" if pred == 1 or gpa < 2.0 else "No Risk"

        if status == "At Risk": st.error(f"⚠️ Status: AT RISK (GPA < 2.0 or Model Triggered) — Risk Probability: {prob:.1f}%")
        else: st.success(f"✅ Status: PASS / NO RISK — Risk Probability: {prob:.1f}%")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Score", f"{total:.1f} / {max_scale}")
        with c2: st.metric("Course Grade", f"{grade} ({gpa:.1f})")
        with c3: st.metric("Risk Probability", f"{prob:.1f}%")
        with c4: st.metric("Evaluation Status", status)

elif page == "Database Logs & Batches":
    st.subheader("🗃️ Institutional Evaluation Logs")
    conn = get_db_connection()
    logs_df = pd.read_sql_query("SELECT * FROM evaluations ORDER BY timestamp DESC", conn)
    conn.close()

    if logs_df.empty:
        st.info("No records found in the database.")
    else:
        batches = ["All Batches"] + list(logs_df["batch_name"].dropna().unique())
        selected_batch = st.selectbox("Filter by Batch", batches)
        filtered = logs_df if selected_batch == "All Batches" else logs_df[logs_df["batch_name"] == selected_batch]
        render_styled_dataframe(filtered)

        excel_bytes = convert_df_to_excel(filtered)
        st.download_button(
            label="📥 Download Filtered Logs (Excel)",
            data=excel_bytes,
            file_name=f"EduGuard_Logs_{selected_batch.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )