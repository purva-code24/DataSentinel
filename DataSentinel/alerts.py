import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import numpy as np
from datetime import datetime

def send_alert(
    receiver_email,
    df,
    health_score,
    sender_email="purvasai021@gmail.com",
    app_password="ezdr pduv qgue nqvo"
):
    # ── CHECK IF ALERT NEEDED ──
    missing_pct = (df.isnull().sum().sum() /
                  (df.shape[0] * df.shape[1]) * 100)
    dup_count = df.duplicated().sum()

    alert_reasons = []

    if missing_pct > 10:
        alert_reasons.append(
            f"🔴 Missing values exceed 10% "
            f"— currently at {round(missing_pct,2)}%"
        )
    if dup_count > 0:
        alert_reasons.append(
            f"🔴 {dup_count} duplicate rows found"
        )
    if health_score < 70:
        alert_reasons.append(
            f"🔴 Health score is critically low "
            f"— {health_score}/100"
        )

    if not alert_reasons:
        print("✅ Data quality is good — "
              "no alert needed!")
        return False

    # ── BUILD EMAIL ──
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = (
        f"🚨 DataSentinel Alert — "
        f"Data Quality Issues Detected — "
        f"{datetime.now().strftime('%d %B %Y')}"
    )

    body = f"""
    <html>
    <body style="font-family: Arial; 
                 color: #1C2333;">
    
    <h2 style="color: #0D1F3C;">
        🛡️ DataSentinel — Data Quality Alert
    </h2>
    
    <p>Your dataset has been scanned and the 
    following issues were detected:</p>
    
    <div style="background: #EBF1FB; 
                padding: 15px; 
                border-radius: 8px;">
        <h3 style="color: #0A7EA4;">
            📊 Dataset Summary
        </h3>
        <p>Total Rows: <b>{df.shape[0]}</b></p>
        <p>Total Columns: <b>{df.shape[1]}</b></p>
        <p>Health Score: 
            <b style="color: red;">
                {health_score}/100
            </b>
        </p>
    </div>
    
    <br>
    
    <div style="background: #FFE8E8; 
                padding: 15px; 
                border-radius: 8px;">
        <h3 style="color: red;">
            ⚠️ Issues Found
        </h3>
        {''.join(f'<p>{r}</p>' 
                 for r in alert_reasons)}
    </div>
    
    <br>
    
    <div style="background: #EBF1FB; 
                padding: 15px; 
                border-radius: 8px;">
        <h3 style="color: #0A7EA4;">
            💡 Recommendations
        </h3>
        <p>• Review and fix missing values 
           before analysis</p>
        <p>• Remove duplicate rows 
           immediately</p>
        <p>• Run DataSentinel again after 
           fixing issues</p>
    </div>
    
    <br>
    <p style="color: #718096; font-size: 12px;">
        Sent by DataSentinel — 
        Automated Data Quality Monitor<br>
        github.com/purva-code24/DataSentinel
    </p>
    
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    # ── ATTACH PDF REPORT ──
    try:
        with open("DataSentinel_Report.pdf", 
                  "rb") as f:
            attachment = MIMEBase(
                'application', 'octet-stream'
            )
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename='DataSentinel_Report.pdf'
            )
            msg.attach(attachment)
    except:
        print("⚠️ PDF not attached — "
              "generate PDF first")

    # ── SEND EMAIL ──
    try:
        server = smtplib.SMTP(
            'smtp.gmail.com', 587
        )
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(
            sender_email,
            receiver_email,
            msg.as_string()
        )
        server.quit()
        print(f"✅ Alert email sent to "
              f"{receiver_email}!")
        return True

    except Exception as e:
        print(f"🔴 Email failed: {e}")
        return False