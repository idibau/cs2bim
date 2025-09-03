from pydantic import BaseModel, Field
from typing import Optional

from core.ifc.model.ifc_version import IfcVersion


class GenerateModelRequest(BaseModel):
    IFC_VERSION: IfcVersion = Field(..., description="The IFC version [IFC4, IFC4x3]")
    NAME: str = Field(..., description="The name of the model")
    POLYGON: str = Field(..., description="The closed WKT string representing the polygon")
    PROJECT_ORIGIN: Optional[str] = Field(None, description="Optional origin as comma-separated string [x,y,z]")
