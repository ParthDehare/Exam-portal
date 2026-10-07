import cv2
import numpy as np
import base64
import logging

logger = logging.getLogger(__name__)

# Load the pre-trained Haar Cascade face detection model
# OpenCV comes with these XML files by default
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(base64_image: str) -> dict:
    """
    Decodes a base64 image and detects faces.
    Returns a dict with status and face count.
    """
    try:
        # 1. Decode the base64 string
        # Handle the data URI scheme if present (e.g. 'data:image/jpeg;base64,...')
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
            
        img_data = base64.b64decode(base64_image)
        nparr = np.frombuffer(img_data, np.uint8)
        
        # 2. Decode image array into OpenCV format
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Failed to decode image"}

        # 3. Convert to grayscale (required for Haar cascades)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 4. Detect faces
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        face_count = len(faces)
        
        # 5. Evaluate proctoring rules
        if face_count == 0:
            violation_type = "NO_FACE_DETECTED"
            message = "Warning: No face detected in the camera frame."
            is_violation = True
        elif face_count > 1:
            violation_type = "MULTIPLE_FACES_DETECTED"
            message = f"Warning: Multiple faces ({face_count}) detected in the camera frame."
            is_violation = True
        else:
            violation_type = None
            message = "Face verification successful."
            is_violation = False

        return {
            "status": "success",
            "face_count": face_count,
            "is_violation": is_violation,
            "violation_type": violation_type,
            "message": message
        }

    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return {"status": "error", "message": str(e)}
