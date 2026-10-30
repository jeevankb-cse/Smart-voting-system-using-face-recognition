# 🗳️ Smart Voting System Using Face Recognition

**A Python-Based Smart Voting Application with Face Recognition and Liveness Detection**

## 📌 Project Overview

The **Smart Voting System Using Face Recognition** is a Python-based application designed to provide an additional layer of voter authentication using facial recognition technology and liveness detection.

Traditional voting approaches may face challenges such as identity verification and duplicate voting. This project explores how computer vision and machine learning can help address these challenges through an automated voter verification process.

The application uses a webcam to capture facial information, verifies registered voters using a K-Nearest Neighbors (KNN) classifier, and performs blink-based liveness detection. It also uses a hashed voter lock mechanism to help prevent multiple voting attempts.

The system is developed using Python, OpenCV, Flask, NumPy and Scikit-learn.

## 🎯 Project Objectives

- Develop a face recognition-based voter authentication system.
- Implement blink detection for basic liveness verification.
- Apply machine learning techniques for facial recognition.
- Reduce duplicate voting attempts.
- Provide a simple and accessible web interface.
- Explore the use of computer vision in digital voting applications.

## ✨ Key Features

### 1. Voter Registration
- Register voters using webcam-based face capture.
- Store facial data for subsequent recognition.

### 2. Face Recognition
- Identify registered voters using facial recognition.
- Use the K-Nearest Neighbors (KNN) algorithm from Scikit-learn.

### 3. Liveness Detection
- Perform blink-based verification.
- Help distinguish a live user interaction from a static facial image.

### 4. Duplicate Voting Prevention
- Use a hashed voter lock mechanism.
- Help prevent repeated voting attempts by the same registered voter.

### 5. Web-Based Interface
- Flask-based application.
- Simple interface for interacting with the voting system.

### 6. Vote Recording
- Record voting information with date and time.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Computer vision and face processing |
| Flask | Backend web framework |
| Scikit-learn | KNN-based face recognition |
| NumPy | Numerical operations |
| HTML | Web page structure |
| CSS | Interface styling |
| JavaScript | Frontend interactions |

## 🏗️ Project Architecture

The system follows a simple application workflow:

1. **Voter Registration:** Capture facial information through a webcam.
2. **Face Processing:** Process facial information using OpenCV.
3. **Liveness Verification:** Perform blink detection.
4. **Face Authentication:** Match the captured face using the trained KNN model.
5. **Voting Process:** Allow an authenticated voter to participate.
6. **Duplicate Check:** Check the voter lock mechanism.
7. **Vote Recording:** Record the voting information.

## 🔄 System Workflow

```text
        START
          |
          v
   Voter Registration
          |
          v
    Capture Face Data
          |
          v
   Face Preprocessing
          |
          v
    Liveness Detection
      (Blink Check)
          |
          v
   Face Recognition
       (KNN Model)
          |
          v
    Voter Verification
          |
          v
    Duplicate Vote Check
          |
          v
      Cast Vote
          |
          v
     Record Vote
          |
          v
         END
```

## 📂 Project Structure

```text
Smart-voting-system-using-face-recognition/
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── add_faces.py
├── app.py
├── give_vote.py
├── clean_data.py
├── test_camera.py
├── background.png
├── README.md
└── LICENSE
```

**Main Python Files:**

- `add_faces.py` – Registers voters using facial capture and blink verification.
- `app.py` – Main Flask web application.
- `give_vote.py` – Standalone voting script.
- `clean_data.py` – Utility for clearing stored face data and votes.
- `test_camera.py` – Tests webcam functionality.

## ⚙️ Installation and Setup

### Prerequisites

- Python installed on your computer.
- Working webcam.
- Git installed.
- Visual Studio Code or another Python IDE.

### Step 1: Clone the Repository

```bash
git clone https://github.com/jeevankb-cse/Smart-voting-system-using-face-recognition.git
```

### Step 2: Navigate to the Project Folder

```bash
cd Smart-voting-system-using-face-recognition
```

### Step 3: Install Dependencies

```bash
pip install opencv-python flask scikit-learn numpy
```

### Step 4: Register Voters

```bash
python add_faces.py
```

Follow the application's facial registration and blink verification process.

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Open in Browser

Visit:

```text
http://127.0.0.1:5000
```

## 💻 Application Details

**Project Type:** Academic / Educational Project

**Domain:** Computer Vision and Machine Learning

**Programming Language:** Python

**Framework:** Flask

**Recognition Algorithm:** K-Nearest Neighbors (KNN)

**Computer Vision Library:** OpenCV

## 🔮 Future Enhancements

- Improve facial recognition accuracy under different lighting conditions.
- Explore stronger presentation-attack detection methods.
- Introduce role-based administrator access.
- Develop a more comprehensive voter management interface.
- Improve auditability and data protection.
- Explore secure database integration.

## ⚠️ Limitations and Disclaimer

This project is an academic prototype developed for educational and demonstration purposes. It is not a certified electronic voting system and should not be used for real public elections.

Facial recognition, blink detection and local vote storage have limitations. A production voting system would require independent security audits, privacy safeguards, accessibility testing, robust identity verification and legally compliant election procedures.

## 👨‍💻 Developer

**Jeevan K B**

Computer Science and Engineering Student

GitHub: https://github.com/jeevankb-cse

## ⭐ Support

If you find this project useful for learning about Python, OpenCV, machine learning or face recognition, consider giving the repository a star.

**Repository:** https://github.com/jeevankb-cse/Smart-voting-system-using-face-recognition

---

*Developed as an academic project to explore the application of face recognition and computer vision in digital voting systems.*
