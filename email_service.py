"""
email_service.py
O-Scan Diagnostics — Automated Email Service
Sends elegant, branded HTML emails at every key user interaction.
All sends are non-blocking (background thread) and safely fail without
crashing the main application.
"""

import os
import threading
from datetime import datetime
from flask_mail import Mail, Message

mail = Mail()


# ─────────────────────────────────────────────
#  INIT
# ─────────────────────────────────────────────

def init_mail(app):
    """Configure Flask-Mail from environment variables and bind to the app."""
    # Strip spaces from App Password (Google shows them grouped but SMTP needs no spaces)
    raw_password = os.environ.get('MAIL_PASSWORD', '')
    clean_password = raw_password.replace(' ', '')

    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=clean_password,
        MAIL_DEFAULT_SENDER=('O-Scan Diagnostics', os.environ.get('MAIL_USERNAME', '')),
    )
    mail.init_app(app)


# ─────────────────────────────────────────────
#  INTERNAL HELPERS
# ─────────────────────────────────────────────

def _send_async(app, msg, attachment_path=None, attachment_name=None):
    """Send a Flask-Mail message inside an application context (background thread)."""
    with app.app_context():
        try:
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as fp:
                    msg.attach(
                        attachment_name or os.path.basename(attachment_path),
                        'application/pdf',
                        fp.read()
                    )
            mail.send(msg)
            print(f"[EMAIL] Sent: {msg.subject} → {msg.recipients}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send '{msg.subject}': {e}")


def _dispatch(app, msg, attachment_path=None, attachment_name=None):
    """Fire-and-forget email dispatch on a daemon thread."""
    t = threading.Thread(
        target=_send_async,
        args=(app, msg, attachment_path, attachment_name),
        daemon=True
    )
    t.start()


# ─────────────────────────────────────────────
#  SHARED TEMPLATE BLOCKS
# ─────────────────────────────────────────────

def _base_html(title: str, header_html: str, body_html: str, footer_note: str = "") -> str:
    """
    Returns full HTML email with O-Scan branding.
    Dark theme with gradient header, clean white content card.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#0f1117;font-family:'Segoe UI',Arial,sans-serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1117;padding:40px 0;">
    <tr><td align="center">

      <!-- Card -->
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:16px;overflow:hidden;
                    box-shadow:0 20px 60px rgba(0,0,0,0.5);max-width:600px;">

        <!-- ── HEADER ── -->
        <tr>
          <td style="background:linear-gradient(135deg,#003366 0%,#0066cc 50%,#00b4d8 100%);
                     padding:36px 40px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <p style="margin:0;font-size:22px;font-weight:800;
                             color:#ffffff;letter-spacing:2px;">
                    🩺 O-SCAN DIAGNOSTICS
                  </p>
                  <p style="margin:4px 0 0;font-size:12px;color:rgba(255,255,255,0.75);
                             letter-spacing:1px;">
                    Advanced AI-Powered Oral Screening System
                  </p>
                </td>
                <td align="right">
                  <span style="display:inline-block;background:rgba(255,255,255,0.15);
                               border-radius:50px;padding:6px 14px;font-size:11px;
                               color:#ffffff;border:1px solid rgba(255,255,255,0.3);">
                    SECURE NOTIFICATION
                  </span>
                </td>
              </tr>
            </table>
            <!-- Header content injected below logo -->
            {header_html}
          </td>
        </tr>

        <!-- ── BODY ── -->
        <tr>
          <td style="padding:36px 40px 28px;color:#1a1a2e;">
            {body_html}
          </td>
        </tr>

        <!-- ── DIVIDER ── -->
        <tr>
          <td style="padding:0 40px;">
            <hr style="border:none;border-top:1px solid #e8ecf0;margin:0;"/>
          </td>
        </tr>

        <!-- ── FOOTER ── -->
        <tr>
          <td style="padding:24px 40px 32px;">
            <p style="margin:0;font-size:11px;color:#a0aec0;line-height:1.7;">
              {footer_note or "This is an automated message from O-Scan Diagnostics. Please do not reply to this email."}
            </p>
            <p style="margin:12px 0 0;font-size:11px;color:#a0aec0;">
              ⚠️ <em>DISCLAIMER: AI-generated screening. Not a medical diagnosis. Consult a qualified physician.</em>
            </p>
            <p style="margin:16px 0 0;font-size:12px;color:#718096;">
              &copy; {datetime.now().year} O-Scan Diagnostics &nbsp;·&nbsp; All rights reserved
            </p>
          </td>
        </tr>

      </table>
      <!-- /Card -->

    </td></tr>
  </table>

</body>
</html>"""


