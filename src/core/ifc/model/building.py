from config.element_entity_type import ElementEntityType
from core.ifc.model.element import Element


class BuildingPart(Element):

    def __init__(self, entity_type: ElementEntityType, faces, color):
        super().__init__()
        self.color = color
        self.faces = faces
        self.entity_type = entity_type


class Building(Element):

    def __init__(self, groups: list[str] = None) -> None:
        super().__init__(groups)
        self.building_parts: list[BuildingPart] = []

    def add_building_part(self, building_part: BuildingPart):
        self.building_parts.append(building_part)
