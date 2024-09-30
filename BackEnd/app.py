
import cv2
from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# Load the YOLOv8 model (pretrained)
model = YOLO('yolov8n.pt')  # YOLOv8n is the small, fast model for testing purposes

# For future use: Dictionary to hold multiple camera sources
# camera_feeds = {
#     'camera_1': cv2.VideoCapture(0),  # Camera 1 (default webcam)
#     'camera_2': cv2.VideoCapture(1),  # Camera 2 (CCTV or external camera)
# }

# Use webcam for testing (camera index 0)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        # Capture frame-by-frame from the webcam
        success, frame = camera.read()
        if not success:
            break
        
        # Perform YOLO object detection on the frame
        results = model(frame)
        
        # Draw bounding boxes and labels on the frame
        annotated_frame = results[0].plot()

        # Encode the frame to bytes for streaming
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Frontend interface
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Route to stream the video feed
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/people_count')
def people_count():
    # Return the number of people detected in the last frame
    # YOLOv8 detects 'person' as one of its classes
    success, frame = camera.read()
    if success:
        results = model(frame)
        # Count how many 'person' class detections we have
        people_count = sum(1 for detection in results[0].boxes.cls if int(detection) == 0)  # '0' is the class ID for 'person'
        return jsonify({'count': people_count})
    else:
        return jsonify({'count': 0})

if __name__ == '__main__':
    app.run(debug=True)
