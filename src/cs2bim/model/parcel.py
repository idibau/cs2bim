class Parcel:
    """Dataclass for parcel information"""

    def __init__(self, wkt: str, nbident: str, nummer: str, egris_egrid: str) -> None:
        self.wkt = wkt
        self.nbident = nbident
        self.nummer = nummer
        self.egris_egrid = egris_egrid
