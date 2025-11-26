from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from api.v1.schemas import (
    AttachmentCreate,
    CommentCreate,
    NotificationCreate,
    NotificationReadUpdate,
    ProjectCreate,
    ProjectUpdate,
    SearchQuery,
    TagCreate,
    TagIds,
    TaskCreate,
    TaskUpdate,
    WorkspaceCreate,
    WorkspaceUpdate,
)
from core.database import get_db_manager
from services.management_service import ManagementService

router = APIRouter()


def get_management_service(db=Depends(get_db_manager)) -> ManagementService:
    return ManagementService(db)


@router.post("/workspaces", tags=["workspaces"])
async def create_workspace(payload: WorkspaceCreate, service: ManagementService = Depends(get_management_service)):
    workspace = await service.create_workspace(payload.model_dump())
    return {"status": "success", "data": workspace}


@router.get("/workspaces", tags=["workspaces"])
async def list_workspaces(service: ManagementService = Depends(get_management_service)):
    workspaces = await service.list_workspaces()
    return {"status": "success", "data": workspaces}


@router.get("/workspaces/{workspace_id}", tags=["workspaces"])
async def get_workspace(workspace_id: str, service: ManagementService = Depends(get_management_service)):
    workspace = await service.get_workspace(workspace_id)
    return {"status": "success", "data": workspace}


@router.put("/workspaces/{workspace_id}", tags=["workspaces"])
async def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdate,
    service: ManagementService = Depends(get_management_service),
):
    workspace = await service.update_workspace(workspace_id, payload.model_dump(exclude_none=True))
    return {"status": "success", "data": workspace}


@router.delete("/workspaces/{workspace_id}", tags=["workspaces"])
async def delete_workspace(workspace_id: str, service: ManagementService = Depends(get_management_service)):
    result = await service.delete_workspace(workspace_id)
    return {"status": "success", "data": result}


@router.post("/projects", tags=["projects"])
async def create_project(payload: ProjectCreate, service: ManagementService = Depends(get_management_service)):
    project = await service.create_project(payload.model_dump())
    return {"status": "success", "data": project}


@router.get("/projects", tags=["projects"])
async def list_projects(workspace_id: str | None = None, service: ManagementService = Depends(get_management_service)):
    projects = await service.list_projects(workspace_id)
    return {"status": "success", "data": projects}


@router.get("/projects/{project_id}", tags=["projects"])
async def get_project(project_id: str, service: ManagementService = Depends(get_management_service)):
    project = await service.get_project(project_id)
    return {"status": "success", "data": project}


@router.put("/projects/{project_id}", tags=["projects"])
async def update_project(
    project_id: str, payload: ProjectUpdate, service: ManagementService = Depends(get_management_service)
):
    project = await service.update_project(project_id, payload.model_dump(exclude_none=True))
    return {"status": "success", "data": project}


@router.delete("/projects/{project_id}", tags=["projects"])
async def delete_project(project_id: str, service: ManagementService = Depends(get_management_service)):
    result = await service.delete_project(project_id)
    return {"status": "success", "data": result}


@router.post("/tasks", tags=["tasks"])
async def create_task(payload: TaskCreate, service: ManagementService = Depends(get_management_service)):
    task = await service.create_task(payload.model_dump())
    return {"status": "success", "data": task}


@router.get("/tasks", tags=["tasks"])
async def list_tasks(
    workspace_id: str | None = None,
    status: str | None = None,
    assignee_id: str | None = None,
    service: ManagementService = Depends(get_management_service),
):
    tasks = await service.list_tasks(workspace_id=workspace_id, status=status, assignee_id=assignee_id)
    return {"status": "success", "data": tasks}


@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task(task_id: str, service: ManagementService = Depends(get_management_service)):
    task = await service.get_task(task_id)
    return {"status": "success", "data": task}


