from fastapi import FastAPI
from app.routers import auth, users, categories, products, orders
from app.database import engine, Base


app = FastAPI(
    title="Marketplace API",
    description="API для маркетплейса с авторизацией",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)  # Добавил
app.include_router(products.router)    # Добавил
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "Welcome to Marketplace API"}