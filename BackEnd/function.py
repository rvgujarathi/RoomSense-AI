import cv2
from datetime import datetime

# Define the specific time to notify (24-hour format, e.g., 14:30 is 2:30 PM)
notification_time = "19:47"

# Initialize the camera (0 is for the default camera)
cap = cv2.VideoCapture(0)

# Use a basic motion detection technique by comparing frames
def detect_motion(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    return len(contours) > 0

# Function to check if current time matches the notification time
def is_time_to_notify():
    now = datetime.now().strftime("%H:%M")
    return now == notification_time

# Capture the first frame
ret, frame1 = cap.read()

while cap.isOpened():
    ret, frame2 = cap.read()
    
    if not ret:
        break

    # Detect motion
    if detect_motion(frame1, frame2) and is_time_to_notify():
        print("Notification: Motion detected at the specified time!")

    # Display the camera feed (optional)
    cv2.imshow("Camera Feed", frame2)

    # Prepare for the next loop
    frame1 = frame2

    # Exit on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release the camera and close the windows
cap.release()
cv2.destroyAllWindows()
