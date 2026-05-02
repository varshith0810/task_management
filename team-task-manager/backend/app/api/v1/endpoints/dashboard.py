"""
/dashboard  – aggregated stats for the authenticated user.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.models import GlobalRole, Project, ProjectMember, Task, TaskStatus, User
from app.schemas.schemas import DashboardResponse, TaskResponse, TaskStatusCount

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return summary stats scoped to the authenticated user (admin sees global stats)."""

    now = datetime.now(timezone.utc)
    is_admin = current_user.role == GlobalRole.ADMIN

    # Base project queryset
    if is_admin:
        project_ids_q = db.query(Project.id).filter(Project.is_active == True)
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
        )

    task_base_q = db.query(Task).filter(Task.project_id.in_(project_ids))

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
    my_tasks_q = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(
            Task.project_id.in_(project_ids),
            Task.assignee_id == current_user.id,
            Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED]),
        )
        .order_by(Task.due_date.asc().nulls_last())
        .limit(20)
    )

    return DashboardResponse(
        total_projects=total_projects,
        total_tasks=total_tasks,
        overdue_tasks=overdue_tasks,
        tasks_by_status=tasks_by_status,
        my_assigned_tasks=[TaskResponse.model_validate(t) for t in my_tasks_q.all()],
    )
