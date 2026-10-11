"""Pydantic schemas for claim models."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.claim import ClaimStatus

class ClaimCreate(BaseModel):
    """Schema for creating a new claim."""

    item_id: int
    proof_description: str = Field(...,min_length=10,max_length=1000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": 5,
                "proof_description": (
                    "The backpack has my initials "
                    "'JD' sewn inside the back pocket."
                )
            }
        }
    )


class ClaimResponse(BaseModel):
    """Schema for claim response."""

    id: int
    item_id: int
    claimant_id: int
    proof_description: str
    status: ClaimStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ClaimUpdate(BaseModel):
    """Schema for updating claim status (admin only)."""

    status: ClaimStatus

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "APPROVED"
            }
        }
    )