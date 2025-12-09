import uuid 
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Integer
from app.backend.db import Base
from sqlalchemy.orm import relationship

#datetime and zone
from datetime import datetime
from zoneinfo import ZoneInfo

# ENUM untuk predicted_y
PredictionEnum = Enum('yes', 'no', name='Prediction')


# Define timezone Jakarta
JAKARTA_TZ = ZoneInfo("Asia/Jakarta")  


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=False)
    createdAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ)  
    )
    updatedAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ), 
        onupdate=lambda: datetime.now(JAKARTA_TZ) 
    )
    # Relations
    campaigns = relationship("Campaign", back_populates="user", foreign_keys='Campaign.userId')


class Customer(Base):
    __tablename__ = "Customer"

    id = Column(String, primary_key=True, index=True) 
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    job = Column(String, nullable=True)
    marital = Column(String, nullable=True)
    education = Column(String, nullable=True)
    default = Column(String, nullable=True)
    balance = Column(Float, nullable=True)
    housing = Column(String, nullable=True)
    loan = Column(String, nullable=True)
    createdAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ)  
    )
    updatedAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ), 
        onupdate=lambda: datetime.now(JAKARTA_TZ) 
    )
   #Relations
    campaigns = relationship("Campaign", back_populates="customer", foreign_keys='Campaign.customerId')
    lead_scores = relationship("LeadScore", back_populates="customer")


class Campaign(Base):
    __tablename__ = "Campaign"

    id = Column(String, primary_key=True, index=True) 
    contact = Column(String, nullable=True)
    day_of_week = Column(String, nullable=True)
    month = Column(String, nullable=True)
    campaign = Column(Integer, nullable=True)
    previous = Column(Integer, nullable=True)
    pdays = Column(Integer, nullable=True)
    poutcome = Column(String, nullable=True)
    customerId = Column(String, ForeignKey("Customer.id"))  
    userId = Column(Integer, ForeignKey("User.id"))  
    createdAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ)  
    )
    updatedAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ), 
        onupdate=lambda: datetime.now(JAKARTA_TZ) 
    )

    # Relations
    customer = relationship("Customer", back_populates="campaigns", foreign_keys=[customerId])
    user = relationship("User", back_populates="campaigns", foreign_keys=[userId])
    lead_scores = relationship("LeadScore", back_populates="campaign")


class MacroData(Base):
    __tablename__ = "MacroData"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=True)
    emp_var_rate = Column(Float, nullable=True)
    cons_price_idx = Column(Float, nullable=True)
    cons_conf_idx = Column(Float, nullable=True)
    euribor3m = Column(Float, nullable=True)
    nr_employed = Column(Float, nullable=True)
    createdAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ)  
    )
    updatedAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ), 
        onupdate=lambda: datetime.now(JAKARTA_TZ) 
    )

class LeadScore(Base):
    __tablename__ = "LeadScore"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Relations
    customerId = Column(String, ForeignKey("Customer.id"), nullable=False)
    campaignId = Column(String, ForeignKey("Campaign.id"), nullable=False)

    # Prediction result
    predicted_y = Column(String)  
    score = Column(Float)          
    threshold = Column(Float)      

    # Model Info
    model_version = Column(String) 
    batch_id = Column(String, index=True)  # 1x per batch run

    # Timestamp
    createdAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ)  
    )
    updatedAt = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(JAKARTA_TZ), 
        onupdate=lambda: datetime.now(JAKARTA_TZ) 
    )
    #  ORM relations
    customer = relationship("Customer", back_populates="lead_scores")
    campaign = relationship("Campaign", back_populates="lead_scores")