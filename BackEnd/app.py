import cv2
from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import numpy as np

app = Flask(__name__)

# Load the YOLOv8 model (pretrained)
model = YOLO('yolov8n.pt')  # YOLOv8n is the small, fast model for testing purposes

# Use webcam or CCTV camera for testing (adjust index as needed)
camera = cv2.VideoCapture(0)

# Detect the camera's resolution and set the appropriate resolution factor
def get_resolution_factor(camera):
    # Manually set resolution (adjust these values as needed)
    manual_resolution = (1280, 720)  # Set your desired resolution here
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, manual_resolution[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, manual_resolution[1])
    
    # Get the current width and height
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return 0.6  # Adjust the factor based on your needs; this is for 720p

# Improved camera view blocked detection based on motion
previous_frame = None

def detect_blockage(frame):
    global previous_frame
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate the difference between the current frame and the previous frame
    if previous_frame is None:
        previous_frame = gray_frame
        return False  # No previous frame to compare against

    frame_diff = cv2.absdiff(previous_frame, gray_frame)
    _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
    
    # Count non-zero pixels in the thresholded image
    non_zero_count = np.count_nonzero(thresh)
    
    # If the number of non-zero pixels is low, consider it blocked
    is_blocked = non_zero_count < 1000  # Adjust this threshold based on your needs

    # Update the previous frame
    previous_frame = gray_frame
    
    return is_blocked  # Returns True if blocked

# Adjust resolution factor based on camera's resolution
resolution_factor = get_resolution_factor(camera)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Check for obstruction in the frame
        is_blocked = detect_blockage(frame)
        
        # Perform YOLO object detection on the frame
        results = model(frame)
        annotated_frame = results[0].plot()

        # Encode the frame to bytes for streaming
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/people_count')
def people_count():
    success, frame = camera.read()
    if success:
        results = model(frame)
        # Count how many 'person' class detections we have (0 is the class ID for 'person')
        people_count = sum(1 for detection in results[0].boxes.cls if int(detection) == 0)
        return jsonify({'count': people_count})
    else:
        return jsonify({'count': 0})

@app.route('/blockage_status')
def blockage_status():
    success, frame = camera.read()
    if success:
        is_blocked = detect_blockage(frame)
        return jsonify({'blocked': bool(is_blocked)})  # Explicitly convert to standard bool
    else:
        return jsonify({'blocked': False})  # Default to not blocked if frame read fails

if __name__ == '__main__':
    app.run(debug=True)
