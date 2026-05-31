#!/usr/bin/env python3
"""CLI tool for attendance system."""
import sys
import warnings

# Suppress pkg_resources deprecation warning from face_recognition_models
warnings.filterwarnings("ignore", category=UserWarning, module="face_recognition_models")

from database import init_database
from enrollment import EnrollmentMode
from attendance import AttendanceSystem

def print_menu():
    """Display main menu."""
    print("\n" + "="*50)
    print("  📚 CLASSROOM ATTENDANCE SYSTEM")
    print("="*50)
    print("\n  1. 📝 Enroll New Student")
    print("  2. 🎥 Start Attendance Session")
    print("  3. 📊 View Today's Report")
    print("  4. 🗑️  Manage Students (Delete)")
    print("  5. ❌ Exit\n")

def manage_students():
    """Interactive student management (delete/view)."""
    from database import get_all_students, delete_student, get_student_embeddings
    
    while True:
        students = get_all_students()
        
        if not students:
            print("\n  ℹ️ No students enrolled yet\n")
            return
        
        print("\n  " + "="*48)
        print("  📋 ENROLLED STUDENTS")
        print("  " + "="*48)
        for idx, (sid, name, emb_count, enroll_date) in enumerate(students, 1):
            print(f"  {idx}. {name:20} | Samples: {emb_count} | Enrolled: {enroll_date}")
        print("  " + "-"*48)
        print("  0. Back to Main Menu\n")
        
        choice = input("  Select student number to delete (or 0 to go back): ").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(students):
                sid, name, emb_count, _ = students[idx]
                
                print(f"\n  ⚠️  Delete {name}?")
                print(f"     This will remove all {emb_count} face samples and attendance records.")
                confirm = input("  Type 'DELETE' to confirm: ").strip()
                
                if confirm == 'DELETE':
                    if delete_student(sid):
                        print(f"  ✅ Successfully deleted {name}\n")
                    else:
                        print(f"  ❌ Failed to delete {name}\n")
                else:
                    print("  ❌ Cancelled\n")
            else:
                print("  ❌ Invalid selection\n")
        except ValueError:
            print("  ❌ Invalid input\n")

def main():
    """Main CLI loop."""
    init_database()
    
    while True:
        print_menu()
        choice = input("  Select option (1-5): ").strip()
        
        if choice == '1':
            enroller = EnrollmentMode()
            if enroller.start_webcam():
                name = input("\n  Enter student name: ").strip()
                if name:
                    enroller.enroll_student(name, num_samples=3)
                else:
                    print("  ❌ Name required")
            enroller.close()
        
        elif choice == '2':
            duration = input("\n  Session duration in seconds (or press Enter for unlimited): ").strip()
            duration = int(duration) if duration.isdigit() else None
            system = AttendanceSystem(confidence_threshold=0.5)
            system.run_webcam(duration)
        
        elif choice == '3':
            from database import get_attendance_report
            report = get_attendance_report()
            if report:
                print("\n  📋 Today's Attendance Report:")
                print("  " + "-"*40)
                for name, count, last_time in report:
                    print(f"  {name:20} | {count:2} marks | {last_time}")
                print("  " + "-"*40)
            else:
                print("\n  ℹ️ No attendance marks yet")
        
        elif choice == '4':
            manage_students()
        
        elif choice == '5':
            print("\n  👋 Goodbye!\n")
            break
        
        else:
            print("  ❌ Invalid option")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  👋 Interrupted\n")
        sys.exit(0)
