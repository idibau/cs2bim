class Color:
    """
    Class holding color information

    Attributes
    ----------
    r : float
        red value
    g : float
        green value
    b : float
        blue value
    a : float
        alpha value
    """

    def __init__(self, r: float, g: float, b: float, a: float) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a
