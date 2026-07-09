from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
import random
from typing import List


class Account(SQLModel, table=True):
    __tablename__ = 'account'
    id: str | None = Field(default_factory=lambda: f"ACC-{random.randint(100000, 999999)}", primary_key=True)
    email: str
    first_name: str
    last_name: str
    password: str
    phone: str
    created_at: datetime | None = Field(default_factory=datetime.now)


class Product(SQLModel, table=True):
    __tablename__ = 'product'
    id: str | None = Field(default_factory=lambda: f"PROD-{random.randint(100000, 999999)}", primary_key=True)
    name: str
    description: str
    price: float
    stock: int | None


class Order(SQLModel, table=True):
    __tablename__ = 'order'
    id: str | None = Field(default_factory=lambda: f"ORD-{random.randint(100000, 999999)}", primary_key=True)
    account: str
    products: List[str] = Field(default=[], sa_column=Column(MutableList.as_mutable(JSON)))
    created_at: datetime | None = Field(default_factory=datetime.now)
    total_price: float


class Payment(SQLModel, table=True):
    __tablename__ = 'payment'
    id: str | None = Field(default_factory=lambda: f"P-{random.randint(100000, 999999)}", primary_key=True)
    order: str
    status: str = Field(default='pending')  # pending | paid
    created_at: datetime | None = Field(default_factory=datetime.now)


class SupportRequest(SQLModel, table=True):
    __tablename__ = 'support_request'
    id: str | None = Field(default_factory=lambda: f"REQ-{random.randint(100000, 999999)}", primary_key=True)
    account: str | None = None
    description: str
    created_at: datetime | None = Field(default_factory=datetime.now)


class SupportComplaint(SQLModel, table=True):
    __tablename__ = 'support_complaint'
    id: str | None = Field(default_factory=lambda: f"CMP-{random.randint(100000, 999999)}", primary_key=True)
    account: str | None = None
    description: str
    created_at: datetime | None = Field(default_factory=datetime.now)

