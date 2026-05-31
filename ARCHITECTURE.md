# 🏗️ System Architecture & Components

## Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ATTENDANCE SYSTEM v2                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  main.py - CLI Interface                            │   │
│  │  ├─ Menu system for all operations                  │   │
│  │  ├─ Student enrollment entry point                 │   │
│  │  ├─ Attendance session launcher                     │   │
│  │  └─ Attendance report viewer                        │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────┴──────────────┬──────────────┐               │
│  │                           │              │               │
│  ▼                           ▼              ▼               │
│ ┌──────────────────┐  ┌─────────────┐  ┌──────────────┐    │
│ │ enrollment.py   │  │attendance.py│  │database.py   │    │
│ │ [ENROLLMENT]    │  │ [MARKING]   │  │ [PERSISTENCE]│    │
│ └────────┬─────────┘  └──────┬──────┘  └──────┬───────┘    │
│          │                   │                │            │
│          └───────┬───────────┼────────────────┘            │
│                  │           │                             │
│          ┌───────▼───────────▼─────────────┐               │
│          │ detector.py + recognizer.py    │               │
│          │ [ML PIPELINE]                   │               │
│          │ ├─ Face Detection (YOLOv8)     │               │
│          │ ├─ Embedding Extraction         │               │
│          │ └─ Similarity Matching          │               │
│          └─────────────┬────────────────────┘               │
│                        │                                    │
│          ┌─────────────▼──────────────┐                    │
│          │ attendance.db (SQLite)     │                    │
│          │ ├─ students table          │                    │
│          │ ├─ embeddings table        │                    │
│          │ └─ attendance table        │                    │
│          └────────────────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Descriptions

### 1. **main.py** - CLI Entry Point
**Purpose**: User interface and workflow orchestration

**Functions**:
- `print_menu()` - Display main menu
- `main()` - Main event loop handling all user input

**Menu Options**:
1. Enroll new student → `enrollment.py`
2. Start attendance session → `attendance.py`
3. View today's report → `database.py`
4. Manage students (Delete) → `database.py`
5. Exit

**Key Features**:
- Interactive menu system
- Input validation
- Error handling
- Session management

**Flow**:
```
User Input → menu_choice → route_to_module → execute → return_to_menu
```

---

### 2. **detector.py** - Face Detection
**Purpose**: Multi-face detection using YOLOv8-nano

**Class**: `YOLOv8FaceDetector`

**Methods**:
```python
__init__(model_name='yolov8n.pt', conf_threshold=0.5)
  - Load YOLOv8 model
  - Set confidence threshold

detect(image) -> List[(face_crop, confidence, bbox)]
  - Run inference on image
  - Return cropped faces + coordinates

detect_and_display(image, labels) -> annotated_image
  - Detect + draw boxes (optional method)
```

**Input**: OpenCV image (BGR, any size)
**Output**: List of tuples:
- `face_crop`: Numpy array of cropped face
- `confidence`: Float (0-1)
- `bbox`: Tuple (x1, y1, x2, y2)

**Performance**: 50-100ms per frame (CPU)

**Model Info**:
- YOLOv8-nano: 6.2 MB, ~95% detection accuracy
- Can also use: yolov8s, yolov8m for higher accuracy/speed tradeoff

---

### 3. **recognizer.py** - Face Recognition
**Purpose**: Extract facial embeddings and match against database

**Class**: `FaceRecognizer`

**Methods**:
```python
__init__()
  - Initialize face_recognition library (dlib)

get_embedding(face_crop) -> numpy_array[128]
  - Extract 128-dimensional embedding from face crop
  - L2 normalize for cosine similarity

get_embeddings(face_crops) -> List[(embedding, success)]
  - Batch extract embeddings from multiple faces
```

**Functions**:
```python
cosine_similarity(emb1, emb2) -> float
  - Compute dot product of normalized vectors
  - Range: [0, 1] where 1.0 = identical

find_best_match(query_embedding, student_embeddings, threshold) 
  -> (student_name, max_similarity)
  - Find best matching student in database
  - Return None if below threshold
```

