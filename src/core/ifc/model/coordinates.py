class Coordinates:
    def __init__(self, x: int | float, y: int | float, z: int | float):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_tuple(self) -> tuple[float, float, float]:
        return self.x, self.y, self.z

    def __str__(self) -> str:
        return f"Coordinate(x={self.x}, y={self.y}, z={self.z})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Coordinates):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))
