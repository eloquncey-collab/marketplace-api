import time

def test_create_category_non_admin_forbidden(client, user_headers):
    r = client.post("/categories/", json={"name": f"cat_x{int(time.time_ns())}", "description": "x"}, headers=user_headers)
    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"
    
def test_create_category_admin_success(client, admin_headers):
    name = f"cat_{int(time.time_ns())}"
    r = client.post("/categories/", json={"name": name, "description": "ok"}, headers=admin_headers)
    assert r.status_code == 201
    assert "id" in r.json()
    assert r.json()["name"] == name