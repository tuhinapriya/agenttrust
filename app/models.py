from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    external_subject = Column(String(255), unique=True, nullable=False)
    issuer = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    disabled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ToolGrant(Base):
    __tablename__ = "tool_grants"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    tool_name = Column(String(255), nullable=False)
    scope = Column(String(255), nullable=True)
    granted_by_admin_id = Column(Integer, nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")
    revoked_at = Column(DateTime, nullable=True)


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    requested_tool = Column(String(255), nullable=False)
    requested_scope = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    outcome = Column(String(50), nullable=False)
    reason_code = Column(String(100), nullable=True)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
