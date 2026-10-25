
from flask import Flask, render_template, request, jsonify
import re
import socket
import smtplib

import dns.resolver
import dns.exception

app = Flask(__name__)

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def check_email(email):
    email = email.strip()

    # Check basic email format first.
    if not email or len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        return {
            "email": email or "(empty)",
            "status": "Likely bounce",
            "reason": "The email address has an invalid format."
        }

    domain = email.rsplit("@", 1)[1].lower()

    # Look for the domain's mail servers.
    try:
        records = dns.resolver.resolve(domain, "MX", lifetime=3)
        mail_servers = sorted(
            records, key=lambda record: record.preference
        )

    except dns.resolver.NXDOMAIN:
        return {
            "email": email,
            "status": "Likely bounce",
            "reason": "The email domain does not exist in DNS."
        }

    except dns.resolver.NoAnswer:
        return {
            "email": email,
            "status": "Unknown",
            "reason": "No MX record was found. Mail routing is unconfirmed."
        }

    except (dns.exception.DNSException, socket.gaierror, OSError):
        return {
            "email": email,
            "status": "Unknown",
            "reason": "The DNS lookup failed or may be blocked by the network."
        }

    # Try a limited SMTP recipient check. No email is sent:
    # the code never issues the SMTP DATA command.
    for record in mail_servers[:2]:
        host = str(record.exchange).rstrip(".")

        try:
            with smtplib.SMTP(host, 25, timeout=4) as server:
                server.ehlo("email-checker.local")

                code, _ = server.mail("check@example.com")
                if code >= 400:
                    continue

                code, _ = server.rcpt(email)

                if 200 <= code < 300:
                    return {
                        "email": email,
                        "status": "Likely delivered",
                        "reason": (
                            "The mail server accepted the recipient check. "
                            "This does not guarantee final delivery."
                        )
                    }

                if code in (550, 551, 553):
                    return {
                        "email": email,
                        "status": "Likely bounce",
                        "reason": (
                            "The mail server rejected the recipient. "
                            "Some servers use generic rejection responses."
                        )
                    }

        except (OSError, smtplib.SMTPException, TimeoutError):
            continue

    return {
        "email": email,
        "status": "Unknown",
        "reason": (
            "The mailbox could not be confirmed. The server may hide "
            "recipient status or block SMTP connections."
        )
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def check_addresses():
    data = request.get_json(silent=True) or {}
    raw_emails = data.get("emails", "")

    if not isinstance(raw_emails, str):
        return jsonify({"error": "Enter email addresses as text."}), 400

    addresses = [
        item.strip()
        for item in re.split(r"[\n,;]+", raw_emails)
        if item.strip()
    ]

    if not addresses:
        return jsonify({"error": "Please enter at least one email."}), 400

    if len(addresses) > 20:
        return jsonify({
            "error": "Please check no more than 20 addresses at a time."
        }), 400

    results = [check_email(address) for address in addresses]

    counts = {
        "total": len(results),
        "likely_delivered": sum(
            item["status"] == "Likely delivered" for item in results
        ),
        "likely_bounce": sum(
            item["status"] == "Likely bounce" for item in results
        ),
        "unknown": sum(
            item["status"] == "Unknown" for item in results
        )
    }

    return jsonify({"results": results, "counts": counts})


if __name__ == "__main__":
    import os
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
