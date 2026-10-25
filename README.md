<CodeBlock language="markdown" editable>
# Email Deliverability Checker


A web application built with HTML, CSS, JavaScript, Python and Flask to
check email address formatting and available mail-server information.
Features
- Accepts multiple email addresses.
- Checks basic email syntax.
- Looks up DNS mail-routing records.
- Attempts a limited SMTP recipient check where network access permits.
- Reports Likely delivered, Likely bounce or Unknown.
- Explains each result.
- Does not send email messages.
How it works
The application validates the address format, looks up the domain's MX
records and may attempt an SMTP recipient check. It never sends an email.
Limitations
SMTP checks are not definitive. Some providers hide mailbox status or
block verification attempts. Hosting providers may also block outbound
SMTP connections.

"Likely delivered" means a server accepted the recipient check; it does
not guarantee final delivery. "Likely bounce" indicates a malformed
address or a rejection that commonly suggests an invalid recipient.
"Unknown" means the available checks could not confirm the result.
Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in the project folder.
3. Install dependencies:
   
   pip install -r requirements.txt
4. Run the application:
   
   python app.py
5. Open http://127.0.0.1:5000 in your browser.
Deployment
The app can be deployed as a Python web service on a compatible hosting
provider. Some providers block outbound SMTP connections. If SMTP is
blocked, the application may return Unknown for addresses it cannot
verify. Test the deployed version and document its actual limitations.
Privacy and responsible use
The app does not send messages. Only check addresses you are permitted
to process, and do not enter sensitive personal information.
</CodeBlock>