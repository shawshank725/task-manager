def test_register_and_login(client):
    # Register
    response = client.post("/api/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201

    # Login
    response = client.post("/api/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200