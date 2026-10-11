"""Claim model for item ownership claims."""

from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ClaimStatus(str, enum.Enum):
    """Status of a claim."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Claim(Base):
    """Claim model representing ownership claims for items."""
    __tablename__ = "claims"
    id = Column(Integer,primary_key=True,index=True)
    item_id = Column(Integer,ForeignKey("items.id"),nullable=False,index=True)
    claimant_id = Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    proof_description = Column(String(1000),nullable=False)
    status = Column(SQLEnum(ClaimStatus),default=ClaimStatus.PENDING,nullable=False,index=True)
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # Relationships
    item = relationship("Item",back_populates="claims")
    claimant = relationship("User",back_populates="claims")

    def __repr__(self):
        return (
            f"<Claim("
            f"id={self.id}, "
            f"item_id={self.item_id}, "
            f"status={self.status}"
            f")>"
        )