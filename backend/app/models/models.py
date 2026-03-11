import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


def generate_uuid():
    return str(uuid.uuid4())


class InstanceStatus(str, enum.Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    instances = relationship("Instance", back_populates="owner", cascade="all, delete-orphan")
    apks = relationship("APK", back_populates="uploader", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class Instance(Base):
    __tablename__ = "instances"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(
        String(20),
        default=InstanceStatus.STOPPED.value,
        nullable=False,
    )
    container_name = Column(String(100), unique=True, nullable=False)
    adb_port = Column(Integer, unique=True, nullable=False)
    stream_port = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="instances")

    def __repr__(self):
        return f"<Instance {self.name} ({self.status})>"


class APK(Base):
    __tablename__ = "apks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    uploader = relationship("User", back_populates="apks")

    def __repr__(self):
        return f"<APK {self.name}>"
