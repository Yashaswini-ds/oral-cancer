"""
test_email.py -- Quick standalone test to verify Gmail SMTP works.
Run with: python test_email.py
"""
import os
import sys

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

print(f"[TEST] Sending from: {MAIL_USERNAME}")
print(f"[TEST] Password loaded: {'YES' if MAIL_PASSWORD else 'NO - CHECK .env'}")

if not MAIL_USERNAME or not MAIL_PASSWORD:
    print("[ERROR] Missing MAIL_USERNAME or MAIL_PASSWORD in .env")
    exit(1)

html = """
<!DOCTYPE html>
<html>
<body style="background:#0f1117;font-family:Arial,sans-serif;padding:40px;">
  <div style="max-width:500px;margin:auto;background:#fff;border-radius:16px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#003366,#0066cc);padding:30px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:22px;">🩺 O-SCAN DIAGNOSTICS</h1>
      <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:13px;">Email System Test</p>
    </div>
    <div style="padding:30px;">
      <h2 style="color:#003366;">✅ Email System Working!</h2>
      <p style="color:#4a5568;line-height:1.7;">
        This is a test email from your O-Scan Diagnostics automated email system.
        If you're reading this, <strong>Gmail SMTP is correctly configured</strong>
        and emails will be sent for:
      </p>
      <ul style="color:#4a5568;font-size:14px;line-height:2;">
        <li>🔐 Login notifications</li>
        <li>🎉 Signup welcome emails</li>
        <li>🩺 Scan results with PDF report</li>
        <li>📋 Doctor new-case alerts</li>
        <li>📅 Appointment confirmations</li>
      </ul>
    </div>
    <div style="background:#f8fafc;padding:20px;text-align:center;">
      <p style="margin:0;font-size:12px;color:#a0aec0;">© 2026 O-Scan Diagnostics</p>
    </div>
  </div>
</body>
</html>
"""

try:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '✅ O-Scan Email System Test — Working!'
    msg['From']    = MAIL_USERNAME
    msg['To']      = MAIL_USERNAME  # Send to yourself as test

    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, MAIL_USERNAME, msg.as_string())

    print(f"\n✅ SUCCESS! Test email sent to {MAIL_USERNAME}")
    print("   Check your Gmail inbox now.")

except smtplib.SMTPAuthenticationError:
    print("\n❌ AUTHENTICATION FAILED!")
    print("   → Make sure you used the 16-char App Password (not your Gmail login password)")
    print("   → App Password must NOT have spaces when used in code")
    print("   → Check: Google Account → Security → App passwords")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
