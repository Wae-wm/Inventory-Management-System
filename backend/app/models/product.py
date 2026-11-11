from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    product_name: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    description: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(30), default="piece", server_default="piece")
    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, server_default="0.00")
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, server_default="0.00")
    reorder_level: Mapped[int] = mapped_column(default=10, server_default="10")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    category: Mapped["Category"] = relationship(back_populates="products")
    balances: Mapped[list["InventoryBalance"]] = relationship(back_populates="product")
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="product")
    supplier_products: Mapped[list["SupplierProduct"]] = relationship(back_populates="product")
