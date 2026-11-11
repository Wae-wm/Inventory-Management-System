# import ทุก model ไว้ที่นี่ เพื่อให้ SQLAlchemy รู้จักทุกตารางและความสัมพันธ์
from app.models.category import Category
from app.models.inventory_balance import InventoryBalance
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.models.supplier_product import SupplierProduct
from app.models.user import User
from app.models.warehouse import Warehouse

__all__ = [
    "Category",
    "InventoryBalance",
    "Product",
    "StockMovement",
    "Supplier",
    "SupplierProduct",
    "User",
    "Warehouse",
]