def _pill(text: str, color: str = "#0066cc") -> str:
    return (f'<span style="display:inline-block;background:{color};color:#fff;'
            f'border-radius:50px;padding:4px 14px;font-size:12px;font-weight:700;">'
            f'{text}</span>')


def _info_row(label: str, value: str) -> str:
    return f"""
    <tr>
      <td style="padding:10px 16px;font-size:13px;font-weight:600;
                 color:#4a5568;background:#f7fafc;border-bottom:1px solid #e8ecf0;
                 width:40%;">{label}</td>
      <td style="padding:10px 16px;font-size:13px;color:#1a202c;
                 border-bottom:1px solid #e8ecf0;">{value}</td>
    </tr>"""


def _section_title(text: str) -> str:
    return f"""
    <p style="margin:24px 0 10px;font-size:13px;font-weight:700;color:#003366;
              text-transform:uppercase;letter-spacing:1.5px;border-left:3px solid #0066cc;
              padding-left:10px;">{text}</p>"""


def _cta_button(text: str, href: str = "#") -> str:
    return f"""
    <div style="text-align:center;margin:28px 0 8px;">
      <a href="{href}" style="display:inline-block;background:linear-gradient(135deg,#003366,#0066cc);
         color:#ffffff;text-decoration:none;padding:14px 36px;border-radius:50px;
         font-size:14px;font-weight:700;letter-spacing:0.5px;
         box-shadow:0 6px 20px rgba(0,102,204,0.4);">
        {text}
      </a>
    </div>"""


# ─────────────────────────────────────────────
#  1. LOGIN NOTIFICATION
# ─────────────────────────────────────────────

def send_login_notification(app, user):
    """Send a login security alert to the user."""
    now = datetime.now().strftime("%d %b %Y at %I:%M %p")

    header_html = f"""
    <div style="margin-top:20px;">
      <p style="margin:0;font-size:28px;font-weight:800;color:#ffffff;">
        🔐 New Login Detected
      </p>
      <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.8);">
        Someone just signed in to your O-Scan account.
      </p>
    </div>"""

    body_html = f"""
    <p style="margin:0 0 8px;font-size:16px;color:#1a202c;">
      Hello, <strong>{user.username}</strong> 👋
    </p>
    <p style="margin:0 0 20px;font-size:14px;color:#4a5568;line-height:1.7;">
      A successful login was recorded on your O-Scan Diagnostics account. Here are the details:
    </p>

    {_section_title("Login Details")}
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-radius:10px;overflow:hidden;border:1px solid #e8ecf0;font-size:13px;">
      {_info_row("Account", user.email)}
      {_info_row("Role", user.role.capitalize())}
      {_info_row("Date &amp; Time", now)}
      {_info_row("Status", "✅ &nbsp;Successful")}
    </table>

    <div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;
                padding:16px 20px;margin:24px 0 8px;">
      <p style="margin:0;font-size:13px;color:#92400e;">
        <strong>⚠️ Wasn't you?</strong> Please change your password immediately and
        contact our support team.
      </p>
    </div>"""

    msg = Message(
        subject="🔐 New Login to Your O-Scan Account",
        recipients=[user.email],
        html=_base_html("Login Notification", header_html, body_html)
    )
    _dispatch(app, msg)


# ─────────────────────────────────────────────
#  2. SIGNUP WELCOME
# ─────────────────────────────────────────────