@router.put("/tasks/{task_id}", tags=["tasks"])
async def update_task(task_id: str, payload: TaskUpdate, service: ManagementService = Depends(get_management_service)):
    task = await service.update_task(task_id, payload.model_dump(exclude_none=True))
    return {"status": "success", "data": task}


@router.delete("/tasks/{task_id}", tags=["tasks"])
async def delete_task(task_id: str, service: ManagementService = Depends(get_management_service)):
    result = await service.delete_task(task_id)
    return {"status": "success", "data": result}


@router.post("/workspaces/{workspace_id}/tags", tags=["tags"])
async def create_tag(workspace_id: str, payload: TagCreate, service: ManagementService = Depends(get_management_service)):
    if workspace_id != payload.workspace_id:
        raise HTTPException(status_code=400, detail="Workspace ID mismatch")
    tag = await service.create_tag(payload.model_dump())
    return {"status": "success", "data": tag}


@router.get("/workspaces/{workspace_id}/tags", tags=["tags"])
async def list_tags(workspace_id: str, service: ManagementService = Depends(get_management_service)):
    tags = await service.list_tags(workspace_id)
    return {"status": "success", "data": tags}


@router.post("/tasks/{task_id}/tags", tags=["tags"])
async def attach_tags_to_task(task_id: str, payload: TagIds, service: ManagementService = Depends(get_management_service)):
    results: Dict[str, Dict] = {}
    for tag_id in payload.tag_ids:
        results[tag_id] = await service.attach_tag_to_task(task_id, tag_id)
    return {"status": "success", "data": list(results.values())}


@router.delete("/tasks/{task_id}/tags/{tag_id}", tags=["tags"])
async def detach_tag_from_task(task_id: str, tag_id: str, service: ManagementService = Depends(get_management_service)):
    result = await service.detach_tag_from_task(task_id, tag_id)
    return {"status": "success", "data": result}


@router.post("/comments", tags=["comments"])
async def add_comment(payload: CommentCreate, service: ManagementService = Depends(get_management_service)):
    comment = await service.add_comment(payload.model_dump())
    return {"status": "success", "data": comment}


@router.get("/comments", tags=["comments"])
async def list_comments(
    resource_type: str,
    resource_id: str,
    service: ManagementService = Depends(get_management_service),
):
    comments = await service.list_comments(resource_type, resource_id)
    return {"status": "success", "data": comments}


@router.post("/attachments", tags=["attachments"])
async def add_attachment(payload: AttachmentCreate, service: ManagementService = Depends(get_management_service)):
    attachment = await service.add_attachment(payload.model_dump())
    return {"status": "success", "data": attachment}


@router.get("/attachments", tags=["attachments"])
async def list_attachments(
    attached_to_type: str,
    attached_to_id: str,
    service: ManagementService = Depends(get_management_service),
):
    attachments = await service.list_attachments(attached_to_type, attached_to_id)
    return {"status": "success", "data": attachments}


@router.post("/notifications", tags=["notifications"])
async def create_notification(payload: NotificationCreate, service: ManagementService = Depends(get_management_service)):
    notification = await service.create_notification(payload.model_dump())
    return {"status": "success", "data": notification}


@router.get("/notifications", tags=["notifications"])
async def list_notifications(
    user_id: str,
    only_unread: bool = False,
    service: ManagementService = Depends(get_management_service),
):
    notifications = await service.list_notifications(user_id, only_unread)
    return {"status": "success", "data": notifications}


@router.patch("/notifications/{notification_id}", tags=["notifications"])
async def mark_notification(
    notification_id: str, payload: NotificationReadUpdate, service: ManagementService = Depends(get_management_service)
):
    if payload.is_read:
        notification = await service.mark_notification_read(notification_id)
    else:
        notification = await service.mark_notification_read(notification_id)
    return {"status": "success", "data": notification}


@router.post("/search", tags=["search"])
async def search(payload: SearchQuery, service: ManagementService = Depends(get_management_service)):
    results = await service.search(payload.query, payload.workspace_id)
    return {"status": "success", "data": results}
