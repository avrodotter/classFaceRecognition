# Classroom Attendance System 


## Starting the programm

### Step 1: Create Virtual Environment (First Time Only)
```bash
python3 -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies (First time only)
```bash
pip install -r requirements.txt
```

### Step 4: Start the System
```bash
python main.py
```

### Step 5: See the Menu
You'll see a menu with 5 options:
```
1. Enroll New Student
2. Start Attendance Session  
3. View Today's Report
4. Manage Students (Delete)
5. Exit
```

---

## Key Features

- **Multi-face Detection**: YOLOv8-face detects all students simultaneously  
- **Live Enrollment**: Capture 3-angle samples for new students  
- **Real-time Recognition**: 128-dim embeddings via face_recognition  
- **Automatic Attendance**: Marks on first detection, prevents duplicates  
- **Attendance Reports**: View today's marks by student  
- **SQLite Storage**: Persistent student database + embeddings  
- **Visual Feedback**: Green boxes (recognized), yellow (unknown)  

---

## First-Time Setup in CLI

### Enroll Your Students (Do This Once)

1. Select **"1. Enroll New Student"**
2. Enter student name: `John Doe`
3. **Press SPACE 3 times** from different angles (front, left, right)
4. System extracts face embeddings automatically
5. Repeat for all students

**Result**: Each student has 3 face samples stored in the database

---

## Daily Attendance

### Run Attendance Session

1. Select **"2. Start Attendance Session"**
2. System loads all student embeddings
3. Point camera at classroom entrance
4. As students appear:
   - **Green boxes** = Recognized student
   - **Yellow boxes** = Unknown face
5. Attendance marked automatically (with 5-sec cooldown to prevent duplicates)

### During Session:
- **Press R**: Show quick attendance report
- **Press Q**: Exit and save attendance

---

## Check Attendance

Select **"3. View Today's Report"** to see all students marked today with timestamps.

---

## Architecture

```
Webcam Input
    ↓
YOLOv8-face Detection (all faces in frame)
    ↓
Face Embedding Extraction (128-dim vectors)
    ↓
Cosine Similarity Matching (against student DB)
    ↓
Mark Attendance + Display Results
```

## Project Structure

```
.
├── main.py              # CLI entry point with menu
├── attendance.py        # Main attendance marking system
├── enrollment.py        # Live student registration
├── detector.py          # YOLOv8-face detection wrapper
├── recognizer.py        # Face embedding extraction (face_recognition)
├── database.py          # SQLite student/embeddings database
├── requirements.txt     # Dependencies
├── attendance.db        # SQLite database (created on first run)
├── yolov8n.pt          # Detection model (downloaded automatically)
```


#### Don't Touch These (Auto-managed)
- `attendance.db` - Your database (created automatically)
- `yolov8n.pt` - Detection model (downloaded automatically)

### Core Code (Can customize)
- `main.py` - CLI interface
- `attendance.py` - Attendance logic
- `enrollment.py` - Enrollment logic
- `detector.py` - Face detection
- `recognizer.py` - Face recognition
- `database.py` - Database operations

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `ultralytics` | YOLOv8 face detection |
| `face-recognition` | 128-dim face embeddings (dlib-based) |
| `opencv-python` | Image processing |
| `numpy` | Numerical operations |
| `scikit-learn` | Cosine similarity calculations |

## Recognition Threshold

Default: **0.5** (cosine similarity)  
- Higher = stricter (fewer false positives, more false negatives)
- Lower = looser (more false positives, fewer false negatives)

Adjust in `attendance.py`:
```python
system = AttendanceSystem(confidence_threshold=0.5)
```


### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    enrollment_date TIMESTAMP,
    status TEXT
)
```

### Embeddings Table
```sql
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    embedding_blob TEXT,  -- JSON: [f1, f2, ..., f128]
    created_at TIMESTAMP
)
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    timestamp TIMESTAMP,
    confidence REAL
)
```

## Performance

- **Detection**: ~50-100ms per frame (CPU)
- **Recognition**: ~30-50ms per face
- **Total**: ~100-150ms per frame with 5 faces

## Future Improvements

1. **ArcFace Integration**: Replace face_recognition with insightface (512-dim embeddings)
   - Requires C++ compiler (g++): `sudo apt install build-essential`
   - Better accuracy for difficult angles/lighting

2. **Multi-GPU Support**: Use GPU acceleration if available

3. **Attendance Export**: CSV/Excel export with attendance summaries

4. **REST API**: Deploy as web service

5. **Duplicate Detection**: Prevent same person enrolling twice

6. **Anti-spoofing**: Detect presentation attacks (photos, videos)

## Troubleshooting

### No faces detected
- Ensure good lighting
- Face should be clearly visible
- Try moving closer to camera

### Accuracy issues
- Enroll with varied angles and lighting
- Lower confidence threshold if too strict
- Use full frontal face for best results

### Slow performance
- Reduce frame resolution
- Use lighter YOLOv8n model (default)
- Close other applications

## License

Educational use only


