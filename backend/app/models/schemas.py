from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ──────────────────────────── Auth ────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ──────────────────────────── Instance ────────────────────────────

class InstanceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class InstanceResponse(BaseModel):
    id: str
    user_id: str
    name: str
    status: str
    container_name: str
    adb_port: int
    stream_port: int
    created_at: datetime

    class Config:
        from_attributes = True


class InstanceListResponse(BaseModel):
    instances: list[InstanceResponse]
    total: int


# ──────────────────────────── APK ────────────────────────────

class APKResponse(BaseModel):
    id: str
    name: str
    file_path: str
    uploaded_by: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class APKListResponse(BaseModel):
    apks: list[APKResponse]
    total: int


# ──────────────────────────── Streaming ────────────────────────────

class TouchEvent(BaseModel):
    x: float
    y: float
    action: str = "tap"  # tap, swipe_start, swipe_end


# ──────────────────────────── System ────────────────────────────

class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_total_gb: float
    memory_available_gb: float
    active_instances: int
    max_instances: int
