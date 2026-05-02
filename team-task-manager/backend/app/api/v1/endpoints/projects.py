"""
/projects  – project CRUD and member management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.v1.deps import (
    get_current_user,
    project_manager_dep,
    project_member_dep,
    project_owner_dep,
    require_admin,
)
from app.db.session import get_db
from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, User
from app.schemas.schemas import (
    AddMemberRequest,
    MemberInProject,
    ProjectCreate,
    ProjectDetail,
    ProjectResponse,
    ProjectUpdate,
    UpdateMemberRole,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Project).filter(Project.is_active == True)
    if current_user.role != GlobalRole.ADMIN:
        q = q.join(ProjectMember).filter(ProjectMember.user_id == current_user.id)
    return q.offset(skip).limit(limit).all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = Project(**payload.model_dump())
    db.add(project)
    db.flush()
    membership = ProjectMember(project_id=project.id, user_id=current_user.id, role=ProjectRole.OWNER)
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(access=Depends(project_member_dep), db: Session = Depends(get_db)):
    project, _ = access
    project_with_members = (
        db.query(Project)
        .options(joinedload(Project.members).joinedload(ProjectMember.user))
        .filter(Project.id == project.id)
        .one()
    )
    task_count = len(project_with_members.tasks)
    detail = ProjectDetail.model_validate(project_with_members)
    detail.task_count = task_count
    return detail


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(payload: ProjectUpdate, access=Depends(project_manager_dep), db: Session = Depends(get_db)):
    project, _ = access
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(access=Depends(project_owner_dep), db: Session = Depends(get_db)):
    project, _ = access
    project.is_active = False
    db.commit()


@router.get("/{project_id}/members", response_model=list[MemberInProject])
def list_members(access=Depends(project_member_dep), db: Session = Depends(get_db)):
    project, _ = access
    return (
        db.query(ProjectMember)
        .options(joinedload(ProjectMember.user))
        .filter_by(project_id=project.id)
        .all()
    )


@router.post("/{project_id}/members", response_model=MemberInProject, status_code=status.HTTP_201_CREATED)
def add_member(payload: AddMemberRequest, access=Depends(project_manager_dep), db: Session = Depends(get_db)):
    project, _ = access
    target_user = db.get(User, payload.user_id)
    if not target_user or not target_user.is_active:
        raise HTTPException(status_code=404, detail="Target user not found")
    existing = db.query(ProjectMember).filter_by(project_id=project.id, user_id=payload.user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member")
    membership = ProjectMember(project_id=project.id, user_id=payload.user_id, role=payload.role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.patch("/{project_id}/members/{user_id}", response_model=MemberInProject)
def update_member_role(user_id: int, payload: UpdateMemberRole, access=Depends(project_owner_dep), db: Session = Depends(get_db)):
    project, _ = access
    membership = db.query(ProjectMember).filter_by(project_id=project.id, user_id=user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    membership.role = payload.role
    db.commit()
    db.refresh(membership)
    return membership


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    user_id: int,
    current_user: User = Depends(get_current_user),
    access=Depends(project_owner_dep),
    db: Session = Depends(get_db),
):
    project, caller_membership = access
    if current_user.id != user_id and caller_membership.role not in (ProjectRole.OWNER,) and current_user.role != GlobalRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not allowed to remove other members")
    membership = db.query(ProjectMember).filter_by(project_id=project.id, user_id=user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    if membership.role == ProjectRole.OWNER:
        owners = db.query(ProjectMember).filter_by(project_id=project.id, role=ProjectRole.OWNER).count()
        if owners <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last owner")
    db.delete(membership)
    db.commit()
