from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_segment: Mapped[str] = mapped_column(String)
    region: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    cases = relationship("Case", back_populates="customer")

class Agent(Base):
    __tablename__ = "agents"
    agent_id: Mapped[str] = mapped_column(String, primary_key=True)
    team: Mapped[str] = mapped_column(String)
    experience_band: Mapped[str] = mapped_column(String)

class Case(Base):
    __tablename__ = "cases"
    case_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id"))
    industry: Mapped[str] = mapped_column(String)
    channel: Mapped[str] = mapped_column(String)
    issue_category: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    first_response_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String)
    escalation_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    current_owner: Mapped[str] = mapped_column(String)
    customer = relationship("Customer", back_populates="cases")
    interactions = relationship("Interaction", back_populates="case", cascade="all, delete-orphan")
    promises = relationship("Promise", back_populates="case", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="case", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="case", uselist=False, cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = "interactions"
    interaction_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.case_id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    interaction_type: Mapped[str] = mapped_column(String)
    actor_type: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    sentiment_ground_truth: Mapped[str] = mapped_column(String)
    sentiment_score: Mapped[float] = mapped_column(Float)
    meaningful_update_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    transfer_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    repeat_explanation_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    case = relationship("Case", back_populates="interactions")

class Promise(Base):
    __tablename__ = "promises"
    promise_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.case_id"))
    promise_created_at: Mapped[datetime] = mapped_column(DateTime)
    promised_update_at: Mapped[datetime] = mapped_column(DateTime)
    actual_update_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    promise_met: Mapped[bool] = mapped_column(Boolean)
    case = relationship("Case", back_populates="promises")

class Intervention(Base):
    __tablename__ = "interventions"
    intervention_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.case_id"))
    intervention_type: Mapped[str] = mapped_column(String)
    intervention_at: Mapped[datetime] = mapped_column(DateTime)
    reason: Mapped[str] = mapped_column(String)
    accepted_flag: Mapped[bool] = mapped_column(Boolean)
    case = relationship("Case", back_populates="interventions")

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.case_id"), unique=True)
    csat_score: Mapped[int] = mapped_column(Integer)
    dsat_flag: Mapped[bool] = mapped_column(Boolean)
    recommendation_score: Mapped[int] = mapped_column(Integer)
    final_sentiment: Mapped[str] = mapped_column(String)
    repeat_contact_flag: Mapped[bool] = mapped_column(Boolean)
    case = relationship("Case", back_populates="feedback")

class Event(Base):
    __tablename__ = "events"
    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.case_id"))
    event_type: Mapped[str] = mapped_column(String)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime)
    actor_type: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
