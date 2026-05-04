from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas import ContactCreate, ContactUpdate, ContactResponse
from app.models import Contact

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    search: str = Query(default=""),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Get all contacts with optional search."""
    query = select(Contact)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Contact.first_name.ilike(search_filter)) |
            (Contact.last_name.ilike(search_filter)) |
            (Contact.email.ilike(search_filter)) |
            (Contact.company.ilike(search_filter))
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    return list(contacts)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get a specific contact by ID."""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    return contact


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Create a new contact."""
    import json
    
    custom_fields_json = None
    if contact_data.custom_fields:
        custom_fields_json = json.dumps(contact_data.custom_fields)
    
    new_contact = Contact(
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        email=contact_data.email,
        phone=contact_data.phone,
        company=contact_data.company,
        position=contact_data.position,
        address=contact_data.address,
        city=contact_data.city,
        country=contact_data.country,
        notes=contact_data.notes,
        custom_fields=custom_fields_json,
        owner_id=current_user["user_id"]
    )
    
    db.add(new_contact)
    await db.flush()
    await db.refresh(new_contact)
    
    return new_contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Update an existing contact."""
    import json
    
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    update_data = contact_update.model_dump(exclude_unset=True)
    
    if "custom_fields" in update_data and update_data["custom_fields"] is not None:
        update_data["custom_fields"] = json.dumps(update_data["custom_fields"])
    
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.flush()
    await db.refresh(contact)
    
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Delete a contact."""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    await db.delete(contact)
    await db.flush()
    
    return None
