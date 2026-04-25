
def test_login_success(client):
    reg = client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
def register_headers(client, username: str, password: str = "password123"):
    email = f"{username}@example.com"

    reg = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201

def test_users_me_without_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"