def send_signup_welcome(app, user):
    """Send a welcome email to a newly registered user."""
    header_html = f"""
    <div style="margin-top:20px;">
      <p style="margin:0;font-size:28px;font-weight:800;color:#ffffff;">
        🎉 Welcome to O-Scan!
      </p>
      <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.8);">
        Your account has been successfully created.
      </p>
    </div>"""

    body_html = f"""
    <p style="margin:0 0 8px;font-size:16px;color:#1a202c;">
      Hello, <strong>{user.username}</strong> 👋
    </p>
    <p style="margin:0 0 20px;font-size:14px;color:#4a5568;line-height:1.7;">
      Welcome aboard! Your O-Scan Diagnostics account is ready. Here's what you can do:
    </p>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
      <tr>
        <td style="padding:14px;background:#f0f7ff;border-radius:10px;margin-bottom:10px;vertical-align:top;width:48%;">
          <p style="margin:0;font-size:22px;">🔬</p>
          <p style="margin:6px 0 0;font-size:13px;font-weight:700;color:#003366;">AI Oral Screening</p>
          <p style="margin:4px 0 0;font-size:12px;color:#4a5568;">Upload images for instant AI-powered oral cancer risk detection.</p>
        </td>
        <td style="width:4%;"></td>
        <td style="padding:14px;background:#f0fff4;border-radius:10px;vertical-align:top;width:48%;">
          <p style="margin:0;font-size:22px;">📋</p>
          <p style="margin:6px 0 0;font-size:13px;font-weight:700;color:#276749;">Doctor Dashboard</p>
          <p style="margin:4px 0 0;font-size:12px;color:#4a5568;">Book appointments and get reports reviewed by specialists.</p>
        </td>
      </tr>
    </table>

    {_section_title("Your Account")}
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-radius:10px;overflow:hidden;border:1px solid #e8ecf0;">
      {_info_row("Name", user.username)}
      {_info_row("Email", user.email)}
      {_info_row("Role", user.role.capitalize())}
      {_info_row("Joined", datetime.now().strftime("%d %B %Y"))}
    </table>

    {_cta_button("Go to Your Dashboard", "http://127.0.0.1:5000/patient_dashboard")}"""

    msg = Message(
        subject="🎉 Welcome to O-Scan Diagnostics!",
        recipients=[user.email],
        html=_base_html("Welcome!", header_html, body_html)
    )
    _dispatch(app, msg)


# ─────────────────────────────────────────────
#  3. SCAN RESULT → PATIENT (PDF attached)
# ─────────────────────────────────────────────

def send_scan_result_to_patient(app, user, record, pdf_path=None):
    """Send scan result email with PDF report attached to the patient."""
    is_risk = "Risk" in (record.prediction or "")
    risk_color = "#dc2626" if is_risk else "#16a34a"
    risk_bg = "#fef2f2" if is_risk else "#f0fdf4"
    risk_icon = "🔴" if is_risk else "🟢"
    risk_label = "HIGH RISK" if is_risk else "LOW RISK"

    header_html = f"""
    <div style="margin-top:20px;">
      <p style="margin:0;font-size:28px;font-weight:800;color:#ffffff;">
        🩺 Your Scan Report is Ready
      </p>
      <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.8);">
        AI analysis complete — view your results below.
      </p>
    </div>"""

    body_html = f"""
    <p style="margin:0 0 8px;font-size:16px;color:#1a202c;">
      Hello, <strong>{user.username}</strong> 👋
    </p>
    <p style="margin:0 0 20px;font-size:14px;color:#4a5568;line-height:1.7;">
      Your oral cancer screening has been processed. Please find your detailed PDF report attached
      to this email.
    </p>

    <!-- Result Banner -->
    <div style="background:{risk_bg};border:2px solid {risk_color};border-radius:12px;
                padding:20px 24px;margin:0 0 24px;text-align:center;">
      <p style="margin:0;font-size:36px;">{risk_icon}</p>
      <p style="margin:8px 0 0;font-size:22px;font-weight:800;color:{risk_color};">
        {risk_label}
      </p>
      <p style="margin:4px 0 0;font-size:14px;color:#4a5568;">
        {record.prediction or "N/A"} &nbsp;·&nbsp; Confidence: <strong>{record.confidence or "—"}%</strong>
      </p>
    </div>

    {_section_title("Screening Details")}
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-radius:10px;overflow:hidden;border:1px solid #e8ecf0;">
      {_info_row("Patient", user.username)}
      {_info_row("Scan ID", record.timestamp or "—")}
      {_info_row("Date", (record.timestamp or "")[:8] or datetime.now().strftime("%Y%m%d"))}
      {_info_row("Result", record.prediction or "—")}
      {_info_row("Confidence", f"{record.confidence or '—'}%")}
    </table>

    {"<div style='background:#fef2f2;border-left:4px solid #dc2626;border-radius:8px;padding:16px 20px;margin:20px 0;'><p style='margin:0;font-size:13px;color:#7f1d1d;line-height:1.7;'><strong>⚠️ URGENT:</strong> High risk indicators were detected. We strongly recommend consulting an oncologist or maxillofacial surgeon <strong>immediately</strong> for further evaluation and biopsy.</p></div>" if is_risk else "<div style='background:#f0fdf4;border-left:4px solid #16a34a;border-radius:8px;padding:16px 20px;margin:20px 0;'><p style='margin:0;font-size:13px;color:#14532d;line-height:1.7;'><strong>✅ Good News:</strong> No significant high-risk markers were detected. Routine follow-up and regular check-ups are still advised.</p></div>"}

    <p style="margin:20px 0 0;font-size:13px;color:#4a5568;">
      📎 <strong>Your full PDF report is attached</strong> to this email for your records.
    </p>"""

    pdf_name = f"OScan_Report_{record.timestamp}.pdf" if record.timestamp else "OScan_Report.pdf"

    msg = Message(
        subject=f"🩺 Your O-Scan Report — {risk_label} Detected",
        recipients=[user.email],
        html=_base_html("Scan Report", header_html, body_html,
                        footer_note="Your health data is protected. This report is confidential and intended only for the recipient.")
    )
    _dispatch(app, msg, attachment_path=pdf_path, attachment_name=pdf_name)


