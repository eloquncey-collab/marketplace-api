from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, ProductWithCategory
from app.models import Product, Category, User
from app.dependencies import get_current_admin
from typing import Optional

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/", response_model=list[ProductWithCategory])
def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    sort_by: str = "id",
    order: str = "asc",
    db: Session = Depends(get_db)):
    
    query = db.query(Product)
    sort_map = {"id": Product.id, "price": Product.price, "created_at": Product.created_at,
                "name": Product.name}
    if sort_by not in sort_map:
        raise HTTPException(status_code=400, detail="Invalid sort_by")
    
    sort_column = sort_map[sort_by]
    order = order.lower()
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid order")
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is True:
        query = query.filter(Product.stock > 0)
    elif in_stock is False:
        query = query.filter(Product.stock == 0)  
    query = query.order_by(sort_column.desc()if order == "desc"else sort_column.asc())
    offset = (page-1) *size
    products = query.offset(offset).limit(size).all()
    return products

@router.get("/{product_id}", response_model=ProductWithCategory)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    # 1. Найти product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 2. Получить данные для обновления
    update_data = product_data.model_dump(exclude_unset=True)
    
    # 3. Если обновляется category_id — проверить что категория существует
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:  # ← Правильный отступ
            raise HTTPException(status_code=404, detail="Category not found")
    
    # 4. Обновить product
    for key, value in update_data.items():
        setattr(product, key, value)  # ← product, не category
        
    db.commit()
    db.refresh(product)  # ← product, не category
    return product  # ← product, не category

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()