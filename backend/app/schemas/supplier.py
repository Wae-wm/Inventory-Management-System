from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierCreate(BaseModel):
    supplier_name: str = Field(min_length=1, max_length=150)
    contact_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None


class SupplierUpdate(BaseModel):
    supplier_name: str | None = Field(default=None, min_length=1, max_length=150)
    contact_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    is_active: bool | None = None


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: int
    supplier_name: str
    contact_name: str | None
    phone: str | None
    email: str | None
    address: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
