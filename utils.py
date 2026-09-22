import pandas as pd
import smtplib
from email.message import EmailMessage

def send_bulk_performance_emails(result_df, smtp_config, email_type_filter="All", specific_student_id=None, fallback_email=None):
    success_count = 0
    try:
        server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
        server.starttls()
        server.login(smtp_config["sender_email"], smtp_config["sender_password"])

        for _, row in result_df.iterrows():
            student_id = str(row.get("Student_ID", row.get("Roll No.", "")))
            student_name = str(row.get("Student_Name", row.get("Name", "Student")))
            status = row.get("Evaluation", row.get("Overall_Status", "No Risk"))

            if specific_student_id and student_id != specific_student_id:
                continue

            if not specific_student_id:
                if email_type_filter == "At Risk" and status != "At Risk":
                    continue
                if email_type_filter == "No Risk" and status == "At Risk":
                    continue

            recipient_email = None
            if "Email" in result_df.columns:
                val = row.get("Email")
                if pd.notna(val) and str(val).strip() != "":
                    recipient_email = str(val).strip()
            
            if not recipient_email and fallback_email:
                recipient_email = fallback_email.strip()

            if not recipient_email:
                continue

            score_details = ""
            for col in result_df.columns:
                if col not in ["S. No.", "Roll No.", "Name", "F_Name", "Program", "Email", "Evaluation", "Overall_Status"]:
                    val = row[col]
                    if pd.notna(val):
                        score_details += f" - {col}: {val}\n"
            
            if not score_details:
                score_details = " - Evaluation completed successfully.\n"
            
            msg = EmailMessage()
            msg["From"] = smtp_config["sender_email"]
            msg["To"] = recipient_email

            if status == "At Risk":
                msg["Subject"] = f"UET Mardan Academic Advisory Notice - {student_id}"
                body = f"""Dear {student_name} ({student_id}),

This is an automated academic update from EduGuard-AI at UET Mardan. 
Based on your recent continuous assessments, your current academic standing requires attention ("At Risk").

Your Personal Assessment Results:
{score_details}

We strongly encourage you to consult with your course instructor and academic advisor during office hours to discuss improvement strategies and support resources available.

Best regards,
Department of Computer Science & Software Engineering
University of Engineering and Technology (UET) Mardan
"""
            else:
                msg["Subject"] = f"UET Mardan Academic Performance Report - {student_id}"
                body = f"""Dear {student_name} ({student_id}),

This is an automated academic update from EduGuard-AI at UET Mardan. 
Your recent continuous assessment evaluations indicate that you are maintaining good academic standing ("No Risk"). 

Your Personal Assessment Results:
{score_details}

Keep up the strong effort in your coursework!

Best regards,
Department of Computer Science & Software Engineering
University of Engineering and Technology (UET) Mardan
"""

            msg.set_content(body)
            server.send_message(msg)
            success_count += 1

        server.quit()
        if success_count == 0:
            return 0, "No emails were sent. Please verify that a valid recipient email or fallback test email was provided."
        return success_count, None
    except Exception as e:
        return success_count, str(e)


def highlight_risk_rows(row):
    eval_val = str(row.get("Evaluation", row.get("Overall_Status", "")))
    if eval_val == "At Risk":
        return ['background-color: #ffcccc; color: #900000; font-weight: bold'] * len(row)
    return [''] * len(row)