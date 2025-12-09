from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional, Any
from dataclasses import dataclass
from modules.databaseman import DatabaseManager
from modules.redisman import RedisManager
from core.database import get_db_manager
from core.redis_cache import get_redis_manager
from services.user_service import UserService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from passlib.context import CryptContext
import jwt
from hashlib import sha256
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
import os
from routes.models.user_models import (
    BaseRequest,
    UserRegisterRequest,
    UserLoginRequest,
    UserLogoutRequest,
    UserProfileUpdateRequest,
    UserDeleteRequest,
    BaseResponse,
    RegisterResponse,
    LoginResponse,
    LogoutResponse,
    UserProfileResponse,
    UserUpdateResponse,
    UserDeleteResponse
)

JWT_SECRET = os.getenv("JWT_SECRET", "secret_key")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(prefix="/user", tags=["users"])


def get_user_service(db_manager: DatabaseManager = Depends(get_db_manager)) -> UserService:
    return UserService(db_manager)


@router.post("/register/", response_model=RegisterResponse)
async def register_user(
    request: UserRegisterRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        now: datetime = datetime.now(UTC)
        if request.token is not None:
            return {"status": "error", "user_id": None, "message": "Token must be null for registration", "time": str(now)}

        existing_user = await service.get_user_by_email(request.email)
        if existing_user:
            return {"status": "error", "user_id": None, "message": "Email already registered", "time": str(now)}

        password_hashed = pwd_context.hash(request.password)
        # password_salt 可置空（hash 内含盐）
        user = await service.create_user(request.email, request.username, password_hashed)

        return {"status": "success", "user_id": str(user["id"]), "message": "注册成功", "time": str(now)}
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/", response_model=LoginResponse)
async def login_user(
    request: UserLoginRequest,
    service: UserService = Depends(get_user_service),
    redisman: RedisManager = Depends(get_redis_manager)
):
    try:
        now: datetime = datetime.now(UTC)
        if request.token is not None:
            return {"status": "error", "message": "Token must be null for login", "time": str(now)}

        user = await service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        stored_hash: str = user["password_hash"]
        if not pwd_context.verify(request.password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        id_string: str = str(user["id"])
        now: datetime = datetime.now(UTC)
        payload = {
            "user_id": id_string,
            "exp": int((now + timedelta(hours=168)).timestamp()),
            "iat": int(now.timestamp())
        }
        # 这个token算法很容易直接暴露原始信息，需要给SHA256后结果作为key。
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        token_hash = sha256(token.encode()).hexdigest()     

        await redisman.set(key=token_hash, value=payload, expire=86400 * 7, serialize="json")

        return {"status": "success", "user_id": id_string, "token": token_hash, "message": "登录成功", "time": str(now)}
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout/", response_model=LogoutResponse)
async def logout_user(
    request: UserLogoutRequest,
    redisman: RedisManager = Depends(get_redis_manager)
):
    if request.token:
        token: str = request.token
        existence: Optional[Any] = await redisman.get(token)
        if existence:
            await redisman.delete(token)
        return {"status": "success", "message": "登出成功"}


@router.post("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    request: BaseRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "data": user}
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile/{user_id}", response_model=UserUpdateResponse)
async def update_user_profile(
    user_id: str,
    request: UserProfileUpdateRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        updated_user = await service.update_user_profile(
            user_id,
            request.full_name,
            request.display_name
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "data": updated_user, "message": "用户信息更新成功"}
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/profile/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
    user_id: str,
    request: UserDeleteRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        result = await service.delete_user(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "message": "用户删除成功"}
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
