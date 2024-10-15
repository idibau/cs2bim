from cs2bim.ifc.enum.group_entity_type import GroupEntityType


class GroupConfig:
    """Build instructions for an ifc group"""

    def __init__(self, entity_type: GroupEntityType, attributes: dict[str, str]) -> None:
        self.entity_type = entity_type
        self.attributes = attributes
