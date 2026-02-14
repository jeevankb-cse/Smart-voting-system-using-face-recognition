# give_vote.py
# Secure Smart Voting System — improved verification: recognized face MUST match entered Aadhaar.
# Prevents same-face multiple IDs: user must confirm the Aadhaar shown by the recognizer.

from sklearn.neighbors import KNeighborsClassifier
import cv2, pickle, numpy as np, os, csv, time, hashlib
from datetime import datetime
from win32com.client import Dispatch
import winsound, tkinter as tk
from tkinter import messagebox, simpledialog

# ---------------- CONFIG ----------------
DATA_DIR = 'data'
BACKGROUND_IMG = "background.png"
VOTES_CSV = "Votes.csv"
HASH_LOCK_FILE = "voted_hashes.txt"
COL_NAMES = ['NAME','VOTE','DATE','TIME']

BLUR_THRESHOLD = 90.0
FACE_SCALE = 1.3; FACE_NEIGHBORS = 5
EYE_SCALE = 1.2; EYE_NEIGHBORS = 5

KNN_K = 5
FADE_DURATION = 2.0
PARTY_KEYS = {'1':'BJP','2':'CONGRESS','3':'AAP','4':'NOTA'}

# If mean KNN neighbor distance is above this → treat as Unknown (tune as needed)
DISTANCE_THRESHOLD = 4000.0

# ---------------- HELPERS ----------------
def speak(msg):
    try:
        Dispatch("SAPI.SpVoice").Speak(msg)
    except:
        pass

def play_alert():
    try:
        winsound.Beep(1000,800)
    except:
        pass

def show_popup(title,msg):
    root = tk.Tk(); root.withdraw(); messagebox.showwarning(title,msg); root.destroy()

def ask_string(title, prompt, parent=None):
    root = tk.Tk(); root.withdraw()
    # simpledialog runs parent window; we'll use root just to show dialog
    res = simpledialog.askstring(title, prompt, parent=root)
    root.destroy()
    return res

def variance_of_laplacian(img):
    return cv2.Laplacian(img, cv2.CV_64F).var()

def voter_hash(label):
    return hashlib.sha256(label.encode('utf-8')).hexdigest()

def ensure_votes_header():
    if not os.path.exists(VOTES_CSV) or os.path.getsize(VOTES_CSV) == 0:
        with open(VOTES_CSV,'w',newline='',encoding='utf-8') as f:
            csv.writer(f).writerow(COL_NAMES)

def load_hashes():
    if not os.path.exists(HASH_LOCK_FILE):
        return set()
    with open(HASH_LOCK_FILE,'r',encoding='utf-8') as f:
        return set(l.strip() for l in f if l.strip())

def save_hash(h):
    with open(HASH_LOCK_FILE,'a',encoding='utf-8') as f:
        f.write(h + "\n")

# Fade overlay text utility
def fade_overlay(base_img, text, pos=(20,40), color=(0,200,100), duration=FADE_DURATION, font_scale=0.8, thickness=2, window_name="Voting"):
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
            cv2.waitKey(700)
            return True

# ---------------- LOAD MODEL / DATA ----------------
os.makedirs(DATA_DIR, exist_ok=True)

names_path = os.path.join(DATA_DIR,'names.pkl')
faces_path = os.path.join(DATA_DIR,'faces_data.pkl')

if not os.path.exists(names_path) or not os.path.exists(faces_path):
    raise FileNotFoundError("names.pkl and faces_data.pkl must exist in data/ — run add_faces.py first.")

with open(names_path,'rb') as f:
    LABELS = pickle.load(f)
with open(faces_path,'rb') as f:
    FACES = pickle.load(f)

min_len = min(len(FACES), len(LABELS))
FACES = np.asarray(FACES[:min_len])
LABELS = np.asarray(LABELS[:min_len])

knn = KNeighborsClassifier(n_neighbors=KNN_K)
knn.fit(FACES, LABELS)

# UI assets
imgBG = cv2.imread(BACKGROUND_IMG)
use_bg = imgBG is not None
frame_w, frame_h = 200,250
frame_x, frame_y = 110,150

