# import base64
# import os
# import pandas as pd
# import streamlit as st
# from utils import highlight_risk_rows, send_bulk_performance_emails

# # ==========================================
# # PAGE CONFIGURATION
# # ==========================================
# st.set_page_config(
#     page_title="EduGuard-AI | UET Mardan",
#     page_icon="🎓",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )


# # ==========================================
# # HELPER FUNCTIONS
# # ==========================================
# def get_base64_image(image_path):
#   if os.path.exists(image_path):
#     with open(image_path, "rb") as img_file:
#       return base64.b64encode(img_file.read()).decode("utf-8")
#   return ""


# # ==========================================
# # HEADER & FOOTER COMPONENTS (OFFICIAL UET BLUE THEME)
# # ==========================================
# def render_header():
#   st.markdown(
#       """
#         <style>
#             .edu-header {
#                 background: linear-gradient(135deg, #0b3c5d 0%, #1d2d50 100%);
#                 color: white;
#                 padding: 20px 30px;
#                 border-radius: 10px;
#                 box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#                 margin-bottom: 20px;
#                 border-left: 6px solid #f39c12;
#             }
#             .edu-header h2 {
#                 margin: 0;
#                 font-size: 24px;
#                 font-weight: 700;
#                 letter-spacing: 0.5px;
#             }
#             .edu-header p {
#                 margin: 5px 0 0 0;
#                 font-size: 14px;
#                 color: #dcdcdc;
#             }
#             .stButton > button {
#                 width: 100%;
#                 background-color: #0b3c5d;
#                 color: white;
#                 border: 1px solid #082b42;
#                 border-radius: 6px;
#                 font-weight: 600;
#                 padding: 0.5rem 1rem;
#                 transition: all 0.3s ease;
#             }
#             .stButton > button:hover {
#                 background-color: #f39c12;
#                 color: #0b3c5d;
#                 border-color: #e08e0b;
#             }
#             .edu-footer {
#                 background: #0b3c5d;
#                 color: #ffffff;
#                 text-align: center;
#                 padding: 18px;
#                 border-radius: 8px;
#                 margin-top: 50px;
#                 font-size: 13px;
#                 border-top: 4px solid #f39c12;
#             }
#             .feature-card {
#                 background-color: #f8f9fa;
#                 border: 1px solid #e9ecef;
#                 padding: 20px;
#                 border-radius: 8px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#                 height: 100%;
#             }
#             /* Enforce uniform fixed height and clean cropping for all card images */
#             .feature-card img {
#                 width: 100% !important;
#                 height: 180px !important;
#                 object-fit: cover !important;
#                 object-position: center !important;
#                 border-radius: 6px;
#                 margin-bottom: 12px;
#             }
#             .block-container {
#                 padding-top: 2rem;
#                 padding-bottom: 3rem;
#             }
#         </style>
        
#         <div class="edu-header">
#             <h2>EduGuard-AI</h2>
#             <p>Department of Computer Science & Software Engineering &bull; University of Engineering and Technology (UET) Mardan</p>
#         </div>
#     """,
#       unsafe_allow_html=True,
#   )


# def render_footer():
#   st.markdown(
#       """
#         <div class="edu-footer">
#             <b>EduGuard-AI Academic Evaluation System</b> &bull; Department of Computer Science & Software Engineering<br>
#             University of Engineering and Technology (UET) Mardan, KPK, Pakistan &copy; 2026. All Rights Reserved.
#         </div>
#     """,
#       unsafe_allow_html=True,
#   )


# def render_navbar():
#   col1, col2, col3, col4, col5 = st.columns(5)
#   with col1:
#     if st.button("Home", use_container_width=True):
#       st.session_state["nav"] = "Home"
#   with col2:
#     if st.button("Dashboard", use_container_width=True):
#       st.session_state["nav"] = "Dashboard"
#   with col3:
#     if st.button("Batch Evaluation & CGPA", use_container_width=True):
#       st.session_state["nav"] = "Batch Evaluation"
#   with col4:
#     if st.button("Single Student", use_container_width=True):
#       st.session_state["nav"] = "Single Student"
#   with col5:
#     if st.button("Database Logs & Batches", use_container_width=True):
#       st.session_state["nav"] = "Database Logs"
#   st.markdown("---")


# if "nav" not in st.session_state:
#   st.session_state["nav"] = "Home"

# render_header()
# render_navbar()

# current_page = st.session_state["nav"]


# # ==========================================
# # PAGE: HOME
# # ==========================================
# if current_page == "Home":
#   # 1. Main Banner Image on Upper Area
#   local_image_path = "uet_banner.jpg"
#   if os.path.exists(local_image_path):
#     st.image(
#         local_image_path,
#         use_container_width=True,
#         caption=(
#             "UET Mardan - Excellence in Engineering and Computing Education"
#         ),
#     )

