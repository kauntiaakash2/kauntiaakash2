"""
Pydantic models for the Smart Classroom Timetable Scheduler
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Annotated
from bson import ObjectId
from datetime import datetime


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class Teacher(BaseModel):
    """Teacher model"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    max_classes_per_day: int = Field(..., ge=1, le=8)
    leave_count: int = Field(default=0, ge=0)
    subjects: List[str] = Field(default=[], description="List of subject IDs the teacher can teach")


class TeacherCreate(BaseModel):
    """Teacher creation model"""
    name: str = Field(..., min_length=1, max_length=100)
    max_classes_per_day: int = Field(..., ge=1, le=8)
    leave_count: int = Field(default=0, ge=0)
    subjects: List[str] = Field(default=[])


class TeacherUpdate(BaseModel):
    """Teacher update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    max_classes_per_day: Optional[int] = Field(None, ge=1, le=8)
    leave_count: Optional[int] = Field(None, ge=0)
    subjects: Optional[List[str]] = None


class Classroom(BaseModel):
    """Classroom model"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    room_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., ge=1, le=200)
    section: str = Field(..., min_length=1, max_length=10)


class ClassroomCreate(BaseModel):
    """Classroom creation model"""
    room_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., ge=1, le=200)
    section: str = Field(..., min_length=1, max_length=10)


class ClassroomUpdate(BaseModel):
    """Classroom update model"""
    room_number: Optional[str] = Field(None, min_length=1, max_length=20)
    capacity: Optional[int] = Field(None, ge=1, le=200)
    section: Optional[str] = Field(None, min_length=1, max_length=10)


class Subject(BaseModel):
    """Subject model"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    classes_per_week: int = Field(..., ge=1, le=10)
    duration_per_class: int = Field(..., ge=30, le=180, description="Duration in minutes")
    assigned_teachers: List[str] = Field(default=[], description="List of teacher IDs assigned to this subject")


class SubjectCreate(BaseModel):
    """Subject creation model"""
    name: str = Field(..., min_length=1, max_length=100)
    classes_per_week: int = Field(..., ge=1, le=10)
    duration_per_class: int = Field(..., ge=30, le=180)
    assigned_teachers: List[str] = Field(default=[])


class SubjectUpdate(BaseModel):
    """Subject update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    classes_per_week: Optional[int] = Field(None, ge=1, le=10)
    duration_per_class: Optional[int] = Field(None, ge=30, le=180)
    assigned_teachers: Optional[List[str]] = None


class Batch(BaseModel):
    """Batch model"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    subjects: List[str] = Field(..., description="List of subject IDs for this batch")
    sections: List[str] = Field(..., description="List of section names")


class BatchCreate(BaseModel):
    """Batch creation model"""
    name: str = Field(..., min_length=1, max_length=100)
    subjects: List[str] = Field(..., min_items=1)
    sections: List[str] = Field(..., min_items=1)


class BatchUpdate(BaseModel):
    """Batch update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subjects: Optional[List[str]] = Field(None, min_items=1)
    sections: Optional[List[str]] = Field(None, min_items=1)


class TimetableSlot(BaseModel):
    """Individual timetable slot"""
    day: str = Field(..., description="Day of the week")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    subject_id: str = Field(..., description="Subject ID")
    teacher_id: str = Field(..., description="Teacher ID")
    classroom_id: str = Field(..., description="Classroom ID")
    batch_id: str = Field(..., description="Batch ID")
    section: str = Field(..., description="Section name")


class TimetableRequest(BaseModel):
    """Timetable generation request"""
    batch_ids: List[str] = Field(..., min_items=1, description="List of batch IDs to generate timetable for")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    working_days: List[str] = Field(default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    start_time: str = Field(default="09:00", description="Daily start time (HH:MM)")
    end_time: str = Field(default="17:00", description="Daily end time (HH:MM)")
    break_duration: int = Field(default=60, description="Break duration in minutes")


class TimetableResponse(BaseModel):
    """Timetable generation response"""
    success: bool
    message: str
    timetable: List[TimetableSlot] = Field(default=[])
    conflicts: List[str] = Field(default=[], description="List of conflicts found during generation")