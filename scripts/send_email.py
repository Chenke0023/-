#!/usr/bin/env python3

import argparse
import os
import smtplib
from email.message import EmailMessage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--attach", action="append", default=[])
    args = parser.parse_args()

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    mail_to = os.getenv("MAIL_TO")
    mail_from = os.getenv("MAIL_FROM", smtp_user or "")

    missing = [
        name
        for name, val in [
            ("SMTP_HOST", smtp_host),
            ("SMTP_USER", smtp_user),
            ("SMTP_PASS", smtp_pass),
            ("MAIL_TO", mail_to),
        ]
        if not val
    ]
    if missing:
        raise SystemExit(f"Missing required env vars: {', '.join(missing)}")

    msg = EmailMessage()
    msg["Subject"] = args.subject
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg.set_content(args.body)

    for path in args.attach:
        if not os.path.exists(path):
            raise SystemExit(f"Attachment not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        filename = os.path.basename(path)
        msg.add_attachment(
            data,
            maintype="application",
            subtype="octet-stream",
            filename=filename,
        )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)


if __name__ == "__main__":
    main()
