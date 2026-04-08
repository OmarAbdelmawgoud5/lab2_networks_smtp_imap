import imaplib
import email

IMAP_SERVER = "imap.gmail.com"
PORT = 993


def fetch_last_email(username, password):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, PORT)
        mail.login(username, password)
        mail.select("INBOX")
        _, data = mail.search(None, "ALL")
        latest_id = data[0].split()[-1]
        _, msg_data = mail.fetch(latest_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        print("From:", msg["From"])
        print("Subject:", msg["Subject"])
        print("Body:")
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    print(part.get_payload(decode=True).decode())
                    break
        else:
            print(msg.get_payload(decode=True).decode())
        mail.logout()
        print("Logged out")
    except Exception as e:
        print(f"Error fetching email: {e}")


fetch_last_email("01159245655a@gmail.com", "rqqypgruzanvpgql")
