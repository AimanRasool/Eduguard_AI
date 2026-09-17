import io
import os
import zipfile

import mysql.connector
import numpy as np
import pandas as pd
import streamlit as st

from sklearn.ensemble import RandomForestClassifier


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EduGuard-AI SaaS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS & MYSQL CONNECTION
# ============================================================

REQUIRED_COLS = [
    "quiz1",
    "quiz2",
    "assignment1",
    "assignment2",
    "midterm",
]

def get_db_connection():
    """Establish connection to MySQL using Streamlit secrets."""
    db_config = st.secrets["mysql"]
    conn = mysql.connector.connect(
        host=db_config["host"],
        port=db_config.get("port", 3306),
        database=db_config["database"],
        user=db_config["username"],
        password=db_config["password"]
    )
    return conn


# ============================================================
# CUSTOM PROFESSIONAL CSS
# ============================================================

st.markdown(
    """
    <style>
    .main { padding-top: 0rem; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .hero-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .hero-container h1 { color: white; font-weight: 700; }
    .hero-container p { color: #e0e0e0; font-size: 1.1rem; }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE SETUP & MIGRATION
# ============================================================

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
            quiz1 FLOAT,
            quiz2 FLOAT,
            assignment1 FLOAT,
            assignment2 FLOAT,
            midterm FLOAT,
            risk_status VARCHAR(50),
            probability FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()

init_db()


# ============================================================
# BASELINE ML MODEL
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

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(df_train[REQUIRED_COLS], y_train)
    return model

model = get_trained_model()


# ============================================================
# MULTI-SUBJECT FILE PARSER
# ============================================================

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

            sub_df["quiz1"] = pd.to_numeric(pd.Series(data_subset.iloc[:, q1_idx].values if q1_idx is not None else 0), errors="coerce").fillna(0)
            sub_df["quiz2"] = pd.to_numeric(pd.Series(data_subset.iloc[:, q2_idx].values if q2_idx is not None else 0), errors="coerce").fillna(0)
            
            val_asg = pd.to_numeric(pd.Series(data_subset.iloc[:, asg_idx].values if asg_idx is not None else 0), errors="coerce").fillna(0)
            sub_df["assignment1"] = val_asg / 2.0
            sub_df["assignment2"] = val_asg / 2.0

            sub_df["midterm"] = pd.to_numeric(pd.Series(data_subset.iloc[:, mid_idx].values if mid_idx is not None else 0), errors="coerce").fillna(0)
            
            parsed_subjects_data[subj] = sub_df

        return parsed_subjects_data, "multi_subject"
    
    else:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return {"General Course": df}, "flat"


def save_batch_to_database(df, subject_name, batch_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        student_id = str(row.get("Student_ID", "Unknown"))
        cursor.execute(
            """
            INSERT INTO evaluations (
                batch_name, student_id, subject, quiz1, quiz2, assignment1, assignment2, midterm, risk_status, probability
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                batch_name,
                student_id,
                subject_name,
                float(row["quiz1"]),
                float(row["quiz2"]),
                float(row["assignment1"]),
                float(row["assignment2"]),
                float(row["midterm"]),
                str(row["Evaluation"]),
                float(row["Risk_Probability"]),
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()


def get_intervention(total_score, midterm):
    recommendations = []
    if midterm < 20:
        recommendations.append("Priority counseling and midterm remediation.")
    if total_score < 37.5:
        recommendations.append("Assign remedial exercises and additional practice.")
    if midterm >= 20 and total_score < 45:
        recommendations.append("Monitor upcoming quizzes and assignments closely.")
    if not recommendations:
        recommendations.append("Continue normal academic monitoring.")
    return " ".join(recommendations)


def marks_to_gpa(total_marks):
    percentage = (total_marks / 75.0) * 100
    if percentage >= 85: return 4.0, "A+"
    elif percentage >= 80: return 4.0, "A"
    elif percentage >= 75: return 3.7, "B+"
    elif percentage >= 70: return 3.3, "B"
    elif percentage >= 65: return 3.0, "C+"
    elif percentage >= 60: return 2.7, "C"
    elif percentage >= 50: return 2.0, "D"
    else: return 0.0, "F"


def color_risk_rows(row):
    """Applies soft red styling for At Risk and soft green for No Risk."""
    status = str(row.get("Evaluation", row.get("Overall_Status", "")))
    if "At Risk" in status:
        return ["background-color: #f8d7da; color: #721c24"] * len(row)
    elif "No Risk" in status:
        return ["background-color: #d4edda; color: #155724"] * len(row)
    return [""] * len(row)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🎓 EduGuard-AI")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Home",
        "📊 Dashboard",
        "📂 Batch Evaluation & CGPA",
        "🔍 Single Student",
        "🗃️ Database Logs & Batches",
    ],
)


