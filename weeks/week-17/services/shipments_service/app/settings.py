import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    project_code: str
    service_name: str
    http_port: int
    grpc_port: int
    database_path: str
    audit_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        project_code=os.getenv("PROJECT_CODE", "shipments-s13"),
        service_name=os.getenv("SERVICE_NAME", "shipments-svc-s13"),
        http_port=int(os.getenv("APP_PORT", "8130")),
        grpc_port=int(os.getenv("GRPC_PORT", "8131")),
        database_path=os.getenv("DATABASE_PATH", "/data/shipments.db"),
        audit_url=os.getenv("AUDIT_URL", "http://audit-service:8132"),
    )