#   st.markdown("<br>", unsafe_allow_html=True)

#   # 2. Welcome Section After the Picture
#   st.markdown("### Welcome to EduGuard-AI Decision Support")
#   st.write(
#       "EduGuard-AI is an advanced institutional analytics and early-warning"
#       " framework engineered specifically for the Department of Computer"
#       " Science & Software Engineering at UET Mardan. It combines continuous"
#       " assessment monitoring, machine learning risk classification, and"
#       " automated multi-channel reporting to support academic advisors."
#   )

#   st.markdown("<br>", unsafe_allow_html=True)

#   # 3. Three Feature Cards with Uniform Images via Base64 HTML Tag
#   col1, col2, col3 = st.columns(3)

#   img1_b64 = get_base64_image("predictive_img.jpg")
#   img2_b64 = get_base64_image("batch_img.jpg")
#   img3_b64 = get_base64_image("automated.jpg")

#   with col1:
   
#     if img1_b64:
#       st.markdown(
#           f'<img src="data:image/jpeg;base64,{img1_b64}" style="width:100%;'
#           " height:160px; object-fit:cover; border-radius:6px;"
#           ' margin-bottom:12px;">',
#           unsafe_allow_html=True,
#       )
#     else:
#       st.info("Upload `predictive_img.jpg`")
#     st.markdown("#### Predictive Analytics")
#     st.write(
#         "Utilizes trained models and SHAP explainability to pinpoint students"
#         " requiring academic support early in the semester."
#     )
#     st.markdown("</div>", unsafe_allow_html=True)

#   with col2:
    
#     if img2_b64:
#       st.markdown(
#           f'<img src="data:image/jpeg;base64,{img2_b64}" style="width:100%;'
#           " height:160px; object-fit:cover; border-radius:6px;"
#           ' margin-bottom:12px;">',
#           unsafe_allow_html=True,
#       )
#     else:
#       st.info("Upload `batch_img.jpg`")
#     st.markdown("#### Batch Processing")
#     st.write(
#         "Seamlessly ingest CSV, Excel, or bulk ZIP grade records to compute"
#         " precise semester GPAs, CGPAs, and categorical risk tags."
#     )
#     st.markdown("</div>", unsafe_allow_html=True)

#   with col3:
   
#     if img3_b64:
#       st.markdown(
#           f'<img src="data:image/jpeg;base64,{img3_b64}" style="width:100%;'
#           " height:160px; object-fit:cover; border-radius:6px;"
#           ' margin-bottom:12px;">',
#           unsafe_allow_html=True,
#       )
#     else:
#       st.info("Upload `automated.jpg`")
#     st.markdown("#### Automated Advisory")
#     st.write(
#         "Dispatches personalized performance notices and feedback digests"
#         " directly to students or advisors securely via SMTP."
#     )
#     st.markdown("</div>", unsafe_allow_html=True)


# # ==========================================
# # PAGE: DASHBOARD
# # ==========================================
# elif current_page == "Dashboard":
#   st.markdown("### Faculty Analytics Dashboard")
#   st.write(
#       "Overview of department-wide academic standing and active risk"
#       " distribution."
#   )

#   col1, col2, col3, col4 = st.columns(4)
#   col1.metric("Total Active Students", "342", "+12")
#   col2.metric("At-Risk Students", "28", "-4")
#   col3.metric("Average Department CGPA", "2.94", "+0.05")
#   col4.metric("Batch Evaluation Status", "Up to Date", "Active")

#   st.markdown("---")
#   st.info(
#       "Upload or select a batch dataset in the **Batch Evaluation & CGPA** tab"
#       " to generate live distribution charts and analytics."
#   )
#   st.markdown("<br><br><br>", unsafe_allow_html=True)


# # ==========================================
# # PAGE: BATCH EVALUATION & CGPA
# # ==========================================
# elif current_page == "Batch Evaluation":
#   st.markdown("### Batch Semester Student Evaluation & CGPA Calculator")
#   st.write(
#       "Upload department grade sheets or CSV datasets to configure course"
#       " credit hours, run automated risk evaluations, and send individual"
#       " student reports."
#   )

#   batch_tag = st.text_input("Batch Tag / ID", "Fall-2026-CS-4")
#   uploaded_file = st.file_uploader(
#       "Upload Course Grades Dataset (CSV, Excel, or ZIP)",
#       type=["csv", "xlsx", "zip"],
#   )

#   if uploaded_file:
#     try:
#       if uploaded_file.name.endswith(".csv"):
#         df = pd.read_csv(uploaded_file)
#       else:
#         df = pd.read_excel(uploaded_file)

#       ignore_keywords = [
#           "s. no",
#           "roll no",
#           "name",
#           "f_name",
#           "program",
#           "email",
#           "unnamed",
#       ]
#       available_columns = [
#           col
#           for col in df.columns
#           if not any(kw in str(col).lower() for kw in ignore_keywords)
#       ]

