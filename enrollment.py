"""Live enrollment mode for registering new students."""
import cv2
import numpy as np
from typing import Optional
from detector import YOLOv8FaceDetector
from recognizer import FaceRecognizer
from database import add_student, store_embedding

class EnrollmentMode:
    """Interactive enrollment mode to register new students."""
    
    def __init__(self):
        self.detector = YOLOv8FaceDetector(conf_threshold=0.6)
        self.recognizer = FaceRecognizer()
        self.cap = None
    
    def start_webcam(self):
        """Start webcam capture."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Cannot open webcam")
            return False
        return True
    
    def enroll_student(self, name: str, num_samples: int = 3) -> bool:
        """
        Capture face samples from student and store embeddings.
        Args:
            name: Student name
            num_samples: Number of samples to capture from different angles
        Returns:
            True if successful
        """
        if not self.cap:
            if not self.start_webcam():
                return False
        
        print(f"\n📸 Starting enrollment for: {name}")
        print(f"Capture {num_samples} different angles of your face")
        print("Press SPACE to capture, ESC to cancel\n")
        
        captured = 0
        embeddings = []
        
        while captured < num_samples:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Detect faces
            detections = self.detector.detect(frame)
            
            # Draw detection boxes
            display = frame.copy()
            for face_crop, conf, (x1, y1, x2, y2) in detections:
                color = (0, 255, 0) if conf > 0.7 else (0, 165, 255)
                cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
                cv2.putText(display, f'Conf: {conf:.2f}', (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Show status
            status_text = f"Captured: {captured}/{num_samples}"
            cv2.putText(display, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display, "SPACE=capture, ESC=cancel", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            cv2.imshow(f'Enrolling: {name}', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("❌ Enrollment cancelled")
                cv2.destroyAllWindows()
                return False
            elif key == 32:  # SPACE
                if len(detections) > 0:
                    face_crop, conf, _ = detections[0]  # Use first (largest) face
                    embedding = self.recognizer.get_embedding(face_crop)
                    
                    if embedding is not None:
                        embeddings.append(embedding)
                        captured += 1
                        print(f"✅ Captured sample {captured}/{num_samples}")
                        # Brief flash
                        cv2.imshow(f'Enrolling: {name}', display * 0.5)
                        cv2.waitKey(200)
                    else:
                        print("⚠️ Could not extract embedding, try again")
                else:
                    print("⚠️ No face detected, try again")
        
        cv2.destroyAllWindows()
        
        # Store to database
        if embeddings:
            student_id = add_student(name)
            for embedding in embeddings:
                store_embedding(student_id, embedding.tolist())
            print(f"✅ Enrolled {name} with {len(embeddings)} samples")
            return True
        else:
            print("❌ No embeddings captured")
            return False
    
    def close(self):
        """Release resources."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    enroller = EnrollmentMode()
    
    # Example usage
    if enroller.start_webcam():
        enroller.enroll_student("John Doe", num_samples=3)
    
    enroller.close()
