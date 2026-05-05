

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
            User.id != current_user.id,  # exclude self
            (User.email.ilike(f"%{q}%") | User.full_name.ilike(f"%{q}%"))
        )
        .limit(20)
        .all()
    )
