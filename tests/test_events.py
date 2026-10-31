def create_customer_with_subscription(client):
    customer_response = client.post(
        "/customers",
        json={
            "name": "Acme",
            "email": "contact@acme.com",
            "webhook_url": "https://acme.com/webhook",
        },
    )

    customer_id = customer_response.json()["id"]

    subscription_response = client.post(
        f"/customers/{customer_id}/subscriptions"
    )

    subscription_id = subscription_response.json()["id"]

    return customer_id, subscription_id


def test_events_are_empty_initially(client):
    response = client.get("/events")

    assert response.status_code == 200
    assert response.json() == []


def test_cancelling_subscription_creates_event(client):
    customer_id, subscription_id = create_customer_with_subscription(client)

    client.post(
        f"/subscriptions/{subscription_id}/cancel"
    )

    response = client.get("/events")

    assert response.status_code == 200

    events = response.json()

    assert len(events) == 1

    event = events[0]

    assert event["event_type"] == "subscription.cancelled"
    assert event["customer_id"] == customer_id
    assert event["subscription_id"] == subscription_id
    assert "created_at" in event


def test_delete_event(client):
    _, subscription_id = create_customer_with_subscription(client)

    client.post(
        f"/subscriptions/{subscription_id}/cancel"
    )

    events_response = client.get("/events")
    event_id = events_response.json()[0]["id"]

    delete_response = client.delete(
        f"/events/{event_id}"
    )

    assert delete_response.status_code == 204

    events_after_delete = client.get("/events")

    assert events_after_delete.status_code == 200
    assert events_after_delete.json() == []


def test_delete_missing_event(client):
    response = client.delete("/events/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_deleting_customer_removes_related_event(client):
    customer_id, subscription_id = create_customer_with_subscription(client)

    client.post(
        f"/subscriptions/{subscription_id}/cancel"
    )

    events_before_delete = client.get("/events")

    assert len(events_before_delete.json()) == 1

    delete_customer_response = client.delete(
        f"/customers/{customer_id}"
    )

    assert delete_customer_response.status_code == 204

    events_after_delete = client.get("/events")

    assert events_after_delete.status_code == 200
    assert events_after_delete.json() == []