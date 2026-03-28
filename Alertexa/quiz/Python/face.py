import cv2

# Load Haar cascades
face_cascade_default = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
face_cascade_alt2 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
face_cascade_profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

video_cap = cv2.VideoCapture(0)
video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not video_cap.isOpened():
    print("Error: Could not open webcam")
    exit()

def merge_faces(faces, threshold=0.5):
    """Merge overlapping face detections based on IoU"""
    merged = []
    for (x, y, w, h) in faces:
        keep = True
        for (mx, my, mw, mh) in merged:
            # Calculate Intersection over Union (IoU)
            xx1, yy1 = max(x, mx), max(y, my)
            xx2, yy2 = min(x + w, mx + mw), min(y + h, my + mh)
            inter_area = max(0, xx2 - xx1) * max(0, yy2 - yy1)
            union_area = (w * h) + (mw * mh) - inter_area
            iou = inter_area / union_area if union_area > 0 else 0

            if iou > threshold:  # If overlap is high, consider same face
                keep = False
                break
        if keep:
            merged.append((x, y, w, h))
    return merged

while True:
    ret, video_data = video_cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    video_data = cv2.flip(video_data, 1)
    video_data = cv2.resize(video_data, (400, 300))
    gray = cv2.cvtColor(video_data, cv2.COLOR_BGR2GRAY)

    # Detect faces from multiple cascades
    faces = []
    faces.extend(face_cascade_default.detectMultiScale(gray, 1.1, 7, minSize=(40, 40)))
    faces.extend(face_cascade_alt2.detectMultiScale(gray, 1.1, 7, minSize=(40, 40)))
    faces.extend(face_cascade_profile.detectMultiScale(gray, 1.1, 7, minSize=(40, 40)))

    # Merge duplicates
    faces = merge_faces(faces)

    # Draw rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(video_data, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.putText(video_data, f"Faces detected: {len(faces)}",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # if len(faces) > 1:
    #     cv2.putText(video_data, "ALERT! Multiple Faces Detected",
    #                 (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("video_live", video_data)

    if cv2.waitKey(10) == ord("a"):
        break

video_cap.release()
cv2.destroyAllWindows()
