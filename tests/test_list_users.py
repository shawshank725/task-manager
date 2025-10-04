def test_list_users(client):
    response = client.post("/api/logout")
    assert response.status_code == 200