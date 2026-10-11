"""User model for authentication and user profiles."""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class User(Base):
    """User model representing registered students and admins."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    items = relationship("Item", back_populates="reporter", foreign_keys="Item.reporter_id")
    claims = relationship("Claim", back_populates="claimant")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
