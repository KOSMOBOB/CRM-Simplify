from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas import LeadCreate, LeadUpdate, LeadResponse, LeadStatusEnum
from app.models import Lead

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Get all leads."""
    query = select(Lead)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    leads = result.scalars().all()
    
    return list(leads)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get a specific lead by ID."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Create a new lead."""
    new_lead = Lead(
        source=lead_data.source or "manual",
        status=lead_data.status,
        score=lead_data.score,
        first_name=lead_data.first_name,
        last_name=lead_data.last_name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        notes=lead_data.notes,
        assigned_to_id=lead_data.assigned_to_id
    )
    
    db.add(new_lead)
    await db.flush()
    await db.refresh(new_lead)
    
    return new_lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Update an existing lead."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    update_data = lead_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    await db.flush()
    await db.refresh(lead)
    
    return lead


@router.post("/{lead_id}/convert", response_model=LeadResponse)
async def convert_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Convert a lead to a contact."""
    from app.models import Contact
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Create contact from lead
    contact = Contact(
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        owner_id=current_user["user_id"]
    )
    
    db.add(contact)
    await db.flush()
    
    # Update lead with contact reference and mark as qualified
    lead.contact_id = contact.id
    lead.status = LeadStatusEnum.QUALIFIED
    
    await db.flush()
    await db.refresh(lead)
    
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Delete a lead."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    await db.delete(lead)
    await db.flush()
    
    return None
