from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class PipelineRequest(BaseModel):
    prompt: str


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class ResourceItem(BaseModel):
    resource_type: str
    name: str
    description: str


class CostLineItem(BaseModel):
    resource: str
    monthly_cost_usd: float
    notes: str


class PipelineResponse(BaseModel):
    intent: dict
    resources: List[ResourceItem]
    terraform_code: str
    validation_passed: bool
    cost_breakdown: List[CostLineItem]
    total_monthly_cost_usd: float
    ready_to_deploy: bool
