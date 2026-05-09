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

# 👉 FALL sirf tab show hoga jab confirm ho
    #if fallen_persist > 10 and status == "FALL":
     #   display_status = "FALL"
    #else:
      #   display_status = "NORMAL" if status not in ["WARNING"] else "WARNING"

    if fallen_persist > 15 and fall_counter > 30:
         display_status = "FALL"
    elif status == "WARNING":
         display_status = "WARNING"
    else:
        display_status = "NORMAL"

        


# 👉 Color logic
    if display_status == "FALL":
          color = (0, 0, 255)

    elif display_status == "WARNING":
          color = (0, 255, 255)

    else:
          display_status = "NORMAL"
          color = (0, 255, 0)

# 👉 Color logic ke baad
    overlay =frame.copy()
    if display_status == "FALL":
        overlay = frame.copy()
        overlay[:] = (0,0,255)
    cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

# 🔥 1. DARK OVERLAY (yaha add karo)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0,0), (frame.shape[1], frame.shape[0]), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)


# 🔥 2. STATUS BOX (overlay ke baad)
    cv2.rectangle(frame, (20,20), (320,100), (0,0,0), -1)


# 🔥 3. BIG FALL ALERT (sirf fall pe)
    if display_status == "FALL":
     cv2.putText(frame, "!!! FALL DETECTED !!!", (80,350),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 4)


# 🔥 4. STATUS TEXT
    cv2.putText(frame, f"Status: {display_status}", (30,70),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


# 🔥 5. ANGLE TEXT
    cv2.putText(frame, f"Angle: {int(angle)}", (30,130),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)


# 🔥 6. SYSTEM TEXT
    cv2.putText(frame, "Monitoring Active", (350,40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)


# 👉 Show window
    cv2.imshow("Fall Detection", frame)




# 👉 Exit condition (IMPORTANT: same indentation)
    if cv2.waitKey(30) & 0xFF == 27:
        break
    

cap.release()
cv2.destroyAllWindows()