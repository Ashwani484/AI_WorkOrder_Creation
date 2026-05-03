from pydantic import BaseModel, Field
from typing import Literal, Optional

class WorkOrderSchema(BaseModel):
    """
    Schema for infrastructure problems. 
    Fields are Optional to prevent hallucination; LLM returns null if information is missing.
    """
    # Intent is restricted to specific categories but remains optional[cite: 2]
    intent: Optional[Literal["server", "network", "hardware", "software", "application"]] = Field(
        None, 
        description="The primary category of the issue. Leave null if not explicitly identifiable."
    )
    
    problem_area: Optional[str] = Field(
        None, 
        description="Specific category like 'LAN' or 'Power'. Leave blank if not found."
    )
    
    severity: Optional[Literal["low", "medium", "high"]] = Field(
        None, 
        description="Severity level. Do not guess; leave null if not stated."
    )
    
    # Use alias to match your specific requirement while keeping Python naming conventions[cite: 2]
    location_id: Optional[str] = Field(
        None, 
        alias="Location id", 
        description="The Site name or ID. Leave null if missing."
    )
    
    summary: Optional[str] = Field(
        None, 
        description="A concise summary of the problem. Leave null if no description provided."
    )

    class Config:
        populate_by_name = True