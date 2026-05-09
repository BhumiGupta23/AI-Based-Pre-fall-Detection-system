import cv2
import mediapipe as mp
import numpy as np

class FallDetection:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360-angle if angle > 180 else angle

    def detect(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            shoulder = [lm[11].x, lm[11].y]
            hip = [lm[23].x, lm[23].y]
            knee = [lm[25].x, lm[25].y]

            angle = self.calculate_angle(shoulder, hip, knee)

            if 25 < angle < 50:
                return "WARNING", angle
            elif angle >= 50:
                return "FALL", angle
            else:
                return "NORMAL", angle

        return "NO PERSON", 0