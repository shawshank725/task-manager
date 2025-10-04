def test_create_category(client):
    client.post("/api/register", json={"username": "catuser", "password": "1234"})
    login = client.post("/api/login", json={"username": "catuser", "password": "1234"})
    
    response = client.post("/api/categories", json={"category_name": "Work"})

    assert response.status_code == 201