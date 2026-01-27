import pytest
from shapely import Point

from core.ifc.model.building.pos_list import PosList
from lxml import etree


class TestPosList:

    def test_from_gml_validates_and_offsets_with_project_origin(self):
        # Create a closed 3D posList with 4 coordinates (12 numbers)
        values = [
            2600000.0, 1200000.0, 400.0,
            2600001.0, 1200000.0, 401.0,
            2600001.0, 1200001.0, 402.0,
            2600000.0, 1200000.0, 400.0,
        ]
        gml = etree.Element("posList")
        gml.text = " ".join(str(v) for v in values)

        origin = Point(2600000.0, 1200000.0, 400.0)
        pl = PosList()
        pl.from_gml(gml, origin)

        # After offset, first coordinate becomes (0,0,0)
        assert len(pl.coordinates) == 3  # last coordinate is closing point and not stored
        assert pl.coordinates[0] == Point(0.0, 0.0, 0.0)

    def test_from_gml_rejects_non_3d_or_unclosed(self):
        origin = Point(0, 0, 0)
        # Not closed
        gml1 = etree.Element("posList")
        gml1.text = "1 2 3 4 5 6"
        with pytest.raises(ValueError):
            PosList().from_gml(gml1, origin)

        # Not multiple of 3
        gml2 = etree.Element("posList")
        gml2.text = "1 2 3 4 5 6 7"
        with pytest.raises(ValueError):
            PosList().from_gml(gml2, origin)

        # Less than 4 coordinates (12 numbers)
        gml3 = etree.Element("posList")
        gml3.text = "1 2 3 1 2 3 1 2 3"  # 3 coords only
        with pytest.raises(ValueError):
            PosList().from_gml(gml3, origin)
