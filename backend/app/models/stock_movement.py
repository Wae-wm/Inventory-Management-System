from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (CheckConstraint("quantity > 0", name="chk_movement_quantity"),)

    movement_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.warehouse_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    movement_type: Mapped[str] = mapped_column(
        Enum("IN", "OUT", "ADJUSTMENT", name="movement_type")
    )
    quantity: Mapped[int]
    reference_no: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="movements")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="movements")
    user: Mapped["User"] = relationship(back_populates="movements")
