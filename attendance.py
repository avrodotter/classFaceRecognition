"""Main attendance marking system with live recognition."""
import cv2
import numpy as np
from datetime import datetime
from detector import YOLOv8FaceDetector
from recognizer import FaceRecognizer, find_best_match
from database import init_database, get_all_embeddings, mark_attendance, get_student_id, get_attendance_report
import time

class AttendanceSystem:
    """Real-time classroom attendance marking system."""
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize attendance system.
        Args:
            confidence_threshold: Minimum match confidence to mark attendance
        """
        init_database()
        self.detector = YOLOv8FaceDetector(conf_threshold=0.6)
        self.recognizer = FaceRecognizer()
        self.confidence_threshold = confidence_threshold
        self.student_embeddings = {}
        self.marked_students = set()  # Prevent duplicate marks within same session
        self.last_mark_time = {}  # Track last mark time per student
        self.mark_cooldown = 5  # Seconds between marks for same student
    
    def load_student_database(self):
        """Load all enrolled students and their embeddings."""
        self.student_embeddings = get_all_embeddings()
        print(f"✅ Loaded {len(self.student_embeddings)} enrolled students")
        return len(self.student_embeddings)
    
    def mark_attendance_if_new(self, student_name: str, confidence: float):
        """Mark attendance with cooldown to avoid duplicates."""
        current_time = time.time()
        last_time = self.last_mark_time.get(student_name, 0)
        
        # Check cooldown period
        if current_time - last_time >= self.mark_cooldown:
            student_id = get_student_id(student_name)
            if student_id:
                mark_attendance(student_id, confidence)
                self.last_mark_time[student_name] = current_time
                print(f"✅ Marked attendance: {student_name} (confidence: {confidence:.2f})")
                return True
        return False
    
    def run_webcam(self, duration_seconds: int = None):
        """
        Run real-time attendance system.
        Args:
            duration_seconds: Run for N seconds, or None for infinite
        """
        if not self.load_student_database():
            print("❌ No enrolled students. Use enrollment mode first.")
            return
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return
        
        print("\n🎥 Starting attendance session")
        print("Press 'R' to show report, 'Q' to quit\n")
        
        start_time = time.time()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect all faces
            detections = self.detector.detect(frame)
            
            # Extract embeddings and match
            display = frame.copy()
            matched_students = []
            
            for face_crop, det_conf, (x1, y1, x2, y2) in detections:
                embedding = self.recognizer.get_embedding(face_crop)
                
                if embedding is not None:
                    # Find matching student
                    student_name, similarity = find_best_match(
                        embedding, 
                        self.student_embeddings, 
                        threshold=self.confidence_threshold
                    )
                    
                    if student_name:
                        # Draw green box for recognized student
                        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f'{student_name} ({similarity:.2f})'
                        cv2.rectangle(display, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                        cv2.putText(display, label, (x1+6, y2-6), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        # Try to mark attendance
                        self.mark_attendance_if_new(student_name, similarity)
                        matched_students.append(student_name)
                    else:
                        # Unknown face - yellow box
                        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 165, 255), 2)
                        cv2.putText(display, f'Unknown ({similarity:.2f})', (x1, y1-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            
            # Display info
            time_elapsed = int(time.time() - start_time)
            cv2.putText(display, f'Faces: {len(detections)} | Recognized: {len(matched_students)} | Time: {time_elapsed}s',
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, 'Q=quit, R=report',
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Attendance System', display)
            
            # Check keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 Ending session")
                break
            elif key == ord('r'):
                # Show today's attendance
                report = get_attendance_report()
                print("\n📋 Today's Attendance:")
                for name, count, last_time in report:
                    print(f"  {name}: {count} mark(s), last at {last_time}")
                print()
            
            # Check duration
            if duration_seconds and time.time() - start_time >= duration_seconds:
                print(f"\n⏱️ Session ended after {duration_seconds}s")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Final report
        report = get_attendance_report()
        if report:
            print("\n📊 Final Attendance Report:")
            for name, count, last_time in report:
                print(f"  ✅ {name}: {count} mark(s)")
        else:
            print("\n⚠️ No attendance marks recorded")

if __name__ == '__main__':
    system = AttendanceSystem(confidence_threshold=0.5)
    system.run_webcam()
