from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    user_id: Optional[int] = None
    
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
    
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock: int = Field(ge=0,description="Stock must be greater than or equal to 0")
    category_id: int
    
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class ProductWithCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int
    created_at: datetime
    category: CategoryResponse
    model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    
class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
   
    
class OrderProductResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductResponse
    model_config = ConfigDict(from_attributes=True)
    
class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    order_products: list[OrderProductResponse]
    model_config = ConfigDict(from_attributes=True)