#       st.success(
#           f"Successfully loaded dataset: {uploaded_file.name} ({len(df)}"
#           " records)"
#       )

#       st.markdown("---")
#       st.markdown("### Select Relevant Courses for Evaluation")
#       selected_courses = []
#       if available_columns:
#         cols_checkbox = st.columns(min(len(available_columns), 3))
#         for idx, col in enumerate(available_columns):
#           with cols_checkbox[idx % len(cols_checkbox)]:
#             if st.checkbox(f"{col}", value=True, key=f"chk_{col}T"):
#               selected_courses.append(col)
#       else:
#         selected_courses = available_columns

#       if selected_courses:
#         if st.button("Run Batch Evaluation"):
#           if "Evaluation" not in df.columns:
#             eval_statuses = []
#             for _, r in df.iterrows():
#               scores = pd.to_numeric(r[selected_courses], errors="coerce")
#               if scores.min() < 35 or (
#                   scores.mean() < 50 and pd.notna(scores.mean())
#               ):
#                 eval_statuses.append("At Risk")
#               else:
#                 eval_statuses.append("No Risk")
#             df["Evaluation"] = eval_statuses

#           st.session_state["active_df"] = df
#           st.session_state["selected_courses"] = selected_courses
#           st.success("Batch evaluation completed successfully!")
#     except Exception as e:
#       st.error(f"Error reading file: {e}")

#   if "active_df" in st.session_state:
#     st.markdown("---")
#     st.markdown("### Evaluated Dataset")
#     active_df = st.session_state["active_df"]
#     st.dataframe(
#         active_df.style.apply(highlight_risk_rows, axis=1),
#         use_container_width=True,
#     )

#   st.markdown("<br><br>", unsafe_allow_html=True)


# # ==========================================
# # PAGE: SINGLE STUDENT (SEARCH & ADD NEW STUDENT)
# # ==========================================
# elif current_page == "Single Student":
#   st.markdown("### Single Student Diagnostics & Advising")
#   st.write(
#       "Search existing student records or **add a new student** to the active"
#       " session database with automated risk evaluation."
#   )

#   tab_search, tab_add = st.tabs(
#       ["Search Existing Student", "Add New Student Record"]
#   )

#   with tab_search:
#     student_search_id = st.text_input(
#         "Enter Student ID / Roll No. to Search (e.g., 24-FA-04626):", ""
#     )
#     if student_search_id:
#       if "active_df" in st.session_state:
#         match_df = st.session_state["active_df"][
#             st.session_state["active_df"]
#             .astype(str)
#             .apply(lambda x: x.str.contains(student_search_id))
#             .any(axis=1)
#         ]
#         if not match_df.empty:
#           st.success(f"Found record for {student_search_id}")
#           st.dataframe(
#               match_df.style.apply(highlight_risk_rows, axis=1),
#               use_container_width=True,
#           )
#           student_row = match_df.iloc[0]
#         else:
#           st.warning(
#               "Student ID not found in the currently loaded dataset."
#           )
#           student_row = None
#       else:
#         st.warning(
#             "No batch dataset loaded. Please upload a dataset in 'Batch"
#             " Evaluation & CGPA' or add the student using the 'Add New Student"
#             " Record' tab."
#         )
#         student_row = None

#       if student_row is not None:
#         with st.expander("Send Individual Student Advisory Notice"):
#           ind_host = st.text_input(
#               "SMTP Host", value="smtp.gmail.com", key="ih"
#           )
#           ind_port = st.number_input("SMTP Port", value=587, step=1, key="ip")
#           ind_sender = st.text_input("Sender Email", value="", key="is")
#           ind_pass = st.text_input(
#               "Sender App Password", type="password", value="", key="ipass"
#           )
#           ind_recipient = st.text_input(
#               "Student / Recipient Email Address", value="", key="irec"
#           )

#           if st.button("Send Single Advisory Notice"):
#             if not ind_sender or not ind_pass or not ind_recipient:
#               st.error(
#                   "Please fill in sender credentials and recipient email."
#               )
#             else:
#               smtp_config = {
#                   "host": ind_host,
#                   "port": int(ind_port),
#                   "sender_email": ind_sender,
#                   "sender_password": ind_pass,
#               }
#               df_single = pd.DataFrame([student_row])
#               with st.spinner("Sending individual notice..."):
#                 count, err = send_bulk_performance_emails(
#                     df_single,
#                     smtp_config,
#                     specific_student_id=student_search_id,
#                     fallback_email=ind_recipient,
#                 )
#                 if err:
#                   st.warning(f"Notice: {err}")
#                 else:
#                   st.success(
#                       "Individual advisory email sent successfully!"
#                   )

