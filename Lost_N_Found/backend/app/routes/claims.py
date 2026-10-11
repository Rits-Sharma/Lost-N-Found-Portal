"""Claims API routes for item ownership verification."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (HTTPAuthorizationCredentials,HTTPBearer,)
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.claim import Claim, ClaimStatus
from app.models.item import Item, ItemStatus, ItemType
from app.models.user import User, UserRole
from app.schemas.claim import ClaimCreate, ClaimResponse, ClaimUpdate

from app.services.auth import decode_token


router = APIRouter(prefix="/api/claims", tags=["claims"])

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),db: Session = Depends(get_db)) -> User:
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


@router.post("",response_model=ClaimResponse,status_code=status.HTTP_201_CREATED)
def create_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a claim for a verified found item."""

    # Find item
    item = (
        db.query(Item)
        .filter(Item.id == claim_data.item_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Only found items can be claimed
    if item.type != ItemType.FOUND:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only found items can be claimed"
        )

    # Item must be verified before claiming
    if item.status != ItemStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only verified items can be claimed"
        )

    # Check whether this user already has a claim
    existing_claim = (
        db.query(Claim)
        .filter(
            Claim.item_id == claim_data.item_id,
            Claim.claimant_id == current_user.id
        )
        .first()
    )

    if existing_claim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a claim for this item"
        )

    # Create claim
    new_claim = Claim(
        item_id=claim_data.item_id,
        claimant_id=current_user.id,
        proof_description=claim_data.proof_description,
        status=ClaimStatus.PENDING
    )

    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)

    return new_claim


@router.get("/item/{item_id}",response_model=List[ClaimResponse])
def get_item_claims(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get claims for an item.

    Only the item's reporter or an admin can view claims.
    """

    # Find item
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

    # Check authorization
    is_reporter = item.reporter_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not is_reporter and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view claims for this item"
        )

    # Get claims
    claims = (
        db.query(Claim)
        .filter(Claim.item_id == item_id)
        .order_by(Claim.created_at.desc())
        .all()
    )

    return claims


@router.patch("/{claim_id}", response_model=ClaimResponse)
def update_claim_status(
    claim_id: int,
    claim_update: ClaimUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject a claim.

    Only administrators can update claim status.
    """

    # Admin check
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update claim status"
        )

    # Find claim
    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    # Prevent changing an already processed claim
    if claim.status != ClaimStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending claims can be updated"
        )

    # Update claim status
    claim.status = claim_update.status

    # If claim is approved
    if claim_update.status == ClaimStatus.APPROVED:

        item = claim.item

        # Make sure item is still available
        if item.status != ItemStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This item is no longer available for claiming"
            )

        # Mark item as claimed
        item.status = ItemStatus.CLAIMED

        # Reject other pending claims for same item
        (
            db.query(Claim)
            .filter(
                Claim.item_id == item.id,
                Claim.id != claim.id,
                Claim.status == ClaimStatus.PENDING
            )
            .update(
                {
                    Claim.status: ClaimStatus.REJECTED
                },
                synchronize_session=False
            )
        )

    db.commit()
    db.refresh(claim)

    return claim


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific claim."""

    claim = (
        db.query(Claim)
        .filter(Claim.id == claim_id)
        .first()
    )

    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )

    # Claimant, item reporter, or admin can view the claim
    is_claimant = claim.claimant_id == current_user.id
    is_reporter = claim.item.reporter_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_claimant or is_reporter or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this claim"
        )

    return claim