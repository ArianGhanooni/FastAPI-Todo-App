from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskBaseSchema(BaseModel):
    title: str = (Field(..., max_length=150, min_length=5, description="Title of the task"))
    description: Optional[str] = (Field(None, max_length=500, description="Description of the task"))
    is_completed: bool = Field(..., description="Status of the task")


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskUpdateSchema(TaskBaseSchema):
    pass


class TaskResponseSchema(TaskBaseSchema):
    id: int = Field(..., description="Unique ID of the task")
    created_at: datetime = Field(..., description="Created at of the task")
    updated_at: datetime = Field(..., description="Updated at of the task")