#   with tab_add:
#     st.markdown("#### Enter Student Details")
#     col_a, col_b = st.columns(2)
#     with col_a:
#       new_roll = st.text_input("Roll No. / Student ID", "24-FA-09999")
#       new_name = st.text_input("Student Name", "John Doe")
#     with col_b:
#       new_email = st.text_input(
#           "Student Email Address", "student@uetmardan.edu.pk"
#       )
#       new_program = st.text_input(
#           "Program / Department", "BS Software Engineering"
#       )

#     st.markdown("#### Course Grades / Marks Entry")
#     default_courses = st.session_state.get(
#         "selected_courses",
#         [
#             "OOP",
#             "Data Structures",
#             "Operating Systems",
#             "Artificial Intelligence",
#         ],
#     )

#     new_grades = {}
#     grade_cols = st.columns(min(len(default_courses), 3))
#     for idx, course in enumerate(default_courses):
#       with grade_cols[idx % len(grade_cols)]:
#         new_grades[course] = st.number_input(
#             f"Marks: {course} (0-100)",
#             min_value=0.0,
#             max_value=100.0,
#             value=75.0,
#             step=1.0,
#             key=f"ng_{course}",
#         )

#     if st.button("Save & Evaluate Student"):
#       avg_score = (
#           sum(new_grades.values()) / len(new_grades) if new_grades else 0
#       )
#       min_score = min(new_grades.values()) if new_grades else 0
#       evaluation_status = (
#           "At Risk" if (min_score < 35 or avg_score < 50) else "No Risk"
#       )

#       new_row = {
#           "Roll No.": new_roll,
#           "Name": new_name,
#           "Email": new_email,
#           "Program": new_program,
#           **new_grades,
#           "Evaluation": evaluation_status,
#       }

#       if "active_df" in st.session_state:
#         new_df_row = pd.DataFrame([new_row])
#         st.session_state["active_df"] = pd.concat(
#             [st.session_state["active_df"], new_df_row], ignore_index=True
#         )
#       else:
#         st.session_state["active_df"] = pd.DataFrame([new_row])

#       st.success(
#           f"Student **{new_name} ({new_roll})** successfully added and"
#           f" evaluated as **{evaluation_status}**!"
#       )

#       st.markdown("##### Updated Active Dataset Preview:")
#       st.dataframe(
#           st.session_state["active_df"].style.apply(
#               highlight_risk_rows, axis=1
#           ),
#           use_container_width=True,
#       )

#   st.markdown("<br><br><br>", unsafe_allow_html=True)


# # ==========================================
# # PAGE: DATABASE LOGS & BATCHES
# # ==========================================
# elif current_page == "Database Logs":
#   st.markdown("### Institutional Database Logs & Batches")
#   st.write(
#       "Audit trail of past batch evaluations, system logs, and communication"
#       " histories."
#   )

#   log_data = pd.DataFrame({
#       "Timestamp": ["2026-09-21 21:16", "2026-09-20 18:30", "2026-09-18 10:15"],
#       "Batch Tag": ["Fall-2026-CS-4", "Fall-2026-SE-2", "Spring-2026-CS-6"],
#       "Records Processed": [45, 52, 38],
#       "Action": [
#           "Batch Evaluation & Emails",
#           "CGPA Calculation",
#           "Risk Assessment",
#       ],
#       "Status": ["Completed", "Completed", "Completed"],
#   })
#   st.dataframe(log_data, use_container_width=True)
#   st.markdown("<br><br><br>", unsafe_allow_html=True)


# # ==========================================
# # GLOBAL FOOTER RENDER
# # ==========================================
# render_footer()

import base64
import os
import pandas as pd
import streamlit as st
from utils import highlight_risk_rows, send_bulk_performance_emails

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="EduGuard-AI | UET Mardan",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_base64_image(image_path):
  if os.path.exists(image_path):
    with open(image_path, "rb") as img_file:
      return base64.b64encode(img_file.read()).decode("utf-8")
  return ""


def calculate_cgpa_and_grades(df, selected_courses, credit_hours_dict):
  """Calculates individual course grade points, SGPA, and Risk status."""
  updated_df = df.copy()

  sgpas = []
  eval_statuses = []

  for _, row in updated_df.iterrows():
    total_quality_points = 0.0
    total_credits = 0.0
    min_marks = 100.0

    for course in selected_courses:
      marks = pd.to_numeric(row.get(course, 0), errors="coerce")
      if pd.isna(marks):
        marks = 0.0
      if marks < min_marks:
        min_marks = marks

      # Standard grading conversion
      if marks >= 85:
        gp = 4.0
      elif marks >= 80:
        gp = 3.7
      elif marks >= 75:
        gp = 3.3
      elif marks >= 70:
        gp = 3.0
      elif marks >= 65:
        gp = 2.7
      elif marks >= 60:
        gp = 2.3
      elif marks >= 55:
        gp = 2.0
      elif marks >= 50:
        gp = 1.0
      else:
        gp = 0.0

      credits = credit_hours_dict.get(course, 3.0)
      total_quality_points += gp * credits
      total_credits += credits

    sgpa = (
        round(total_quality_points / total_credits, 2)
        if total_credits > 0
        else 0.0
    )
    sgpas.append(sgpa)

    # Risk criteria: min marks below 35 or SGPA below 2.0
    if min_marks < 35 or sgpa < 2.0:
      eval_statuses.append("At Risk")
    else:
      eval_statuses.append("No Risk")

  updated_df["SGPA / CGPA"] = sgpas
  updated_df["Evaluation"] = eval_statuses
  return updated_df


