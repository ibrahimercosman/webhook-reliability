from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from operations import (
    cancel_subscription,
    create_customer,
    create_subscription,
    delete_customer,
    delete_event,
    get_active_subscription_by_customer,
    get_customer_by_id,
    get_events,
    get_subscription_history,
)
from schemas import (
    CustomerCreate,
    CustomerResponse,
    EventResponse,
    SubscriptionResponse,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Webhook Reliability API"
)


@app.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=201,
)
def create_customer_endpoint(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_customer(
            db,
            customer_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@app.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@app.delete(
    "/customers/{customer_id}",
    status_code=204,
)
def delete_customer_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        delete_customer(
            db,
            customer_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@app.post(
    "/customers/{customer_id}/subscriptions",
    response_model=SubscriptionResponse,
    status_code=201,
)
def create_subscription_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return create_subscription(
            db,
            customer_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@app.get(
    "/customers/{customer_id}/subscriptions/active",
    response_model=SubscriptionResponse,
)
def get_active_subscription_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    subscription = (
        get_active_subscription_by_customer(
            db,
            customer_id,
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Active subscription not found",
        )

    return subscription


@app.get(
    "/customers/{customer_id}/subscriptions",
    response_model=list[SubscriptionResponse],
)
def get_subscription_history_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_subscription_history(
            db,
            customer_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@app.post(
    "/subscriptions/{subscription_id}/cancel",
    response_model=SubscriptionResponse,
)
def cancel_subscription_endpoint(
    subscription_id: int,
    db: Session = Depends(get_db),
):
    try:
        return cancel_subscription(
            db,
            subscription_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@app.get(
    "/events",
    response_model=list[EventResponse],
)
def get_events_endpoint(
    db: Session = Depends(get_db),
):
    return get_events(db)


@app.delete(
    "/events/{event_id}",
    status_code=204,
)
def delete_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
):
    try:
        delete_event(
            db,
            event_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )