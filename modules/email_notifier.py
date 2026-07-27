"""Email Notifier — sends fraud alerts and notifications via SMTP."""

import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from utils.vault import encrypt, decrypt
from utils.app_logger import get_logger

logger = get_logger("email_notifier")

MAX_RETRIES = 3
RETRY_DELAY = 2


class EmailNotifier:
    """Sends email notifications for fraud alerts and system events."""

    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = ""
        self.sender_password = ""
        self.manager_email = ""
        self.enabled = False

    def configure(self, smtp_server, smtp_port, sender_email, sender_password, manager_email):
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port)
        self.sender_email = sender_email
        self.sender_password = encrypt(sender_password)
        self.manager_email = manager_email
        self.enabled = bool(sender_email and sender_password and manager_email)

    def is_configured(self):
        return self.enabled and bool(self.sender_email and self.sender_password and self.manager_email)

    def send_alert(self, alert):
        """Send a single fraud alert email."""
        if not self.is_configured():
            return False, "Email not configured"

        import html as _html
        severity = alert.get("severity", "low")
        icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        icon = icons.get(severity, "⚪")
        severity_label = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}.get(severity, "INFO")

        subject = f"{icon} [{severity_label}] Smart Accounting — Fraud Alert"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; direction: rtl; max-width: 600px; margin: 0 auto;">
            <div style="background: {'#E74C3C' if severity == 'high' else '#F39C12' if severity == 'medium' else '#27AE60'}; color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="margin: 0;">{icon} Smart Accounting — Fraud Alert</h2>
                <p style="margin: 5px 0 0 0;">Severity: {severity_label}</p>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border: 1px solid #ddd;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px; font-weight: bold; width: 120px;">Time:</td><td style="padding: 8px;">{_html.escape(str(alert.get('time', 'N/A')))}</td></tr>
                    <tr><td style="padding: 8px; font-weight: bold;">Rule:</td><td style="padding: 8px;">{_html.escape(str(alert.get('rule', 'N/A')))}</td></tr>
                    <tr><td style="padding: 8px; font-weight: bold;">Field:</td><td style="padding: 8px;">{_html.escape(str(alert.get('field', 'N/A')))}</td></tr>
                    <tr><td style="padding: 8px; font-weight: bold;">Detail:</td><td style="padding: 8px;">{_html.escape(str(alert.get('detail', 'N/A')))}</td></tr>
                    <tr><td style="padding: 8px; font-weight: bold;">Old Value:</td><td style="padding: 8px;">{_html.escape(str(alert.get('old_value', 'N/A')))}</td></tr>
                    <tr><td style="padding: 8px; font-weight: bold;">New Value:</td><td style="padding: 8px;">{_html.escape(str(alert.get('new_value', 'N/A')))}</td></tr>
                    <tr><td style="padding: 8px; font-weight: bold;">User:</td><td style="padding: 8px;">{_html.escape(str(alert.get('user', 'N/A')))}</td></tr>
                </table>
            </div>
            <div style="background: #fff; padding: 15px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px; text-align: center; color: #666; font-size: 12px;">
                Smart Accounting Platform — Automated Alert
            </div>
        </div>
        """

        return self._send(subject, html_content)

    def send_summary(self, alert_count, high_alerts):
        """Send a daily/weekly summary email."""
        if not self.is_configured():
            return False, "Email not configured"

        subject = f"📊 Smart Accounting — Security Summary ({datetime.now().strftime('%Y-%m-%d')})"

        rows = ""
        for alert in high_alerts[-10:]:
            rows += f"""
            <tr>
                <td style="padding: 6px; border-bottom: 1px solid #ddd;">{alert.get('time', '')}</td>
                <td style="padding: 6px; border-bottom: 1px solid #ddd;">{alert.get('rule', '')}</td>
                <td style="padding: 6px; border-bottom: 1px solid #ddd;">{alert.get('field', '')}</td>
                <td style="padding: 6px; border-bottom: 1px solid #ddd;">{alert.get('detail', '')}</td>
            </tr>
            """

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #2C3E50; color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="margin: 0;">📊 Security Summary</h2>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border: 1px solid #ddd;">
                <p><b>Total Alerts:</b> {alert_count.get('total', 0)}</p>
                <p style="color: #E74C3C;">🔴 High: {alert_count.get('high', 0)}</p>
                <p style="color: #F39C12;">🟡 Medium: {alert_count.get('medium', 0)}</p>
                <p style="color: #27AE60;">🟢 Low: {alert_count.get('low', 0)}</p>
                <hr>
                <h3>Recent High-Severity Alerts:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #eee;"><th style="padding: 6px;">Time</th><th style="padding: 6px;">Rule</th><th style="padding: 6px;">Field</th><th style="padding: 6px;">Detail</th></tr>
                    {rows if rows else '<tr><td colspan="4" style="padding: 10px; text-align: center;">No high-severity alerts</td></tr>'}
                </table>
            </div>
        </div>
        """

        return self._send(subject, html)

    def _send(self, subject: str, html: str) -> tuple:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = self.sender_email
                msg["To"] = self.manager_email
                msg.attach(MIMEText(html, "html", "utf-8"))

                context = ssl.create_default_context()
                password = decrypt(self.sender_password)
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15) as server:
                    server.starttls(context=context)
                    server.login(self.sender_email, password)
                    server.sendmail(self.sender_email, self.manager_email, msg.as_string())

                return True, "Email sent successfully"
            except Exception as e:
                logger.warning(f"Email send failed (attempt {attempt}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
        return False, f"Failed after {MAX_RETRIES} attempts"


# Singleton
email_notifier = EmailNotifier()
