import cv2
import pytesseract
import re
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def clean(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text
"""
def read_plate(plate_img):
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(2.0, (8,8))
    gray = clahe.apply(gray)

    gray = cv2.resize(gray, None, fx=2, fy=2)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 5
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h_img = thresh.shape[0]

    filtered = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # keep only large characters
        if h > 0.4 * h_img:   # 🔥 threshold to tune
            filtered.append((x, y, w, h))

    if not filtered:
        return ""
    
    filtered = sorted(filtered, key=lambda b: b[0])

    mask = np.zeros_like(thresh)

    for (x, y, w, h) in filtered:
        mask[y:y+h, x:x+w] = thresh[y:y+h, x:x+w]

    config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(thresh, config=config)

    return clean(text)

"""

import easyocr

reader = easyocr.Reader(['en'])

def read_plate(plate_img):
    results = reader.readtext(plate_img)

    if not results:
        return ""

    # pick highest confidence
    best = max(results, key=lambda x: x[2])

    text = best[1]
    conf = best[2]

    return text