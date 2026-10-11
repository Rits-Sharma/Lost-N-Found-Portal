"""Match model for caching NLP and rule-based match scores."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Match(Base):
    """Match model caching match scores between lost and found items."""

    __tablename__ = "matches"

    __table_args__ = (
        UniqueConstraint(
            "lost_item_id",
            "found_item_id",
            name="uq_lost_found_match"
        ),
    )

    id = Column(Integer,primary_key=True,index=True)
    lost_item_id = Column(Integer,ForeignKey("items.id"),nullable=False,index=True)
    found_item_id = Column(Integer,ForeignKey("items.id"),nullable=False,index=True)
    # Rule-based matching score: 0.0 to 1.0
    rule_score = Column(Float,nullable=False)
    # TF-IDF + Cosine Similarity score: 0.0 to 1.0
    nlp_score = Column(Float,nullable=False)
    # Combined matching score: 0.0 to 1.0
    total_score = Column(Float,nullable=False,index=True)
    calculated_at = Column(DateTime,default=datetime.utcnow,nullable=False)

    # Relationships
    lost_item = relationship("Item",foreign_keys=[lost_item_id],back_populates="lost_matches")
    found_item = relationship("Item",foreign_keys=[found_item_id],back_populates="found_matches")

    def __repr__(self):
        return (
            f"<Match("
            f"lost_id={self.lost_item_id}, "
            f"found_id={self.found_item_id}, "
            f"score={self.total_score:.2f}"
            f")>"
        )