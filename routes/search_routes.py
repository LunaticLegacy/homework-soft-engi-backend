from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.search_service import SearchService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


router = APIRouter(prefix="/search", tags=["search"])


def get_search_service(db: DatabaseManager = Depends(get_db_manager)) -> SearchService:
    return SearchService(db)


from pydantic import BaseModel


class SearchRequest(BaseModel):
    workspace_id: str
    q: str


@router.post("/", response_model=Dict[str, Any])
async def search(request: SearchRequest, svc: SearchService = Depends(get_search_service)):
    try:
        data = await svc.search(request.workspace_id, request.q)
        return {"status": "success", "data": data}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
