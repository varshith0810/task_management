from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import UserPublic

router = APIRouter(prefix="", tags=["Users"])


@router.get("/users/search", response_model=list[UserPublic])
def search_users(
    q: str = Query(..., min_length=1, description="Search by email or name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Any authenticated user can search for others to add to projects."""
    return (
        db.query(User)
        .filter(
            User.is_active == True,
            User.id != current_user.id,

            User.organization_name == current_user.organization_name,

            (User.email.ilike(f"%{q}%") | User.full_name.ilike(f"%{q}%")),
        )
        .limit(20)
        .all()
    )