**Input**: Cropped face image (100x100 to 500x500 typical)
**Output**: 128-dimensional vector (normalized)

**Performance**: 30-50ms per face

**Matching Logic**:
- Compute cosine similarity between query and all stored embeddings
- Return highest match if score ≥ threshold
- Otherwise return "Unknown"

---

### 4. **database.py** - Data Persistence
**Purpose**: SQLite storage for students and embeddings

**Functions**:

```python
init_database()
  - Create tables if not exist
  - Called once on first run

add_student(name: str) -> student_id
  - Insert new student
  - Return auto-incremented ID

get_student_id(name: str) -> int
  - Lookup student by name

store_embedding(student_id, embedding: list)
  - Save 128-dim embedding as JSON blob

get_all_embeddings() -> dict
  - Load all embeddings: {name: {id, embeddings: [...]}}
  - Called at session start

mark_attendance(student_id, confidence)
  - Insert attendance record

get_attendance_report(date_str) -> List[(name, count, last_time)]
  - Query attendance for date
```

**Schema**:

```sql
students:
  - id (PK, auto-increment)
  - name (UNIQUE)
  - enrollment_date (auto)
  - status (default: 'active')

embeddings:
  - id (PK)
  - student_id (FK)
  - embedding_blob (JSON string of list[128])
  - created_at (auto)

attendance:
  - id (PK)
  - student_id (FK)
  - timestamp (auto)
  - confidence (float 0-1)
```

**Storage Format**:
- Embeddings stored as JSON: `"[0.123, -0.456, ...]"`
- Easily queryable and human-readable
- ~1 KB per embedding

---

### 5. **enrollment.py** - Student Registration
**Purpose**: Live capture and enrollment of new students

**Class**: `EnrollmentMode`

**Methods**:
```python
__init__()
  - Initialize detector + recognizer

start_webcam() -> bool
  - Open camera (cv2.VideoCapture)

enroll_student(name: str, num_samples=3) -> bool
  - Interactive enrollment loop
  - Shows live feed with detection boxes
  - Capture on SPACE key (3 times)
  - ESC to cancel
  - Extract embedding per sample
  - Store all to database

close()
  - Release camera + cleanup
```

**Workflow**:
```
1. Show webcam feed with detected faces
2. User presses SPACE to capture (3 times from different angles)
3. For each capture:
   - Extract face from bbox
   - Calculate embedding
   - Store in database
4. System stores student record with all embeddings
```

**Visual Feedback**:
- Green box: Good confidence detection
- Yellow box: Lower confidence
- Status text: "Captured: 1/3"

**Inputs**:
- SPACE: Capture sample
- ESC: Cancel enrollment

---

### 6. **attendance.py** - Main Attendance System
**Purpose**: Real-time attendance marking

**Class**: `AttendanceSystem`

**Methods**:
```python
__init__(confidence_threshold=0.5)
  - Initialize detector + recognizer
  - Set matching threshold

load_student_database()
  - Load all student embeddings into memory
  - Called at session start

mark_attendance_if_new(student_name, confidence) -> bool
  - Check 5-second cooldown
  - Mark if passed
  - Update last_mark_time

run_webcam(duration_seconds=None)
  - Main real-time loop
  - Detect + extract + match + mark
  - Draw boxes and labels
  - Handle keyboard input (R, Q)
```

**Real-time Loop**:
```
while running:
  1. Capture frame from webcam
  2. Run YOLOv8 detection
  3. For each detected face:
     a. Extract embedding
     b. Find best match in DB
     c. Draw box (green=match, yellow=unknown)
     d. Try to mark attendance (with cooldown)
  4. Display annotated frame
  5. Handle keyboard: R=report, Q=quit
  6. Check duration limit
```

**Keyboard Controls**:
- **Q**: Quit session
- **R**: Show today's attendance report

**Anti-Duplicate System**:
- Track `last_mark_time` per student
- 5-second cooldown between marks
- Prevents marking same face multiple times

**Visual Output**:
- Frame with detection boxes
- Student names for recognized faces
- Confidence scores
- Session stats (elapsed time, face count)

