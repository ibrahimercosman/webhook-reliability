def create_test_customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Acme",
            "email": "contact@acme.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    return response.json()["id"]


def test_subscription_history_is_empty(client):
    customer_id = create_test_customer(client)

    response = client.get(
        f"/customers/{customer_id}/subscriptions"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_active_subscription_when_none_exists(client):
    customer_id = create_test_customer(client)

    response = client.get(
        f"/customers/{customer_id}/subscriptions/active"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Active subscription not found"


def test_create_subscription(client):
    customer_id = create_test_customer(client)

    response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == customer_id
    assert data["status"] == "active"
    assert data["cancelled_at"] is None
    assert "id" in data
    assert "subscribed_at" in data


def test_cannot_create_second_active_subscription(client):
    customer_id = create_test_customer(client)

    client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Customer already has an active subscription"
    )


def test_get_active_subscription(client):
    customer_id = create_test_customer(client)

    create_response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    subscription_id = create_response.json()["id"]

    response = client.get(
        f"/customers/{customer_id}/subscriptions/active"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subscription_id
    assert data["customer_id"] == customer_id
    assert data["status"] == "active"


def test_cannot_delete_customer_with_active_subscription(client):
    customer_id = create_test_customer(client)

    client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    response = client.delete(
        f"/customers/{customer_id}"
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Customer has an active subscription"
    )


def test_cancel_subscription(client):
    customer_id = create_test_customer(client)

    create_response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    subscription_id = create_response.json()["id"]

    response = client.post(
        f"/subscriptions/{subscription_id}/cancel"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subscription_id
    assert data["status"] == "cancelled"
    assert data["cancelled_at"] is not None


def test_cannot_cancel_subscription_twice(client):
    customer_id = create_test_customer(client)

    create_response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    subscription_id = create_response.json()["id"]

    client.post(
        f"/subscriptions/{subscription_id}/cancel"
    )

    response = client.post(
        f"/subscriptions/{subscription_id}/cancel"
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Subscription already cancelled"
    )


def test_customer_can_resubscribe_after_cancellation(client):
    customer_id = create_test_customer(client)

    first_response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    first_subscription_id = first_response.json()["id"]

    client.post(
        f"/subscriptions/{first_subscription_id}/cancel"
    )

    second_response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    assert second_response.status_code == 201

    second_data = second_response.json()

    assert second_data["status"] == "active"
    assert second_data["id"] != first_subscription_id

    history_response = client.get(
        f"/customers/{customer_id}/subscriptions"
    )

    history = history_response.json()

    assert history_response.status_code == 200
    assert len(history) == 2
    assert history[0]["status"] == "cancelled"
    assert history[1]["status"] == "active"


def test_create_subscription_for_missing_customer(client):
    response = client.post(
        "/customers/999999/subscriptions"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_cancel_missing_subscription(client):
    response = client.post(
        "/subscriptions/999999/cancel"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Subscription not found"