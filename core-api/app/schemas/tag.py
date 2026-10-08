from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(default="#64748b", max_length=20)


class TagRead(BaseModel):
    id: str
    name: str
    color: str

    model_config = {"from_attributes": True}