# ==========================================
# HEADER & FOOTER COMPONENTS (OFFICIAL UET BLUE THEME)
# ==========================================
def render_header():
  st.markdown(
      """
        <style>
            .edu-header {
                background: linear-gradient(135deg, #0b3c5d 0%, #1d2d50 100%);
                color: white;
                padding: 20px 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                border-left: 6px solid #f39c12;
            }
            .edu-header h2 {
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            .edu-header p {
                margin: 5px 0 0 0;
                font-size: 14px;
                color: #dcdcdc;
            }
            .stButton > button {
                width: 100%;
                background-color: #0b3c5d;
                color: white;
                border: 1px solid #082b42;
                border-radius: 6px;
                font-weight: 600;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #f39c12;
                color: #0b3c5d;
                border-color: #e08e0b;
            }
            .edu-footer {
                background: #0b3c5d;
                color: #ffffff;
                text-align: center;
                padding: 18px;
                border-radius: 8px;
                margin-top: 50px;
                font-size: 13px;
                border-top: 4px solid #f39c12;
            }
            .feature-card {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                height: 100%;
            }
            .feature-card img {
                width: 100% !important;
                height: 180px !important;
                object-fit: cover !important;
                object-position: center !important;
                border-radius: 6px;
                margin-bottom: 12px;
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
        </style>
        
        <div class="edu-header">
            <h2>EduGuard-AI</h2>
            <p>Department of Computer Science & Software Engineering &bull; University of Engineering and Technology (UET) Mardan</p>
        </div>
    """,
      unsafe_allow_html=True,
  )


def render_footer():
  st.markdown(
      """
        <div class="edu-footer">
            <b>EduGuard-AI Academic Evaluation System</b> &bull; Department of Computer Science & Software Engineering<br>
            University of Engineering and Technology (UET) Mardan, KPK, Pakistan &copy; 2026. All Rights Reserved.
        </div>
    """,
      unsafe_allow_html=True,
  )


def render_navbar():
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    if st.button("Home", use_container_width=True):
      st.session_state["nav"] = "Home"
  with col2:
    if st.button("Dashboard", use_container_width=True):
      st.session_state["nav"] = "Dashboard"
  with col3:
    if st.button("Batch Evaluation & CGPA", use_container_width=True):
      st.session_state["nav"] = "Batch Evaluation"
  with col4:
    if st.button("Single Student", use_container_width=True):
      st.session_state["nav"] = "Single Student"
  with col5:
    if st.button("Database Logs & Batches", use_container_width=True):
      st.session_state["nav"] = "Database Logs"
  st.markdown("---")


if "nav" not in st.session_state:
  st.session_state["nav"] = "Home"

render_header()
render_navbar()

current_page = st.session_state["nav"]


