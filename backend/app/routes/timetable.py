"""
Timetable generation routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import TimetableRequest, TimetableResponse
from app.utils.timetable import TimetableGenerator
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


@router.post("/generate-timetable", response_model=TimetableResponse)
async def generate_timetable(request: TimetableRequest, current_user: dict = Depends(get_current_user)):
    """Generate optimized timetable based on constraints"""
    try:
        generator = TimetableGenerator()
        timetable_slots, conflicts = await generator.generate_timetable(request)
        
        return TimetableResponse(
            success=len(conflicts) == 0,
            message="Timetable generated successfully" if len(conflicts) == 0 else "Timetable generated with conflicts",
            timetable=timetable_slots,
            conflicts=conflicts
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate timetable: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for timetable service"""
    return {"status": "healthy", "service": "timetable"}