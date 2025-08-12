from typing import Optional

from pydantic import BaseModel, Field

from cs2bim.ifc.enum.ifc_version import IfcVersion


class GenerateModelRequest(BaseModel):
    IFC_VERSION: IfcVersion = Field(..., description="The IFC version")
    NAME: str = Field(..., description="The name of the model")
    POLYGON: str = Field(..., description="WKT string representing the polygon (must be closed)")
    PROJECT_ORIGIN: Optional[str] = Field(None, description="Optional origin as comma-separated string 'x,y,z'")