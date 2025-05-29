# Hand and Face Gesture Recognition for System Control

This project uses real-time hand gesture recognition to control system volume and perform utility actions like muting/unmuting or taking screenshots — all using your webcam and hand gestures.

## Features

- Volume Up / Down using hand gestures
- Mute / Unmute with toggle gesture
- Take a screenshot with a custom gesture
- Real-time hand tracking using MediaPipe
- CNN-based gesture classification with TensorFlow
- Pycaw for volume control on Windows
- PyAutoGUI for automated screenshot

## How It Works

- MediaPipe detects hand landmarks (21 points per hand).
- The 2D `(x, y)` coordinates of landmarks are flattened and preprocessed.
- These coordinates are passed to a **1D Convolutional Neural Network (CNN)** built using TensorFlow/Keras.
- The CNN classifies the gesture into one of four predefined categories.
- A queue is used to stabilize predictions by averaging recent outputs.
- Based on the predicted gesture, the corresponding action (volume change, mute/unmute, screenshot) is performed.

## Tech Stack

- Python 3.8+
- OpenCV – Webcam input and UI rendering
- MediaPipe – Hand landmark detection
- TensorFlow / Keras – Gesture classification (Conv1D model)
- NumPy – Data preprocessing
- PyAutoGUI – Screenshot capture
- PyCAW – Audio volume control via COM
- Deque – Smoothing predictions for stable classification

## Gesture Classes

| Class ID | Gesture        | Action              |
|----------|----------------|---------------------|
| 0        | Volume Up      | Increases volume    |
| 1        | Volume Down    | Decreases volume    |
| 2        | Mute/Unmute    | Toggles mute        |
| 3        | Screenshot     | Takes a screenshot  |
