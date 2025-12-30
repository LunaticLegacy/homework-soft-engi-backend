from fastapi import APIRouter, Depends

from api.v1.schemas import (
    ProjectCreate,
    ProjectUpdate,
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


