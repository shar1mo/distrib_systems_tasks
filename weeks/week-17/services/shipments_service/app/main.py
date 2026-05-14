import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app.event_client import publish_shipment_event
from app.grpc_server import build_server
from app.models import Shipment, ShipmentCreate, ShipmentStatusUpdate
from app.repository import ShipmentRepository
from app.settings import get_settings

logging.basicConfig(level=logging.INFO)
settings = get_settings()
repository = ShipmentRepository(settings.database_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    grpc_server = build_server(repository, settings.grpc_port)
    grpc_server.start()
    logging.info("gRPC server started on port %s", settings.grpc_port)
    try:
        yield
    finally:
        grpc_server.stop(grace=3).wait()


app = FastAPI(title="shipments-s13 service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "project_code": settings.project_code,
        "service": settings.service_name,
        "http_port": settings.http_port,
        "grpc_port": settings.grpc_port,
    }


@app.get("/shipments", response_model=list[Shipment])
def list_shipments(limit: int = 100) -> list[dict]:
    return repository.list(limit)


@app.post("/shipments", response_model=Shipment, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate) -> dict:
    try:
        shipment = repository.create(payload.destination, payload.tracking)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    publish_shipment_event("shipment.created", shipment)
    return shipment


@app.get("/shipments/{shipment_id}", response_model=Shipment)
def get_shipment(shipment_id: int) -> dict:
    shipment = repository.get(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="shipment not found")
    return shipment


@app.patch("/shipments/{shipment_id}/status", response_model=Shipment)
def update_shipment_status(shipment_id: int, payload: ShipmentStatusUpdate) -> dict:
    try:
        shipment = repository.update_status(shipment_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="shipment not found")
    publish_shipment_event("shipment.status_updated", shipment)
    return shipment
