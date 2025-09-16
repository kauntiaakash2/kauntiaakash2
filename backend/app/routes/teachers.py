"""
Teacher routes for CRUD operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import Teacher, TeacherCreate, TeacherUpdate
from app.utils.database import get_collection
from app.utils.auth import verify_token
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()


async def get_current_user(token: str = Depends(security)):
    """Dependency to get current authenticated user (placeholder)"""
    # For MVP, we'll just verify the token structure
    # In production, you'd verify against a user database
    try:
        payload = verify_token(token.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.post("/", response_model=Teacher, status_code=status.HTTP_201_CREATED)
async def create_teacher(teacher: TeacherCreate, current_user: dict = Depends(get_current_user)):
    """Create a new teacher"""
    try:
        collection = await get_collection("teachers")
        
        # Check if teacher with same name already exists
        existing_teacher = await collection.find_one({"name": teacher.name})
        if existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher with this name already exists"
            )
        
        teacher_dict = teacher.dict()
        result = await collection.insert_one(teacher_dict)
        
        # Retrieve the created teacher
        created_teacher = await collection.find_one({"_id": result.inserted_id})
        return Teacher(**created_teacher)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create teacher: {str(e)}"
        )


@router.get("/", response_model=List[Teacher])
async def get_teachers(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get all teachers with pagination"""
    try:
        collection = await get_collection("teachers")
        teachers = await collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [Teacher(**teacher) for teacher in teachers]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve teachers: {str(e)}"
        )


@router.get("/{teacher_id}", response_model=Teacher)
async def get_teacher(teacher_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific teacher by ID"""
    try:
        if not ObjectId.is_valid(teacher_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid teacher ID format"
            )
        
        collection = await get_collection("teachers")
        teacher = await collection.find_one({"_id": ObjectId(teacher_id)})
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        return Teacher(**teacher)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve teacher: {str(e)}"
        )


@router.put("/{teacher_id}", response_model=Teacher)
async def update_teacher(teacher_id: str, teacher_update: TeacherUpdate, current_user: dict = Depends(get_current_user)):
    """Update a teacher"""
    try:
        if not ObjectId.is_valid(teacher_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid teacher ID format"
            )
        
        collection = await get_collection("teachers")
        
        # Check if teacher exists
        existing_teacher = await collection.find_one({"_id": ObjectId(teacher_id)})
        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Update only provided fields
        update_data = {k: v for k, v in teacher_update.dict().items() if v is not None}
        
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(teacher_id)},
                {"$set": update_data}
            )
        
        # Return updated teacher
        updated_teacher = await collection.find_one({"_id": ObjectId(teacher_id)})
        return Teacher(**updated_teacher)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update teacher: {str(e)}"
        )


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(teacher_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a teacher"""
    try:
        if not ObjectId.is_valid(teacher_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid teacher ID format"
            )
        
        collection = await get_collection("teachers")
        
        # Check if teacher exists
        existing_teacher = await collection.find_one({"_id": ObjectId(teacher_id)})
        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Delete the teacher
        await collection.delete_one({"_id": ObjectId(teacher_id)})
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete teacher: {str(e)}"
        )