"""YOLOv8-face detector wrapper."""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple

class YOLOv8FaceDetector:
    """Detects multiple faces in an image using YOLOv8-face."""
    
    def __init__(self, model_name: str = 'yolov8n.pt', conf_threshold: float = 0.5):
        """
        Initialize detector.
        Args:
            model_name: YOLOv8 model to use (n/s/m/l/x for nano/small/medium/large/xlarge)
            conf_threshold: Confidence threshold for detections
        """
        self.model = YOLO(model_name)
        self.conf_threshold = conf_threshold
    
    def detect(self, image: np.ndarray) -> List[Tuple[np.ndarray, float, Tuple[int, int, int, int]]]:
        """
        Detect faces in image.
        Returns:
            List of tuples: (face_crop, confidence, bbox) where bbox = (x1, y1, x2, y2)
        """
        results = self.model(image, conf=self.conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                
                # Crop face from image
                face_crop = image[y1:y2, x1:x2]
                if face_crop.size > 0:
                    detections.append((face_crop, confidence, (x1, y1, x2, y2)))
        
        return detections
    
    def detect_and_display(self, image: np.ndarray, labels: List[str] = None) -> np.ndarray:
        """
        Detect faces and draw bounding boxes.
        Args:
            image: Input image
            labels: Optional list of labels for each detection
        Returns:
            Image with drawn boxes and labels
        """
        results = self.model(image, conf=self.conf_threshold, verbose=False)
        annotated = results[0].plot()
        return annotated

if __name__ == '__main__':
    detector = YOLOv8FaceDetector()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        detections = detector.detect(frame)
        print(f"Detected {len(detections)} faces")
        
        # Draw boxes
        for face_crop, conf, (x1, y1, x2, y2) in detections:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'{conf:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow('YOLOv8 Face Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
