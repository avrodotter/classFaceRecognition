"""SQLite database schema and operations for attendance system."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path('attendance.db')

def init_database():
    """Initialize database with students and embeddings tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Embeddings table (stores 512-dim ArcFace embeddings)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            embedding_blob TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    # Attendance records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence REAL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_student(name: str) -> int:
    """Add new student to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO students (name) VALUES (?)', (name,))
        conn.commit()
        student_id = cursor.lastrowid
        return student_id
    except sqlite3.IntegrityError:
        return get_student_id(name)
    finally:
        conn.close()

def get_student_id(name: str) -> int:
    """Get student ID by name."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM students WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def store_embedding(student_id: int, embedding: list):
    """Store face embedding as JSON blob."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    embedding_json = json.dumps(embedding)
    cursor.execute(
        'INSERT INTO embeddings (student_id, embedding_blob) VALUES (?, ?)',
        (student_id, embedding_json)
    )
    conn.commit()
    conn.close()

def get_all_embeddings():
    """Load all student embeddings from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, s.name, e.embedding_blob 
        FROM students s 
        JOIN embeddings e ON s.id = e.student_id
    ''')
    results = cursor.fetchall()
    conn.close()
    
    students = {}
    for student_id, name, embedding_json in results:
        embedding = json.loads(embedding_json)
        if name not in students:
            students[name] = {'id': student_id, 'embeddings': []}
        students[name]['embeddings'].append(embedding)
    
    return students

def mark_attendance(student_id: int, confidence: float):
    """Mark student attendance with confidence score."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO attendance (student_id, confidence) VALUES (?, ?)',
        (student_id, confidence)
    )
    conn.commit()
    conn.close()

def get_attendance_report(date_str: str = None):
    """Get attendance report for a specific date or today."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT s.name, COUNT(*) as count, MAX(a.timestamp) as last_seen
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE DATE(a.timestamp) = ?
        GROUP BY a.student_id
        ORDER BY s.name
    ''', (date_str,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_students():
    """Get list of all enrolled students with embedding count."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, s.name, COUNT(e.id) as embedding_count, s.enrollment_date
        FROM students s
        LEFT JOIN embeddings e ON s.id = e.student_id
        GROUP BY s.id
        ORDER BY s.name
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def delete_student(student_id: int) -> bool:
    """Delete student and all their embeddings and attendance records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM embeddings WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error deleting student: {e}")
        return False
    finally:
        conn.close()

def delete_student_embedding(embedding_id: int) -> bool:
    """Delete a specific face embedding."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM embeddings WHERE id = ?', (embedding_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error deleting embedding: {e}")
        return False
    finally:
        conn.close()

def get_student_embeddings(student_id: int):
    """Get all embeddings for a specific student."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, created_at FROM embeddings
        WHERE student_id = ?
        ORDER BY created_at DESC
    ''', (student_id,))
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == '__main__':
    init_database()
