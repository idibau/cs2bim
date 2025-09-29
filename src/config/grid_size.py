from enum import Enum


class GridSize(float, Enum):
    """Available grid sizes for projections"""

    SMALL = 0.5  # 0.5 meters
    LARGE = 2.0  # 2 meters