# ============================================================
# PAGE 0 — HOME PAGE
# ============================================================

if page == "🏠 Home":
    st.markdown(
        """
        <div class="hero-container">
            <h1>Welcome to EduGuard-AI 🎓</h1>
            <p>Advanced Academic Risk Evaluation & Multi-Course Semester CGPA Intelligence Platform</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Platform Overview")
        st.markdown(
            """
            EduGuard-AI empowers educators and academic departments to seamlessly analyze student performance, 
            predict academic risk using machine learning classifiers, compute semester-wide CGPAs, and generate 
            actionable early intervention roadmaps.
            
            * **Automated Risk Scoring:** Evaluates quizzes, assignments, and midterms.
            * **Multi-Subject Batch Processing:** Upload complex spreadsheets covering multiple courses at once.
            * **Comprehensive CGPA Engine:** Calculates overall semester GPA and cumulative quality points instantly.
            """
        )
    with col2:
        st.subheader("⚡ Quick Start")
        st.markdown("Ready to evaluate student performance for the current semester?")
        if st.button("🚀 Go to Batch Evaluation & Start Now", type="primary", use_container_width=True):
            st.switch_page = "📂 Batch Evaluation & CGPA" # Streamlit state trick or prompt user
            st.info("Please select **📂 Batch Evaluation & CGPA** from the sidebar menu on the left to upload your marksheet.")

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 Real-Time Analytics")
        st.markdown("Instant visibility into department-wide risk percentages, grade distributions, and trends.")
    with col2:
        st.markdown("### 🛡️ Early Interventions")
        st.markdown("Automated recommendation system flagging students needing priority counseling or remediation.")
    with col3:
        st.markdown("### 🗃️ Secure MySQL Storage")
        st.markdown("All batch logs and student evaluations are stored securely in your connected MySQL database.")


# ============================================================
# PAGE 1 — DASHBOARD
# ============================================================

elif page == "📊 Dashboard":
    st.header("📊 Executive Analytics Dashboard")
    st.markdown("High-level overview of student performance records stored in the database.")
    
    conn = get_db_connection()
    logs_df = pd.read_sql_query("SELECT * FROM evaluations ORDER BY timestamp DESC", conn)
    conn.close()

    total_evaluations = len(logs_df)
    if total_evaluations > 0:
        at_risk = int((logs_df["risk_status"] == "At Risk").sum())
        safe = int((logs_df["risk_status"] == "No Risk").sum())
        risk_percentage = (at_risk / total_evaluations) * 100
    else:
        at_risk, safe, risk_percentage = 0, 0, 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Evaluations", total_evaluations, delta="Records")
    with col2:
        st.metric("Students At Risk", at_risk, delta_color="inverse")
    with col3:
        st.metric("No Risk Students", safe)
    with col4:
        st.metric("Department Risk Rate", f"{risk_percentage:.1f}%")

    if not logs_df.empty:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Risk Distribution Status")
            st.bar_chart(logs_df["risk_status"].value_counts())
        with col2:
            st.subheader("Evaluations by Batch Tag")
            if "batch_name" in logs_df.columns:
                st.bar_chart(logs_df["batch_name"].value_counts())
        
        st.divider()
        st.subheader("Recent Evaluation Logs")
        styled_logs = logs_df.head(25).style.apply(
            lambda r: ["background-color: #f8d7da; color: #721c24" if r["risk_status"] == "At Risk" else "background-color: #d4edda; color: #155724" for _ in r], 
            axis=1
        )
        st.dataframe(styled_logs, use_container_width=True, height=400)
    else:
        st.info("No student evaluations logged yet. Navigate to **📂 Batch Evaluation & CGPA** to begin.")


# ============================================================
# PAGE 2 — BATCH EVALUATION & CGPA
# ============================================================

elif page == "📂 Batch Evaluation & CGPA":
    st.header("📂 Batch Semester Student Evaluation & CGPA Calculator")
    st.markdown("Upload your semester marksheet spreadsheet, tag your batch, and run evaluations.")

    batch_name = st.text_input("🏷️ Enter Batch / Semester Tag", "Fall-2026-CS-4")
    uploaded_file = st.file_uploader("Upload Semester Dataset (CSV, Excel, or ZIP)", type=["csv", "xlsx", "xls", "zip"])

    if uploaded_file is not None:
        try:
            subjects_data, file_type = load_multi_subject_file(uploaded_file)
            st.success(f"Successfully loaded dataset ({file_type} layout). Total subjects detected: {len(subjects_data)}")

            st.sidebar.divider()
            st.sidebar.subheader("Evaluation Scope Options")
            eval_mode = st.sidebar.radio(
                "Choose Mode", ["Single Course Evaluation", "Overall CGPA & Multi-Course"]
            )

            if eval_mode == "Single Course Evaluation":
                selected_subject = st.sidebar.selectbox("Select Course for Deep-Dive", list(subjects_data.keys()))
                input_df = subjects_data[selected_subject]

                if "Student_ID" not in input_df.columns:
                    input_df["Student_ID"] = [f"STUDENT-{i+1:03d}" for i in range(len(input_df))]

                st.subheader(f"Preview: {selected_subject} ({len(input_df)} Students)")
                st.dataframe(input_df.head(10), use_container_width=True, height=300)

                if st.button(f"🤖 Run AI Evaluation for {selected_subject} ({batch_name})", type="primary"):
                    with st.spinner("Running machine learning risk evaluation..."):
                        features = input_df[REQUIRED_COLS]
                        predictions = model.predict(features)
                        probabilities = model.predict_proba(features)[:, 1]

                        input_df["Evaluation"] = ["At Risk" if p == 1 else "No Risk" for p in predictions]
                        input_df["Risk_Probability"] = (probabilities * 100).round(1)
                        input_df["Total_Score"] = input_df[REQUIRED_COLS].sum(axis=1)
                        
                        gpa_list, grade_list = [], []
                        for _, r in input_df.iterrows():
                            g, gr = marks_to_gpa(r["Total_Score"])
                            gpa_list.append(g)
                            grade_list.append(gr)
                        input_df["GPA"] = gpa_list
                        input_df["Grade"] = grade_list

                        input_df["Recommendation"] = input_df.apply(
                            lambda row: get_intervention(row["Total_Score"], row["midterm"]), axis=1
                        )

                        save_batch_to_database(input_df, selected_subject, batch_name)

                    st.success(f"Evaluation for {selected_subject} under batch '{batch_name}' saved to MySQL!")

                    risk_count = int((input_df["Evaluation"] == "At Risk").sum())
                    safe_count = int((input_df["Evaluation"] == "No Risk").sum())

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Students", len(input_df))
                    with col2:
                        st.metric("At Risk", risk_count, delta_color="inverse")
                    with col3:
                        st.metric("No Risk", safe_count)

                    st.subheader("Evaluation Results (Color-Coded)")
                    styled_df = input_df.style.apply(color_risk_rows, axis=1)
                    st.dataframe(styled_df, use_container_width=True, height=450)

                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        input_df.to_excel(writer, index=False, sheet_name="Evaluations")
                    processed_data = output.getvalue()

                    st.download_button(
                        label=f"📥 Download Report for {selected_subject} ({batch_name})",
                        data=processed_data,
                        file_name=f"EduGuard_{batch_name}_{selected_subject.replace(' ', '_')}_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

            else:
                st.subheader("🌐 Overall Semester CGPA & Multi-Course Analysis")
                selected_courses = st.sidebar.multiselect(
                    "Select Courses to Include in CGPA", 
                    list(subjects_data.keys()), 
                    default=list(subjects_data.keys())
                )
                credit_hours_per_course = st.sidebar.number_input("Credit Hours per Course", 1, 4, 3)

                if selected_courses and st.button(f"📊 Calculate Overall CGPA & Save Batch ({batch_name})", type="primary"):
                    with st.spinner("Aggregating multi-course scores and calculating CGPA..."):
                        base_students = subjects_data[selected_courses[0]][["Student_ID", "Student_Name"]].copy()
                        
                        cgpa_records = []
                        for _, student in base_students.iterrows():
                            sid = student["Student_ID"]
                            sname = student["Student_Name"]
                            
                            total_quality_points = 0.0
                            total_credits = 0.0
                            course_breakdown = {}
                            overall_risk_flag = False

                            for course in selected_courses:
                                course_df = subjects_data[course]
                                student_row = course_df[course_df["Student_ID"] == sid]
                                
                                if not student_row.empty:
                                    r = student_row.iloc[0]
                                    t_score = r["quiz1"] + r["quiz2"] + r["assignment1"] + r["assignment2"] + r["midterm"]
                                    
                                    sample = pd.DataFrame([[r["quiz1"], r["quiz2"], r["assignment1"], r["assignment2"], r["midterm"]]], columns=REQUIRED_COLS)
                                    pred = model.predict(sample)[0]
                                    if pred == 1:
                                        overall_risk_flag = True

                                    gp, grade = marks_to_gpa(t_score)
                                    total_quality_points += gp * credit_hours_per_course
                                    total_credits += credit_hours_per_course
                                    course_breakdown[f"{course} (Marks)"] = t_score
                                    course_breakdown[f"{course} (Grade)"] = grade

                            cgpa = round(total_quality_points / total_credits, 2) if total_credits > 0 else 0.0
                            overall_status = "At Risk" if overall_risk_flag or cgpa < 2.0 else "No Risk"

                            record = {
                                "Student_ID": sid,
                                "Student_Name": sname,
                                "CGPA": cgpa,
                                "Overall_Status": overall_status
                            }
                            record.update(course_breakdown)
                            cgpa_records.append(record)

                        cgpa_df = pd.DataFrame(cgpa_records)

                    st.success("Overall CGPA calculation complete!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Evaluated Students", len(cgpa_df))
                    with col2:
                        st.metric("Average Semester CGPA", f"{cgpa_df['CGPA'].mean():.2f}")
                    with col3:
                        st.metric("Overall At Risk", int((cgpa_df["Overall_Status"] == "At Risk").sum()), delta_color="inverse")

                    st.subheader("Comprehensive Semester CGPA Summary (CGPA First)")
                    styled_cgpa_df = cgpa_df.style.apply(color_risk_rows, axis=1)
                    st.dataframe(styled_cgpa_df, use_container_width=True, height=500)

                    output_cgpa = io.BytesIO()
                    with pd.ExcelWriter(output_cgpa, engine="openpyxl") as writer:
                        cgpa_df.to_excel(writer, index=False, sheet_name="CGPA_Summary")
                    cgpa_processed = output_cgpa.getvalue()

                    st.download_button(
                        label=f"📥 Download Overall CGPA Report ({batch_name})",
                        data=cgpa_processed,
                        file_name=f"EduGuard_{batch_name}_Overall_CGPA_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                elif not selected_courses:
                    st.warning("Please select at least one course from the sidebar.")

        except Exception as e:
                st.error(f"Dataset processing failed: {e}")


# ============================================================
# PAGE 3 — SINGLE STUDENT
# ============================================================

elif page == "🔍 Single Student":
    st.header("🔍 Individual Student Risk Assessment")
    st.markdown("Evaluate a single student profile manually.")
    
    col1, col2 = st.columns(2)
    with col1:
        batch_name = st.text_input("Batch / Semester Tag", "Fall-2026-CS-4")
        student_id = st.text_input("Student Registration ID", "UET-2026-001")
        subject_name = st.text_input("Subject Name", "Artificial Intelligence")
        quiz1 = st.number_input("Quiz 1 Marks (Max 10)", 0.0, 10.0, 6.0)
    with col2:
        quiz2 = st.number_input("Quiz 2 Marks (Max 10)", 0.0, 10.0, 7.0)
        assignment1 = st.number_input("Assignment 1 Marks (Max 7.5)", 0.0, 15.0, 5.0)
        assignment2 = st.number_input("Assignment 2 Marks (Max 7.5)", 0.0, 15.0, 6.0)
        midterm = st.number_input("Midterm Marks (Max 40)", 0.0, 40.0, 22.0)

    if st.button("🤖 Evaluate Student Profile", type="primary"):
        sample = pd.DataFrame([[quiz1, quiz2, assignment1, assignment2, midterm]], columns=REQUIRED_COLS)
        prediction = model.predict(sample)[0]
        probability = model.predict_proba(sample)[0][1] * 100
        total_score = quiz1 + quiz2 + assignment1 + assignment2 + midterm
        gpa, grade = marks_to_gpa(total_score)
        status = "At Risk" if prediction == 1 else "No Risk"
        recommendation = get_intervention(total_score, midterm)

        st.divider()
        if status == "At Risk":
            st.error(f"⚠️ AT RISK STATUS — Estimated Risk Probability: {probability:.1f}%")
        else:
            st.success(f"✅ NO RISK STATUS — Estimated Risk Probability: {probability:.1f}%")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Score", f"{total_score:.1f} / 75")
        with col2:
            st.metric("Course Grade", f"{grade} ({gpa:.1f})")
        with col3:
            st.metric("Risk Probability", f"{probability:.1f}%")
        with col4:
            st.metric("Evaluation", status)

        st.subheader("🎯 Recommended Intervention")
        st.info(recommendation)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO evaluations (batch_name, student_id, subject, quiz1, quiz2, assignment1, assignment2, midterm, risk_status, probability)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (batch_name, student_id, subject_name, float(quiz1), float(quiz2), float(assignment1), float(assignment2), float(midterm), status, float(probability)),
        )
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Evaluation successfully logged to MySQL database.")


# ============================================================
# PAGE 4 — DATABASE LOGS & BATCHES
# ============================================================

elif page == "🗃️ Database Logs & Batches":
    st.header("🗃️ Batch & Semester Evaluation Logs")
    st.markdown("Inspect historical records stored in your MySQL database.")
    
    conn = get_db_connection()
    logs_df = pd.read_sql_query("SELECT * FROM evaluations ORDER BY timestamp DESC", conn)
    conn.close()

    if logs_df.empty:
        st.info("No evaluation records found in database.")
    else:
        batches = ["All Batches"] + list(logs_df["batch_name"].dropna().unique())
        selected_batch_filter = st.selectbox("📂 Filter by Batch / Semester", batches)

        filtered_df = logs_df.copy()
        if selected_batch_filter != "All Batches":
            filtered_df = filtered_df[filtered_df["batch_name"] == selected_batch_filter]

        search = st.text_input("🔎 Search Student Registration ID")
        if search:
            filtered_df = filtered_df[filtered_df["student_id"].astype(str).str.contains(search, case=False, na=False)]

        risk_filter = st.selectbox("Filter by Risk Status", ["All", "At Risk", "No Risk"])
        if risk_filter != "All":
            filtered_df = filtered_df[filtered_df["risk_status"] == risk_filter]

        st.write(f"Showing {len(filtered_df)} records for batch: **{selected_batch_filter}**")
        
        styled_filtered_df = filtered_df.style.apply(
            lambda r: ["background-color: #f8d7da; color: #721c24" if r["risk_status"] == "At Risk" else "background-color: #d4edda; color: #155724" for _ in r], 
            axis=1
        )
        st.dataframe(styled_filtered_df, use_container_width=True, height=500)

        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download Logs for [{selected_batch_filter}]",
            data=csv_data,
            file_name=f"EduGuard_{selected_batch_filter}_Logs.csv",
            mime="text/csv",
        )