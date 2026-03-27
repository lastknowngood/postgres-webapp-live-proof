from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    value: str
    source: str = 'manual'


class EntryRecord(BaseModel):
    id: int
    value: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