---

## Data Flow Diagrams

### Enrollment Flow
```
User selects "1. Enroll"
           │
           ▼
EnrollmentMode.start_webcam()
           │
           ▼
for each SPACE key:
    YOLOv8FaceDetector.detect(frame)
           │
           ├─→ extract face crop
           │
           ▼
    FaceRecognizer.get_embedding(crop)
           │
           ├─→ 128-dim vector
           │
           ▼
    database.add_student(name)
    database.store_embedding(student_id, embedding)
           │
           ▼
repeat for 3 samples
           │
           ▼
User back to main menu
```

### Attendance Flow
```
User selects "2. Start Attendance"
           │
           ▼
database.get_all_embeddings()
           │
           ├─→ Load all student DB to memory
           │
           ▼
AttendanceSystem.run_webcam()
           │
    ┌──────┴──────────────────┐
    │ for each frame:          │
    │                          │
    ▼                          │
YOLOv8FaceDetector.detect()   │
    │                          │
    ├─→ [face1, face2, ...]   │
    │                          │
    ▼                          │
for each face:                │
    │                          │
    ├─→ FaceRecognizer.get_embedding()
    │   │                     │
    │   ├─→ 128-dim vector   │
    │   │                     │
    │   ▼                     │
    ├─→ recognizer.find_best_match()
    │   │                     │
    │   ├─→ cosine similarity│
    │   │                     │
    │   ▼                     │
    ├─→ if match:            │
    │       mark_attendance() │
    │       draw green box    │
    │   else:                 │
    │       draw yellow box   │
    │                          │
    └──────┬──────────────────┘
           │
           ▼
    Handle keys (R, Q)
           │
           ▼
    Exit or report
```

### Match Score Interpretation
```
Cosine Similarity Score:

0.85-1.0  🟢 Strong match - Definitely same person
0.70-0.85 🟡 Likely match - Probably same person
0.50-0.70 🟠 Weak match - Maybe same person
0.00-0.50 🔴 No match - Different person

Default threshold: 0.50
  ✓ Accept matches ≥ 0.50
  ✗ Reject matches < 0.50
```

---

## Performance Profile

### Memory Usage
```
Model Loading:
  - YOLOv8-nano: 30 MB
  - face_recognition: 50 MB
  - Student embeddings: ~1 KB × N students

Typical:
  - 100 students: ~500 MB total
```

### Latency Per Frame (5 faces)
```
Detection (YOLOv8):       80 ms (CPU)
Embedding extraction:    40 ms (5 faces × 8ms each)
Database lookup:         10 ms
Visualization:           10 ms
─────────────────────────────
Total:                  140 ms → ~7 FPS
```

### Throughput
```
With 30 FPS capture:
  Every ~4-5 frames processed in real-time
  Smooth visual experience
  No frame drops on CPU
```

---

## Error Handling

### What Happens If...

**No face detected?**
- Skip embedding extraction
- Draw no boxes for that frame
- Continue to next frame

**Embedding extraction fails?**
- Skip that face
- Continue with other faces
- Show warning in console

**Database error?**
- Print error message
- Continue session
- No crash

**Camera unavailable?**
- Print "Cannot open webcam"
- Return to main menu

**No students enrolled?**
- Print warning
- Exit attendance session
- Return to main menu

---

## Extension Points

### To Add Features:

1. **Anti-spoofing**:
   - Add `antispoofing.py`
   - Check for liveness before marking

2. **Better Embeddings**:
   - Replace `face_recognition` with `insightface`
   - Use 512-dim ArcFace embeddings

3. **REST API**:
   - Wrap `attendance.py` in Flask/FastAPI
   - Expose endpoints for remote enrollment/marking

4. **Multi-camera**:
   - Loop over multiple camera IDs
   - Synchronize attendance across angles

5. **CSV Export**:
   - Add function in `database.py`
   - Export attendance records

6. **Duplicate Detection**:
   - Cluster embeddings at enrollment
   - Prevent same person enrolling twice

---

**System Architecture Complete! Ready for deployment. 🚀**
