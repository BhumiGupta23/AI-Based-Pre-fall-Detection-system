import cv2
import time
import os
import threading
from datetime import datetime
from detection import FallDetection
from alert import voice_alert, send_email_alert
from database import create_db, insert_event

# ---------- SETUP ----------
cap = cv2.VideoCapture("emer.mp4")
detector = FallDetection()
create_db()

alert_sent = False
filename = ""

fall_counter = 0
fallen_persist = 0

start_time = time.time()

#last_normal_time = 0
#stable_status ="NORMAL"
#status_counter = 0

if not os.path.exists("images"):
    os.makedirs("images")

while True:

    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    status, angle = detector.detect(frame)

    # -------- IGNORE STARTUP ----------
    if time.time() - start_time < 5:
        cv2.imshow("Fall Detection", frame)

        if cv2.waitKey(30) & 0xFF == 27:
            break

        continue

    # -------- FALL COUNT ----------
    if status == "FALL":
        fall_counter += 1
    else:
        fall_counter = 0

    # -------- FALL CONFIRM ----------
    if fall_counter > 30:
        fallen_persist += 1

        # Save fall image once
        if filename == "":
            now = datetime.now()

            filename = f"images/fall_{now.strftime('%H%M%S')}.jpg"

            blurred = cv2.GaussianBlur(frame, (51, 51), 0)

            cv2.imwrite(filename, blurred)

    else:
        fallen_persist = 0

    # -------- EMERGENCY ----------
    if (fallen_persist > 150 and not alert_sent):

        threading.Thread(
            target=voice_alert,
            args=("Emergency. No recovery detected",),
            daemon=True
        ).start()

        threading.Thread(
            target=send_email_alert,
            daemon=True
        ).start()

        now = datetime.now()

        data = (
            str(now.date()),
            now.strftime("%H:%M:%S"),
            "Fall",
            angle,
            "High",
            "Not Recovered",
            "Yes",
            filename
        )

        insert_event(data)

        alert_sent = True

    # -------- RECOVERY FIX ----------
    if status != "FALL":
        fallen_persist = 0
        alert_sent = False
        filename = ""

    # -------- DISPLAY ----------
    if status == "FALL":
        color = (0, 0, 255)

    elif status == "WARNING":
        color = (0, 255, 255)

    else:
        status = "NORMAL"
        color = (0, 255, 0)

    cv2.putText(
        frame,
        status,
        (50, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )

    cv2.imshow("Fall Detection", frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()