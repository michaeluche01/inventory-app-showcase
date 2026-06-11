"""
Email Service — Throve
HTTP-based email delivery via Resend API (works on Railway, Render, and all cloud platforms).
Falls back to SMTP for local development if no Resend key is configured.

WHY RESEND INSTEAD OF SMTP:
  Railway (and most PaaS platforms) block outbound SMTP on ports 25, 465, and 587
  to prevent spam abuse. Resend sends via HTTPS — no blocked ports, no firewall issues.

HOW TO SET UP RESEND (2 minutes):
  1. Sign up at https://resend.com (free — 3,000 emails/month, 100/day)
  2. Dashboard → API Keys → Create API Key
  3. Copy the key (starts with re_...)
  4. Add RESEND_API_KEY to your .env and Railway environment variables

FROM ADDRESS RULES:
  - Without a verified domain → use "onboarding@resend.dev" as SMTP_FROM_EMAIL
    (Resend's test domain — emails only deliver to YOUR OWN Resend account email)
  - Once throve.app is live → add it in Resend dashboard → verify DNS records
    → change SMTP_FROM_EMAIL to "noreply@throve.app" → emails deliver to anyone

ENV VARS NEEDED:
  RESEND_API_KEY="re_xxxxxxxxxxxx"      ← from Resend dashboard
  SMTP_FROM_EMAIL="onboarding@resend.dev"  ← until you have a verified domain
  SMTP_FROM_NAME="Throve"
  APP_BASE_URL="https://your-app.up.railway.app"  ← your Railway URL

LOCAL FALLBACK (if RESEND_API_KEY is not set):
  SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL
  These are used automatically when RESEND_API_KEY is absent.
"""

import smtplib
import ssl
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from sqlalchemy.orm import Session

from app.services import email_templates as tpl
from app.utils.logger import LoggerAdapter
from config import get_settings

settings = get_settings()
log = LoggerAdapter(__name__)

# Resend SDK — installed via: pip install resend
try:
    import resend as _resend_sdk
    _RESEND_AVAILABLE = True
except ImportError:
    _resend_sdk = None
    _RESEND_AVAILABLE = False


# ─────────────────────────────────────────────
# DB email log writer
# ─────────────────────────────────────────────

