"""
Subject routes for CRUD operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import Subject, SubjectCreate, SubjectUpdate
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


@router.post("/", response_model=Subject, status_code=status.HTTP_201_CREATED)
async def create_subject(subject: SubjectCreate, current_user: dict = Depends(get_current_user)):
    """Create a new subject"""
    try:
        collection = await get_collection("subjects")
        
        # Check if subject with same name already exists
        existing_subject = await collection.find_one({"name": subject.name})
        if existing_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject with this name already exists"
            )
        
        subject_dict = subject.dict()
        result = await collection.insert_one(subject_dict)
        
        # Retrieve the created subject
        created_subject = await collection.find_one({"_id": result.inserted_id})
        return Subject(**created_subject)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subject: {str(e)}"
        )


@router.get("/", response_model=List[Subject])
async def get_subjects(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get all subjects with pagination"""
    try:
        collection = await get_collection("subjects")
        subjects = await collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [Subject(**subject) for subject in subjects]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subjects: {str(e)}"
        )


@router.get("/{subject_id}", response_model=Subject)
async def get_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific subject by ID"""
    try:
        if not ObjectId.is_valid(subject_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subject ID format"
            )
        
        collection = await get_collection("subjects")
        subject = await collection.find_one({"_id": ObjectId(subject_id)})
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        return Subject(**subject)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subject: {str(e)}"
        )


@router.put("/{subject_id}", response_model=Subject)
async def update_subject(subject_id: str, subject_update: SubjectUpdate, current_user: dict = Depends(get_current_user)):
    """Update a subject"""
    try:
        if not ObjectId.is_valid(subject_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subject ID format"
            )
        
        collection = await get_collection("subjects")
        
        # Check if subject exists
        existing_subject = await collection.find_one({"_id": ObjectId(subject_id)})
        if not existing_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Update only provided fields
        update_data = {k: v for k, v in subject_update.dict().items() if v is not None}
        
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(subject_id)},
                {"$set": update_data}
            )
        
        # Return updated subject
        updated_subject = await collection.find_one({"_id": ObjectId(subject_id)})
        return Subject(**updated_subject)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subject: {str(e)}"
        )


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a subject"""
    try:
        if not ObjectId.is_valid(subject_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subject ID format"
            )
        
        collection = await get_collection("subjects")
        
        # Check if subject exists
        existing_subject = await collection.find_one({"_id": ObjectId(subject_id)})
        if not existing_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Delete the subject
        await collection.delete_one({"_id": ObjectId(subject_id)})
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subject: {str(e)}"
        )