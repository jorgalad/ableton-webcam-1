import cv2
import mediapipe as mp
import numpy as np
import rtmidi
from rtmidi.midiconstants import (CONTROL_CHANGE)
import time
import random

from pythonosc.udp_client import SimpleUDPClient


ip = "127.0.0.1"
to_ableton = 11000
from_ableton = 11001
client = SimpleUDPClient(ip, to_ableton)

midiout = rtmidi.MidiOut()
midiout.open_port(2)

cap = cv2.VideoCapture(1)
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

def convert_range(value, in_min, in_max, out_min, out_max):
    l_span = in_max - in_min
    r_span = out_max - out_min
    scaled_value = (value - in_min) / l_span
    scaled_value = out_min + (scaled_value * r_span)
    return np.round(scaled_value)

def send_notes(pitch=60, repeat=1):
    for i in range(repeat):
        note_on = [0x90, pitch, 112]
        note_off = [0x80, pitch, 0]
        midiout.send_message(note_on)
        time.sleep(random.uniform(0.1, 0.8))
        midiout.send_message(note_off)

def send_mod(cc=1, value=0):
    mod1 = ([CONTROL_CHANGE | 0, cc, value])
    print(value)
    if value > 0.0:
        midiout.send_message(mod1)

def enable_dev(name):
    if name == 'tonic':
        # Start playback
        client.send_message("/live/song/start_playing", None)
        # DEV 1 OFF
        client.send_message("/live/device/set/parameters/value", [0, 0, 0, 0, 0, 0, 0, 128, 0, 1, 2, 3, 5, 5, 6, 7, 8, 9, 10, 11])
        # DEV 2 OFF
        client.send_message("/live/device/set/parameters/value", [0, 1, 0, 0, 0, 0, 0, 128, 0, 1, 2, 3, 3, 5, 6, 7, 8, 8, 10, 11])
    elif name == 'VI':
        # DEV 1 ON
        client.send_message("/live/device/set/parameters/value", [0, 0, 1, 0, 0, 0, 0, 128, 0, 1, 2, 3, 5, 5, 6, 7, 8, 9, 10, 11])
        # DEV 2 OFF
        client.send_message("/live/device/set/parameters/value", [0, 1, 0, 0, 0, 0, 0, 128, 0, 1, 2, 3, 3, 5, 6, 7, 8, 8, 10, 11])
    elif name == 'V':
        # DEV 1 OFF
        client.send_message("/live/device/set/parameters/value", [0, 0, 0, 0, 0, 0, 0, 128, 0, 1, 2, 3, 5, 5, 6, 7, 8, 9, 10, 11])
        # DEV 2 ON
        client.send_message("/live/device/set/parameters/value", [0, 1, 1, 0, 0, 0, 0, 128, 0, 1, 2, 3, 3, 5, 6, 7, 8, 8, 10, 11])
    elif name == 'both':
        # DEV 1 ON
        client.send_message("/live/device/set/parameters/value", [0, 0, 1, 0, 0, 0, 0, 128, 0, 1, 2, 3, 5, 5, 6, 7, 8, 9, 10, 11])
        # DEV 2 ON
        client.send_message("/live/device/set/parameters/value", [0, 1, 1, 0, 0, 0, 0, 128, 0, 1, 2, 3, 3, 5, 6, 7, 8, 8, 10, 11])


def webcam():
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape

        # Drawing lines and such
        img = cv2.rectangle(img, (0, 0), (int(w/2), 270), (64, 224, 208), 2)
        img = cv2.rectangle(img, (0, 0), (int(w/2), 540), (64, 224, 208), 2)
        img = cv2.rectangle(img, (0, 0), (int(w/2), 810), (64, 224, 208), 2)
        img = cv2.rectangle(img, (0, 0), (int(w/2), 1080), (64, 224, 208), 2)
        # Right side
        img = cv2.rectangle(img, (int(w/2), int(h/2)), (w, 0), (164, 24, 208), 2)
        img = cv2.rectangle(img, (int(w / 2), int(h)), (w, int(h/2)), (164, 24, 28), 2)
        # Text
        font = cv2.FONT_HERSHEY_SIMPLEX
        img = cv2.putText(img, 'Tonic (A minor) & Start', (10, h - 18), font, 0.9, (255, 200, 5), 4, cv2.LINE_AA)
        img = cv2.putText(img, 'VI (F major)', (10, h - 290), font, 0.9, (255, 200, 5), 4, cv2.LINE_AA)
        img = cv2.putText(img, 'V (E Maj)', (10, h - 560), font, 0.9, (255, 200, 5), 4, cv2.LINE_AA)
        img = cv2.putText(img, 'Both (F Min)', (10, h - 830), font, 0.9, (255, 200, 5), 4, cv2.LINE_AA)

        img = cv2.putText(img, 'Melody', (1800, h - 30), font, 0.9, (255, 200, 5), 4, cv2.LINE_AA)
        img = cv2.putText(img, 'Modulation', (1749, 520), font, 0.9, (255, 200, 5), 4, cv2.LINE_AA)

        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                pink_x = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_TIP].x
                pink_y = hand_landmarks.landmark[mpHands.HandLandmark.PINKY_TIP].y

                if pink_x < 0.5:
                    if round(pink_y * h) in range(787, 1050):
                        enable_dev('tonic')
                    if round(pink_y * h) in range(525, 786):
                        enable_dev('VI')
                    if round(pink_y * h) in range(262, 524):
                        enable_dev('V')
                    if round(pink_y * h) in range(1, 261):
                        enable_dev('both')
                elif pink_x > 0.5:
                    if round(pink_y * h) in range(525, 1050):
                        print("Melody")
                        v2 = convert_range(pink_y, 1.0, -1.0, 60, 92)
                        send_notes(v2, 1)
                    if round(pink_y * h) in range(1, 524):
                        print("Modulation")
                        v1 = convert_range(pink_y, 1.0, 0.5, 0, 127)
                        send_mod(1, v1)
                else:
                    print('Outside Range')
                mpDraw.draw_landmarks(img, hand_landmarks, mpHands.HAND_CONNECTIONS)
        fps = 1
        cv2.imshow("My face", img)
        cv2.waitKey(fps)

webcam()
