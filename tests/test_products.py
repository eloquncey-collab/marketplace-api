import pytest

@pytest.mark.parametrize("params,expected_detail", [
    ({"sort_by": "wrong"}, "Invalid sort_by"),
    ({"order": "up"}, "Invalid order"),
    ({"min_price": 1000, "max_price": 100}, "min_price cannot be greater than max_price")
])

def test_products_invalid_query_params(client, params, expected_detail):
    r = client.get("/products/", params=params)
    assert r.status_code == 400
    assert r.json()["detail"] == expected_detail
    