# ─────────────────────────────────────────────
#  4. NEW CASE → DOCTOR
# ─────────────────────────────────────────────

def send_new_case_to_doctor(app, doctor, patient, record):
    """Notify the assigned doctor of a new patient scan submission."""
    is_risk = "Risk" in (record.prediction or "")
    priority_color = "#dc2626" if is_risk else "#2563eb"
    priority_label = "🔴 HIGH PRIORITY" if is_risk else "🔵 ROUTINE"

    header_html = f"""
    <div style="margin-top:20px;">
      <p style="margin:0;font-size:28px;font-weight:800;color:#ffffff;">
        📋 New Patient Case Assigned
      </p>
      <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.8);">
        A patient has completed their oral screening.
      </p>
    </div>"""

    body_html = f"""
    <p style="margin:0 0 8px;font-size:16px;color:#1a202c;">
      Dear, <strong>Dr. {doctor.username}</strong> 👨‍⚕️
    </p>
    <p style="margin:0 0 20px;font-size:14px;color:#4a5568;line-height:1.7;">
      A new oral screening case has been submitted and assigned to you. Please review
      the patient's results on your dashboard at your earliest convenience.
    </p>

    <!-- Priority Banner -->
    <div style="background:#f8fafc;border:2px solid {priority_color};border-radius:10px;
                padding:12px 20px;margin-bottom:20px;text-align:center;">
      <p style="margin:0;font-size:14px;font-weight:800;color:{priority_color};">
        {priority_label}
      </p>
    </div>

    {_section_title("Patient Information")}
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-radius:10px;overflow:hidden;border:1px solid #e8ecf0;">
      {_info_row("Patient Name", patient.username)}
      {_info_row("Patient Email", patient.email)}
      {_info_row("Scan ID", record.timestamp or "—")}
      {_info_row("AI Result", record.prediction or "—")}
      {_info_row("Confidence", f"{record.confidence or '—'}%")}
      {_info_row("Pain Level", record.pain_level or "—")}
      {_info_row("Bleeding", record.bleeding or "—")}
      {_info_row("Swelling", record.swelling or "—")}
      {_info_row("Habits", record.habits or "None reported")}
    </table>

    {_cta_button("Open Doctor Dashboard →", "http://127.0.0.1:5000/doctor_dashboard")}

    <p style="margin:16px 0 0;font-size:12px;color:#a0aec0;">
      You are receiving this because this patient selected you as their assigned physician.
    </p>"""

    msg = Message(
        subject=f"📋 New Case: {patient.username} — {record.prediction or 'Result Pending'}",
        recipients=[doctor.email],
        html=_base_html("New Case Alert", header_html, body_html,
                        footer_note="This notification was sent as you are the assigned doctor for this patient.")
    )
    _dispatch(app, msg)


# ─────────────────────────────────────────────
#  5. APPOINTMENT CONFIRMATION → PATIENT
# ─────────────────────────────────────────────

