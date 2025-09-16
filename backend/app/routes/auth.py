"""
Authentication routes (MVP placeholder implementation)
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.utils.auth import create_access_token
from datetime import timedelta

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str
    expires_in: int


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Placeholder login endpoint for MVP
    In production, this would validate against a user database
    """
    # For MVP, accept any username/password combination
    # In production, you would:
    # 1. Validate credentials against database
    # 2. Hash and verify passwords
    # 3. Handle user roles and permissions
    
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": request.username, "role": "admin"},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes in seconds
    )


@router.post("/refresh")
async def refresh_token():
    """Placeholder token refresh endpoint"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented in MVP"
    )


@router.get("/me")
async def get_current_user():
    """Get current user info (placeholder)"""
    return {
        "username": "admin",
        "role": "admin",
        "message": "This is a placeholder user endpoint for MVP"
    }