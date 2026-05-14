from dataclasses import dataclass
from typing import Any

import grpc

from shipments.v1 import shipments_pb2 as pb2
from shipments.v1 import shipments_pb2_grpc as pb2_grpc


@dataclass
class UpstreamError(Exception):
    status_code: int
    detail: str


def _shipment_to_dict(shipment: pb2.Shipment) -> dict[str, Any]:
    return {
        "id": shipment.id,
        "destination": shipment.destination,
        "tracking": shipment.tracking,
        "status": shipment.status,
        "created_at": shipment.created_at,
    }


def _map_error(exc: grpc.RpcError) -> UpstreamError:
    code = exc.code()
    detail = exc.details() or "shipments service error"
    if code == grpc.StatusCode.NOT_FOUND:
        return UpstreamError(404, detail)
    if code == grpc.StatusCode.ALREADY_EXISTS:
        return UpstreamError(409, detail)
    if code == grpc.StatusCode.INVALID_ARGUMENT:
        return UpstreamError(400, detail)
    return UpstreamError(502, detail)


class ShipmentsGrpcClient:
    def __init__(self, target: str, timeout: float = 5.0) -> None:
        self.target = target
        self.timeout = timeout

    def _stub(self):
        channel = grpc.insecure_channel(self.target)
        return channel, pb2_grpc.ShipmentsServiceStub(channel)

    def create_shipment(self, destination: str, tracking: str) -> dict[str, Any]:
        channel, stub = self._stub()
        try:
            response = stub.CreateShipment(
                pb2.CreateShipmentRequest(destination=destination, tracking=tracking),
                timeout=self.timeout,
            )
            return _shipment_to_dict(response)
        except grpc.RpcError as exc:
            raise _map_error(exc) from exc
        finally:
            channel.close()

    def get_shipment(self, shipment_id: int) -> dict[str, Any]:
        channel, stub = self._stub()
        try:
            response = stub.GetShipment(pb2.GetShipmentRequest(id=shipment_id), timeout=self.timeout)
            return _shipment_to_dict(response)
        except grpc.RpcError as exc:
            raise _map_error(exc) from exc
        finally:
            channel.close()

    def list_shipments(self, limit: int = 100) -> list[dict[str, Any]]:
        channel, stub = self._stub()
        try:
            response = stub.ListShipments(pb2.ListShipmentsRequest(limit=limit), timeout=self.timeout)
            return [_shipment_to_dict(item) for item in response.shipments]
        except grpc.RpcError as exc:
            raise _map_error(exc) from exc
        finally:
            channel.close()

    def update_shipment_status(self, shipment_id: int, status: str) -> dict[str, Any]:
        channel, stub = self._stub()
        try:
            response = stub.UpdateShipmentStatus(
                pb2.UpdateShipmentStatusRequest(id=shipment_id, status=status),
                timeout=self.timeout,
            )
            return _shipment_to_dict(response)
        except grpc.RpcError as exc:
            raise _map_error(exc) from exc
        finally:
            channel.close()
