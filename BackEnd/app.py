import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
from datetime import datetime
#import mysql.connector                                                     #For Database Connection
#from mysql.connector import Error                                          #For Database Connection

app = Flask(__name__)

# Load the YOLOv8 model (pretrained)
model = YOLO('yolov8n.pt')  # YOLOv8n is the small, fast model for testing purposes

# Use webcam or CCTV camera for testing (adjust index as needed)
camera = cv2.VideoCapture(0)

# Store the reference detections when all objects are present
reference_detections = []

# Notification time
notification_time = "19:47"

# Detect the camera's resolution and set the appropriate resolution factorcamera = cv2.VideoCapture(0)

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

get_resolution_factor(camera)

# Motion detection using frame comparison
previous_frame = None
def detect_motion(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours) > 0

# Blockage detection based on motion
def calculate_entropy(image):
    """Calculate the entropy of an image."""
    # Convert the image to a 1D array of pixel values
    pixels = image.flatten()
    
    # Calculate histogram
    histogram, _ = np.histogram(pixels, bins=256, range=(0, 256))
    
    # Normalize the histogram to get probabilities
    histogram = histogram / histogram.sum()
    
    # Calculate entropy
    entropy = -np.sum(histogram[histogram > 0] * np.log2(histogram[histogram > 0]))
    
    return entropy

def detect_blockage(frame):
    global previous_frame
    
    # Convert the frame to a float32 type for accurate calculations
    frame_float = frame.astype(np.float32)
    
    # Calculate color entropy
    entropy = calculate_entropy(frame_float)

    # Define an appropriate threshold for entropy to detect blockage
    entropy_threshold = 6  # You may need to adjust this based on your specific setup

    # If the entropy is low, consider it blocked
    is_blocked = entropy < entropy_threshold

    # Optional: Print or log the entropy value for debugging
    print(f"Current Entropy: {entropy:.2f}, Blocked: {is_blocked}")

    return is_blocked  # Returns True if blocked

# Check if current time matches notification time
def is_time_to_notify():
    now = datetime.now().strftime("%H:%M")
    return now == notification_time

# Capture reference frame and store detected objects
def capture_reference_frame():
    success, frame = camera.read()
    if success:
        results = model(frame)
        return results[0].boxes
    return None

# Detect missing objects by comparing current frame with reference frame
def detect_missing_objects(current_boxes):
    missing_objects = []
    if reference_detections:
        ref_classes = [int(box.cls) for box in reference_detections]
        current_classes = [int(box.cls) for box in current_boxes]
        for ref_class in ref_classes:
            if ref_class not in current_classes:
                missing_objects.append(ref_class)
    return missing_objects

# Stream video frames with YOLO annotations
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        is_blocked = detect_blockage(frame)
        results = model(frame)
        annotated_frame = results[0].plot()
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Endpoint to get people count and check for crowd detection
@app.route('/people_count')
def people_count():
    success, frame = camera.read()
    if success:
        results = model(frame)
        # Count the number of people (YOLO class 0 typically corresponds to 'person')
        people_count = sum(1 for detection in results[0].boxes.cls if int(detection) == 0)
        
        # Crowd detection: if more than 5 people are detected
        crowd_detected = people_count > 5
        
        return jsonify({'count': people_count, 'crowd_detected': crowd_detected})
    else:
        return jsonify({'count': 0, 'crowd_detected': False})

@app.route('/blockage_status')
def blockage_status():
    success, frame = camera.read()
    if success:
        is_blocked = detect_blockage(frame)
        return jsonify({'blocked': bool(is_blocked)})
    else:
        return jsonify({'blocked': False})

@app.route('/capture_reference')
def capture_reference():
    global reference_detections
    reference_detections = capture_reference_frame()
    if reference_detections is not None:
        return jsonify({'message': 'Reference frame captured!', 'objects': len(reference_detections)})
    else:
        return jsonify({'message': 'Failed to capture reference frame'}), 500

@app.route('/check_missing_objects')
def check_missing_objects():
    success, frame = camera.read()
    if success:
        results = model(frame)
        current_boxes = results[0].boxes
        missing_objects = detect_missing_objects(current_boxes)
        if missing_objects:
            return jsonify({'missing_objects': missing_objects})
        else:
            return jsonify({'message': 'No objects are missing'})
    else:
        return jsonify({'message': 'Failed to read the frame'}), 500
"""                                                                        For Database Connection Only
def dbconnect():
    # Database credentials
    host_name = "localhost"
    user_name = "root"  # Change this to your MySQL username
    user_password = "Malkapur@123"  # Change this to your MySQL password
    db_name = "LabManagement"

    # Create a database connection
    connection = create_connection(host_name, user_name, user_password, db_name)

    if connection:
        # Fetch lab info
        lab_info = fetch_lab_info(connection)

        # Print the lab information
        for lab in lab_info:
            print(f"Lab No: {lab['room_no']}, Opening Time: {lab['opening_time']}, Closing Time: {lab['closing_time']}")

        # Close the database connection
        connection.close()

      
def create_connection(host_name, user_name, user_password, db_name):                         #for database connection
    #Create a database connection.                                                           #for database connection
    connection = None                                                                        #for database connection
    try:                                                                                     #for database connection
        connection = mysql.connector.connect(                                                #for database connection
            host=host_name,                                                                  #for database connection
            user=user_name,                                                                  #for database connection
            password=user_password,                                                          #for database connection
            database=db_name                                                                 #for database connection
        )                                                                                    #for database connection
        print("Connection to MySQL DB successful")                                           #for database connection
    except Error as e:                                                                       #for database connection
        print(f"The error '{e}' occurred")                                                   #for database connection
    return connection                                                                        #for database connection
                                                                                             #for database connection
def fetch_lab_info(connection):                                                              #for database connection
    #Fetch lab details: room number, opening time, and closing time.                         #for database connection
    cursor = connection.cursor()                                                             #for database connection
    lab_info_query = "SELECT room_no, opening_time, closing_time FROM Lab_Info;"             #for database connection
    cursor.execute(lab_info_query)                                                           #for database connection
    results = cursor.fetchall()                                                              #for database connection
                                                                                             #for database connection
    lab_details = []                                                                         #for database connection
    for row in results:                                                                      #for database connection
        lab_details.append({                                                                 #for database connection 
            "room_no": row[0],                                                               #for database connection
            "opening_time": row[1],                                                          #for database connection
            "closing_time": row[2]                                                           #for database connection
        })                                                                                   #for database connection
                                                                                             #for database connection
    return lab_details                                                                       #for database connection
"""

if __name__ == '__main__':
    app.run(debug=True)
