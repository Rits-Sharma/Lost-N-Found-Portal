"""Pydantic schemas for match models."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.item import ItemResponse


class MatchResponse(BaseModel):
    id: int
    lost_item_id: int
    found_item_id: int
    rule_score: float = Field(..., ge=0.0, le=1.0)
    nlp_score: float = Field(..., ge=0.0, le=1.0)
    total_score: float = Field(..., ge=0.0, le=1.0)
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchWithItemResponse(BaseModel):
    matched_item: ItemResponse
    rule_score: float = Field(..., ge=0.0, le=1.0)
    nlp_score: float = Field(..., ge=0.0, le=1.0)
    total_score: float = Field(..., ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)