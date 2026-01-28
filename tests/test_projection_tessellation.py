from shapely import Point

from core.ifc.model.projection.projection import Projection
from core.ifc.model.projection.tessellation import Tessellation


class DummyIfcFile:
    def __init__(self):
        self.calls = []

    def create_ifc_triangulated_face_set(self, vertices, indices):
        # record and return a dummy handle
        self.calls.append(("create_ifc_triangulated_face_set", vertices, indices))
        return {"type": "IfcTriangulatedFaceSet", "vertices": vertices, "indices": indices}

    def create_ifc_product_definition_shape(self, sub_ctx, label, items):
        self.calls.append(("create_ifc_product_definition_shape", label, items))
        return {"type": "IfcProductDefinitionShape", "items": items}

    def create_ifc_styled_item(self, ifc_face_set, ifc_style):
        self.calls.append(("create_ifc_styled_item", ifc_face_set, ifc_style))

    def create_ifc_local_placement(self, coord):
        self.calls.append(("create_ifc_local_placement", coord))
        return {"type": "IfcLocalPlacement", "coord": coord}

    def create_relative_ifc_local_placement(self, placement_rel_to, coord):
        self.calls.append(("create_ifc_local_placement", coord))
        return {"type": "IfcLocalPlacement", "coord": coord}

    def create_ifc_product(self, entity, placement, shape):
        self.calls.append(("create_ifc_product", entity, placement, shape))
        return {"type": entity}

class TestTessellation:

    def test_map_to_ifc_builds_unique_vertices_and_indices(self):
        v1, v2, v3, v4 = Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0), Point(1, 1, 0)
        # Two triangles that share an edge (v2-v3)
        faces = [
            (v1, v2, v3),
            (v2, v4, v3),
        ]
        tess = Tessellation(faces)
        dummy = DummyIfcFile()
        face_set = tess.map_to_ifc(dummy)

        # Expect unique vertices condensed, indices referencing same objects
        assert face_set["type"] == "IfcTriangulatedFaceSet"
        # Vertices must include exactly the unique set {v1, v2, v3, v4}
        assert len(face_set["vertices"]) == 4
        # Two triangles => two index rows of length 3
        assert len(face_set["indices"]) == 2
        assert all(len(row) == 3 for row in face_set["indices"])


class TestProjection:

    def test_projection_init_and_map_to_ifc_geographic_element(self):
        points = [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
        indices = [[0, 1, 2]]

        proj = Projection((points, indices))
        assert len(proj.triangles) == 1

        dummy = DummyIfcFile()
        # The Projection.map_to_ifc chooses based on entity, we select IFC_GEOGRAPHIC_ELEMENT path
        # Pass sentinel to go through first branch
        elem = proj.map_to_ifc(dummy, "IfcGeographicElement", None, None, None)
        assert isinstance(elem, dict) and elem.get("type") == "IfcGeographicElement"
