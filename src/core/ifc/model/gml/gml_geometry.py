from abc import ABC, abstractmethod

from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement

from core.ifc.ifc_file import IfcFile
from core.ifc.model.coordinates import Coordinates


class GmlGeometry(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def from_gml(self, gml: XmlElement, project_origin: Coordinates):
        pass

    @abstractmethod
    def map_to_ifc(self, ifc_file: IfcFile, ifc_style: entity_instance) -> list[entity_instance]:
        pass

    @abstractmethod
    def create_ifc_product_definition_shape(self, ifc_file: IfcFile, ifc_representation_sub_context: entity_instance,
                                            ifc_representations: list[entity_instance]) -> entity_instance:
        pass
