"""
This module contains wrapper functions to simplify the process of building an ifc using ifcopenshells "create_entity" function.
"""

import datetime
import logging
from ifcopenshell import file, entity_instance, guid

from config.configuration import Color, config
from i18n.translator import Translator

logger = logging.getLogger(__name__)


class IfcFile:
    def __init__(self, schema, file_name, language):
        self.file = file(schema=schema)
        self.file.header.file_name.name = file_name
        self.file.header.file_name.author = [config.ifc.author]
        self.file.header.file_name.organization = [config.ifc.author]
        self.translator = Translator()
        self.language = language

    def write(self, path: str):
        self.file.write(path)

    def create_ifc_cartesian_point(self, coordinates: tuple[float, float, float]) -> entity_instance:
        return self.file.create_entity("IfcCartesianPoint", Coordinates=coordinates)

    def create_ifc_owner_history(self, name: str, version: str, application_full_name: str) -> entity_instance:
        the_person = self.file.create_entity("IfcPerson", GivenName=name)
        the_organization = self.file.create_entity("IfcOrganization", Name=name)
        owning_user = self.file.create_entity(
            "IfcPersonAndOrganization", ThePerson=the_person, TheOrganization=the_organization
        )
        owning_application = self.file.create_entity(
            "IfcApplication",
            ApplicationDeveloper=the_organization,
            Version=version,
            ApplicationFullName=application_full_name,
            ApplicationIdentifier=application_full_name,
        )
        timestamp = int(datetime.datetime.now().timestamp())
        return self.file.create_entity(
            "IfcOwnerHistory",
            OwningUser=owning_user,
            OwningApplication=owning_application,
            ChangeAction="ADDED",
            LastModifiedDate=timestamp,
            CreationDate=timestamp,
        )

    def create_ifc_si_unit(self, unit_type: str, name: str) -> entity_instance:
        return self.file.create_entity("IfcSIUnit", UnitType=unit_type, Name=name)

    def create_ifc_unit_assignment(
            self,
            length_unit: entity_instance,
            area_unit: entity_instance,
            volume_unit: entity_instance,
            degree_unit: entity_instance,
    ) -> entity_instance:
        plane_angle_measure = self.file.create_entity("IfcPlaneAngleMeasure", 0.017453292519943295)
        conversion_factor = self.file.create_entity(
            "IfcMeasureWithUnit", ValueComponent=plane_angle_measure, UnitComponent=degree_unit
        )
        dimensions = self.file.create_entity(
            "IfcDimensionalExponents",
            LengthExponent=0,
            MassExponent=0,
            TimeExponent=0,
            ElectricCurrentExponent=0,
            ThermodynamicTemperatureExponent=0,
            AmountOfSubstanceExponent=0,
            LuminousIntensityExponent=0,
        )
        conversion_based_unit = self.file.create_entity(
            "IfcConversionBasedUnit",
            Dimensions=dimensions,
            UnitType="PLANEANGLEUNIT",
            Name="DEGREE",
            ConversionFactor=conversion_factor,
        )
        return self.file.create_entity(
            "IfcUnitAssignment", Units=[length_unit, area_unit, volume_unit, conversion_based_unit]
        )

    def create_ifc_geometric_representation_context(
            self, location_coordinates: tuple[float, float, float]
    ) -> entity_instance:
        location = self.create_ifc_cartesian_point(location_coordinates)
        world_coordinate_system = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity(
            "IfcGeometricRepresentationContext",
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=1e-05,
            WorldCoordinateSystem=world_coordinate_system,
        )

    def create_ifc_geometric_representation_sub_context(
            self, geometric_representation_context: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcGeometricRepresentationSubContext",
            ContextIdentifier="Body",
            ContextType="Model",
            ParentContext=geometric_representation_context,
            TargetView="MODEL_VIEW",
        )

    def create_ifc_map_conversion(
            self,
            map_unit: entity_instance,
            source_crs: entity_instance,
            origin: tuple[float, float, float],
    ) -> entity_instance:
        target_crs = self.file.create_entity(
            "IfcProjectedCRS",
            Name="EPSG:2056",
            Description="CH1903+ / LV95 -- Swiss CH1903+ / LV95",
            GeodeticDatum="CH1903+",
            VerticalDatum="LN02",
            MapProjection="CH1903+ / LV95",
            MapUnit=map_unit,
        )
        return self.file.create_entity(
            "IfcMapConversion",
            SourceCRS=source_crs,
            TargetCRS=target_crs,
            Eastings=origin[0],
            Northings=origin[1],
            OrthogonalHeight=origin[2],
            XAxisAbscissa=1,
            XAxisOrdinate=0,
        )

    def create_ifc_project(
            self,
            name: str,
            owner_history: entity_instance,
            representation_context: entity_instance,
            units_in_context: entity_instance,
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcProject",
            Name=name,
            GlobalId=guid.new(),
            OwnerHistory=owner_history,
            RepresentationContexts=[representation_context],
            UnitsInContext=units_in_context,
        )

    def create_ifc_local_placement(self, location_coordinates: tuple[float, float, float]) -> entity_instance:
        location = self.create_ifc_cartesian_point(location_coordinates)
        relative_placement = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity("IfcLocalPlacement", RelativePlacement=relative_placement)

    def create_ifc_rel_aggregates(
            self, relating_object: entity_instance, related_objects: list[entity_instance]
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcRelAggregates",
            GlobalId=guid.new(),
            RelatingObject=relating_object,
            RelatedObjects=related_objects,
        )

    def create_ifc_rel_contained_in_spatial_structure(self, related_elements: list[entity_instance],
                                                      relating_structure: entity_instance) -> entity_instance:
        return self.file.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=guid.new(),
            RelatedElements=related_elements,
            RelatingStructure=relating_structure,
        )

    def create_ifc_rel_defines_by_type(self, related_objects, relating_type) -> entity_instance:
        return self.file.create_entity(
            "IfcRelDefinesByType",
            GlobalId=guid.new(),
            RelatedObjects=related_objects,
            RelatingType=relating_type,
        )

    def create_ifc_group(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcGroup", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_distribution_system(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcDistributionSystem", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_distribution_circuit(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcDistributionCircuit", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_building_system(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcBuildingSystem", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_built_system(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcBuiltSystem", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_structural_analysis_model(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcStructuralAnalysisModel", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_zone(self, name: str) -> entity_instance:
        return self.file.create_entity("IfcZone", GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_rel_assigns_to_group(
            self, related_objects: list[entity_instance], group: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcRelAssignsToGroup", GlobalId=guid.new(), RelatedObjects=related_objects, RelatingGroup=group
        )

    def create_ifc_poly_loop(self, polygon: list[entity_instance]) -> entity_instance:
        return self.file.create_entity("IfcPolyLoop", Polygon=polygon)

    def create_ifc_face(self, exterior_poly_loop: entity_instance,
                        interior_poly_loops: list[entity_instance]) -> entity_instance:
        outer_bound = self.file.create_entity("IfcFaceOuterBound", Bound=exterior_poly_loop, Orientation=True)
        inner_bounds = []
        if interior_poly_loops:
            for interior_poly_loop in interior_poly_loops:
                inner_bound = self.file.create_entity("IfcFaceBound", Bound=interior_poly_loop, Orientation=False)
                inner_bounds.append(inner_bound)
        return self.file.create_entity("IfcFace", Bounds=[outer_bound] + inner_bounds)

    def create_ifc_faceted_brep(self, cfs_faces: list[entity_instance]) -> entity_instance:
        outer = self.file.create_entity("IfcClosedShell", CfsFaces=cfs_faces)
        return self.file.create_entity("IfcFacetedBrep", Outer=outer)

    def create_ifc_faceted_brep_with_voids(self, outer_faces: list[entity_instance],
                                           void_faces_list: list[list[entity_instance]]) -> entity_instance:
        outer = self.file.create_entity("IfcClosedShell", CfsFaces=outer_faces)
        voids = [self.file.create_entity("IfcClosedShell", CfsFaces=void_faces) for void_faces in void_faces_list]
        return self.file.create_entity("IfcFacetedBrepWithVoids", Outer=outer, Voids=voids)

    def create_ifc_triangulated_face_set(
            self, coord_list: list[tuple[float, float, float]], coord_index: list[tuple[int, int, int]]
    ) -> entity_instance:
        coordinates = self.file.create_entity("IfcCartesianPointList3D", CoordList=coord_list)
        return self.file.create_entity("IfcTriangulatedFaceSet", Coordinates=coordinates, CoordIndex=coord_index)

    def create_ifc_polygonal_face_set(
            self, coord_list: list[tuple[float, float, float]], faces: list[entity_instance]
    ) -> entity_instance:
        coordinates = self.file.create_entity("IfcCartesianPointList3D", CoordList=coord_list)
        return self.file.create_entity("IfcPolygonalFaceSet", Coordinates=coordinates, Faces=faces)

    def create_ifc_indexed_polygonal_face(
            self, coord_index: list[tuple[int, int, int]]
    ) -> entity_instance:
        return self.file.create_entity("IfcIndexedPolygonalFace", CoordIndex=coord_index)

    def create_ifc_indexed_polygonal_face_with_voids(
            self, coord_index: list[tuple[int, int, int]], inner_cord_indices: list[list[tuple[int, int, int]]]
    ) -> entity_instance:
        return self.file.create_entity("IfcIndexedPolygonalFaceWithVoids", CoordList=coord_index,
                                       InnerCoordIndices=inner_cord_indices)

    def create_ifc_product_definition_shape(
            self, context_of_items: entity_instance, representation_type: str, items: list[entity_instance]
    ) -> entity_instance:
        representation = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context_of_items,
            RepresentationIdentifier="Body",
            RepresentationType=representation_type,
            Items=items
        )
        return self.file.create_entity("IfcProductDefinitionShape", Representations=[representation])

    def create_ifc_geographic_element(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcGeographicElement", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_spatial_zone(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcSpatialZone", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_annotation(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcAnnotation", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_site(
            self, object_placement: entity_instance, representation: entity_instance = None
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcAnnotation", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_building(
            self, object_placement: entity_instance, representation: entity_instance = None
    ) -> entity_instance:
        if representation is None:
            return self.file.create_entity("IfcAnnotation", GlobalId=guid.new(), ObjectPlacement=object_placement)
        else:
            return self.file.create_entity(
                "IfcAnnotation", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
            )

    def create_ifc_geographic_element_type(self) -> entity_instance:
        return self.file.create_entity(
            "IfcGeographicElementType", GlobalId=guid.new()
        )

    def create_ifc_spatial_zone_type(self) -> entity_instance:
        return self.file.create_entity(
            "IfcSpatialZoneType", GlobalId=guid.new()
        )

    def create_ifc_space(self, object_placement: entity_instance, representation: entity_instance
                         ) -> entity_instance:
        return self.file.create_entity(
            "IfcSpace", GlobalId=guid.new(), ObjectPlacement=object_placement,
            Representation=representation
        )

    def create_ifc_building_element_proxy(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcBuildingElementProxy", GlobalId=guid.new(), Name="", ObjectPlacement=object_placement,
            Representation=representation
        )

    def create_ifc_wall(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcWall", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_roof(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcRoof", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_slab(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcSlab", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_surface_style(self, color: Color) -> entity_instance:
        surface_colour = self.file.create_entity("IfcColourRgb", Red=color.r, Green=color.g, Blue=color.b)
        style = self.file.create_entity("IfcSurfaceStyleShading", SurfaceColour=surface_colour, Transparency=color.a)
        return self.file.create_entity("IfcSurfaceStyle", Side="BOTH", Styles=[style])

    def create_ifc_styled_item(self, item: entity_instance, style: entity_instance) -> entity_instance:
        return self.file.create_entity("IfcStyledItem", Item=item, Styles=[style])

    def create_ifc_property_single_value(self, name: str, text: str) -> entity_instance:
        nominal_value = self.file.create_entity("IfcText", self.translator.translate(text, self.language))
        return self.file.create_entity("IfcPropertySingleValue", Name=self.translator.translate(name, self.language),
                                       NominalValue=nominal_value)

    def create_ifc_property_set(
            self, name: str, has_properties: list[entity_instance], related_object: entity_instance
    ) -> entity_instance:
        relating_property_definition = self.file.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name=self.translator.translate(name, self.language),
            HasProperties=has_properties
        )
        self.file.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[related_object],
            RelatingPropertyDefinition=relating_property_definition,
        )
        return relating_property_definition

    def add_attribute(self, item: entity_instance, attribute, value):
        if hasattr(item, attribute):
            setattr(item, attribute, self.translator.translate(value, self.language))
