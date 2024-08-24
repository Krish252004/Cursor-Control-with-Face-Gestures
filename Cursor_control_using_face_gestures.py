import cv2
import mediapipe as mp
import time
import math
import numpy as np
import pyautogui

cam = cv2.VideoCapture(0)
mpface = mp.solutions.face_mesh
mphand = mp.solutions.hands
hand = mphand.Hands(min_detection_confidence=0.7)
face_mesh = mpface.FaceMesh(refine_landmarks=True)
mpdraw = mp.solutions.drawing_utils

CTime = 0
Ptime = 0


def findposition(image, handNo=0, draw=False):
    lmlist = []
    if results.multi_hand_landmarks:
        myhand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myhand.landmark):
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmlist.append([id, cx, cy])
            if draw:
                cv2.circle(image, (cx, cy), 15, (255, 0, 0), 2, cv2.FILLED)
    return lmlist

while True:
    success, image = cam.read()
    if not success:
        continue

    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hand.process(imgRGB)
    face_detection = face_mesh.process(imgRGB)

    if face_detection.multi_face_landmarks:
        multiplefaces = face_detection.multi_face_landmarks
        frame_h, frame_w, _ = image.shape
    else:
        multiplefaces = None

    if multiplefaces:
        for each_face in multiplefaces:
            drawspec = mpdraw.DrawingSpec(thickness=1, circle_radius=1)
            mpdraw.draw_landmarks(image, each_face, mpface.FACEMESH_CONTOURS, drawspec, drawspec)
        singleface = multiplefaces[0].landmark
        for id, landmark in enumerate(singleface[474:478]):
            x_e = int(landmark.x * frame_w)
            y_e = int(landmark.y * frame_h)
            cv2.circle(image, (x_e, y_e), 3, (0, 255, 0))
            if id == 1:
                screen_w, screen_h = pyautogui.size()
                screen_x = screen_w * landmark.x
                screen_y = screen_h * landmark.y
                pyautogui.moveTo(screen_x, screen_y)
        left = [singleface[145], singleface[159]]
        for landmark in left:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(image, (x, y), 3, (0, 255, 255))
        if (left[0].y - left[1].y) < 0.014:
            pyautogui.click()
            pyautogui.sleep(1)

    if results.multi_hand_landmarks:
        for everylandmark in results.multi_hand_landmarks:
            if True:
                mpdraw.draw_landmarks(image, everylandmark, mphand.HAND_CONNECTIONS)

    if results.multi_hand_landmarks:
        x = findposition(image)
        x1 = x[4][1]
        y1 = x[4][2]
        x2 = x[8][1]
        y2 = x[8][2]
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        cv2.circle(image, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(image, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(image, (x1, y1), (x2, y2), (255, 255, 0), 3)
        cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        minvol = -65.25
        maxvol = 0.0
        volumex = np.interp(length, [30, 230], [minvol, maxvol], left=None, right=None, period=None)
        print(volumex)
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import GUID
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL

        IID_IAudioEndpointVolume = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IID_IAudioEndpointVolume, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(volumex, None)

    Ctime = time.time()
    FPS = 1 / (Ctime - Ptime)
    Ptime = Ctime

    flip = cv2.flip(image, flipCode=1)
    cv2.putText(flip, f'FPS:{(int(FPS))}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
    cv2.imshow("Image", flip)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
cam.release()
