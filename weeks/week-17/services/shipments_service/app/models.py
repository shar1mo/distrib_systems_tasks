from typing import Literal

from pydantic import BaseModel, Field


ShipmentStatus = Literal["created", "in_transit", "delivered", "cancelled"]


class ShipmentCreate(BaseModel):
    destination: str = Field(..., min_length=2, max_length=120)
    tracking: str = Field(..., min_length=3, max_length=80)


class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatus


class Shipment(ShipmentCreate):
    id: int
    status: ShipmentStatus
    created_at: str
