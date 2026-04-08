import smtplib
import imaplib
import email
import yaml
import tkinter as tk
from tkinter import messagebox, scrolledtext
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- Server Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT   = 993

# --- Core Functions ---
def send_email(email_address, password, recipient, subject, body):
    """Send an email and return a success or error message."""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(email_address, password)

        msg = MIMEMultipart()
        msg["From"]    = email_address
        msg["To"]      = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully!"

    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Check your email and App Password."
    except smtplib.SMTPConnectError:
        return False, "Could not connect to the SMTP server."
    except smtplib.SMTPRecipientsRefused:
        return False, f"Recipient '{recipient}' was refused by the server."
    except Exception as e:
        return False, f"Error sending email: {e}"

def fetch_last_email(username, password):
    """Fetch the latest email and return it as a formatted string."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(username, password)
        mail.select("INBOX")

        _, data = mail.search(None, "ALL")
        if not data[0]:
            return False, "Inbox is empty. No emails to fetch."

        latest_id = data[0].split()[-1]
        _, msg_data = mail.fetch(latest_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Format the output string
        output = f"From: {msg['From']}\n"
        output += f"Subject: {msg['Subject']}\n"
        output += "-"*40 + "\nBody:\n"

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    output += part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            output += msg.get_payload(decode=True).decode(errors='ignore')

        mail.logout()
        return True, output

    except imaplib.IMAP4.error:
        return False, "Authentication failed. Check credentials/IMAP settings."
    except Exception as e:
        return False, f"Error fetching email: {e}"

# --- Tkinter GUI Application ---
class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Client App")
        self.root.geometry("600x700")
        self.root.config(padx=20, pady=20)

        # Load secrets for pre-filling 
        self.secrets = {"sender_email": "", "sender_password": "", "reciever_email": ""}
        try:
            with open('secret.yaml', 'r') as file:
                self.secrets = yaml.safe_load(file) or self.secrets
        except FileNotFoundError:
            pass # It's fine if the file doesn't exist, fields will just be empty

        self.create_widgets()

    def create_widgets(self):
        # 1. Sender Email
        tk.Label(self.root, text="Your Email:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.email_entry = tk.Entry(self.root, width=50)
        self.email_entry.grid(row=0, column=1, pady=5)
        self.email_entry.insert(0, self.secrets.get("sender_email", ""))

        # 2. Password
        tk.Label(self.root, text="App Password:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.pass_entry = tk.Entry(self.root, width=50, show="*")
        self.pass_entry.grid(row=1, column=1, pady=5)
        self.pass_entry.insert(0, self.secrets.get("sender_password", ""))

        # 3. Recipient Email
        tk.Label(self.root, text="Recipient Email:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.recipient_entry = tk.Entry(self.root, width=50)
        self.recipient_entry.grid(row=2, column=1, pady=5)
        self.recipient_entry.insert(0, self.secrets.get("reciever_email", ""))

        # 4. Subject
        tk.Label(self.root, text="Subject:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        self.subject_entry = tk.Entry(self.root, width=50)
        self.subject_entry.grid(row=3, column=1, pady=5)

        # 5. Body
        tk.Label(self.root, text="Message Body:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="nw", pady=5)
        self.body_text = scrolledtext.ScrolledText(self.root, width=48, height=8, wrap=tk.WORD)
        self.body_text.grid(row=4, column=1, pady=5)

        # 6. Action Buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Send Email", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15, command=self.handle_send).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Fetch Last Email", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15, command=self.handle_fetch).pack(side=tk.LEFT, padx=10)

        # 7. Output / Inbox Display area
        tk.Label(self.root, text="Console / Inbox Display:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="nw", pady=5)
        self.output_display = scrolledtext.ScrolledText(self.root, width=65, height=12, wrap=tk.WORD, bg="#f4f4f4")
        self.output_display.grid(row=7, column=0, columnspan=2, pady=5)
        self.output_display.config(state=tk.DISABLED)

    def log_to_display(self, message):
        """Helper to write messages to the bottom text area."""
        self.output_display.config(state=tk.NORMAL)
        self.output_display.delete(1.0, tk.END)
        self.output_display.insert(tk.END, message)
        self.output_display.config(state=tk.DISABLED)

    def handle_send(self):
        # Gather inputs
        sender = self.email_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        recipient = self.recipient_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()

        if not all([sender, pwd, recipient]):
            messagebox.showwarning("Missing Info", "Sender, Password, and Recipient are required fields.")
            return

        self.log_to_display("Sending email... Please wait.")
        self.root.update() # Force UI to update

        success, message = send_email(sender, pwd, recipient, subject, body)
        
        if success:
            messagebox.showinfo("Success", message)
            self.log_to_display("Status: " + message)
            self.body_text.delete(1.0, tk.END) # Clear body after sending
            self.subject_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)
            self.log_to_display("Error: " + message)

    def handle_fetch(self):
        sender = self.email_entry.get().strip()
        pwd = self.pass_entry.get().strip()

        if not all([sender, pwd]):
            messagebox.showwarning("Missing Info", "Sender Email and Password are required to fetch emails.")
            return

        self.log_to_display("Fetching latest email... Please wait.")
        self.root.update()

        success, content = fetch_last_email(sender, pwd)
        self.log_to_display(content)


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailApp(root)
    root.mainloop()
