import cv2

print("Testing camera with DirectShow...")

# DirectShow backend (recommended for Windows)
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("❌ Camera failed with CAP_DSHOW. Trying default backend...")
    camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Still cannot access camera. Try changing the index (1 or 2).")
else:
    print("✅ Camera opened successfully! Press 'Q' to quit.")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("⚠️ Frame grab failed.")
            break

        cv2.imshow("Camera Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()
