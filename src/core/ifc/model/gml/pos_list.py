class PosList:
    def __init__(self):
        super().__init__()
        self.coordinates = []

    def from_gml(self, gml, project_origin: tuple[float, float, float]):
        coords = list(map(float, gml.text.split()))
        if len(coords) % 3 != 0:
            raise ValueError("PosList is not 3 dimensional")
        if len(coords) < 12:
            raise ValueError("PosList must have at least 4 coordinates")
        if coords[:3] != coords[-3:]:
            raise ValueError("PosList must be closed")
        for i in range(0, len(coords) - 3, 3):
            self.coordinates.append((float(coords[i] - project_origin[0]), float(coords[i + 1] - project_origin[1]),
                                     float(coords[i + 2] - project_origin[2])))
