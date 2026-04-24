import pyttsx3
import smtplib

from email.mime.text import MIMEText

engine = pyttsx3.init()

def voice_alert(msg):
    engine.say(msg)
    engine.runAndWait()


def send_email_alert():
    sender_email = "bhumi3663@gmail.com"
    receiver_email = "bhumi3663@gmail.com"
    password = "pwotzhqsspmkqivt"

    message = MIMEText("Emergency! Fall detected. Please check immediately.")
    message["Subject"] = "Fall Detection Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()

        voice_alert("Emergency alert sent")   # ✅ add this
        print("Email sent successfully")

    except Exception as e:
        print("Error sending email:", e)