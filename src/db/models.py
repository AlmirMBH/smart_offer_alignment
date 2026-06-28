from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    component = Column(String, nullable=False, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    offer_items = relationship("OfferItem", back_populates="offer")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    component = Column(String, nullable=False, index=True)
    embed_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)

    offer_items = relationship("OfferItem", back_populates="item")


class OfferItem(Base):
    __tablename__ = "offer_items"

    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    source_sheet = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    approved = Column(Boolean, nullable=False, default=False)
    auto_approved = Column(Boolean, nullable=False, default=False)

    offer = relationship("Offer", back_populates="offer_items")
    item = relationship("Item", back_populates="offer_items")


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
