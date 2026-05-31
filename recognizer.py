"""Face recognizer wrapper for face embedding extraction.
Using face_recognition (dlib-based) with 128-dim embeddings.
Can be upgraded to insightface (512-dim ArcFace) when compiler issues resolved.
"""
import cv2
import numpy as np
import face_recognition
from sklearn.preprocessing import normalize
from typing import List, Tuple

class FaceRecognizer:
    """Extracts face embeddings using face_recognition (dlib-based)."""
    
    def __init__(self):
        """Initialize face recognizer."""
        pass
    
    def get_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Extract embedding from face crop.
        Args:
            face_crop: Face image (BGR format from OpenCV)
        Returns:
            128-dimensional embedding vector (or 512-dim if using ArcFace)
        """
        # Convert BGR to RGB
        if len(face_crop.shape) != 3:
            return None
        
        rgb_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        
        try:
            # Extract embedding using face_recognition
            encodings = face_recognition.face_encodings(rgb_face)
            if len(encodings) == 0:
                return None
            return normalize([encodings[0]])[0]  # L2 normalize
        except Exception as e:
            print(f"⚠️ Error extracting embedding: {e}")
            return None
    
    def get_embeddings(self, face_crops: List[np.ndarray]) -> List[Tuple[np.ndarray, bool]]:
        """
        Extract embeddings from multiple face crops.
        Args:
            face_crops: List of face images
        Returns:
            List of tuples: (embedding, success)
        """
        embeddings = []
        for crop in face_crops:
            emb = self.get_embedding(crop)
            embeddings.append((emb, emb is not None))
        return embeddings

def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Compute cosine similarity between two embeddings."""
    if emb1 is None or emb2 is None:
        return 0.0
    return np.dot(emb1, emb2)

def find_best_match(query_embedding: np.ndarray, 
                   student_embeddings: dict, 
                   threshold: float = 0.4) -> Tuple[str, float]:
    """
    Find best matching student for a query embedding.
    Args:
        query_embedding: Embedding to match
        student_embeddings: Dict {name: {id, embeddings: [...]}}
        threshold: Minimum similarity score to consider a match
    Returns:
        Tuple of (student_name, max_similarity) or (None, 0.0) if no match
    """
    best_match = None
    best_score = 0.0
    
    for name, data in student_embeddings.items():
        for stored_emb in data['embeddings']:
            sim = cosine_similarity(query_embedding, stored_emb)
            if sim > best_score:
                best_score = sim
                best_match = name
    
    if best_score >= threshold:
        return best_match, best_score
    return None, best_score

if __name__ == '__main__':
    recognizer = FaceRecognizer()
    print("✅ Face recognizer initialized")
