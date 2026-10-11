"""Item model for lost and found items."""

from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.database import Base


class ItemType(str, enum.Enum):
    """Type of item (lost or found)."""
    LOST = "LOST"
    FOUND = "FOUND"


class ItemCategory(str, enum.Enum):
    """Category of item."""
    ID_CARDS = "ID Cards"
    ELECTRONICS = "Electronics"
    BOOKS = "Books"
    WALLETS_KEYS = "Wallets/Keys"
    CLOTHING = "Clothing"
    OTHER = "Other"


class ItemStatus(str, enum.Enum):
    """Status of item in the lifecycle."""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    CLAIMED = "CLAIMED"
    RETURNED = "RETURNED"
    CLOSED = "CLOSED"


class Item(Base):
    """Item model representing lost and found items."""
    __tablename__ = "items"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(255),nullable=False,index=True)
    description = Column(String(2000),nullable=False)
    type = Column(SQLEnum(ItemType),nullable=False,index=True)
    category = Column(SQLEnum(ItemCategory),nullable=False,index=True)
    location = Column(String(255),nullable=False,index=True)
    brand = Column(String(255),nullable=True)
    color = Column(String(100),nullable=True)
    date_event = Column(Date,nullable=False)
    image_url = Column(String(500),nullable=True)
    status = Column(SQLEnum(ItemStatus),default=ItemStatus.PENDING,nullable=False,index=True)
    reporter_id = Column(Integer,ForeignKey("users.id"),nullable=True,index=True)
    reporter_contact = Column(String(255),nullable=True)  # For guest finders
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False,index=True)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # Relationships

    reporter = relationship("User",back_populates="items",foreign_keys=[reporter_id])

    claims = relationship("Claim",back_populates="item",cascade="all, delete-orphan")

    lost_matches = relationship("Match",foreign_keys="Match.lost_item_id",back_populates="lost_item",cascade="all, delete-orphan")

    found_matches = relationship("Match",foreign_keys="Match.found_item_id",back_populates="found_item",cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Item("
            f"id={self.id}, "
            f"title={self.title}, "
            f"type={self.type}, "
            f"status={self.status}"
            f")>"
        )