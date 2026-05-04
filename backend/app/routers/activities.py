from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas import ActivityCreate, ActivityUpdate, ActivityResponse
from app.models import Activity

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=List[ActivityResponse])
async def get_activities(
    skip: int = 0,
    limit: int = 100,
    contact_id: int = None,
    lead_id: int = None,
    deal_id: int = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Get all activities with optional filters."""
    query = select(Activity)
    
    if contact_id:
        query = query.where(Activity.contact_id == contact_id)
    if lead_id:
        query = query.where(Activity.lead_id == lead_id)
    if deal_id:
        query = query.where(Activity.deal_id == deal_id)
    
    query = query.order_by(Activity.created_at.desc())
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return list(activities)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get a specific activity by ID."""
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    return activity


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Create a new activity."""
    import json
    
    metadata_json = None
    if activity_data.metadata:
        metadata_json = json.dumps(activity_data.metadata)
    
    new_activity = Activity(
        activity_type=activity_data.activity_type,
        subject=activity_data.subject,
        description=activity_data.description,
        scheduled_at=activity_data.scheduled_at,
        user_id=current_user["user_id"],
        contact_id=activity_data.contact_id,
        lead_id=activity_data.lead_id,
        deal_id=activity_data.deal_id,
        task_id=activity_data.task_id,
        metadata=metadata_json
    )
    
    db.add(new_activity)
    await db.flush()
    await db.refresh(new_activity)
    
    return new_activity


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Update an existing activity."""
    import json
    
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    update_data = activity_update.model_dump(exclude_unset=True)
    
    if "metadata" in update_data and update_data["metadata"] is not None:
        update_data["metadata"] = json.dumps(update_data["metadata"])
    
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    await db.flush()
    await db.refresh(activity)
    
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Delete an activity."""
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    await db.delete(activity)
    await db.flush()
    
    return None
