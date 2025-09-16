"""
Batch routes for CRUD operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models import Batch, BatchCreate, BatchUpdate
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


@router.post("/", response_model=Batch, status_code=status.HTTP_201_CREATED)
async def create_batch(batch: BatchCreate, current_user: dict = Depends(get_current_user)):
    """Create a new batch"""
    try:
        collection = await get_collection("batches")
        
        # Check if batch with same name already exists
        existing_batch = await collection.find_one({"name": batch.name})
        if existing_batch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch with this name already exists"
            )
        
        batch_dict = batch.dict()
        result = await collection.insert_one(batch_dict)
        
        # Retrieve the created batch
        created_batch = await collection.find_one({"_id": result.inserted_id})
        return Batch(**created_batch)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch: {str(e)}"
        )


@router.get("/", response_model=List[Batch])
async def get_batches(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get all batches with pagination"""
    try:
        collection = await get_collection("batches")
        batches = await collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [Batch(**batch) for batch in batches]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve batches: {str(e)}"
        )


@router.get("/{batch_id}", response_model=Batch)
async def get_batch(batch_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific batch by ID"""
    try:
        if not ObjectId.is_valid(batch_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid batch ID format"
            )
        
        collection = await get_collection("batches")
        batch = await collection.find_one({"_id": ObjectId(batch_id)})
        
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        return Batch(**batch)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve batch: {str(e)}"
        )


@router.put("/{batch_id}", response_model=Batch)
async def update_batch(batch_id: str, batch_update: BatchUpdate, current_user: dict = Depends(get_current_user)):
    """Update a batch"""
    try:
        if not ObjectId.is_valid(batch_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid batch ID format"
            )
        
        collection = await get_collection("batches")
        
        # Check if batch exists
        existing_batch = await collection.find_one({"_id": ObjectId(batch_id)})
        if not existing_batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        # Update only provided fields
        update_data = {k: v for k, v in batch_update.dict().items() if v is not None}
        
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(batch_id)},
                {"$set": update_data}
            )
        
        # Return updated batch
        updated_batch = await collection.find_one({"_id": ObjectId(batch_id)})
        return Batch(**updated_batch)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update batch: {str(e)}"
        )


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(batch_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a batch"""
    try:
        if not ObjectId.is_valid(batch_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid batch ID format"
            )
        
        collection = await get_collection("batches")
        
        # Check if batch exists
        existing_batch = await collection.find_one({"_id": ObjectId(batch_id)})
        if not existing_batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        # Delete the batch
        await collection.delete_one({"_id": ObjectId(batch_id)})
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete batch: {str(e)}"
        )