from abc import ABC, abstractmethod
from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement
from shapely import Point

from core.ifc.ifc_file import IfcFile


class GmlGeometry(ABC):
    """
    Abstract base class for GML (Geography Markup Language) geometry representations.
    """

    def __init__(self):
        pass

    @abstractmethod
    def from_gml(self, gml: XmlElement, project_origin: Point):
        """
        Parse geometry from a GML element.

        Args:
            gml: The XML element containing GML geometry data.
            project_origin: The project origin to apply for spatial transformation.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("from_gml must be implemented by subclasses")

    @abstractmethod
    def map_to_ifc(self, ifc_file: IfcFile, ifc_style: entity_instance,
                   ifc_representation_sub_context: entity_instance) -> entity_instance:
        """
        Create an IFC Product Definition Shape entity for this geometry.

        Args:
            ifc_file: An instance of the IFC file to which geometry should be added.
            ifc_style: IFC style definition to apply.
            ifc_representation_sub_context: IFC sub-context entity.

        Returns:
            The created IFC Product Definition Shape entity.
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("map_to_ifc must be implemented by subclasses")
