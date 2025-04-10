from cs2bim.ifc.enum.ifc_version import IfcVersion
from cs2bim.ifc.model.element import Element


class Model:
    """
    Class holding all variable data for creating the ifc

    Attributes
    ----------
    file_name : str
        Name of the file
    schema : str
        IFC schema has to be either IFC4 or IFC4x3
    origin: tuple[float, float, float]
        Origin coordinate (east, north, height)
    elements : list[Element]
        List of all elements that should be added
    """

    def __init__(self, file_name: str, schema: IfcVersion, origin: tuple[float, float, float]) -> None:
        self.file_name = file_name
        self.schema = schema
        self.origin = origin
        self.feature_classes = {}

    def add_element(self, feature_class_key: str, element: Element) -> None:
        if not feature_class_key in self.feature_classes:
            self.feature_classes[feature_class_key] = []
        self.feature_classes[feature_class_key].append(element)
