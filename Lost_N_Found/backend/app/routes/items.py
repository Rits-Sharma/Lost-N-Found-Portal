"""Items API routes for lost and found items."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item, ItemStatus, ItemType
from app.models.user import User, UserRole
from app.models.match import Match

from app.schemas.item import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)

from app.schemas.match import MatchWithItemResponse

from app.services.auth import decode_token


router = APIRouter(prefix="/api/items",tags=["items"])

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the currently authenticated user."""

    token = credentials.credentials

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return user


@router.get("",response_model=List[ItemResponse])
def get_items(
    db: Session = Depends(get_db),
    type: Optional[ItemType] = Query(None),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status_filter: Optional[ItemStatus] = Query(None,alias="status"),
    search_query: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get items with optional filtering."""

    query = db.query(Item)

    if type:
        query = query.filter(Item.type == type)
    if category:
        query = query.filter(Item.category == category)
    if location:
        query = query.filter(Item.location.ilike(f"%{location}%"))

    if status_filter:
        query = query.filter(Item.status == status_filter)

    if search_query:
        query = query.filter((Item.title.ilike(f"%{search_query}%")) | 
                             (Item.description.ilike(f"%{search_query}%")))

    items = (
        query
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items


@router.get("/{item_id}",response_model=ItemResponse)
def get_item(item_id: int,db: Session = Depends(get_db)):
    """Get a specific item by ID."""

    item = (
        db.query(Item)
        .filter(Item.id == item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    return item


@router.post("/lost", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def report_lost_item(item_data: ItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Report a lost item."""

    new_item = Item(
        title=item_data.title,
        description=item_data.description,
        type=ItemType.LOST,
        category=item_data.category,
        location=item_data.location,
        brand=item_data.brand,
        color=item_data.color,
        date_event=item_data.date_event,
        image_url=item_data.image_url,
        status=ItemStatus.PENDING,
        reporter_id=current_user.id,
        reporter_contact=item_data.reporter_contact
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.post("/found", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def report_found_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """Report a found item.

    Registration/login is not required.
    """

    new_item = Item(
        title=item_data.title,
        description=item_data.description,
        type=ItemType.FOUND,
        category=item_data.category,
        location=item_data.location,
        brand=item_data.brand,
        color=item_data.color,
        date_event=item_data.date_event,
        image_url=item_data.image_url,
        status=ItemStatus.PENDING,
        reporter_contact=item_data.reporter_contact
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.get("/{item_id}/matches",response_model=List[MatchWithItemResponse])
def get_item_matches(item_id: int, db: Session = Depends(get_db)):
    """Get possible matches for an item."""

    item = (
        db.query(Item)
        .filter(Item.id == item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    if item.type == ItemType.LOST:

        match_records = (
            db.query(Match)
            .filter(
                Match.lost_item_id == item_id
            )
            .order_by(
                Match.total_score.desc()
            )
            .all()
        )

    else:

        match_records = (
            db.query(Match)
            .filter(
                Match.found_item_id == item_id
            )
            .order_by(
                Match.total_score.desc()
            )
            .all()
        )

    matches_response = []

    for match_record in match_records:

        if item.type == ItemType.LOST:
            matched_item = match_record.found_item
        else:
            matched_item = match_record.lost_item

        matches_response.append(
            MatchWithItemResponse(
                matched_item=matched_item,
                rule_score=match_record.rule_score,
                nlp_score=match_record.nlp_score,
                total_score=match_record.total_score
            )
        )

    return matches_response


@router.patch("/{item_id}",response_model=ItemResponse)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an item (owner or admin only)."""
    item = db.query(Item).filter(Item.id == item_id).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    is_owner = (item.reporter_id == current_user.id)
    is_admin = (current_user.role == UserRole.ADMIN)

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    # Update normal item fields
    if item_update.title is not None:
        item.title = item_update.title

    if item_update.description is not None:
        item.description = item_update.description

    if item_update.location is not None:
        item.location = item_update.location

    if item_update.brand is not None:
        item.brand = item_update.brand

    if item_update.color is not None:
        item.color = item_update.color

    # Only admins can change status
    if item_update.status is not None:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change item status"
            )

        item.status = item_update.status

    db.commit()
    db.refresh(item)

    return item