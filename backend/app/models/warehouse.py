from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    warehouse_code: Mapped[str] = mapped_column(String(20), unique=True)
    warehouse_name: Mapped[str] = mapped_column(String(150))
    address: Mapped[str | None] = mapped_column(Text)
    contact_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    balances: Mapped[list["InventoryBalance"]] = relationship(back_populates="warehouse")
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="warehouse")
