from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class LeadStatusEnum(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    WON = "won"
    LOST = "lost"


class DealStageEnum(str, Enum):
    NEW = "new"
    CONTACT_MADE = "contact_made"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActivityTypeEnum(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"
    SYSTEM = "system"


# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Contact Schemas
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict[str, Any]] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict[str, Any]] = None


class ContactResponse(ContactBase):
    id: int
    owner_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Lead Schemas
class LeadBase(BaseModel):
    source: Optional[str] = None
    status: LeadStatusEnum = LeadStatusEnum.NEW
    score: int = 0
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    assigned_to_id: Optional[int] = None


class LeadUpdate(BaseModel):
    source: Optional[str] = None
    status: Optional[LeadStatusEnum] = None
    score: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    contact_id: Optional[int] = None
    assigned_to_id: Optional[int] = None


class LeadResponse(LeadBase):
    id: int
    contact_id: Optional[int]
    assigned_to_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Deal Schemas
class DealBase(BaseModel):
    title: str
    stage: DealStageEnum = DealStageEnum.NEW
    value: float = 0
    probability: int = Field(default=10, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    notes: Optional[str] = None


class DealCreate(DealBase):
    contact_id: int
    owner_id: Optional[int] = None


class DealUpdate(BaseModel):
    title: Optional[str] = None
    stage: Optional[DealStageEnum] = None
    value: Optional[float] = None
    probability: Optional[int] = Field(default=None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    contact_id: Optional[int] = None
    owner_id: Optional[int] = None
    notes: Optional[str] = None


class DealResponse(DealBase):
    id: int
    contact_id: int
    owner_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    status: str = "pending"
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    deal_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriorityEnum] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deal_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    deal_id: Optional[int]
    assignee_id: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Activity Schemas
class ActivityBase(BaseModel):
    activity_type: ActivityTypeEnum
    subject: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


class ActivityCreate(ActivityBase):
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    task_id: Optional[int] = None


class ActivityUpdate(BaseModel):
    activity_type: Optional[ActivityTypeEnum] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


class ActivityResponse(ActivityBase):
    id: int
    user_id: Optional[int]
    contact_id: Optional[int]
    lead_id: Optional[int]
    deal_id: Optional[int]
    task_id: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Pipeline/Analytics Schemas
class PipelineStageStats(BaseModel):
    stage: DealStageEnum
    count: int
    total_value: float
    weighted_value: float


class DashboardStats(BaseModel):
    total_contacts: int
    total_leads: int
    total_deals: int
    total_tasks: int
    pending_tasks: int
    deals_won: int
    deals_lost: int
    total_revenue: float
    pipeline_value: float
    conversion_rate: float
