import pytest
from lxml import etree
from shapely import Point

from core.ifc.model.building.polygon import Polygon


class TestGmlPolygon:
    NS_GML = "http://www.opengis.net/gml"
    nsmap = {"gml": NS_GML}

    def test_polygon_with_hole_orientation_and_area(self):
        # Outer ring: square 0,0,0 to 10,10,0 (closed)
        outer = etree.Element(f"{{{self.NS_GML}}}exterior")
        lr_outer = etree.SubElement(outer, f"{{{self.NS_GML}}}LinearRing")
        pos_outer = etree.SubElement(lr_outer, f"{{{self.NS_GML}}}posList")
        pos_outer.text = "0 0 0  10 0 0  10 10 0  0 10 0  0 0 0"

        # Inner ring (hole): square 2,2,0 to 4,4,0 (closed)
        inner = etree.Element(f"{{{self.NS_GML}}}interior")
        lr_inner = etree.SubElement(inner, f"{{{self.NS_GML}}}LinearRing")
        pos_inner = etree.SubElement(lr_inner, f"{{{self.NS_GML}}}posList")
        pos_inner.text = "2 2 0  4 2 0  4 4 0  2 4 0  2 2 0"

        gml_poly = etree.Element(f"{{{self.NS_GML}}}Polygon")
        gml_poly.append(outer)
        gml_poly.append(inner)

        origin = Point(0, 0, 0)
        poly = Polygon()
        poly.from_gml(gml_poly, origin)

        # Expect one outer ring and one hole
        assert len(poly.exterior.coordinates) == 4
        assert len(poly.interior) == 1
        assert len(poly.interior[0].coordinates) == 4

    def test_invalid_open_ring_raises(self):
        outer = etree.Element(f"{{{self.NS_GML}}}exterior")
        lr_outer = etree.SubElement(outer, f"{{{self.NS_GML}}}LinearRing")
        pos_outer = etree.SubElement(lr_outer, f"{{{self.NS_GML}}}posList")
        # Not closed: missing return to start
        pos_outer.text = "0 0 0  1 0 0  1 1 0  0 1 0"

        gml_poly = etree.Element(f"{{{self.NS_GML}}}Polygon")
        gml_poly.append(outer)

        with pytest.raises(ValueError,  match="PosList must be closed"):
            Polygon().from_gml(gml_poly, Point(0, 0, 0))
