def test_create_customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Acme",
            "email": "contact@acme.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Acme"
    assert data["email"] == "contact@acme.com"
    assert data["webhook_url"] == "https://acme.com/webhook"
    assert "id" in data


def test_duplicate_email(client):
    customer_data = {
        "name": "Acme",
        "email": "contact@acme.com",
        "webhook_url": "https://acme.com/webhook",
    }

    client.post("/customers", json=customer_data)

    response = client.post(
        "/customers",
        json={
            "name": "Another Company",
            "email": "contact@acme.com",
            "webhook_url": "https://another.com/webhook",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


def test_duplicate_webhook_url(client):
    client.post(
        "/customers",
        json={
            "name": "Acme",
            "email": "contact@acme.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    response = client.post(
        "/customers",
        json={
            "name": "Another Company",
            "email": "another@example.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Webhook URL already exists"


def test_get_customer(client):
    create_response = client.post(
        "/customers",
        json={
            "name": "Acme",
            "email": "contact@acme.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    customer_id = create_response.json()["id"]

    response = client.get(
        f"/customers/{customer_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Acme"


def test_get_missing_customer(client):
    response = client.get("/customers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_delete_customer(client):
    create_response = client.post(
        "/customers",
        json={
            "name": "Acme",
            "email": "contact@acme.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    customer_id = create_response.json()["id"]

    response = client.delete(
        f"/customers/{customer_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/customers/{customer_id}"
    )

    assert get_response.status_code == 404


def test_delete_missing_customer(client):
    response = client.delete("/customers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"