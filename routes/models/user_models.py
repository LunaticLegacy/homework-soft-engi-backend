from typing import Dict, Optional, Any
from pydantic import BaseModel
from dataclasses import dataclass

from .base_models import BaseRequest, BaseResponse


@dataclass
class UserRegisterRequest(BaseRequest):
    username: str
    password: str
    email: str


@dataclass
class UserLoginRequest(BaseRequest):
    time: str
    email: str
    password: str


@dataclass
class UserLogoutRequest(BaseRequest):
    pass


@dataclass
class UserProfileUpdateRequest(BaseRequest):
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None


@dataclass
class UserDeleteRequest(BaseRequest):
    pass


@dataclass
class RegisterResponse(BaseResponse):
    status: str
    user_id: Optional[str] = None
    message: str


@dataclass
class LoginResponse(BaseModel):
    status: str
    user_id: str
    token: str
    message: str


@dataclass
class LogoutResponse(BaseModel):
    status: str
    message: str


@dataclass
class UserProfileResponse(BaseModel):
    status: str
    data: Dict[str, Any]


@dataclass
class UserUpdateResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str


@dataclass
class UserDeleteResponse(BaseModel):
    status: str
    message: str