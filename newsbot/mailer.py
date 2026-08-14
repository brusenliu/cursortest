from __future__ import annotations

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

from newsbot.config import Settings

log = logging.getLogger("newsbot.mailer")

PROVIDERS: dict[str, tuple[str, int, str]] = {
    "qq.com": ("smtp.qq.com", 465, "ssl"),
    "foxmail.com": ("smtp.qq.com", 465, "ssl"),
    "163.com": ("smtp.163.com", 465, "ssl"),
    "126.com": ("smtp.126.com", 465, "ssl"),
    "yeah.net": ("smtp.yeah.net", 465, "ssl"),
    "gmail.com": ("smtp.gmail.com", 587, "starttls"),
    "googlemail.com": ("smtp.gmail.com", 587, "starttls"),
    "outlook.com": ("smtp.office365.com", 587, "starttls"),
    "hotmail.com": ("smtp.office365.com", 587, "starttls"),
    "live.com": ("smtp.office365.com", 587, "starttls"),
    "sina.com": ("smtp.sina.com", 465, "ssl"),
    "139.com": ("smtp.139.com", 465, "ssl"),
}


def _domain(address: str) -> str:
    _, addr = parseaddr(address)
    if "@" not in addr:
        return ""
    return addr.rsplit("@", 1)[-1].lower()


def resolve_smtp(settings: Settings) -> tuple[str, int, str]:
    if settings.smtp_host:
        security = settings.smtp_security or ("ssl" if settings.smtp_port == 465 else "starttls")
        return settings.smtp_host, settings.smtp_port, security
    domain = _domain(settings.smtp_user or settings.smtp_from or settings.mail_to)
    if domain in PROVIDERS:
        host, port, security = PROVIDERS[domain]
        port = settings.smtp_port or port
        security = settings.smtp_security or security
        return host, port, security
    raise RuntimeError(
        "无法从邮箱推断 SMTP。请设置 SMTP_HOST，例如 smtp.qq.com / smtp.gmail.com"
    )


def send_email(settings: Settings, subject: str, html_body: str) -> None:
    if not settings.mail_enabled:
        raise RuntimeError("邮件未配置：需要 MAIL_TO 和 SMTP_PASSWORD")
    host, port, security = resolve_smtp(settings)
    from_addr = settings.smtp_from or settings.smtp_user
    user = settings.smtp_user or from_addr
    recipients = settings.mail_recipients
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("每日资讯", from_addr))
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    log.info("sending mail via %s:%s (%s) to %s", host, port, security, recipients)
    context = ssl.create_default_context()
    if security == "ssl":
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as smtp:
            smtp.login(user, settings.smtp_password)
            smtp.sendmail(from_addr, recipients, msg.as_string())
    else:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            if security == "starttls":
                smtp.starttls(context=context)
                smtp.ehlo()
            smtp.login(user, settings.smtp_password)
            smtp.sendmail(from_addr, recipients, msg.as_string())
    log.info("mail sent: %s", subject)
