import pytest
import time

def _register_and_get_headers(client, username: str, password: str = "password123"):
    email = f"{username}@example.com"

    reg = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201
    
    login = client.post(
        "/auth/login",
        json={"username": username, "email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_order_reduces_stock(client, admin_headers):
    # 1) создаём обычного пользователя (кто будет оформлять заказ)
    user_headers = _register_and_get_headers(client, f"user_order_{time.time_ns()}")

    # 2) создаём категорию (админ)
    category_name = f"cat_order_{time.time_ns()}"
    cat_resp = client.post(
        "/categories/",
        json={"name": category_name, "description": "for order test"},
        headers=admin_headers,
    )
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    # 3) создаём товар (админ)
    product_name = f"prod_order_{time.time_ns()}"
    product_resp = client.post(
        "/products/",
        json={
            "name": product_name,
            "description": "for order test",
            "price": 100.0,
            "stock": 10,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert product_resp.status_code == 201
    product_data = product_resp.json()
    product_id = product_data["id"]
    price = float(product_data["price"])

    # 4) создаём заказ (обычный пользователь)
    order_resp = client.post(
        "/orders/",
        json={"items": [{"product_id": product_id, "quantity": 2}]},
        headers=user_headers,
    )
    assert order_resp.status_code == 201
    order_data = order_resp.json()
    assert order_data["total_price"] == pytest.approx(price * 2)

    # 5) проверяем, что stock уменьшился
    product_after = client.get(f"/products/{product_id}")
    assert product_after.status_code == 200
    assert product_after.json()["stock"] == 8

def test_create_order_not_enough_stock(client, admin_headers):
    user_headers = _register_and_get_headers(client, f"user_stock_{time.time_ns()}")

    category_name = f"cat_stock_{time.time_ns()}"
    cat_resp = client.post(
        "/categories/",
        json={"name": category_name, "description": "for stock test"},
        headers=admin_headers,
    )
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    product_name = f"prod_stock_{time.time_ns()}"
    product_resp = client.post(
        "/products/",
        json={
            "name": product_name,
            "description": "for stock test",
            "price": 50.0,
            "stock": 2,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert product_resp.status_code == 201
    product_id = product_resp.json()["id"]

    order_resp = client.post(
        "/orders/",
        json={"items": [{"product_id": product_id, "quantity": 20}]},
        headers=user_headers,
    )
    assert order_resp.status_code == 400
    assert "Not enough stock" in order_resp.json()["detail"]

def test_get_order_not_owner_forbidden(client, admin_headers):
    # пользователь A
    user_a_headers = _register_and_get_headers(client, f"user_a_{time.time_ns()}")
    # пользователь B
    user_b_headers = _register_and_get_headers(client, f"user_b_{time.time_ns()}")

    category_name = f"cat_owner_{time.time_ns()}"
    cat_resp = client.post(
        "/categories/",
        json={"name": category_name, "description": "for owner test"},
        headers=admin_headers,
    )
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    product_name = f"prod_owner_{time.time_ns()}"
    product_resp = client.post(
        "/products/",
        json={
            "name": product_name,
            "description": "for owner test",
            "price": 80.0,
            "stock": 10,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert product_resp.status_code == 201
    product_id = product_resp.json()["id"]

    # заказ создаёт пользователь A
    order_resp = client.post(
        "/orders/",
        json={"items": [{"product_id": product_id, "quantity": 1}]},
        headers=user_a_headers,
    )
    assert order_resp.status_code == 201
    order_id = order_resp.json()["id"]

    # пользователь B пытается получить чужой заказ
    forbidden_resp = client.get(f"/orders/{order_id}", headers=user_b_headers)
    assert forbidden_resp.status_code == 403
    assert forbidden_resp.json()["detail"] == "Not your order"

def test_create_order_empty_items_validation(client):
    user_headers = _register_and_get_headers(client, f"user_empty_{time.time_ns()}")

    resp = client.post("/orders/", json={"items": []}, headers=user_headers)
    assert resp.status_code == 422