def _persist_log(
    db: Optional[Session],
    *,
    to_email: str,
    subject: str,
    email_type: str,
    business_id: Optional[str],
    user_id: Optional[str],
    success: bool,
    error_message: Optional[str] = None,
) -> None:
    """Write one row to email_logs. Swallows all errors — never raises."""
    if db is None:
        return
    try:
        from app.models.email_log import EmailLog
        entry = EmailLog(
            id=str(uuid.uuid4()),
            to_email=to_email,
            subject=subject,
            email_type=email_type,
            business_id=business_id,
            user_id=user_id,
            success=success,
            error_message=error_message,
            sent_at=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
    except Exception as exc:
        log.error("Failed to persist email log", error=str(exc))


# ─────────────────────────────────────────────
# Device summary parser
# ─────────────────────────────────────────────

def _parse_device(user_agent: Optional[str]) -> str:
    """Return a human-readable device/browser summary from a User-Agent string."""
    if not user_agent:
        return "Unknown device"

    ua = user_agent.lower()

    if "android" in ua:
        os_hint = "Android"
    elif "iphone" in ua or "ipad" in ua:
        os_hint = "iOS"
    elif "windows" in ua:
        os_hint = "Windows"
    elif "mac os" in ua or "macos" in ua:
        os_hint = "macOS"
    elif "linux" in ua:
        os_hint = "Linux"
    else:
        os_hint = "Unknown OS"

    if "flutter" in ua or "dart" in ua:
        client = "Throve mobile app"
    elif "okhttp" in ua:
        client = "Throve mobile app (Android)"
    elif "chrome" in ua and "edge" not in ua:
        client = "Chrome"
    elif "firefox" in ua:
        client = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        client = "Safari"
    elif "edge" in ua:
        client = "Edge"
    elif "postman" in ua:
        client = "Postman / API client"
    else:
        client = "Unknown client"

    return f"{client} on {os_hint}"


# ─────────────────────────────────────────────
# Email Service
# ─────────────────────────────────────────────

class EmailService:
    """
    Singleton email service.

    Delivery priority:
      1. Resend HTTP API  — if RESEND_API_KEY is set (works on all cloud platforms)
      2. SMTP fallback    — if RESEND_API_KEY is absent (works locally, blocked on Railway)

    All link URLs in emails are built from APP_BASE_URL so nothing is hardcoded.
    """

    def __init__(self) -> None:
        # ── Resend settings ───────────────────────────────────────────────
        self.resend_api_key: Optional[str] = getattr(settings, "RESEND_API_KEY", None)
        self.use_resend: bool = bool(self.resend_api_key and _RESEND_AVAILABLE)

        # ── SMTP fallback settings ────────────────────────────────────────
        self.smtp_server:   Optional[str] = settings.SMTP_SERVER
        self.smtp_port:     int           = settings.SMTP_PORT or 587
        self.smtp_user:     Optional[str] = settings.SMTP_USER
        self.smtp_password: Optional[str] = settings.SMTP_PASSWORD
        self.smtp_use_ssl:  bool          = getattr(settings, "SMTP_USE_SSL", False)

        # ── Shared ────────────────────────────────────────────────────────
        self.from_email: Optional[str] = settings.SMTP_FROM_EMAIL
        self.from_name:  str           = getattr(settings, "SMTP_FROM_NAME", "Throve")
        self.base_url:   str           = getattr(settings, "APP_BASE_URL", "http://localhost:8000").rstrip("/")

        self.smtp_enabled: bool = all([
            self.smtp_server, self.smtp_user, self.smtp_password, self.from_email
        ])

        self.enabled: bool = self.use_resend or self.smtp_enabled

        # ── Startup log ───────────────────────────────────────────────────
        if self.use_resend:
            log.info("EmailService: ready — Resend HTTP API (cloud-safe)")
        elif self.smtp_enabled:
            mode = f"SMTP_SSL port {self.smtp_port}" if self.smtp_use_ssl else f"STARTTLS port {self.smtp_port}"
            log.info(f"EmailService: ready — {mode} via {self.smtp_server} (SMTP fallback)")
        else:
            log.warning(
                "EmailService: disabled — set RESEND_API_KEY in .env to enable emails. "
                "Sign up free at https://resend.com"
            )

    # ──────────────────────────────────────────
    # Internal: Resend send
    # ──────────────────────────────────────────

    def _send_via_resend(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        html_body: str,
    ) -> bool:
        """Send via Resend HTTP API. Returns True on success."""
        try:
            _resend_sdk.api_key = self.resend_api_key

            from_addr = (
                f"{self.from_name} <{self.from_email}>"
                if self.from_email
                else f"{self.from_name} <onboarding@resend.dev>"
            )

            params = {
                "from":    from_addr,
                "to":      [to_email],
                "subject": subject,
                "html":    html_body,
            }

            response = _resend_sdk.Emails.send(params)

            # Resend returns {"id": "..."} on success
            if response and response.get("id"):
                return True

            log.error("Resend returned unexpected response", response=str(response))
            return False

        except Exception as exc:
            raise  # Re-raise so _send() can catch and log it properly

    # ──────────────────────────────────────────
    # Internal: SMTP send
    # ──────────────────────────────────────────

    def _send_via_smtp(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        html_body: str,
    ) -> bool:
        """Send via SMTP. Returns True on success."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{self.from_name} <{self.from_email}>"
        msg["To"]      = f"{to_name} <{to_email}>" if to_name else to_email
        msg["X-Mailer"] = "Throve/1.0"
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        context = ssl.create_default_context()

        if self.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                self.smtp_server, self.smtp_port,
                context=context, timeout=15
            ) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
        else:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

        return True

    # ──────────────────────────────────────────
    # Internal: unified send + logging
    # ──────────────────────────────────────────

    def _send(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        html_body: str,
        db: Optional[Session],
        email_type: str,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        if not self.enabled:
            log.warning(
                "Email skipped — not configured. "
                "Set RESEND_API_KEY in .env (https://resend.com — free)",
                to=to_email, subject=subject, type=email_type,
            )
            return False

        try:
            if self.use_resend:
                success = self._send_via_resend(to_email, to_name, subject, html_body)
            else:
                success = self._send_via_smtp(to_email, to_name, subject, html_body)

            if success:
                log.info("Email sent", to=to_email, subject=subject,
                         type=email_type, via="resend" if self.use_resend else "smtp")
                _persist_log(db, to_email=to_email, subject=subject,
                             email_type=email_type, business_id=business_id,
                             user_id=user_id, success=True)
            return success

        except smtplib.SMTPAuthenticationError as exc:
            err = "SMTP authentication failed — check SMTP_USER and SMTP_PASSWORD"
            log.error(err, error=str(exc), to=to_email)
            _persist_log(db, to_email=to_email, subject=subject, email_type=email_type,
                         business_id=business_id, user_id=user_id,
                         success=False, error_message=err)
            return False

        except Exception as exc:
            err = f"Email send failed: {exc}"
            log.error(err, to=to_email, subject=subject)
            _persist_log(db, to_email=to_email, subject=subject, email_type=email_type,
                         business_id=business_id, user_id=user_id,
                         success=False, error_message=err)
            return False

    # ──────────────────────────────────────────
    # Public send methods
    # ──────────────────────────────────────────

    def send_welcome_owner(
        self,
        db: Optional[Session],
        *,
        owner_name: str,
        owner_email: str,
        business_name: str,
        temporary_password: str,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Welcome email to a newly created business owner."""
        subject, html = tpl.welcome_owner(
            owner_name=owner_name,
            business_name=business_name,
            email=owner_email,
            temporary_password=temporary_password,
            login_url=f"{self.base_url}/login",
        )
        return self._send(owner_email, owner_name, subject, html,
                          db, "welcome_owner", business_id, user_id)

    def send_welcome_staff(
        self,
        db: Optional[Session],
        *,
        staff_name: str,
        staff_email: str,
        business_name: str,
        role: str,
        temporary_password: str,
        added_by_name: str,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Welcome email to a new staff or manager."""
        subject, html = tpl.welcome_staff(
            staff_name=staff_name,
            business_name=business_name,
            role=role,
            email=staff_email,
            temporary_password=temporary_password,
            login_url=f"{self.base_url}/login",
            added_by_name=added_by_name,
        )
        return self._send(staff_email, staff_name, subject, html,
                          db, "welcome_staff", business_id, user_id)

    def send_login_activity(
        self,
        db: Optional[Session],
        *,
        user_name: str,
        user_email: str,
        login_time: datetime,
        ip_address: Optional[str],
        user_agent: Optional[str],
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Login activity notification sent to the user themselves."""
        subject, html = tpl.login_activity(
            user_name=user_name,
            email=user_email,
            login_time=login_time,
            ip_address=ip_address or "Unknown",
            user_agent=user_agent or "",
            device_summary=_parse_device(user_agent),
        )
        return self._send(user_email, user_name, subject, html,
                          db, "login_activity", business_id, user_id)

    def send_staff_login_alert(
        self,
        db: Optional[Session],
        *,
        owner_name: str,
        owner_email: str,
        staff_name: str,
        staff_email: str,
        staff_role: str,
        business_name: str,
        login_time: datetime,
        ip_address: Optional[str],
        user_agent: Optional[str],
        business_id: Optional[str] = None,
    ) -> bool:
        """Alert the business owner when a staff member logs in."""
        subject, html = tpl.staff_login_alert(
            owner_name=owner_name,
            staff_name=staff_name,
            staff_email=staff_email,
            staff_role=staff_role,
            business_name=business_name,
            login_time=login_time,
            ip_address=ip_address or "Unknown",
            device_summary=_parse_device(user_agent),
        )
        return self._send(owner_email, owner_name, subject, html,
                          db, "staff_login_alert", business_id)

    def send_password_reset(
        self,
        db: Optional[Session],
        *,
        user_name: str,
        user_email: str,
        reset_token: str,
        expires_minutes: int = 60,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Send password-reset email.
        Accepts the raw token — builds the full URL here using APP_BASE_URL.
        No hardcoded domain in route code.
        """
        reset_url = f"{self.base_url}/reset-password?token={reset_token}"
        subject, html = tpl.password_reset(
            user_name=user_name,
            reset_url=reset_url,
            expires_minutes=expires_minutes,
        )
        return self._send(user_email, user_name, subject, html,
                          db, "password_reset", business_id, user_id)

    def send_low_stock_digest(
        self,
        db: Optional[Session],
        *,
        recipient_name: str,
        recipient_email: str,
        business_name: str,
        branch_name: str,
        items: list[dict],
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Daily low-stock digest for owner/manager."""
        if not items:
            return False
        subject, html = tpl.low_stock_digest(
            recipient_name=recipient_name,
            business_name=business_name,
            branch_name=branch_name,
            items=items,
            app_url=self.base_url,
        )
        return self._send(recipient_email, recipient_name, subject, html,
                          db, "low_stock_digest", business_id, user_id)

    def send_adjustment_alert(
        self,
        db: Optional[Session],
        *,
        recipient_name: str,
        recipient_email: str,
        product_name: str,
        product_sku: str,
        business_name: str,
        performed_by_name: str,
        performed_by_email: str,
        previous_qty: int,
        new_qty: int,
        reason: str,
        alert_level: str,
        suspicious_patterns: list[str],
        business_id: Optional[str] = None,
    ) -> bool:
        """Email manager/owner about a flagged stock adjustment."""
        subject, html = tpl.adjustment_alert(
            recipient_name=recipient_name,
            product_name=product_name,
            product_sku=product_sku,
            business_name=business_name,
            performed_by_name=performed_by_name,
            performed_by_email=performed_by_email,
            previous_qty=previous_qty,
            new_qty=new_qty,
            reason=reason,
            alert_level=alert_level,
            suspicious_patterns=suspicious_patterns,
            review_url=f"{self.base_url}/admin/adjustments",
        )
        return self._send(recipient_email, recipient_name, subject, html,
                          db, "adjustment_alert", business_id)


# ── Singleton ─────────────────────────────────────────────────────────────
email_service = EmailService()