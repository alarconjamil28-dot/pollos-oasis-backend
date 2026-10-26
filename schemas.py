from pydantic import BaseModel
from typing import List
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    purchase_price: float
    sale_price: float
    stock: int
    min_stock: int = 5

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    active: bool

    class Config:
        from_attributes = True

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int

class SaleCreate(BaseModel):
    payment_method: str = "Efectivo"
    items: List[SaleItemCreate]

class SaleOut(BaseModel):
    id: int
    created_at: datetime
    payment_method: str
    total_amount: float

    class Config:
        from_attributes = True
