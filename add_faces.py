# add_faces.py
# Registers a new voter using their Aadhaar number and ensures face clarity & blink verification.
import cv2, pickle, numpy as np, os, time
from win32com.client import Dispatch

# Config
DATA_DIR = 'data'
FRAMES_TOTAL = 51
CAPTURE_EVERY_N_FRAME = 2
BLUR_THRESHOLD = 90.0
FACE_SCALE = 1.3; FACE_NEIGHBORS = 5
EYE_SCALE = 1.2; EYE_NEIGHBORS = 5
FADE_DURATION = 2.0  # seconds fade

# Helpers
def speak(text):
    try:
        Dispatch("SAPI.SpVoice").Speak(text)
    except Exception:
        pass

def variance_of_laplacian(img):
    return cv2.Laplacian(img, cv2.CV_64F).var()

def fade_message(window_name, base_img, text, pos=(50,240), font_scale=1.0, thickness=2,
                 color=(0,200,100), duration=FADE_DURATION):
    start = time.time()
    overlay = base_img.copy()
    while True:
        now = time.time()
        alpha = min(1.0, (now - start) / duration)
        tmp = overlay.copy()
        cv2.putText(tmp, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
        blended = cv2.addWeighted(tmp, alpha, overlay, 1 - alpha, 0)
        cv2.imshow(window_name, blended)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        if alpha >= 1.0:
            cv2.waitKey(600)
            return True

# Setup
os.makedirs(DATA_DIR, exist_ok=True)
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not video.isOpened(): raise RuntimeError("Cannot open webcam.")
face_cas = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cas  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

faces_data = []; i = 0
name = input("Enter your Aadhaar number: ").strip()
if not name: raise ValueError("Aadhaar cannot be empty.")

# Improved blink detection
def wait_for_blink(timeout=15):
    blink_state_open = None
    start = time.time()
    speak("Please look at the camera and blink once.")
    while True:
        if time.time() - start > timeout:
            speak("Blink not detected. Please try again.")
            return False
        ok, frame = video.read()
        if not ok: return False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cas.detectMultiScale(gray, FACE_SCALE, FACE_NEIGHBORS)
        if len(faces) == 0:
            cv2.putText(frame, "Face not detected. Please align.", (20,40), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,80,200),2)
        else:
            x,y,w,h = max(faces, key=lambda b:b[2]*b[3])
            fg = gray[y:y+h, x:x+w]
            eyes = eye_cas.detectMultiScale(fg, EYE_SCALE, EYE_NEIGHBORS)
            eyes_open = (len(eyes) > 0)
            if blink_state_open is None:
                blink_state_open = eyes_open
            elif blink_state_open and not eyes_open:
                blink_state_open = False
            elif (not blink_state_open) and eyes_open:
                speak("Blink detected.")
                cv2.putText(frame, "Blink detected!", (20,80), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,200,100),2)
                cv2.imshow("Register", frame); cv2.waitKey(700)
                return True
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame, "Please blink once to verify.", (20,40), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,200,100),2)
        cv2.imshow("Register", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): return False

# Start
black = np.zeros((480,640,3), dtype=np.uint8)
fade_message("Register", black, "SMART VOTING SYSTEM - FACE REGISTRATION", pos=(30,40), font_scale=0.9, color=(190,200,255))

if not wait_for_blink():
    video.release(); cv2.destroyAllWindows(); raise SystemExit("Blink not detected.")

speak("Capturing face samples. Hold steady.")
print("Capturing samples...")

while True:
    ret, frame = video.read()
    if not ret: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cas.detectMultiScale(gray, FACE_SCALE, FACE_NEIGHBORS)
    if len(faces) == 0:
        cv2.putText(frame, "Face not detected - align to camera", (20,40), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,100,200),2)
        cv2.imshow("Register", frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
        continue
    x,y,w,h = max(faces, key=lambda b:b[2]*b[3])
    face_gray = gray[y:y+h, x:x+w]
    blur = variance_of_laplacian(face_gray)
    if blur < BLUR_THRESHOLD:
        cv2.putText(frame, "Face not clear - hold steady", (20,40), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,100,200),2)
        cv2.imshow("Register", frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
        continue
    crop = frame[y:y+h, x:x+w]
    resized = cv2.resize(crop, (50,50))
    if (len(faces_data) < FRAMES_TOTAL) and (i % CAPTURE_EVERY_N_FRAME == 0):
        faces_data.append(resized)
    i += 1
    cv2.putText(frame, f"Samples: {len(faces_data)}/{FRAMES_TOTAL}", (20,80), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,200,100),2)
    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,200,0),1)
    cv2.imshow("Register", frame)
    if len(faces_data) >= FRAMES_TOTAL or (cv2.waitKey(1)&0xFF)==ord('q'):
        break

video.release(); cv2.destroyAllWindows()

faces_data = np.asarray(faces_data).reshape((FRAMES_TOTAL, -1))
pnames = os.path.join(DATA_DIR, 'names.pkl'); pf = os.path.join(DATA_DIR, 'faces_data.pkl')

# names
if not os.path.exists(pnames):
    names = [name]*FRAMES_TOTAL
else:
    with open(pnames,'rb') as f: names = pickle.load(f)
    names = names + [name]*FRAMES_TOTAL
with open(pnames,'wb') as f: pickle.dump(names,f)

# faces
if not os.path.exists(pf):
    with open(pf,'wb') as f: pickle.dump(faces_data,f)
else:
    with open(pf,'rb') as f: faces = pickle.load(f)
    faces = np.append(faces, faces_data, axis=0)
    with open(pf,'wb') as f: pickle.dump(faces,f)

fade_message("Register", np.zeros((480,640,3), dtype=np.uint8), "Registration Complete! Thank you.", pos=(80,240), color=(0,200,100))
speak("Registration complete. Thank you.")
print("Registration complete.")

