import pytest

from main import app
import time


def _register_and_get_headers(client, username: str, password: str = "password123"):
    email = f"{username}@example.com"
    login = client.post(
        "/auth/login",
        json={"username": username, "email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


    