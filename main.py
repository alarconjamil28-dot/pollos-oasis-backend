from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Pollos Oasis - Compra, Venta e Inventario")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API de Pollos Oasis activa y conectada a Supabase"}

@app.get("/api/v1/products", response_model=List[schemas.ProductOut], tags=["Inventario"])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.post("/api/v1/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED, tags=["Inventario"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.sku == product.sku).first()
    if db_product:
        raise HTTPException(status_code=400, detail="El SKU ya existe")

    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.post("/api/v1/sales/checkout", response_model=schemas.SaleOut, status_code=status.HTTP_201_CREATED, tags=["Ventas"])
def checkout_sale(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    if not sale_in.items:
        raise HTTPException(status_code=400, detail="La orden no contiene productos")

    total = 0.0
    items_to_create = []

    try:
        for item in sale_in.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stock insuficiente para '{product.name}'. Disponible: {product.stock}"
                )

            product.stock -= item.quantity
            subtotal = product.sale_price * item.quantity
            total += subtotal

            items_to_create.append({
                "product_id": product.id,
                "quantity": item.quantity,
                "unit_price": product.sale_price
            })

        db_sale = models.Sale(total_amount=total, payment_method=sale_in.payment_method)
        db.add(db_sale)
        db.flush()

        for detail in items_to_create:
            db_detail = models.SaleItem(
                sale_id=db_sale.id,
                product_id=detail["product_id"],
                quantity=detail["quantity"],
                unit_price=detail["unit_price"]
            )
            db.add(db_detail)

        db.commit()
        db.refresh(db_sale)
        return db_sale

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la transacción: {str(e)}")
