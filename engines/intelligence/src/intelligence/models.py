from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InventoryItem(BaseModel):
    name: str
    file: str
    line: int
    extra: Dict[str, str] = Field(default_factory=dict)


class ApiItem(BaseModel):
    method: str
    path: str
    handler: str
    file: str
    line: int


class ModelItem(BaseModel):
    name: str
    table: Optional[str] = None
    file: str
    line: int


class DependencyItem(BaseModel):
    name: str
    version: Optional[str] = None
    source: str


class FlowStep(BaseModel):
    layer: str  # controller | service | repository | database | external
    symbol: str
    file: Optional[str] = None
    line: Optional[int] = None
    operation: Optional[str] = None


class FlowTrace(BaseModel):
    endpoint: str
    chain: List[str] = Field(default_factory=list)
    steps: List[FlowStep] = Field(default_factory=list)
    confidence: float
    uncertainties: List[str] = Field(default_factory=list)
    sequence_diagram: Optional[str] = None

    def sync_chain_from_steps(self) -> None:
        self.chain = [step.symbol for step in self.steps]


class Inventories(BaseModel):
    services: List[InventoryItem] = Field(default_factory=list)
    controllers: List[InventoryItem] = Field(default_factory=list)
    apis: List[ApiItem] = Field(default_factory=list)
    models: List[ModelItem] = Field(default_factory=list)
    tests: List[InventoryItem] = Field(default_factory=list)
    dependencies: List[DependencyItem] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    repository: str
    framework: str
    confidence: float
    generated_at: str
    inventories: Inventories
    flow_traces: List[FlowTrace] = Field(default_factory=list)
    rust_scan: Optional[Dict[str, Any]] = None

    @classmethod
    def empty(cls, repository: str, framework: str, confidence: float) -> "AnalysisResult":
        return cls(
            repository=repository,
            framework=framework,
            confidence=confidence,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inventories=Inventories(),
        )
