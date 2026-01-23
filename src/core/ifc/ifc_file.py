"""
This module contains wrapper functions to simplify the process of building an ifc using ifcopenshells "create_entity" function.
"""

import math
import datetime
import logging
from ifcopenshell import file, entity_instance, guid
from shapely import Point

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

    def create_ifc_cartesian_point(self, point: Point) -> entity_instance:
        return self.file.create_entity("IfcCartesianPoint", Coordinates=point.coords[0])

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

    def create_ifc_geometric_representation_context(self, location_coordinates: Point) -> entity_instance:
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
            origin: Point,
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
            Eastings=origin.x,
            Northings=origin.y,
            OrthogonalHeight=origin.z,
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

    def create_ifc_local_placement(self, location_coordinates: Point) -> entity_instance:
        location = self.create_ifc_cartesian_point(location_coordinates)
        relative_placement = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity("IfcLocalPlacement", RelativePlacement=relative_placement)

    def create_relative_ifc_local_placement(self, placement_rel_to: entity_instance,
                                            location_coordinates: Point) -> entity_instance:
        location = self.create_ifc_cartesian_point(location_coordinates)
        relative_placement = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity("IfcLocalPlacement",
                                       PlacementRelTo=placement_rel_to,
                                       RelativePlacement=relative_placement)

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
            self, coord_list: list[Point], coord_index: list[tuple[int, int, int]]
    ) -> entity_instance:
        coordinates = self.file.create_entity("IfcCartesianPointList3D",
                                              CoordList=[coord.coords[0] for coord in coord_list])
        return self.file.create_entity("IfcTriangulatedFaceSet", Coordinates=coordinates, CoordIndex=coord_index)

    def create_ifc_polygonal_face_set(
            self, coord_list: list[Point], faces: list[entity_instance]
    ) -> entity_instance:
        coordinates = self.file.create_entity("IfcCartesianPointList3D",
                                              CoordList=[coord.coords[0] for coord in coord_list])
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

    def create_ifc_geographic_element_type(self) -> entity_instance:
        return self.file.create_entity(
            "IfcGeographicElementType", GlobalId=guid.new()
        )

    def create_ifc_spatial_zone(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        return self.file.create_entity(
            "IfcSpatialZone", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_spatial_zone_type(self) -> entity_instance:
        return self.file.create_entity(
            "IfcSpatialZoneType", GlobalId=guid.new()
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
        if representation is None:
            return self.file.create_entity("IfcSite", GlobalId=guid.new(), ObjectPlacement=object_placement)
        return self.file.create_entity(
            "IfcSite", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_building(
            self, object_placement: entity_instance, representation: entity_instance = None
    ) -> entity_instance:
        if representation is None:
            return self.file.create_entity("IfcBuilding", GlobalId=guid.new(), ObjectPlacement=object_placement)
        else:
            return self.file.create_entity(
                "IfcBuilding", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
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

    def create_ifc_pipe_segment(self, object_placement: entity_instance, representation: entity_instance
                                ) -> entity_instance:
        return self.file.create_entity(
            "IfcPipeSegment", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_pipe_segment_type(self) -> entity_instance:
        return self.file.create_entity(
            "IfcPipeSegmentType", GlobalId=guid.new()
        )

    def create_ifc_distribution_flow_element(self, object_placement: entity_instance, representation: entity_instance
                                             ) -> entity_instance:
        return self.file.create_entity(
            "IfcDistributionFlowElement", GlobalId=guid.new(), ObjectPlacement=object_placement,
            Representation=representation
        )

    def create_ifc_swept_disk_solid(self, directrix: entity_instance, radius: float) -> entity_instance:
        return self.file.create_entity(
            "IfcSweptDiskSolid",
            Directrix=directrix,
            Radius=radius
        )

    def create_ifc_polyline(self, points: list[Point]) -> entity_instance:
        if len(points) > 1 and points[0] == points[-1]:
            cartesian_points = [self.create_ifc_cartesian_point(point) for point in points[:-1]]
            cartesian_points.append(cartesian_points[0])
        else:
            cartesian_points = [self.create_ifc_cartesian_point(point) for point in points]
        return self.file.create_entity(
            "IfcPolyline",
            Points=cartesian_points
        )

    def create_ifc_arbitrary_closed_profile_def(self, outer_curve: list[Point]):
        ifc_outer_curve = self.create_ifc_polyline(outer_curve)
        return self.file.create_entity(
            "IfcArbitraryClosedProfileDef",
            ProfileType="AREA",
            OuterCurve=ifc_outer_curve
        )

    def create_ifc_rectangle_profile_def(self, x_dim: float, y_dim: float) -> entity_instance:
        return self.file.create_entity(
            "IfcRectangleProfileDef",
            ProfileType="AREA",
            XDim=x_dim,
            YDim=y_dim
        )

    def create_ifc_circle_profile_def(self, radius: float) -> entity_instance:
        return self.file.create_entity(
            "IfcCircleProfileDef",
            ProfileType="AREA",
            Radius=radius
        )

    def create_ifc_sectioned_solid_horizontal(self, ifc_profile_def: entity_instance,
                                              directrix: entity_instance) -> entity_instance:
        ifc_start_point = self.create_ifc_axis_2_placement_linear(
            self.create_ifc_point_by_distance_expression(0.0, directrix))
        ifc_end_point = self.create_ifc_axis_2_placement_linear(
            self.create_ifc_point_by_distance_expression(1.0, directrix))
        return self.file.create_entity(
            "IfcSectionedSolidHorizontal",
            Directrix=directrix,
            CrossSections=[ifc_profile_def, ifc_profile_def],
            CrossSectionPositions=[ifc_start_point, ifc_end_point]
        )

    def create_ifc_fixed_reference_swept_area_solid(self, ifc_profile_def: entity_instance, directrix: entity_instance):
        fixed_ref = self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        return self.file.create_entity("IfcFixedReferenceSweptAreaSolid",
                                       SweptArea=ifc_profile_def,
                                       Directrix=directrix,
                                       FixedReference=fixed_ref
                                       )

    def create_ifc_extruded_area_solid(self, ifc_profile_def: entity_instance,
                                       position: Point, depth: float, orientation: float):
        if orientation:
            angle_rad = math.radians(90.0 - orientation)
            x = math.cos(angle_rad)
            y = math.sin(angle_rad)
            ifc_direction_orientation = self.file.create_entity("IfcDirection", DirectionRatios=[x, y])
            ifc_axis_2_placement_3d = self.file.create_entity("IfcAxis2Placement3D",
                                                              Location=self.create_ifc_cartesian_point(position),
                                                              RefDirection=ifc_direction_orientation)
        else:
            ifc_axis_2_placement_3d = self.file.create_entity("IfcAxis2Placement3D",
                                                              Location=self.create_ifc_cartesian_point(position))
        ifc_direction = self.file.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0])
        return self.file.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=ifc_profile_def,
            Position=ifc_axis_2_placement_3d,
            ExtrudedDirection=ifc_direction,
            Depth=depth
        )

    def create_ifc_axis_2_placement_linear(self, point: entity_instance):
        return self.file.create_entity(
            "IfcAxis2PlacementLinear",
            Location=point
        )

    def create_ifc_point_by_distance_expression(self, distance_along: float, basis_curve: entity_instance):
        return self.file.create_entity(
            "IfcPointByDistanceExpression",
            DistanceAlong=self.file.createIfcParameterValue(distance_along),
            BasisCurve=basis_curve,
        )

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

    def create_attribute(self, item: entity_instance, attribute, value):
        if hasattr(item, attribute):
            setattr(item, attribute, self.translator.translate(value, self.language))
