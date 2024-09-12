from cs2bim.ifc.entity.ifc_element import IfcElement


class IfcModel:
    """
    Class holding all variable data for creating the ifc

    Attributes
    ----------
    file_name : str
        Name of the file
    schema : str
        IFC schema has to be either IFC4 or IFC4x3
    origin: tuple[float, float, float]
        Origin coordinate x, y, z
    elements : list[Element]
        List of all elements that should be added
    """

    def __init__(self, file_name: str, schema: str, origin: tuple[float, float, float]) -> None:
        self.file_name = file_name
        self.schema = schema
        self.origin = origin
        self.feature_classes = {}

    def add_ifc_element(self, feature_class_key: str, element: IfcElement) -> None:
        if not feature_class_key in self.feature_classes:
            self.feature_classes[feature_class_key] = []
        self.feature_classes[feature_class_key].append(element)
