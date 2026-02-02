from abc import abstractmethod, ABC
from ifcopenshell import entity_instance

from core.ifc.ifc_file import IfcFile
from core.ifc.model.feature_element import FeatureElement


class Extrusion(FeatureElement, ABC):

    @abstractmethod
    def map_to_ifc(self, ifc_file: IfcFile, entity: str, placement_rel_to: entity_instance,
                   ifc_representation_sub_context: entity_instance, ifc_style: entity_instance) -> entity_instance:
        raise NotImplementedError("map_to_ifc must be implemented by subclasses")
