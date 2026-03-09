import smtplib

class EmailSender:
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def send_email(self, to_address, subject, body):
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            message = f'Subject: {subject}\n\n{body}'.encode('utf-8')
            server.sendmail(self.username, to_address, message)