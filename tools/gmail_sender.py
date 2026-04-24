"""
Gmail SMTP sender — authentic mail from sales@astrastaging.com via the
actual Google Workspace mailbox. Messages show up in the Sent folder
automatically (unlike Mailgun, which sends via its own infrastructure).

Drop-in replacement for tools.email_service.EmailService for transactional
sends. Reads SALES_GWS_APP_PASSWORD + SALES_EMAIL + SALES_SMTP_{HOST,PORT}
from .env.

Parallel send via a threadpool would exceed Gmail's per-connection rate;
keep sends serial + small.
"""
from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from typing import Iterable, Optional, Union

logger = logging.getLogger(__name__)


class GmailSendError(RuntimeError):
    pass


def _creds() -> tuple[str, str, str, int]:
    user = os.getenv("SALES_EMAIL", "sales@astrastaging.com")
    pw = os.getenv("SALES_GWS_APP_PASSWORD", "").strip()
    host = os.getenv("SALES_SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SALES_SMTP_PORT", "587"))
    if not pw:
        raise GmailSendError("SALES_GWS_APP_PASSWORD not set in .env")
    return user, pw, host, port


class GmailSender:
    """Thin wrapper mirroring tools.email_service.EmailService.send_email."""

    def __init__(self, sender_name: str = "Astra Staging"):
        self.user, self.pw, self.host, self.port = _creds()
        self.sender_name = sender_name
        self.from_header = f"{sender_name} <{self.user}>"

    def send_email(
        self,
        to_email: Union[str, Iterable[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[Union[str, Iterable[str]]] = None,
        bcc: Optional[Union[str, Iterable[str]]] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> dict:
        """Send one message. `in_reply_to` + `references` let us thread
        into an existing conversation (useful for reply-bot use cases).
        Returns {"success": bool, "message_id": str | None, "error": str | None}."""
        msg = EmailMessage()
        msg["From"] = self.from_header
        if isinstance(to_email, str):
            msg["To"] = to_email
            to_list = [to_email]
        else:
            to_list = list(to_email)
            msg["To"] = ", ".join(to_list)
        if cc:
            cc_list = [cc] if isinstance(cc, str) else list(cc)
            msg["Cc"] = ", ".join(cc_list)
            to_list += cc_list
        if bcc:
            bcc_list = [bcc] if isinstance(bcc, str) else list(bcc)
            to_list += bcc_list
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="astrastaging.com")
        if reply_to:
            msg["Reply-To"] = reply_to
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references

        msg.set_content(text_content or "Please view this email in an HTML-capable client.")
        if html_content:
            msg.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(self.host, self.port, timeout=30) as s:
                s.starttls()
                s.login(self.user, self.pw)
                s.send_message(msg, from_addr=self.user, to_addrs=to_list)
            mid = msg["Message-ID"]
            logger.info(f"sent via Gmail SMTP to {', '.join(to_list)}: {mid}")
            return {"success": True, "message_id": mid, "error": None}
        except Exception as e:
            logger.error(f"Gmail SMTP send to {to_list} failed: {e}")
            return {"success": False, "message_id": None, "error": str(e)}
