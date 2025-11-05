from core.ifc.model.element import Element


class FeatureElement(Element):

    def __init__(self):
        super().__init__()
        self.element_type = None
        self.spatial_structure =  None
        self.groups = []


    def add_group(self, name: str):
        if not name in self.groups:
            self.groups.append(name)