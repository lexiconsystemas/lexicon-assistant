"""Database models for the productivity agent."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model representing Discord users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    checkins = relationship("Checkin", back_populates="user")
    productivity_scores = relationship("ProductivityScore", back_populates="user")


class Checkin(Base):
    """Checkin model storing user responses to productivity prompts."""
    
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checkin_type = Column(String, nullable=False)  # morning, midday, night
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="checkins")


class ProductivityScore(Base):
    """ProductivityScore model storing daily productivity evaluations."""
    
    __tablename__ = "productivity_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)  # 1-10
    recommended_action = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="productivity_scores")


class Memory(Base):
    """Memory model storing behavior summaries and patterns."""
    
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # missed_outreach, productive_day, blocker, behavior_pattern
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
