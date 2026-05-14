import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    project_code: str
    service_name: str
    database_path: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        project_code=os.getenv("PROJECT_CODE", "shipments-s13"),
        service_name=os.getenv("SERVICE_NAME", "audit-service"),
        database_path=os.getenv("DATABASE_PATH", "/data/audit.db"),
    )
