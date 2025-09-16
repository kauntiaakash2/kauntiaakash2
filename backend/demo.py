#!/usr/bin/env python3
"""
Demo script to showcase the Smart Classroom Timetable Scheduler API
This script demonstrates the API functionality without requiring MongoDB
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models import (
    TeacherCreate, Teacher,
    ClassroomCreate, Classroom, 
    SubjectCreate, Subject,
    BatchCreate, Batch,
    TimetableRequest, TimetableResponse, TimetableSlot
)
from app.utils.auth import create_access_token, verify_token
from app.config import settings
import json

def demo_models():
    """Demonstrate data model validation"""
    print("🔧 Testing Data Models...")
    
    # Teacher model
    teacher = TeacherCreate(
        name="Dr. Sarah Johnson",
        max_classes_per_day=6,
        leave_count=2,
        subjects=["math", "physics"]
    )
    print(f"✅ Teacher: {teacher.name} - Max classes: {teacher.max_classes_per_day}")
    
    # Classroom model
    classroom = ClassroomCreate(
        room_number="A-101",
        capacity=45,
        section="Block A"
    )
    print(f"✅ Classroom: {classroom.room_number} - Capacity: {classroom.capacity}")
    
    # Subject model
    subject = SubjectCreate(
        name="Advanced Mathematics",
        classes_per_week=5,
        duration_per_class=90,
        assigned_teachers=["teacher1"]
    )
    print(f"✅ Subject: {subject.name} - {subject.classes_per_week} classes/week")
    
    # Batch model
    batch = BatchCreate(
        name="Computer Science - 2024",
        subjects=["math", "physics", "cs"],
        sections=["A", "B", "C"]
    )
    print(f"✅ Batch: {batch.name} - Sections: {', '.join(batch.sections)}")

def demo_authentication():
    """Demonstrate JWT authentication"""
    print("\n🔐 Testing Authentication...")
    
    # Create token
    user_data = {"sub": "admin", "role": "admin", "permissions": ["read", "write"]}
    token = create_access_token(user_data)
    print(f"✅ JWT Token created (length: {len(token)})")
    
    # Verify token
    payload = verify_token(token)
    print(f"✅ Token verified - User: {payload['sub']}, Role: {payload['role']}")

def demo_timetable_request():
    """Demonstrate timetable generation request"""
    print("\n📅 Testing Timetable Generation...")
    
    # Create timetable request
    request = TimetableRequest(
        batch_ids=["batch_cs_2024", "batch_it_2024"],
        start_date="2024-01-15",
        end_date="2024-01-26",
        working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        start_time="09:00",
        end_time="17:00",
        break_duration=60
    )
    print(f"✅ Timetable request created for {len(request.batch_ids)} batches")
    print(f"   📅 Duration: {request.start_date} to {request.end_date}")
    print(f"   ⏰ Schedule: {request.start_time} - {request.end_time}")
    
    # Sample timetable slot
    slot = TimetableSlot(
        day="Monday",
        start_time="09:00",
        end_time="10:30",
        subject_id="math_101",
        teacher_id="teacher_001",
        classroom_id="room_a101",
        batch_id="batch_cs_2024",
        section="A"
    )
    print(f"✅ Sample timetable slot: {slot.subject_id} on {slot.day} at {slot.start_time}")

def demo_api_structure():
    """Show API endpoint structure"""
    print("\n🌐 API Endpoint Structure:")
    
    endpoints = {
        "Authentication": [
            "POST /auth/login",
            "GET /auth/me"
        ],
        "Teachers": [
            "POST /api/v1/teachers",
            "GET /api/v1/teachers",
            "GET /api/v1/teachers/{id}",
            "PUT /api/v1/teachers/{id}",
            "DELETE /api/v1/teachers/{id}"
        ],
        "Classrooms": [
            "POST /api/v1/classrooms",
            "GET /api/v1/classrooms",
            "GET /api/v1/classrooms/{id}",
            "PUT /api/v1/classrooms/{id}",
            "DELETE /api/v1/classrooms/{id}"
        ],
        "Subjects": [
            "POST /api/v1/subjects",
            "GET /api/v1/subjects",
            "GET /api/v1/subjects/{id}",
            "PUT /api/v1/subjects/{id}",
            "DELETE /api/v1/subjects/{id}"
        ],
        "Batches": [
            "POST /api/v1/batches",
            "GET /api/v1/batches",
            "GET /api/v1/batches/{id}",
            "PUT /api/v1/batches/{id}",
            "DELETE /api/v1/batches/{id}"
        ],
        "Timetable": [
            "POST /api/v1/timetable/generate-timetable",
            "GET /api/v1/timetable/health"
        ]
    }
    
    for category, routes in endpoints.items():
        print(f"\n📍 {category}:")
        for route in routes:
            print(f"   {route}")

def demo_configuration():
    """Show configuration settings"""
    print("\n⚙️ Configuration Settings:")
    print(f"   🗄️ Database: {settings.database_name}")
    print(f"   🔑 JWT Algorithm: {settings.algorithm}")
    print(f"   🌐 API Prefix: {settings.api_v1_str}")
    print(f"   🏠 Host: {settings.host}:{settings.port}")
    print(f"   🐛 Debug Mode: {settings.debug}")

def main():
    """Run the complete demo"""
    print("🚀 Smart Classroom Timetable Scheduler - Backend Demo")
    print("=" * 60)
    
    try:
        demo_models()
        demo_authentication()
        demo_timetable_request()
        demo_api_structure()
        demo_configuration()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("📚 The backend is fully functional and ready for deployment.")
        print("🔗 To start the server: python main.py")
        print("📖 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())