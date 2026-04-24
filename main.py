import cv2
import time
import os
import winsound
from datetime import datetime
from detection import FallDetection
from alert import voice_alert
from database import create_db, insert_event
from alert import send_email_alert

# Setup
cap = cv2.VideoCapture("one.mp4")
detector = FallDetection()
create_db()

fall_time = None
alert_sent = False
last_alert_time = 0
fall_counter = 0
filename = ""

start_time = time.time()   # START FIX

# Create images folder
if not os.path.exists("images"):
    os.makedirs("images")

while True:
    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    status, angle = detector.detect(frame)

    # ================= START STABILIZATION =================
    if time.time() - start_time < 3:
        cv2.imshow("Fall Detection", frame)
        if cv2.waitKey(10) & 0xFF == 27:
            break
        continue

    # ================= WARNING =================
    if status == "WARNING":
        if time.time() - last_alert_time > 5:
            voice_alert("Warning. Please stabilize yourself")
            last_alert_time = time.time()

    # ================= FALL DETECTION =================
    if status == "FALL":
        fall_counter += 1
    else:
        fall_counter = 0

    if fall_counter > 8:
        if fall_time is None:
            fall_time = time.time()
            alert_sent = False

            now = datetime.now()
            filename = f"images/fall_{now.strftime('%H%M%S')}.jpg"

            blurred = cv2.GaussianBlur(frame, (51, 51), 0)
            cv2.imwrite(filename, blurred)

    # ================= RECOVERY CHECK =================
    if fall_time and filename != "":
        if time.time() - fall_time > 10:
            if not alert_sent:
                if time.time() - last_alert_time > 5:
                    voice_alert("Emergency. No recovery detected")
                    for _ in range(4):
                        winsound.Beep(2000,500)
                        winsound.Beep(1000,500)
                    send_email_alert()
                    last_alert_time = time.time()

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

    # ================= RESET LOGIC =================
    if fall_time and time.time() - fall_time < 5:
     status = "FALL"
    #if status != "FALL":
        #fall_time = None
        #filename = ""
        

    # ================= DISPLAY =================
    if status == "FALL":
        color = (0, 0, 255)   # Red
    elif status == "WARNING":
        color = (0, 255, 255) # Yellow
    else:
        color = (0, 255, 0)   # Green

    cv2.putText(frame, status, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Fall Detection", frame)

    if cv2.waitKey(10) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()