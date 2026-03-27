from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    value: str


class EntryRecord(BaseModel):
    id: int
    value: str

    model_config = ConfigDict(from_attributes=True)
