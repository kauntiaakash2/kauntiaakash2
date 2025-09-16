"""
Classroom routes for CRUD operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import Classroom, ClassroomCreate, ClassroomUpdate
from app.utils.database import get_collection
from app.utils.auth import verify_token
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()


async def get_current_user(token: str = Depends(security)):
    """Dependency to get current authenticated user (placeholder)"""
    try:
        payload = verify_token(token.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.post("/", response_model=Classroom, status_code=status.HTTP_201_CREATED)
async def create_classroom(classroom: ClassroomCreate, current_user: dict = Depends(get_current_user)):
    """Create a new classroom"""
    try:
        collection = await get_collection("classrooms")
        
        # Check if classroom with same room number already exists
        existing_classroom = await collection.find_one({"room_number": classroom.room_number})
        if existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Classroom with this room number already exists"
            )
        
        classroom_dict = classroom.dict()
        result = await collection.insert_one(classroom_dict)
        
        # Retrieve the created classroom
        created_classroom = await collection.find_one({"_id": result.inserted_id})
        return Classroom(**created_classroom)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create classroom: {str(e)}"
        )


@router.get("/", response_model=List[Classroom])
async def get_classrooms(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get all classrooms with pagination"""
    try:
        collection = await get_collection("classrooms")
        classrooms = await collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [Classroom(**classroom) for classroom in classrooms]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve classrooms: {str(e)}"
        )


@router.get("/{classroom_id}", response_model=Classroom)
async def get_classroom(classroom_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific classroom by ID"""
    try:
        if not ObjectId.is_valid(classroom_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid classroom ID format"
            )
        
        collection = await get_collection("classrooms")
        classroom = await collection.find_one({"_id": ObjectId(classroom_id)})
        
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Classroom not found"
            )
        
        return Classroom(**classroom)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve classroom: {str(e)}"
        )


@router.put("/{classroom_id}", response_model=Classroom)
async def update_classroom(classroom_id: str, classroom_update: ClassroomUpdate, current_user: dict = Depends(get_current_user)):
    """Update a classroom"""
    try:
        if not ObjectId.is_valid(classroom_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid classroom ID format"
            )
        
        collection = await get_collection("classrooms")
        
        # Check if classroom exists
        existing_classroom = await collection.find_one({"_id": ObjectId(classroom_id)})
        if not existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Classroom not found"
            )
        
        # Update only provided fields
        update_data = {k: v for k, v in classroom_update.dict().items() if v is not None}
        
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(classroom_id)},
                {"$set": update_data}
            )
        
        # Return updated classroom
        updated_classroom = await collection.find_one({"_id": ObjectId(classroom_id)})
        return Classroom(**updated_classroom)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update classroom: {str(e)}"
        )


@router.delete("/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(classroom_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a classroom"""
    try:
        if not ObjectId.is_valid(classroom_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid classroom ID format"
            )
        
        collection = await get_collection("classrooms")
        
        # Check if classroom exists
        existing_classroom = await collection.find_one({"_id": ObjectId(classroom_id)})
        if not existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Classroom not found"
            )
        
        # Delete the classroom
        await collection.delete_one({"_id": ObjectId(classroom_id)})
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete classroom: {str(e)}"
        )