# Open camera
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not video.isOpened():
    # fallback without CAP_DSHOW
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        raise RuntimeError("Cannot open webcam.")

face_cas = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cas  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# ---------------- LIVENESS (BLINK) ----------------
def blink_gate(timeout=15):
    blink_open = None
    start = time.time()
    speak("Please look at the camera and blink once to verify.")
    while True:
        if time.time() - start > timeout:
            speak("Blink not detected. Please try again.")
            return False, None, None, None
        ok, frame = video.read()
        if not ok:
            return False, None, None, None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cas.detectMultiScale(gray, FACE_SCALE, FACE_NEIGHBORS)
        msg = "Align your face properly."
        color = (0,200,100)
        if len(faces) == 0:
            msg = "Face not detected. Please move closer."
            color = (0,80,200)
        else:
            x,y,w,h = max(faces, key=lambda b: b[2]*b[3])
            face_gray = gray[y:y+h, x:x+w]
            blur = variance_of_laplacian(face_gray)
            if blur < BLUR_THRESHOLD:
                msg = "Face not clear - hold steady."
                color = (0,80,200)
            else:
                eyes = eye_cas.detectMultiScale(face_gray, EYE_SCALE, EYE_NEIGHBORS)
                eyes_open = (len(eyes) > 0)
                if blink_open is None:
                    blink_open = eyes_open
                elif blink_open and not eyes_open:
                    blink_open = False
                elif (not blink_open) and eyes_open:
                    speak("Blink detected.")
                    cv2.putText(frame, "Blink detected!", (20,80), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,200,100),2)
                    cv2.imshow("Voting", frame)
                    cv2.waitKey(700)
                    return True, frame, (x,y,w,h), gray
                msg = "Please blink once to verify."
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,200,0),2)
        # Compose UI
        if use_bg:
            resized = cv2.resize(frame,(frame_w,frame_h))
            bg = imgBG.copy()
            bg[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = resized
            cv2.putText(bg, msg, (20,40), cv2.FONT_HERSHEY_SIMPLEX,0.7, color, 2)
            cv2.putText(bg, "Press Q to cancel", (20,75), cv2.FONT_HERSHEY_SIMPLEX,0.6,(80,80,80),1)
            cv2.imshow("Voting", bg)
        else:
            cv2.putText(frame, msg, (20,40), cv2.FONT_HERSHEY_SIMPLEX,0.7, color, 2)
            cv2.imshow("Voting", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False, None, None, None

# ---------------- MAIN ----------------
ensure_votes_header()
voted = load_hashes()

ok_live, frame_live, face_box, gray_live = blink_gate()
if not ok_live:
    video.release(); cv2.destroyAllWindows(); raise SystemExit("Liveness failed or cancelled.")

x,y,w,h = face_box
crop = frame_live[y:y+h, x:x+w]
resized = cv2.resize(crop,(50,50)).flatten().reshape(1,-1)

# get KNN distances to check confidence
distances, indices = knn.kneighbors(resized, n_neighbors=KNN_K, return_distance=True)
mean_distance = float(distances.mean())
pred = knn.predict(resized)
label = str(pred[0]) if len(pred) > 0 else "Unknown"

# treat as Unknown if mean distance too large
if mean_distance > DISTANCE_THRESHOLD:
    label = "Unknown"

# Show recognition result and require Aadhaar confirmation from user
if label == "Unknown":
    speak("Identity not verified.")
    if use_bg:
        bg = imgBG.copy(); small = cv2.resize(frame_live,(frame_w,frame_h))
        bg[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = small
        fade_overlay(bg, "Identity not verified. Contact admin.", pos=(20,60), color=(0,80,200))
    else:
        fade_overlay(frame_live, "Identity not verified. Contact admin.", pos=(20,60), color=(0,80,200))
    video.release(); cv2.destroyAllWindows(); raise SystemExit

# Prompt user to confirm the recognized Aadhaar — user must enter the SAME Aadhaar
speak(f"Identified Aadhaar {label}. Please enter your Aadhaar to confirm.")
confirm_msg = f"Identified Aadhaar: {label}\nPlease enter your Aadhaar to confirm (must match)."
entered = ask_string("Confirm Aadhaar", confirm_msg)

if entered is None:
    # user cancelled
    speak("Voting cancelled by user.")
    video.release(); cv2.destroyAllWindows(); raise SystemExit("Voting cancelled by user.")

entered = entered.strip()
if entered == "":
    speak("Aadhaar is required. Voting cancelled.")
    show_popup("Error", "Aadhaar entry required. Voting cancelled.")
    video.release(); cv2.destroyAllWindows(); raise SystemExit("Aadhaar entry required.")

# Enforce that entered Aadhaar must equal the recognized label
if entered != label:
    speak("Entered Aadhaar does not match recognized Aadhaar. Access denied.")
    play_alert()
    show_popup("Access Denied", "Entered Aadhaar does not match the recognized Aadhaar. Voting denied.")
    if use_bg:
        bg = imgBG.copy(); small = cv2.resize(frame_live,(frame_w,frame_h))
        bg[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = small
        fade_overlay(bg, "Access Denied — Aadhaar mismatch", pos=(20,60), color=(0,80,200))
    else:
        fade_overlay(frame_live, "Access Denied — Aadhaar mismatch", pos=(20,60), color=(0,80,200))
    video.release(); cv2.destroyAllWindows(); raise SystemExit("Aadhaar mismatch — voting denied.")

# Now we have a confirmed label (entered == label)
vh = voter_hash(label)
if vh in voted:
    speak("Access denied. You have already voted.")
    play_alert()
    show_popup("Access Denied","You have already voted. Multiple votes are not allowed.")
    if use_bg:
        bg = imgBG.copy(); small = cv2.resize(frame_live,(frame_w,frame_h))
        bg[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = small
        fade_overlay(bg, "Access Denied — You have already voted", pos=(20,60), color=(0,80,200))
    else:
        fade_overlay(frame_live, "Access Denied — You have already voted", pos=(20,60), color=(0,80,200))
    video.release(); cv2.destroyAllWindows(); raise SystemExit

# Identity verified — allow voting
speak("Identity verified. You may cast your vote now.")
if use_bg:
    base = imgBG.copy()
    small = cv2.resize(frame_live,(frame_w,frame_h))
    base[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = small
    fade_overlay(base, "Identity verified. Please cast your vote.", pos=(20,40), color=(0,200,100))
else:
    fade_overlay(frame_live, "Identity verified. Please cast your vote.", pos=(20,40), color=(0,200,100))

# Voting input loop
while True:
    ok, frame = video.read()
    if not ok:
        break
    if use_bg:
        small = cv2.resize(frame,(frame_w,frame_h))
        bg = imgBG.copy()
        bg[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = small
        cv2.putText(bg, "Press Q to quit", (20,75), cv2.FONT_HERSHEY_SIMPLEX,0.6,(80,80,80),1)
        cv2.imshow("Voting", bg)
    else:
        cv2.putText(frame,"Press Q to quit",(20,75),cv2.FONT_HERSHEY_SIMPLEX,0.6,(80,80,80),1)
        cv2.imshow("Voting", frame)

    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break
    key = chr(k) if 32<=k<127 else ''
    if key in PARTY_KEYS:
        party = PARTY_KEYS[key]
        ts = datetime.now(); date_s = ts.strftime("%d-%m-%Y"); time_s = ts.strftime("%H:%M-%S")
        ensure_votes_header()
        with open(VOTES_CSV,'a',newline='',encoding='utf-8') as f:
            csv.writer(f).writerow([label, party, date_s, time_s])
        save_hash(vh)
        speak("Your vote has been recorded. Thank you.")
        if use_bg:
            base2 = imgBG.copy(); small = cv2.resize(frame,(frame_w,frame_h))
            base2[frame_y:frame_y+frame_h, frame_x:frame_x+frame_w] = small
            fade_overlay(base2, "Your vote has been securely recorded. Thank you!", pos=(20,60), color=(0,200,100))
        else:
            fade_overlay(frame, "Your vote has been securely recorded. Thank you!", pos=(20,60), color=(0,200,100))
        cv2.waitKey(1000)
        break

video.release()
cv2.destroyAllWindows()
