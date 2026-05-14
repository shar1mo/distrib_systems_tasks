from concurrent import futures
from datetime import datetime, timezone
from typing import Any

import grpc

from app.event_client import publish_shipment_event
from app.repository import ShipmentRepository
from shipments.v1 import shipments_pb2 as pb2
from shipments.v1 import shipments_pb2_grpc as pb2_grpc


def to_proto(shipment: dict[str, Any]) -> pb2.Shipment:
    return pb2.Shipment(
        id=int(shipment["id"]),
        destination=str(shipment["destination"]),
        tracking=str(shipment["tracking"]),
        status=str(shipment["status"]),
        created_at=str(shipment["created_at"]),
    )


class ShipmentsService(pb2_grpc.ShipmentsServiceServicer):
    def __init__(self, repository: ShipmentRepository) -> None:
        self.repository = repository

    def CreateShipment(self, request, context):
        try:
            shipment = self.repository.create(request.destination, request.tracking)
        except ValueError as exc:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, str(exc))
        publish_shipment_event("shipment.created", shipment)
        return to_proto(shipment)

    def GetShipment(self, request, context):
        shipment = self.repository.get(request.id)
        if shipment is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "shipment not found")
        return to_proto(shipment)

    def ListShipments(self, request, context):
        shipments = [to_proto(item) for item in self.repository.list(request.limit or 100)]
        return pb2.ListShipmentsResponse(shipments=shipments)

    def UpdateShipmentStatus(self, request, context):
        try:
            shipment = self.repository.update_status(request.id, request.status)
        except ValueError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
        if shipment is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "shipment not found")
        publish_shipment_event("shipment.status_updated", shipment)
        return to_proto(shipment)

    def StreamShipmentEvents(self, request, context):
        for shipment in self.repository.list(request.limit or 100):
            yield pb2.ShipmentEvent(
                type="shipment.snapshot",
                shipment=to_proto(shipment),
                emitted_at=datetime.now(timezone.utc).isoformat(),
            )


def build_server(repository: ShipmentRepository, port: int) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ShipmentsServiceServicer_to_server(ShipmentsService(repository), server)
    bound_port = server.add_insecure_port(f"[::]:{port}")
    if bound_port == 0:
        raise RuntimeError(f"failed to bind gRPC server on port {port}")
    return server
