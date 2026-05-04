from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas import DealCreate, DealUpdate, DealResponse, DealStageEnum, PipelineStageStats, DashboardStats
from app.models import Deal, Contact, Task, Lead

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("", response_model=List[DealResponse])
async def get_deals(
    skip: int = 0,
    limit: int = 100,
    stage: str = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Get all deals with optional stage filter."""
    query = select(Deal)
    
    if stage:
        try:
            stage_enum = DealStageEnum(stage)
            query = query.where(Deal.stage == stage_enum)
        except ValueError:
            pass
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    deals = result.scalars().all()
    
    return list(deals)


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get a specific deal by ID."""
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    return deal


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Create a new deal."""
    new_deal = Deal(
        title=deal_data.title,
        stage=deal_data.stage,
        value=deal_data.value,
        probability=deal_data.probability,
        expected_close_date=deal_data.expected_close_date,
        contact_id=deal_data.contact_id,
        owner_id=deal_data.owner_id or current_user["user_id"],
        notes=deal_data.notes
    )
    
    db.add(new_deal)
    await db.flush()
    await db.refresh(new_deal)
    
    return new_deal


@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    deal_update: DealUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Update an existing deal."""
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    update_data = deal_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(deal, field, value)
    
    await db.flush()
    await db.refresh(deal)
    
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Delete a deal."""
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    await db.delete(deal)
    await db.flush()
    
    return None


@router.get("/pipeline/stats", response_model=List[PipelineStageStats])
async def get_pipeline_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get pipeline statistics by stage."""
    query = select(
        Deal.stage,
        func.count(Deal.id).label("count"),
        func.sum(Deal.value).label("total_value"),
        func.sum(Deal.value * Deal.probability / 100).label("weighted_value")
    ).group_by(Deal.stage)
    
    result = await db.execute(query)
    rows = result.all()
    
    stats = []
    for row in rows:
        stats.append(PipelineStageStats(
            stage=row.stage,
            count=row.count or 0,
            total_value=float(row.total_value or 0),
            weighted_value=float(row.weighted_value or 0)
        ))
    
    return stats


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get dashboard statistics."""
    # Get counts
    contacts_count = await db.scalar(select(func.count(Contact.id)))
    leads_count = await db.scalar(select(func.count(Lead.id)))
    deals_count = await db.scalar(select(func.count(Deal.id)))
    tasks_count = await db.scalar(select(func.count(Task.id)))
    pending_tasks = await db.scalar(select(func.count(Task.id)).where(Task.status == "pending"))
    deals_won = await db.scalar(select(func.count(Deal.id)).where(Deal.stage == DealStageEnum.CLOSED_WON))
    deals_lost = await db.scalar(select(func.count(Deal.id)).where(Deal.stage == DealStageEnum.CLOSED_LOST))
    
    # Get revenue
    total_revenue_result = await db.execute(
        select(func.sum(Deal.value)).where(Deal.stage == DealStageEnum.CLOSED_WON)
    )
    total_revenue = float(total_revenue_result.scalar() or 0)
    
    # Get pipeline value
    pipeline_value_result = await db.execute(
        select(func.sum(Deal.value)).where(
            Deal.stage.not_in([DealStageEnum.CLOSED_WON, DealStageEnum.CLOSED_LOST])
        )
    )
    pipeline_value = float(pipeline_value_result.scalar() or 0)
    
    # Calculate conversion rate
    total_closed = deals_won + deals_lost
    conversion_rate = (deals_won / total_closed * 100) if total_closed > 0 else 0.0
    
    return DashboardStats(
        total_contacts=contacts_count or 0,
        total_leads=leads_count or 0,
        total_deals=deals_count or 0,
        total_tasks=tasks_count or 0,
        pending_tasks=pending_tasks or 0,
        deals_won=deals_won or 0,
        deals_lost=deals_lost or 0,
        total_revenue=total_revenue,
        pipeline_value=pipeline_value,
        conversion_rate=round(conversion_rate, 2)
    )