def send_appointment_confirmation(app, patient, doctor, appointment):
    """Send appointment booking confirmation to the patient."""
    date_str = appointment.start_time.strftime("%A, %d %B %Y")
    time_str = appointment.start_time.strftime("%I:%M %p")
    end_str  = appointment.end_time.strftime("%I:%M %p")

    header_html = f"""
    <div style="margin-top:20px;">
      <p style="margin:0;font-size:28px;font-weight:800;color:#ffffff;">
        📅 Appointment Confirmed
      </p>
      <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.8);">
        Your appointment has been successfully scheduled.
      </p>
    </div>"""

    body_html = f"""
    <p style="margin:0 0 8px;font-size:16px;color:#1a202c;">
      Hello, <strong>{patient.username}</strong> 👋
    </p>
    <p style="margin:0 0 20px;font-size:14px;color:#4a5568;line-height:1.7;">
      Your appointment with <strong>Dr. {doctor.username}</strong> has been confirmed.
      Please find the details below.
    </p>

    <!-- Date + Time Highlight -->
    <div style="background:linear-gradient(135deg,#003366,#0066cc);border-radius:12px;
                padding:24px;text-align:center;margin-bottom:24px;">
      <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.75);letter-spacing:1px;">
        APPOINTMENT DATE
      </p>
      <p style="margin:8px 0 0;font-size:26px;font-weight:800;color:#ffffff;">
        {date_str}
      </p>
      <p style="margin:6px 0 0;font-size:18px;color:rgba(255,255,255,0.9);">
        🕐 {time_str} – {end_str}
      </p>
    </div>

    {_section_title("Appointment Details")}
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-radius:10px;overflow:hidden;border:1px solid #e8ecf0;">
      {_info_row("Doctor", f"Dr. {doctor.username}")}
      {_info_row("Specialization", doctor.specialization or "General")}
      {_info_row("Date", date_str)}
      {_info_row("Time", f"{time_str} – {end_str}")}
      {_info_row("Duration", "30 minutes")}
      {_info_row("Reason", appointment.reason or "General consultation")}
      {_info_row("Status", "✅ &nbsp;Scheduled")}
    </table>

    <div style="background:#f0f7ff;border-radius:10px;padding:16px 20px;margin:20px 0;">
      <p style="margin:0;font-size:13px;color:#1e3a5f;line-height:1.7;">
        📌 <strong>Reminder:</strong> Please arrive 10 minutes early.
        Bring any previous medical records relevant to oral health.
      </p>
    </div>

    {_cta_button("View My Appointments", "http://127.0.0.1:5000/appointments")}"""

    msg = Message(
        subject=f"📅 Appointment Confirmed — {date_str} with Dr. {doctor.username}",
        recipients=[patient.email],
        html=_base_html("Appointment Confirmed", header_html, body_html)
    )
    _dispatch(app, msg)


# ─────────────────────────────────────────────
#  6. APPOINTMENT ALERT → DOCTOR
# ─────────────────────────────────────────────

def send_appointment_to_doctor(app, doctor, patient, appointment):
    """Notify doctor of a newly booked appointment."""
    date_str = appointment.start_time.strftime("%A, %d %B %Y")
    time_str = appointment.start_time.strftime("%I:%M %p")
    end_str  = appointment.end_time.strftime("%I:%M %p")

    header_html = f"""
    <div style="margin-top:20px;">
      <p style="margin:0;font-size:28px;font-weight:800;color:#ffffff;">
        🗓️ New Appointment Booked
      </p>
      <p style="margin:6px 0 0;font-size:14px;color:rgba(255,255,255,0.8);">
        A patient has scheduled an appointment with you.
      </p>
    </div>"""

    body_html = f"""
    <p style="margin:0 0 8px;font-size:16px;color:#1a202c;">
      Dear, <strong>Dr. {doctor.username}</strong> 👨‍⚕️
    </p>
    <p style="margin:0 0 20px;font-size:14px;color:#4a5568;line-height:1.7;">
      A patient has booked an appointment with you via O-Scan Diagnostics.
      Please review and prepare accordingly.
    </p>

    <!-- Date Highlight -->
    <div style="background:linear-gradient(135deg,#1a2a4a,#2563eb);border-radius:12px;
                padding:24px;text-align:center;margin-bottom:24px;">
      <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.75);letter-spacing:1px;">
        NEW APPOINTMENT
      </p>
      <p style="margin:8px 0 0;font-size:26px;font-weight:800;color:#ffffff;">
        {date_str}
      </p>
      <p style="margin:6px 0 0;font-size:18px;color:rgba(255,255,255,0.9);">
        🕐 {time_str} – {end_str}
      </p>
    </div>

    {_section_title("Patient & Appointment Info")}
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border-radius:10px;overflow:hidden;border:1px solid #e8ecf0;">
      {_info_row("Patient Name", patient.username)}
      {_info_row("Patient Email", patient.email)}
      {_info_row("Date", date_str)}
      {_info_row("Time", f"{time_str} – {end_str}")}
      {_info_row("Reason", appointment.reason or "Not specified")}
      {_info_row("Status", "✅ &nbsp;Scheduled")}
    </table>

    {_cta_button("Open Doctor Dashboard →", "http://127.0.0.1:5000/doctor_dashboard")}"""

    msg = Message(
        subject=f"🗓️ New Appointment: {patient.username} on {date_str}",
        recipients=[doctor.email],
        html=_base_html("New Appointment", header_html, body_html,
                        footer_note="You are receiving this as you have a new appointment scheduled through O-Scan Diagnostics.")
    )
    _dispatch(app, msg)
