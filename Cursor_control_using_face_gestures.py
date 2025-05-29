import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import math
import pyautogui
import time
from collections import deque
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from comtypes import GUID

IID_IAudioEndpointVolume = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IID_IAudioEndpointVolume, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
minVol, maxVol = volume.GetVolumeRange()[:2]

num_classes = 4

def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(64, kernel_size=3, activation='relu', input_shape=(42, 1)),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Conv1D(128, kernel_size=3, activation='relu'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

model = create_model()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def preprocess_landmarks(landmarks):
    coords = []
    for lm in landmarks:
        coords.append(lm.x)
        coords.append(lm.y)
    coords = np.array(coords)
    return coords.reshape(1, -1, 1)

def set_volume(level):
    vol = np.interp(level, [0, 1], [minVol, maxVol])
    volume.SetMasterVolumeLevel(vol, None)

gesture_names = ['Volume Up', 'Volume Down', 'Mute/Unmute', 'Screenshot']
pred_queue = deque(maxlen=5)
last_action_time = 0
is_muted = False
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)
    gesture_text = "No Hand Detected"
    new_vol = volume.GetMasterVolumeLevelScalar()

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0].landmark
        mp_draw.draw_landmarks(img, result.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
        input_data = preprocess_landmarks(hand_landmarks)
        prediction = model.predict(input_data, verbose=0)
        class_id = int(np.argmax(prediction))
        confidence = prediction[0][class_id]
        pred_queue.append(class_id)
        stable_prediction = max(set(pred_queue), key=pred_queue.count)
        gesture_text = f"{gesture_names[stable_prediction]} ({confidence*100:.1f}%)"

        if confidence > 0.7 and (time.time() - last_action_time) > 1:
            last_action_time = time.time()
            if stable_prediction == 0:
                new_vol = min(new_vol + 0.05, 1.0)
                set_volume(new_vol)
            elif stable_prediction == 1:
                new_vol = max(new_vol - 0.05, 0.0)
                set_volume(new_vol)
            elif stable_prediction == 2:
                if not is_muted:
                    set_volume(0.0)
                    is_muted = True
                else:
                    set_volume(0.5)
                    is_muted = False
            elif stable_prediction == 3:
                pyautogui.screenshot("gesture_screenshot.png")

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    bar_height = int(np.interp(new_vol, [0.0, 1.0], [400, 150]))
    cv2.rectangle(img, (50, bar_height), (85, 400), (0, 255, 0), cv2.FILLED)
    vol_percent = int(new_vol * 100)
    cv2.putText(img, f'{vol_percent} %', (40, 430), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
    cv2.putText(img, gesture_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow("Hand Gesture Volume Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
