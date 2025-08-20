from core.ifc.model.element import Element


class Building(Element):

    def __init__(self, points, attributes: dict[str, str] = None, groups: list[str] = None) -> None:
        super().__init__(attributes, groups)
        self.points = points