# ==========================================
# PAGE: HOME
# ==========================================
if current_page == "Home":
  local_image_path = "uet_banner.jpg"
  if os.path.exists(local_image_path):
    st.image(
        local_image_path,
        use_container_width=True,
        caption=(
            "UET Mardan - Excellence in Engineering and Computing Education"
        ),
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown("### Welcome to EduGuard-AI Decision Support")
  st.write(
      "EduGuard-AI is an advanced institutional analytics and early-warning"
      " framework engineered specifically for the Department of Computer"
      " Science & Software Engineering at UET Mardan. It combines continuous"
      " assessment monitoring, machine learning risk classification, and"
      " automated multi-channel reporting to support academic advisors."
  )

  st.markdown("<br>", unsafe_allow_html=True)

  col1, col2, col3 = st.columns(3)
  img1_b64 = get_base64_image("predictive_img.jpg")
  img2_b64 = get_base64_image("batch_img.jpg")
  img3_b64 = get_base64_image("automated.jpg")

  with col1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    if img1_b64:
      st.markdown(
          f'<img src="data:image/jpeg;base64,{img1_b64}" style="width:100%;'
          " height:160px; object-fit:cover; border-radius:6px;"
          ' margin-bottom:12px;">',
          unsafe_allow_html=True,
      )
    else:
      st.info("Upload `predictive_img.jpg`")
    st.markdown("#### Predictive Analytics")
    st.write(
        "Utilizes trained models and SHAP explainability to pinpoint students"
        " requiring academic support early in the semester."
    )
    st.markdown("</div>", unsafe_allow_html=True)

  with col2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    if img2_b64:
      st.markdown(
          f'<img src="data:image/jpeg;base64,{img2_b64}" style="width:100%;'
          " height:160px; object-fit:cover; border-radius:6px;"
          ' margin-bottom:12px;">',
          unsafe_allow_html=True,
      )
    else:
      st.info("Upload `batch_img.jpg`")
    st.markdown("#### Batch Processing")
    st.write(
        "Seamlessly ingest CSV, Excel, or bulk ZIP grade records to compute"
        " precise semester GPAs, CGPAs, and categorical risk tags."
    )
    st.markdown("</div>", unsafe_allow_html=True)

  with col3:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    if img3_b64:
      st.markdown(
          f'<img src="data:image/jpeg;base64,{img3_b64}" style="width:100%;'
          " height:160px; object-fit:cover; border-radius:6px;"
          ' margin-bottom:12px;">',
          unsafe_allow_html=True,
      )
    else:
      st.info("Upload `automated.jpg`")
    st.markdown("#### Automated Advisory")
    st.write(
        "Dispatches personalized performance notices and feedback digests"
        " directly to students or advisors securely via SMTP."
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# PAGE: DASHBOARD
# ==========================================
elif current_page == "Dashboard":
  st.markdown("### Faculty Analytics Dashboard")
  st.write(
      "Overview of department-wide academic standing and active risk"
      " distribution."
  )

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Active Students", "342", "+12")
  col2.metric("At-Risk Students", "28", "-4")
  col3.metric("Average Department CGPA", "2.94", "+0.05")
  col4.metric("Batch Evaluation Status", "Up to Date", "Active")

  st.markdown("---")
  st.info(
      "Upload or select a batch dataset in the **Batch Evaluation & CGPA** tab"
      " to generate live distribution charts and analytics."
  )
  st.markdown("<br><br><br>", unsafe_allow_html=True)


# ==========================================
# PAGE: BATCH EVALUATION & CGPA
# ==========================================
elif current_page == "Batch Evaluation":
  st.markdown("### Batch Semester Student Evaluation & CGPA Calculator")
  st.write(
      "Upload department grade sheets or CSV datasets, configure course credit"
      " hours, compute accurate SGPA/CGPA, download clean reports, and send"
      " individual results to all students."
  )

  batch_tag = st.text_input("Batch Tag / ID", "Fall-2026-CS-4")
  uploaded_file = st.file_uploader(
      "Upload Course Grades Dataset (CSV or Excel)", type=["csv", "xlsx"]
  )

  if uploaded_file:
    try:
      if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
      else:
        df = pd.read_excel(uploaded_file)

      ignore_keywords = [
          "s. no",
          "roll no",
          "name",
          "f_name",
          "program",
          "email",
          "unnamed",
          "sgpa",
          "cgpa",
          "evaluation",
      ]
      available_columns = [
          col
          for col in df.columns
          if not any(kw in str(col).lower() for kw in ignore_keywords)
      ]

      st.success(
          f"Successfully loaded dataset: {uploaded_file.name} ({len(df)}"
          " records)"
      )

      st.markdown("---")
      st.markdown(
          "### Select Relevant Courses & Configure Credit Hours (Cr. Hr)"
      )

      selected_courses = []
      credit_hours_dict = {}

      if available_columns:
        cols_per_row = 3
        for i in range(0, len(available_columns), cols_per_row):
          row_cols = st.columns(cols_per_row)
          for j in range(cols_per_row):
            if i + j < len(available_columns):
              col_name = available_columns[i + j]
              with row_cols[j]:
                is_sel = st.checkbox(
                    f"Include {col_name}", value=True, key=f"chk_{col_name}"
                )
                if is_sel:
                  selected_courses.append(col_name)
                  credit_hours_dict[col_name] = st.selectbox(
                      f"Cr. Hr for {col_name}", [3.0, 4.0, 2.0, 1.0], key=f"cr_{col_name}"
                  )
      else:
        selected_courses = available_columns

      if selected_courses:
        if st.button("Run Batch Evaluation & Calculate CGPA"):
          evaluated_df = calculate_cgpa_and_grades(
              df, selected_courses, credit_hours_dict
          )
          st.session_state["active_df"] = evaluated_df
          st.session_state["selected_courses"] = selected_courses
          st.success(
              "Batch evaluation and accurate CGPA calculation completed"
              " successfully!"
          )

    except Exception as e:
      st.error(f"Error reading file: {e}")

  if "active_df" in st.session_state:
    st.markdown("---")
    st.markdown("### Evaluated Dataset & Clean Report")

    active_df = st.session_state["active_df"]

    # Filter/clean unnecessary columns for display and export
    essential_cols = [
        col
        for col in active_df.columns
        if not str(col).lower().startswith("unnamed")
    ]
    display_df = active_df[essential_cols]

    st.dataframe(
        display_df.style.apply(highlight_risk_rows, axis=1),
        use_container_width=True,
    )

    # CSV Download Button
    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Evaluated Results & CGPA as CSV",
        data=csv_data,
        file_name=f"EduGuard_AI_Batch_Results_{batch_tag}.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("### Automated Bulk Email Dispatch to All Students")
    st.write(
        "Send each student an individual email containing only their own"
        " results and CGPA summary."
    )

    with st.expander("Configure SMTP & Send Individual Reports"):
      col_e1, col_e2 = st.columns(2)
      with col_e1:
        smtp_host = st.text_input(
            "SMTP Host", value="smtp.gmail.com", key="batch_sh"
        )
        smtp_port = st.number_input(
            "SMTP Port", value=587, step=1, key="batch_sp"
        )
      with col_e2:
        sender_email = st.text_input("Sender Email", value="", key="batch_se")
        sender_password = st.text_input(
            "Sender App Password", type="password", value="", key="batch_spass"
        )

      if st.button("Send Individual Results to All Students via Email"):
        if not sender_email or not sender_password:
          st.error("Please provide sender email and app password.")
        elif "Email" not in active_df.columns:
          st.error(
              "No 'Email' column found in the dataset to dispatch emails."
          )
        else:
          smtp_config = {
              "host": smtp_host,
              "port": int(smtp_port),
              "sender_email": sender_email,
              "sender_password": sender_password,
          }
          with st.spinner("Dispatching individual emails to all students..."):
            success_count, error_msg = send_bulk_performance_emails(
                active_df, smtp_config
            )
            if error_msg:
              st.warning(f"Completed with notices: {error_msg}")
            else:
              st.success(
                  f"Successfully sent individual result emails to all students!"
              )

  st.markdown("<br><br>", unsafe_allow_html=True)


# ==========================================
# PAGE: SINGLE STUDENT (SEARCH & ADD NEW STUDENT)
# ==========================================
elif current_page == "Single Student":
  st.markdown("### Single Student Diagnostics & Advising")
  st.write(
      "Search existing student records or **add a new student** to the active"
      " session database with automated risk evaluation."
  )

  tab_search, tab_add = st.tabs(
      ["Search Existing Student", "Add New Student Record"]
  )

  with tab_search:
    student_search_id = st.text_input(
        "Enter Student ID / Roll No. to Search (e.g., 24-FA-04626):", ""
    )
    if student_search_id:
      if "active_df" in st.session_state:
        match_df = st.session_state["active_df"][
            st.session_state["active_df"]
            .astype(str)
            .apply(lambda x: x.str.contains(student_search_id))
            .any(axis=1)
        ]
        if not match_df.empty:
          st.success(f"Found record for {student_search_id}")
          st.dataframe(
              match_df.style.apply(highlight_risk_rows, axis=1),
              use_container_width=True,
          )
          student_row = match_df.iloc[0]
        else:
          st.warning(
              "Student ID not found in the currently loaded dataset."
          )
          student_row = None
      else:
        st.warning(
            "No batch dataset loaded. Please upload a dataset in 'Batch"
            " Evaluation & CGPA' or add the student using the 'Add New Student"
            " Record' tab."
        )
        student_row = None

      if student_row is not None:
        with st.expander("Send Individual Student Advisory Notice"):
          ind_host = st.text_input(
              "SMTP Host", value="smtp.gmail.com", key="ih"
          )
          ind_port = st.number_input("SMTP Port", value=587, step=1, key="ip")
          ind_sender = st.text_input("Sender Email", value="", key="is")
          ind_pass = st.text_input(
              "Sender App Password", type="password", value="", key="ipass"
          )
          ind_recipient = st.text_input(
              "Student / Recipient Email Address", value="", key="irec"
          )

          if st.button("Send Single Advisory Notice"):
            if not ind_sender or not ind_pass or not ind_recipient:
              st.error(
                  "Please fill in sender credentials and recipient email."
              )
            else:
              smtp_config = {
                  "host": ind_host,
                  "port": int(ind_port),
                  "sender_email": ind_sender,
                  "sender_password": ind_pass,
              }
              df_single = pd.DataFrame([student_row])
              with st.spinner("Sending individual notice..."):
                count, err = send_bulk_performance_emails(
                    df_single,
                    smtp_config,
                    specific_student_id=student_search_id,
                    fallback_email=ind_recipient,
                )
                if err:
                  st.warning(f"Notice: {err}")
                else:
                  st.success(
                      "Individual advisory email sent successfully!"
                  )

  with tab_add:
    st.markdown("#### Enter Student Details")
    col_a, col_b = st.columns(2)
    with col_a:
      new_roll = st.text_input("Roll No. / Student ID", "24-FA-09999")
      new_name = st.text_input("Student Name", "John Doe")
    with col_b:
      new_email = st.text_input(
          "Student Email Address", "student@uetmardan.edu.pk"
      )
      new_program = st.text_input(
          "Program / Department", "BS Software Engineering"
      )

    st.markdown("#### Course Grades / Marks Entry")
    default_courses = st.session_state.get(
        "selected_courses",
        [
            "OOP",
            "Data Structures",
            "Operating Systems",
            "Artificial Intelligence",
        ],
    )

    new_grades = {}
    grade_cols = st.columns(min(len(default_courses), 3))
    for idx, course in enumerate(default_courses):
      with grade_cols[idx % len(grade_cols)]:
        new_grades[course] = st.number_input(
            f"Marks: {course} (0-100)",
            min_value=0.0,
            max_value=100.0,
            value=75.0,
            step=1.0,
            key=f"ng_{course}",
        )

    st.markdown("---")
    st.markdown("#### SMTP Configuration for Direct Email Dispatch")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
      add_smtp_host = st.text_input(
          "SMTP Host", value="smtp.gmail.com", key="add_ih"
      )
      add_smtp_port = st.number_input(
          "SMTP Port", value=587, step=1, key="add_ip"
      )
      add_sender = st.text_input("Sender Email", value="", key="add_is")
    with col_s2:
      add_pass = st.text_input(
          "Sender App Password", type="password", value="", key="add_ipass"
      )
      send_email_toggle = st.checkbox(
          "Send Performance Report Email to Student Upon Saving", value=True
      )

    if st.button("Save, Evaluate & Send Report"):
      avg_score = (
          sum(new_grades.values()) / len(new_grades) if new_grades else 0
      )
      min_score = min(new_grades.values()) if new_grades else 0
      evaluation_status = (
          "At Risk" if (min_score < 35 or avg_score < 50) else "No Risk"
      )

      new_row = {
          "Roll No.": new_roll,
          "Name": new_name,
          "Email": new_email,
          "Program": new_program,
          **new_grades,
          "SGPA / CGPA": 3.2,
          "Evaluation": evaluation_status,
      }

      if "active_df" in st.session_state:
        new_df_row = pd.DataFrame([new_row])
        st.session_state["active_df"] = pd.concat(
            [st.session_state["active_df"], new_df_row], ignore_index=True
        )
      else:
        st.session_state["active_df"] = pd.DataFrame([new_row])

      st.success(
          f"Student **{new_name} ({new_roll})** successfully added and"
          f" evaluated as **{evaluation_status}**!"
      )

      if send_email_toggle:
        if not add_sender or not add_pass or not new_email:
          st.warning(
              "Student saved, but email could not be sent: Missing sender"
              " credentials or recipient email address."
          )
        else:
          smtp_config = {
              "host": add_smtp_host,
              "port": int(add_smtp_port),
              "sender_email": add_sender,
              "sender_password": add_pass,
          }
          df_single = pd.DataFrame([new_row])
          with st.spinner("Sending performance report to student..."):
            count, err = send_bulk_performance_emails(
                df_single,
                smtp_config,
                specific_student_id=new_roll,
                fallback_email=new_email,
            )
            if err:
              st.warning(f"Notice: {err}")
            else:
              st.success(
                  f"Performance report email successfully sent to"
                  f" {new_email}!"
              )

      st.markdown("##### Updated Active Dataset Preview:")
      st.dataframe(
          st.session_state["active_df"].style.apply(
              highlight_risk_rows, axis=1
          ),
          use_container_width=True,
      )

  st.markdown("<br><br><br>", unsafe_allow_html=True)


# ==========================================
# PAGE: DATABASE LOGS & BATCHES
# ==========================================
elif current_page == "Database Logs":
  st.markdown("### Institutional Database Logs & Batches")
  st.write(
      "Audit trail of past batch evaluations, system logs, and communication"
      " histories."
  )

  log_data = pd.DataFrame({
      "Timestamp": ["2026-09-21 21:16", "2026-09-20 18:30", "2026-09-18 10:15"],
      "Batch Tag": ["Fall-2026-CS-4", "Fall-2026-SE-2", "Spring-2026-CS-6"],
      "Records Processed": [45, 52, 38],
      "Action": [
          "Batch Evaluation & Emails",
          "CGPA Calculation",
          "Risk Assessment",
      ],
      "Status": ["Completed", "Completed", "Completed"],
  })
  st.dataframe(log_data, use_container_width=True)
  st.markdown("<br><br><br>", unsafe_allow_html=True)


# ==========================================
# GLOBAL FOOTER RENDER
# ==========================================
render_footer()