import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    project_code: str
    gateway_prefix: str
    shipments_grpc_target: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        project_code=os.getenv("PROJECT_CODE", "shipments-s13"),
        gateway_prefix=os.getenv("GATEWAY_PREFIX", "/api"),
        shipments_grpc_target=os.getenv("SHIPMENTS_GRPC_TARGET", "localhost:8131"),
    )
