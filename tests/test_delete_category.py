def test_delete_category(client):
    client.post("/api/register", json={"username": "catuser", "password": "1234"})
    login = client.post("/api/login", json={"username": "catuser", "password": "1234"})
    
    add_category = client.post("/api/categories", json={"category_name": "Work"})
    category_list = client.get("/api/categories").get_json()
    print(category_list)
    category_id = category_list[0]["id"]  # get the first category's id
    print(category_id)
    # Delete the category
    delete_response = client.delete(f"/api/categories/{category_id}")
    print("RESPONSE IS THIS - " , delete_response)
    assert delete_response.status_code == 200 