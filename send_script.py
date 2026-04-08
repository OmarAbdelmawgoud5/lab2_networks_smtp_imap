import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
PORT = 587


def send_email(email, password, recipient, subject, body):
    try:
        server = smtplib.SMTP(SMTP_SERVER, PORT)
        server.starttls()
        server.login(email, password)
        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        _ = server.send_message(msg)
        _ = server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")


send_email(
    "01159245655a@gmail.com",
    "rqqypgruzanvpgql",
    "omar.abdelmawgoud10@gmail.com",
    "is this still working",
    "testing this service",
)
