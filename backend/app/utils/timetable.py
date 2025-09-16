"""
Timetable generation utilities and algorithms
"""
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
from app.models import TimetableSlot, TimetableRequest, Batch, Subject, Teacher, Classroom
from app.utils.database import get_collection
from bson import ObjectId
import random


class TimetableGenerator:
    """Timetable generation algorithm"""
    
    def __init__(self):
        self.conflicts = []
        
    async def generate_timetable(self, request: TimetableRequest) -> Tuple[List[TimetableSlot], List[str]]:
        """Generate optimized timetable based on constraints"""
        self.conflicts = []
        timetable_slots = []
        
        try:
            # Fetch all required data
            batches = await self._get_batches(request.batch_ids)
            subjects = await self._get_subjects_for_batches(batches)
            teachers = await self._get_all_teachers()
            classrooms = await self._get_all_classrooms()
            
            # Generate time slots
            time_slots = self._generate_time_slots(request)
            
            # Create schedule matrix to track conflicts
            schedule_matrix = self._initialize_schedule_matrix(time_slots, teachers, classrooms)
            
            # Generate timetable for each batch
            for batch in batches:
                batch_subjects = [s for s in subjects if str(s["_id"]) in batch["subjects"]]
                batch_slots = await self._generate_batch_timetable(
                    batch, batch_subjects, teachers, classrooms, time_slots, schedule_matrix
                )
                timetable_slots.extend(batch_slots)
            
            return timetable_slots, self.conflicts
            
        except Exception as e:
            self.conflicts.append(f"Failed to generate timetable: {str(e)}")
            return [], self.conflicts
    
    async def _get_batches(self, batch_ids: List[str]) -> List[Dict]:
        """Fetch batch data"""
        collection = await get_collection("batches")
        object_ids = [ObjectId(bid) for bid in batch_ids if ObjectId.is_valid(bid)]
        batches = await collection.find({"_id": {"$in": object_ids}}).to_list(length=None)
        return batches
    
    async def _get_subjects_for_batches(self, batches: List[Dict]) -> List[Dict]:
        """Fetch subjects for all batches"""
        subject_ids = set()
        for batch in batches:
            subject_ids.update(batch.get("subjects", []))
        
        collection = await get_collection("subjects")
        object_ids = [ObjectId(sid) for sid in subject_ids if ObjectId.is_valid(sid)]
        subjects = await collection.find({"_id": {"$in": object_ids}}).to_list(length=None)
        return subjects
    
    async def _get_all_teachers(self) -> List[Dict]:
        """Fetch all teachers"""
        collection = await get_collection("teachers")
        teachers = await collection.find().to_list(length=None)
        return teachers
    
    async def _get_all_classrooms(self) -> List[Dict]:
        """Fetch all classrooms"""
        collection = await get_collection("classrooms")
        classrooms = await collection.find().to_list(length=None)
        return classrooms
    
    def _generate_time_slots(self, request: TimetableRequest) -> List[Dict]:
        """Generate available time slots"""
        slots = []
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime("%A")
            if day_name in request.working_days:
                # Generate hourly slots from start_time to end_time
                start_time = datetime.strptime(request.start_time, "%H:%M").time()
                end_time = datetime.strptime(request.end_time, "%H:%M").time()
                
                # Create 1-hour slots
                current_time = datetime.combine(current_date, start_time)
                day_end = datetime.combine(current_date, end_time)
                
                while current_time < day_end:
                    slot_end = current_time + timedelta(hours=1)
                    if slot_end.time() <= end_time:
                        slots.append({
                            "date": current_date.strftime("%Y-%m-%d"),
                            "day": day_name,
                            "start_time": current_time.strftime("%H:%M"),
                            "end_time": slot_end.strftime("%H:%M")
                        })
                    current_time = slot_end
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _initialize_schedule_matrix(self, time_slots: List[Dict], teachers: List[Dict], classrooms: List[Dict]) -> Dict:
        """Initialize schedule tracking matrix"""
        matrix = {
            "teacher_schedule": {},
            "classroom_schedule": {}
        }
        
        # Initialize teacher schedules
        for teacher in teachers:
            teacher_id = str(teacher["_id"])
            matrix["teacher_schedule"][teacher_id] = set()
        
        # Initialize classroom schedules
        for classroom in classrooms:
            classroom_id = str(classroom["_id"])
            matrix["classroom_schedule"][classroom_id] = set()
        
        return matrix
    
    async def _generate_batch_timetable(self, batch: Dict, subjects: List[Dict], 
                                       teachers: List[Dict], classrooms: List[Dict], 
                                       time_slots: List[Dict], schedule_matrix: Dict) -> List[TimetableSlot]:
        """Generate timetable for a specific batch"""
        batch_slots = []
        
        # Calculate total classes needed per subject
        subject_requirements = {}
        for subject in subjects:
            subject_id = str(subject["_id"])
            classes_per_week = subject.get("classes_per_week", 2)
            # Calculate total classes needed for the period
            weeks = max(1, len(set(slot["date"] for slot in time_slots)) // 7)
            total_classes = classes_per_week * weeks
            subject_requirements[subject_id] = total_classes
        
        # Assign classes to time slots
        slot_index = 0
        for subject in subjects:
            subject_id = str(subject["_id"])
            classes_needed = subject_requirements[subject_id]
            
            # Find available teachers for this subject
            available_teachers = self._find_available_teachers(subject, teachers)
            
            classes_assigned = 0
            while classes_assigned < classes_needed and slot_index < len(time_slots):
                time_slot = time_slots[slot_index]
                
                # Try to assign this slot
                assigned = await self._try_assign_slot(
                    batch, subject, available_teachers, classrooms, 
                    time_slot, schedule_matrix, batch_slots
                )
                
                if assigned:
                    classes_assigned += 1
                
                slot_index += 1
        
        return batch_slots
    
    def _find_available_teachers(self, subject: Dict, teachers: List[Dict]) -> List[Dict]:
        """Find teachers who can teach a specific subject"""
        subject_id = str(subject["_id"])
        available_teachers = []
        
        for teacher in teachers:
            teacher_subjects = teacher.get("subjects", [])
            if subject_id in teacher_subjects or not teacher_subjects:  # Allow teachers with no specific subjects
                available_teachers.append(teacher)
        
        # If no specific teachers found, use any available teacher (for MVP)
        if not available_teachers:
            available_teachers = teachers[:1] if teachers else []
        
        return available_teachers
    
    async def _try_assign_slot(self, batch: Dict, subject: Dict, available_teachers: List[Dict],
                              classrooms: List[Dict], time_slot: Dict, 
                              schedule_matrix: Dict, batch_slots: List[TimetableSlot]) -> bool:
        """Try to assign a subject to a time slot"""
        
        # Find available teacher
        teacher = self._find_available_teacher_for_slot(available_teachers, time_slot, schedule_matrix)
        if not teacher:
            self.conflicts.append(f"No available teacher for {subject['name']} at {time_slot['start_time']} on {time_slot['day']}")
            return False
        
        # Find available classroom
        classroom = self._find_available_classroom_for_slot(classrooms, time_slot, schedule_matrix)
        if not classroom:
            self.conflicts.append(f"No available classroom for {subject['name']} at {time_slot['start_time']} on {time_slot['day']}")
            return False
        
        # Create the timetable slot
        slot_key = f"{time_slot['date']}_{time_slot['start_time']}"
        teacher_id = str(teacher["_id"])
        classroom_id = str(classroom["_id"])
        
        # Mark resources as used
        schedule_matrix["teacher_schedule"][teacher_id].add(slot_key)
        schedule_matrix["classroom_schedule"][classroom_id].add(slot_key)
        
        # Create timetable slot for each section in the batch
        for section in batch.get("sections", ["A"]):
            timetable_slot = TimetableSlot(
                day=time_slot["day"],
                start_time=time_slot["start_time"],
                end_time=time_slot["end_time"],
                subject_id=str(subject["_id"]),
                teacher_id=teacher_id,
                classroom_id=classroom_id,
                batch_id=str(batch["_id"]),
                section=section
            )
            batch_slots.append(timetable_slot)
        
        return True
    
    def _find_available_teacher_for_slot(self, teachers: List[Dict], time_slot: Dict, 
                                        schedule_matrix: Dict) -> Dict:
        """Find an available teacher for a specific time slot"""
        slot_key = f"{time_slot['date']}_{time_slot['start_time']}"
        
        for teacher in teachers:
            teacher_id = str(teacher["_id"])
            if slot_key not in schedule_matrix["teacher_schedule"][teacher_id]:
                # Check if teacher hasn't exceeded daily class limit
                day_slots = [key for key in schedule_matrix["teacher_schedule"][teacher_id] 
                           if key.startswith(time_slot['date'])]
                max_classes = teacher.get("max_classes_per_day", 6)
                
                if len(day_slots) < max_classes:
                    return teacher
        
        return None
    
    def _find_available_classroom_for_slot(self, classrooms: List[Dict], time_slot: Dict, 
                                          schedule_matrix: Dict) -> Dict:
        """Find an available classroom for a specific time slot"""
        slot_key = f"{time_slot['date']}_{time_slot['start_time']}"
        
        for classroom in classrooms:
            classroom_id = str(classroom["_id"])
            if slot_key not in schedule_matrix["classroom_schedule"][classroom_id]:
                return classroom
        
        return None