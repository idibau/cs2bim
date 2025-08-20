from core.ifc.model.element import Element


class ClippedTerrain(Element):

    def __init__(self, data: tuple[list[list[float]], list[list[int]]], attributes: dict[str, str] = None, groups: list[str] = None) -> None:
        super().__init__(attributes, groups)
        self.triangles = []
        point_list = data[0]
        index_list = data[1]
        for triangle in index_list:
            p1 = self._create_tuple(point_list[triangle[0]])
            p2 = self._create_tuple(point_list[triangle[1]])
            p3 = self._create_tuple(point_list[triangle[2]])
            self.triangles.append((p1, p2, p3))

    @classmethod
    def _create_tuple(cls, l: list) -> tuple[float, float, float]:
        return float(l[0]), float(l[1]), float(l[2])

