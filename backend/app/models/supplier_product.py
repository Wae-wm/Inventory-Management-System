from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupplierProduct(Base):
    __tablename__ = "supplier_products"

    # primary key แบบ composite: คู่ (supplier_id, product_id) ต้องไม่ซ้ำกัน
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.supplier_id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    supplier_sku: Mapped[str | None] = mapped_column(String(50))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, server_default="0.00")
    lead_time_days: Mapped[int] = mapped_column(default=0, server_default="0")
    is_preferred: Mapped[bool] = mapped_column(default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    supplier: Mapped["Supplier"] = relationship(back_populates="supplier_products")
    product: Mapped["Product"] = relationship(back_populates="supplier_products")
