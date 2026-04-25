from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OrderCreate, OrderResponse
from app.models import Order, OrderProduct, Product, User
from app.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_price = 0
    order_items = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
             raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "price": float(product.price)
        })
        total_price += float(product.price) * item.quantity
    
    new_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status="pending"
    )
    db.add(new_order)
    db.flush()
    
    for item_data in order_items:
        order_product = OrderProduct(
            order_id=new_order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_product)
        
        item_data["product"].stock -= item_data["quantity"]
        
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/",response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    return order