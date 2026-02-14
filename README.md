# Smart Voting System Using Face Recognition

## 📌 Overview
This project is a smart voting system that uses face recognition and liveness (blink) detection to verify voters and prevent duplicate voting. It registers voters using a webcam, authenticates them using a KNN-based face recognition model, and records votes securely. The goal is to reduce fraud and improve trust in digital voting systems.

## 🚀 Features
- Voter registration using face capture
- Liveness check using blink detection
- Face recognition using KNN (scikit-learn)
- Prevents multiple voting using hashed voter lock
- Simple web interface using Flask
- Stores votes with date and time
- Camera testing utility included

## 🛠️ Technologies Used
- Python
- OpenCV
- Flask
- scikit-learn (KNN)
- NumPy
- HTML, CSS, JavaScript

## 📂 Project Structure
- `add_faces.py` → Register new voters with face and blink verification  
- `app.py` → Main Flask web application for voting  
- `give_vote.py` → Standalone secure voting script  
- `clean_data.py` → Clears stored face data and votes  
- `test_camera.py` → Test webcam functionality  
- `templates/index.html` → Web UI  
- `static/style.css` → Styling  
- `static/script.js` → Frontend logic  
- `background.png` → UI background image  

## ▶️ How to Run

### 1️⃣ Install dependencies

```bash
pip install opencv-python flask scikit-learn numpy
```
### 2️⃣ Register a voter
```bash
python add_faces.py
```
### 3️⃣ Start the web app
```bash
python app.py
```
### 4️⃣ Open in browser
```bash
http://127.0.0.1:5000
```
