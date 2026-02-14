from flask import Flask, render_template, Response, jsonify, request
import cv2, pickle, numpy as np, os, hashlib, csv, time
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)

DATA_DIR = "data"
VOTES_FILE = os.path.join(DATA_DIR, "Votes.csv")
HASH_FILE = os.path.join(DATA_DIR, "voted_hashes.txt")

# recognition config
KNN_K = 5
FRAME_SIZE = (50, 50)          # same as registration
DISTANCE_THRESHOLD = 4000.0    # <-- may need tuning for your dataset

# Load trained face data (names are Aadhaar numbers in your setup)
with open(os.path.join(DATA_DIR, "names.pkl"), "rb") as f:
    LABELS = pickle.load(f)
with open(os.path.join(DATA_DIR, "faces_data.pkl"), "rb") as f:
    FACES = pickle.load(f)

# ensure arrays line up
min_len = min(len(FACES), len(LABELS))
FACES = np.asarray(FACES[:min_len])
LABELS = np.asarray(LABELS[:min_len])

# train simple KNN on flattened faces
knn = KNeighborsClassifier(n_neighbors=KNN_K)
knn.fit(FACES, LABELS)

# helpers
def voter_hash(label):
    return hashlib.sha256(label.encode("utf-8")).hexdigest()

def has_voted_hash(vhash):
    if not os.path.exists(HASH_FILE):
        return False
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        existing = {line.strip() for line in f if line.strip()}
    return vhash in existing

def mark_voted_hash(vhash):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HASH_FILE, "a", encoding="utf-8") as f:
        f.write(vhash + "\n")

def save_vote(voter, party):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(VOTES_FILE)
    date_str = datetime.now().strftime("%d-%m-%Y")
    time_str = datetime.now().strftime("%H:%M:%S")
    with open(VOTES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["NAME","VOTE","DATE","TIME"])
        writer.writerow([voter, party, date_str, time_str])

# Attempt to capture one frame from the webcam and identify the person.
def identify_from_camera(timeout=5):
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        # Try without CAP_DSHOW on non-windows
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return {"status":"error", "message":"Cannot open webcam."}

    start = time.time()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    found_label = None
    while time.time() - start < timeout:
        ok, frame = cam.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            # keep trying until timeout
            continue
        # pick largest face
        x,y,w,h = max(faces, key=lambda b: b[2]*b[3])
        face_roi = frame[y:y+h, x:x+w]
        try:
            face_resized = cv2.resize(face_roi, FRAME_SIZE)
        except Exception:
            continue
        face_flat = face_resized.flatten().reshape(1, -1)
        # check neighbor distances to decide if recognized
        distances, indices = knn.kneighbors(face_flat, n_neighbors=KNN_K, return_distance=True)
        mean_distance = float(distances.mean())
        # get prediction
        pred = knn.predict(face_flat)[0]
        # decide unknown / recognized by threshold
        if mean_distance <= DISTANCE_THRESHOLD:
            found_label = str(pred)
        else:
            found_label = "Unknown"
        break

    cam.release()
    if found_label is None:
        return {"status":"error", "message":"No face detected. Please align to camera and try again."}
    return {"status":"ok", "label": found_label, "distance": mean_distance}

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/identify", methods=["GET"])
def identify():
    result = identify_from_camera()
    if result.get("status") == "error":
        return jsonify({"status":"error", "message": result.get("message")})
    # result: {"status":"ok","label":..., "distance":...}
    return jsonify({"status":"ok", "label": result["label"], "distance": result.get("distance", None)})

@app.route("/vote", methods=["POST"])
def vote():
    data = request.json
    voter = (data.get("voter") or "").strip()   # this should be Aadhaar label (from identify) or manual input
    party = (data.get("party") or "").strip()
    if not voter:
        return jsonify({"status":"error", "message":"Aadhaar (voter) not provided."})
    if not party:
        return jsonify({"status":"error", "message":"Party not provided."})

    vhash = voter_hash(voter)
    if has_voted_hash(vhash):
        return jsonify({"status":"error", "message":f"Aadhaar {voter} has already voted. Multiple votes are not allowed."})

    # save vote and mark hash
    save_vote(voter, party)
    mark_voted_hash(vhash)
    return jsonify({"status":"success", "message":f"Vote recorded for Aadhaar {voter}."})

# Optional video feed (keeps working for preview)
@app.route("/video_feed")
def video_feed():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera = cv2.VideoCapture(0)
    def generate_frames():
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(debug=True)
