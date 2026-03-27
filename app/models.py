from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    value: str


class EntryRecord(BaseModel):
    id: int
    value: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)