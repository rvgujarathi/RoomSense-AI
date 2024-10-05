
# Store the reference detections when all objects are present
reference_detections = []

# Function to capture the reference frame
def capture_reference_frame():
    success, frame = camera.read()
    if success:
        results = model(frame)
        return results[0].boxes  # Return the detected boxes (bounding boxes of objects)
    return None

# Function to detect missing objects
def detect_missing_objects(current_boxes):
    missing_objects = []
    
    # Check if reference detections are available
    if reference_detections:
        ref_classes = [int(box.cls) for box in reference_detections]  # Object classes in reference frame
        current_classes = [int(box.cls) for box in current_boxes]  # Object classes in current frame
        
        # Find which objects are in the reference frame but not in the current frame
        for ref_class in ref_classes:
            if ref_class not in current_classes:
                missing_objects.append(ref_class)  # Add missing objects
        
    return missing_objects

# Endpoint to capture the reference frame
@app.route('/capture_reference')
def capture_reference():
    global reference_detections
    reference_detections = capture_reference_frame()
    if reference_detections is not None:
        return jsonify({'message': 'Reference frame captured successfully!', 'objects': len(reference_detections)})
    else:
        return jsonify({'message': 'Failed to capture reference frame'}), 500

# Endpoint to check if any objects are missing
@app.route('/check_missing_objects')
def check_missing_objects():
    success, frame = camera.read()
    if success:
        results = model(frame)
        current_boxes = results[0].boxes
        
        # Detect if any objects are missing
        missing_objects = detect_missing_objects(current_boxes)
        
        if missing_objects:
            return jsonify({'missing_objects': missing_objects})
        else:
            return jsonify({'message': 'No objects are missing'})
    else:
        return jsonify({'message': 'Failed to read the frame'}), 500

if __name__ == '__main__':
    app.run(debug=True)
