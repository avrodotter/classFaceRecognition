# 🪟 Windows Setup Guide

Complete guide to run the **Face Recognition Attendance System** on Windows.

---

## ⚠️ Important: Virtual Environment is Platform-Specific

**Do NOT copy the `venv` folder from Linux/Mac to Windows.** Virtual environments contain platform-specific compiled binaries that won't work across operating systems.

### Why It Won't Work
- `venv` contains Linux executables (`.so` files) and paths
- Windows expects `.exe` and `.dll` files
- Packages like `opencv-python`, `face-recognition`, `numpy` have compiled C extensions
- Shell scripts (`.sh`) don't run on Windows

---

## ✅ Option 1: Fresh Setup on Windows (Recommended)

### Step 1: Copy Project Files Only
Copy the project folder to Windows, **excluding the `venv` directory**:
```
Attendence_facerecognition_v2/
├── main.py
├── attendance.py
├── enrollment.py
├── detector.py
├── recognizer.py
├── database.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── attendance.db         (optional)
├── yolov8n.pt           (optional)
└── ImagesAttendance/    (optional)
```

**Do NOT copy:**
- `venv/` directory
- `__pycache__/` directory
- `.sh` files

### Step 2: Create Virtual Environment
Open **Command Prompt** or **PowerShell** in the project folder:

```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Command Prompt:**
```cmd
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

> **Note:** On PowerShell, you might need to enable script execution:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

This will install all packages fresh for Windows (takes 2-3 minutes).

### Step 5: Run the Application
```cmd
python main.py
```

You'll see the menu:
```
1. 📝 Enroll New Student
2. 🎥 Start Attendance Session
3. 📊 View Today's Report
4. ❌ Exit
```

---

## ✅ Option 2: If You Already Copied the Entire Folder

If you already copied the `venv` folder and it's not working:

### Step 1: Delete the Old venv
**Command Prompt:**
```cmd
rmdir /s venv
```

**PowerShell:**
```powershell
Remove-Item venv -Recurse -Force
```

### Step 2: Create Fresh venv and Install
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 🎯 First Use: Enroll Students

1. Select **Option 1: Enroll New Student**
2. Enter student name: `John Doe`
3. **Press SPACE 3 times** from different angles:
   - Front view
   - Left profile
   - Right profile
4. System extracts face embeddings automatically
5. Repeat for all students

**Result:** Student faces stored in `attendance.db`

---

## 📸 Daily Attendance Session

1. Select **Option 2: Start Attendance Session**
2. System loads all student embeddings
3. Point camera at classroom/entrance
4. As students appear:
   - **Green boxes** = Recognized student ✅
   - **Yellow boxes** = Unknown face 🟡
5. Attendance marked automatically (with 5-second cooldown)

### During Session:
- **Press R** - Show quick attendance report
- **Press Q** - Exit and save attendance

---

## 📊 View Attendance Report

Select **Option 3: View Today's Report** to see:
- All students marked today
- Timestamps of each mark
- Confidence scores

---

## 🔧 Troubleshooting

### Python Not Found
Ensure Python is installed and added to PATH:
```cmd
python --version
```

### pip Install Fails
Try upgrading pip first:
```cmd
python -m pip install --upgrade pip
```

### No Webcam Detected
- Check if webcam is connected and enabled
- Verify no other app is using the camera
- Run Windows device manager to confirm camera is recognized

### Poor Face Recognition
- Ensure good lighting
- Enroll students with varied angles
- Move closer to camera (30-60cm optimal)
- Adjust confidence threshold in `attendance.py`:
  ```python
  system = AttendanceSystem(confidence_threshold=0.5)
  ```
  - Higher value = stricter (fewer false positives)
  - Lower value = looser (more false negatives)

### Slow Performance
- Close other applications
- Reduce video frame resolution
- Use lighter YOLOv8 model (default is `yolov8n` - already optimized)

---

## 📁 Project Structure

```
Attendence_facerecognition_v2/
├── main.py                 # CLI entry point
├── attendance.py           # Attendance marking system
├── enrollment.py           # Student registration
├── detector.py             # YOLOv8-face detection
├── recognizer.py           # Face embedding extraction
├── database.py             # SQLite operations
├── requirements.txt        # Python dependencies
├── attendance.db           # SQLite database (auto-created)
├── yolov8n.pt             # Detection model (auto-downloaded)
├── README.md              # Main documentation
├── ARCHITECTURE.md        # System design
├── WINDOWS_SETUP.md       # This file
└── ImagesAttendance/      # Captured enrollment images
```

---

## 📋 Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| opencv-python | ≥4.8.0 | Image/video processing |
| numpy | ≥1.24.0 | Numerical operations |
| ultralytics | ≥8.0.0 | YOLOv8 face detection |
| onnxruntime | ≥1.16.0 | ONNX model runtime |
| scikit-learn | ≥1.3.0 | Cosine similarity |
| face-recognition | ≥1.3.0 | 128-dim face embeddings |

---

## 🚀 Quick Command Reference

```cmd
# Activate venv
venv\Scripts\activate

# Deactivate venv
deactivate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Update a package
pip install --upgrade package_name

# View installed packages
pip list
```

---

## 💡 Tips

- **Keep venv activated** while working on the project
- **Windows paths use backslashes** (`\`) instead of forward slashes (`/`)
- **Use Command Prompt or PowerShell** (both work equally well)
- **First run takes longer** because models download automatically

---

**Ready to go! Start with `python main.py` 🎓**
