from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models import Customer, Event, Subscription
from schemas import CustomerCreate


def get_customer_by_email(db: Session, email: str):
    statement = select(Customer).where(
        Customer.email == email
    )

    return db.scalar(statement)


def get_customer_by_webhook_url(
    db: Session,
    webhook_url: str,
):
    statement = select(Customer).where(
        Customer.webhook_url == webhook_url
    )

    return db.scalar(statement)


def get_customer_by_id(
    db: Session,
    customer_id: int,
):
    return db.get(Customer, customer_id)


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
):
    if get_customer_by_email(
        db,
        customer_data.email,
    ) is not None:
        raise ValueError("Email already exists")

    if get_customer_by_webhook_url(
        db,
        customer_data.webhook_url,
    ) is not None:
        raise ValueError("Webhook URL already exists")

    customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        webhook_url=customer_data.webhook_url,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_active_subscription_by_customer(
    db: Session,
    customer_id: int,
):
    statement = select(Subscription).where(
        Subscription.customer_id == customer_id,
        Subscription.status == "active",
    )

    return db.scalar(statement)


def delete_customer(
    db: Session,
    customer_id: int,
):
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise LookupError("Customer not found")

    active_subscription = (
        get_active_subscription_by_customer(
            db,
            customer_id,
        )
    )

    if active_subscription is not None:
        raise ValueError(
            "Customer has an active subscription"
        )

    db.execute(
        delete(Event).where(
            Event.customer_id == customer_id
        )
    )

    db.execute(
        delete(Subscription).where(
            Subscription.customer_id == customer_id
        )
    )

    db.delete(customer)
    db.commit()


def create_subscription(
    db: Session,
    customer_id: int,
):
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise LookupError("Customer not found")

    active_subscription = (
        get_active_subscription_by_customer(
            db,
            customer_id,
        )
    )

    if active_subscription is not None:
        raise ValueError(
            "Customer already has an active subscription"
        )

    subscription = Subscription(
        customer_id=customer_id,
        status="active",
        subscribed_at=datetime.now(),
        cancelled_at=None,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_subscription_history(
    db: Session,
    customer_id: int,
):
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise LookupError("Customer not found")

    statement = (
        select(Subscription)
        .where(
            Subscription.customer_id == customer_id
        )
        .order_by(Subscription.id)
    )

    return list(db.scalars(statement).all())


def cancel_subscription(
    db: Session,
    subscription_id: int,
):
    subscription = db.get(
        Subscription,
        subscription_id,
    )

    if subscription is None:
        raise LookupError(
            "Subscription not found"
        )

    if subscription.status == "cancelled":
        raise ValueError(
            "Subscription already cancelled"
        )

    cancellation_time = datetime.now()

    subscription.status = "cancelled"
    subscription.cancelled_at = cancellation_time

    event = Event(
        event_type="subscription.cancelled",
        customer_id=subscription.customer_id,
        subscription_id=subscription.id,
        created_at=cancellation_time,
    )

    db.add(event)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_events(db: Session):
    statement = select(Event).order_by(
        Event.id
    )

    return list(db.scalars(statement).all())


def delete_event(
    db: Session,
    event_id: int,
):
    event = db.get(Event, event_id)

    if event is None:
        raise LookupError("Event not found")

    db.delete(event)
    db.commit()