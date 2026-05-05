"""
/dashboard  – aggregated stats for the authenticated user.
"""
 
from datetime import datetime, timezone
 
from fastapi import APIRouter, Depends
from sqlalchemy import func, nullslast
from sqlalchemy.orm import Session, joinedload
 
from app.api.v1.deps import get_current_user
from app.db.session import get_db

from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, Task, TaskStatus, User


from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, Task, TaskStatus, User

from app.models.models import GlobalRole, Project, ProjectMember, Task, TaskStatus, User
  
from app.schemas.schemas import DashboardResponse, MemberTaskCount, TaskResponse, TaskStatusCount
 
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
 
 
@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return summary stats scoped to the authenticated user.

    Admin/manager users are scoped to projects where they are OWNER or MANAGER.
    """
 
    now = datetime.now(timezone.utc)
    is_admin = current_user.role == GlobalRole.ADMIN
 
    # Base project queryset
    if is_admin:
        project_ids_q = (
            db.query(ProjectMember.project_id)
            .join(Project, Project.id == ProjectMember.project_id)
            .filter(
                ProjectMember.user_id == current_user.id,
                ProjectMember.role.in_([ProjectRole.OWNER, ProjectRole.MANAGER]),
                Project.is_active == True,
            )
        )
    else:
        project_ids_q = (
            db.query(ProjectMember.project_id)
            .join(Project, Project.id == ProjectMember.project_id)
            .filter(ProjectMember.user_id == current_user.id, Project.is_active == True)
        )
 
    project_ids = [r[0] for r in project_ids_q.all()]
 
    total_projects = len(project_ids)
 
    if not project_ids:
        return DashboardResponse(
            total_projects=0,
            total_tasks=0,
            overdue_tasks=0,
            tasks_by_status=[],
            my_assigned_tasks=[],
            member_task_counts=[],
codex/update-login-and-dashboard-behavior-hrr3vj
            managed_tasks=[],

            managed_tasks=[],
          
        )
 
    task_base_q = db.query(Task).filter(Task.project_id.in_(project_ids))
    if is_admin:
        # Manager dashboard should show only tasks allocated by this manager.
        task_base_q = task_base_q.filter(Task.creator_id == current_user.id)
 
    total_tasks: int = task_base_q.count()
 
    # Overdue: past due_date and not terminal
    overdue_tasks: int = task_base_q.filter(
        Task.due_date < now,
        Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED]),
    ).count()
 
    # Tasks by status
    status_rows = (
        task_base_q
        .with_entities(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )
    tasks_by_status = [TaskStatusCount(status=s, count=c) for s, c in status_rows]
 
    # My assigned tasks (across all my projects)
    # nullslast() is the SA-idiomatic function — works on 1.4+ and 2.x.
    my_tasks_q = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(
            Task.project_id.in_(project_ids),
            Task.assignee_id == current_user.id,
            Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED]),
        )
        .order_by(nullslast(Task.due_date.asc()))
        .limit(20)
    )
 
    member_task_counts: list[MemberTaskCount] = []
    if is_admin:
        member_rows = (
            db.query(User.id, User.full_name, func.count(Task.id))
            .join(Task, Task.assignee_id == User.id)

        
            .filter(
                Task.project_id.in_(project_ids),
                Task.creator_id == current_user.id,
            )

            .filter(Task.project_id.in_(project_ids))
          
            .group_by(User.id, User.full_name)
            .order_by(func.count(Task.id).desc())
            .all()
        )
        member_task_counts = [
            MemberTaskCount(user_id=user_id, full_name=full_name, task_count=count)
            for user_id, full_name, count in member_rows
        ]


     
    managed_tasks_q = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.project_id.in_(project_ids))
        .order_by(Task.updated_at.desc())
        .limit(30)
    )
    if is_admin:
        managed_tasks_q = managed_tasks_q.filter(Task.creator_id == current_user.id)


    return DashboardResponse(
        total_projects=total_projects,
        total_tasks=total_tasks,
        overdue_tasks=overdue_tasks,
        tasks_by_status=tasks_by_status,
        my_assigned_tasks=[TaskResponse.model_validate(t) for t in my_tasks_q.all()],
        member_task_counts=member_task_counts,

        managed_tasks=[TaskResponse.model_validate(t) for t in managed_tasks_q.all()],

      
        managed_tasks=[TaskResponse.model_validate(t) for t in managed_tasks_q.all()],
      
    )
 
