from abc import ABC, abstractmethod

from ifcopenshell import entity_instance


class GmlGeometry(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def from_gml(self, gml, project_origin: tuple[float, float, float]) -> None:
        pass

    @abstractmethod
    def map_to_ifc(self, ifc_file, ifc_style) -> list[entity_instance]:
        pass

    @abstractmethod
    def create_ifc_product_definition_shape(self, ifc_file, ifc_representation_sub_context,
                                            ifc_representations: list[entity_instance]):
        pass
