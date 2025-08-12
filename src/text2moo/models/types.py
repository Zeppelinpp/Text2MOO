from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict


class BaseUnit(BaseModel):
    """
    Base unit of user's data.
    """

    id: str
    name: Optional[str] = None
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Attributes of the unit."
    )


class OptimizationGroup(BaseModel):
    """
    Search space of optimization based on user's data.
    """

    unit_attr: List[str] = Field(
        default_factory=list, description="Attribute keys of the unit."
    )
    units: List[BaseUnit] = Field(
        default_factory=list, description="Units of the search space."
    )


class OptimizationData(BaseModel):
    data: Dict[str, OptimizationGroup]
