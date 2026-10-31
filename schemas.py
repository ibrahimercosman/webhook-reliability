from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    name: str
    email: str
    webhook_url: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    webhook_url: str

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    subscribed_at: datetime
    cancelled_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    id: int
    event_type: str
    customer_id: int
    subscription_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)