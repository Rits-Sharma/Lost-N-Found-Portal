"""Pydantic schemas for item models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.item import ItemType, ItemCategory, ItemStatus


class ItemCreate(BaseModel):
    """Schema for creating a new item (lost or found)."""

    title: str = Field(...,min_length=1,max_length=255)
    description: str = Field(...,min_length=10,max_length=2000)
    type: ItemType
    category: ItemCategory
    location: str = Field(...,min_length=1,max_length=255)
    brand: Optional[str] = Field(default=None,max_length=255)
    color: Optional[str] = Field(default=None,max_length=100)
    date_event: date
    image_url: Optional[str] = Field(default=None,max_length=500)
    reporter_contact: Optional[str] = Field(default=None,max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Blue Backpack",
                "description": "Lost blue backpack with laptop",
                "type": "LOST",
                "category": "Other",
                "location": "Library 3rd Floor",
                "brand": "Nike",
                "color": "Blue",
                "date_event": "2026-09-20",
                "image_url": "https://example.com/image.jpg",
                "reporter_contact": "user@college.edu"
            }
        }
    )


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    title: Optional[str] = Field(default=None,min_length=1,max_length=255)
    description: Optional[str] = Field(default=None,min_length=10,max_length=2000)
    location: Optional[str] = Field(default=None,min_length=1,max_length=255)
    brand: Optional[str] = Field(default=None,max_length=255)
    color: Optional[str] = Field(default=None,max_length=100)
    status: Optional[ItemStatus] = None


class ItemResponse(BaseModel):
    """Schema for item response."""

    id: int
    title: str
    description: str
    type: ItemType
    category: ItemCategory
    location: str
    brand: Optional[str]
    color: Optional[str]
    date_event: date
    image_url: Optional[str]
    status: ItemStatus
    reporter_id: Optional[int]
    reporter_contact: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )