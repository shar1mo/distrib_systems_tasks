from typing import Literal

import strawberry
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from strawberry.fastapi import GraphQLRouter

from app.grpc_client import ShipmentsGrpcClient, UpstreamError
from app.settings import get_settings

settings = get_settings()
client = ShipmentsGrpcClient(settings.shipments_grpc_target)


class ShipmentCreate(BaseModel):
    destination: str = Field(..., min_length=2, max_length=120)
    tracking: str = Field(..., min_length=3, max_length=80)


class ShipmentStatusUpdate(BaseModel):
    status: Literal["created", "in_transit", "delivered", "cancelled"]


@strawberry.type(name="Shipment")
class ShipmentGraphQL:
    id: int
    destination: str
    tracking: str
    status: str
    created_at: str


def _as_graphql(item: dict) -> ShipmentGraphQL:
    return ShipmentGraphQL(
        id=item["id"],
        destination=item["destination"],
        tracking=item["tracking"],
        status=item["status"],
        created_at=item["created_at"],
    )


def _handle_upstream_error(exc: UpstreamError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@strawberry.type
class Query:
    @strawberry.field
    def shipments(self, limit: int = 100) -> list[ShipmentGraphQL]:
        return [_as_graphql(item) for item in client.list_shipments(limit)]


@strawberry.type
class Mutation:
    @strawberry.mutation(name="createShipment")
    def create_shipment(self, destination: str, tracking: str) -> ShipmentGraphQL:
        return _as_graphql(client.create_shipment(destination, tracking))


schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI(title="shipments-s13 gateway", version="1.0.0")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "project_code": settings.project_code,
        "upstream": settings.shipments_grpc_target,
    }


@app.get("/api/shipments")
def list_shipments(limit: int = 100) -> list[dict]:
    try:
        return client.list_shipments(limit)
    except UpstreamError as exc:
        _handle_upstream_error(exc)


@app.post("/api/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate) -> dict:
    try:
        return client.create_shipment(payload.destination, payload.tracking)
    except UpstreamError as exc:
        _handle_upstream_error(exc)


@app.get("/api/shipments/{shipment_id}")
def get_shipment(shipment_id: int) -> dict:
    try:
        return client.get_shipment(shipment_id)
    except UpstreamError as exc:
        _handle_upstream_error(exc)


@app.patch("/api/shipments/{shipment_id}/status")
def update_shipment_status(shipment_id: int, payload: ShipmentStatusUpdate) -> dict:
    try:
        return client.update_shipment_status(shipment_id, payload.status)
    except UpstreamError as exc:
        _handle_upstream_error(exc)
