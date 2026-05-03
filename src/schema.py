from pydantic import BaseModel, Field
from typing import Literal

class WorkOrderSchema(BaseModel):
    """Schema for detecting common infrastructure problems."""
    intent: str = Field(..., description="Action to be performed, e.g., 'Create Work Order'")
    problem_area: str = Field(..., description="Category of the issue, e.g., 'LAN', 'Hardware', 'Electrical'")
    severity: Literal["low", "medium", "high"] = Field(
        ..., description="The severity of the user query"
    )
    location_id: str = Field(..., alias="Location id", description="The ID/Site name of the location")
    summary: str = Field(..., description="A brief summary of the user query")

    class Config:
        populate_by_name = True