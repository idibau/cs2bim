"""
This module contains wrapper funcitons to simplify the process of building an ifc using ifcopenshells "create_entity" function.
"""

import logging
import datetime
from ifcopenshell import file, entity_instance, guid

from cs2bim.ifc.model.color import Color

logger = logging.getLogger(__name__)


def add_ifc_cartesian_point(ifc_file: file, coordinates: tuple[float, float, float]) -> entity_instance:
    return ifc_file.create_entity("IfcCartesianPoint", Coordinates=coordinates)


def add_ifc_owner_history(ifc_file: file, name: str, version: str, application_full_name: str) -> entity_instance:
    the_person = ifc_file.create_entity("IfcPerson", GivenName=name)
    the_organization = ifc_file.create_entity("IfcOrganization", Name=name)
    owning_user = ifc_file.create_entity(
        "IfcPersonAndOrganization", ThePerson=the_person, TheOrganization=the_organization
    )
    owning_application = ifc_file.create_entity(
        "IfcApplication",
        ApplicationDeveloper=the_organization,
        Version=version,
        ApplicationFullName=application_full_name,
        ApplicationIdentifier=application_full_name,
    )
    timestamp = int(datetime.datetime.now().timestamp())
    return ifc_file.create_entity(
        "IfcOwnerHistory",
        OwningUser=owning_user,
        OwningApplication=owning_application,
        ChangeAction="ADDED",
        LastModifiedDate=timestamp,
        CreationDate=timestamp,
    )


def add_ifc_si_unit(ifc_file: file, unit_type: str, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcSIUnit", UnitType=unit_type, Name=name)


def add_ifc_unit_assignment(
    ifc_file: file,
    length_unit: entity_instance,
    area_unit: entity_instance,
    volume_unit: entity_instance,
    degree_unit: entity_instance,
) -> entity_instance:
    plane_angle_measure = ifc_file.create_entity("IfcPlaneAngleMeasure", 0.017453292519943295)
    conversion_factor = ifc_file.create_entity(
        "IfcMeasureWithUnit", ValueComponent=plane_angle_measure, UnitComponent=degree_unit
    )
    dimensions = ifc_file.create_entity(
        "IfcDimensionalExponents",
        LengthExponent=0,
        MassExponent=0,
        TimeExponent=0,
        ElectricCurrentExponent=0,
        ThermodynamicTemperatureExponent=0,
        AmountOfSubstanceExponent=0,
        LuminousIntensityExponent=0,
    )
    conversion_based_unit = ifc_file.create_entity(
        "IfcConversionBasedUnit",
        Dimensions=dimensions,
        UnitType="PLANEANGLEUNIT",
        Name="DEGREE",
        ConversionFactor=conversion_factor,
    )
    return ifc_file.create_entity(
        "IfcUnitAssignment", Units=[length_unit, area_unit, volume_unit, conversion_based_unit]
    )


def add_ifc_geometric_representation_context(
    ifc_file: file, location_coordinates: tuple[float, float, float]
) -> entity_instance:
    location = add_ifc_cartesian_point(ifc_file, location_coordinates)
    world_coordinate_system = ifc_file.create_entity("IfcAxis2Placement3D", Location=location)
    return ifc_file.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-05,
        WorldCoordinateSystem=world_coordinate_system,
    )


def add_ifc_geometric_representation_sub_context(
    ifc_file: file, geometric_representation_context: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcGeometricRepresentationSubContext",
        ContextIdentifier="Body",
        ContextType="Model",
        ParentContext=geometric_representation_context,
        TargetView="MODEL_VIEW",
    )


def add_ifc_map_conversion(
    ifc_file: file,
    map_unit: entity_instance,
    source_crs: entity_instance,
    origin: tuple[float, float, float],
) -> entity_instance:
    target_crs = ifc_file.create_entity(
        "IfcProjectedCRS",
        Name="EPSG:2056",
        Description="CH1903+ / LV95 -- Swiss CH1903+ / LV95",
        GeodeticDatum="CH1903+",
        VerticalDatum="LN02",
        MapProjection="CH1903+ / LV95",
        MapUnit=map_unit,
    )
    return ifc_file.create_entity(
        "IfcMapConversion",
        SourceCRS=source_crs,
        TargetCRS=target_crs,
        Eastings=origin[0],
        Northings=origin[1],
        OrthogonalHeight=origin[2],
        XAxisAbscissa=1,
        XAxisOrdinate=0,
    )


def add_ifc_project(
    ifc_file: file,
    name: str,
    owner_history: entity_instance,
    representation_context: entity_instance,
    units_in_context: entity_instance,
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcProject",
        Name=name,
        GlobalId=guid.new(),
        OwnerHistory=owner_history,
        RepresentationContexts=[representation_context],
        UnitsInContext=units_in_context,
    )


def add_ifc_local_placement(ifc_file: file, location_coordinates: tuple[float, float, float]) -> entity_instance:
    location = add_ifc_cartesian_point(ifc_file, location_coordinates)
    relative_placement = ifc_file.create_entity("IfcAxis2Placement3D", Location=location)
    return ifc_file.create_entity("IfcLocalPlacement", RelativePlacement=relative_placement)


def add_ifc_site(
    ifc_file: file,
    object_placement: entity_instance,
    project: entity_instance,
) -> entity_instance:
    site = ifc_file.create_entity("IfcSite", GlobalId=guid.new(), ObjectPlacement=object_placement)
    add_ifc_rel_aggregates(ifc_file, project, [site])
    return site


def add_ifc_rel_aggregates(
    ifc_file: file, relating_object: entity_instance, related_objects: list[entity_instance]
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcRelAggregates",
        GlobalId=guid.new(),
        RelatingObject=relating_object,
        RelatedObjects=related_objects,
    )

def add_ifc_rel_contained_in_spatial_structure(
    ifc_file: file, related_elements: list[entity_instance], relating_structure: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=guid.new(),
        RelatedElements=related_elements,
        RelatingStructure=relating_structure,
    )


def add_ifc_group(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcGroup", GlobalId=guid.new(), Name=name)


def add_ifc_distribution_system(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcDistributionSystem", GlobalId=guid.new(), Name=name)


def add_ifc_distribution_circuit(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcDistributionCircuit", GlobalId=guid.new(), Name=name)


def add_ifc_building_system(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcBuildingSystem", GlobalId=guid.new(), Name=name)


def add_ifc_structural_analysis_model(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcStructuralAnalysisModel", GlobalId=guid.new(), Name=name)


def add_ifc_zone(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcZone", GlobalId=guid.new(), Name=name)


def add_ifc_rel_assigns_to_group(
    ifc_file: file, related_objects: list[entity_instance], group: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcRelAssignsToGroup", GlobalId=guid.new(), RelatedObjects=related_objects, RelatingGroup=group
    )


def add_ifc_face(ifc_file: file, polygon: list[tuple[float, float, float]]) -> entity_instance:
    poly_loop = ifc_file.create_entity("IfcPolyLoop", Polygon=polygon)
    bound = ifc_file.create_entity("IfcFaceOuterBound", Bound=poly_loop, Orientation=True)
    return ifc_file.create_entity("IfcFace", Bounds=[bound])


def add_ifc_faceted_brep(ifc_file: file, cfs_faces: list[entity_instance]) -> entity_instance:
    outer = ifc_file.create_entity("IfcClosedShell", CfsFaces=cfs_faces)
    return ifc_file.create_entity("IfcFacetedBrep", Outer=outer)


def add_ifc_product_definition_shape(
    ifc_file: file, context_of_items: entity_instance, representation_type: str, item: entity_instance
) -> entity_instance:
    representation = ifc_file.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context_of_items,
        RepresentationIdentifier="Body",
        RepresentationType=representation_type,
        Items=[item],
    )
    return ifc_file.create_entity("IfcProductDefinitionShape", Representations=[representation])


def add_ifc_triangulated_face_set(
    ifc_file: file, coord_list: list[tuple[float, float, float]], coord_index: list[tuple[int, int, int]]
) -> entity_instance:
    coordinates = ifc_file.create_entity("IfcCartesianPointList3D", CoordList=coord_list)
    return ifc_file.create_entity("IfcTriangulatedFaceSet", Coordinates=coordinates, CoordIndex=coord_index)


def add_ifc_geographic_element(
    ifc_file: file, object_placement: entity_instance, representaion: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcGeographicElement", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representaion
    )


def add_ifc_surface_style(ifc_file: file, color: Color) -> entity_instance:
    surface_colour = ifc_file.create_entity("IfcColourRgb", Red=color.r, Green=color.g, Blue=color.b)
    style = ifc_file.create_entity("IfcSurfaceStyleShading", SurfaceColour=surface_colour, Transparency=color.a)
    return ifc_file.create_entity("IfcSurfaceStyle", Side="BOTH", Styles=[style])


def add_ifc_styled_item(ifc_file: file, item: entity_instance, style: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcStyledItem", Item=item, Styles=[style])


def add_ifc_property_single_value(ifc_file: file, name: str, text: str) -> entity_instance:
    nominal_value = ifc_file.create_entity("IfcText", text)
    return ifc_file.create_entity("IfcPropertySingleValue", Name=name, NominalValue=nominal_value)


def add_ifc_property_set(
    ifc_file: file, name: str, has_properties: list[entity_instance], related_object: entity_instance
) -> entity_instance:
    relating_property_definition = ifc_file.create_entity(
        "IfcPropertySet", GlobalId=guid.new(), Name=name, HasProperties=has_properties
    )
    ifc_file.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=guid.new(),
        RelatedObjects=[related_object],
        RelatingPropertyDefinition=relating_property_definition,
    )
    return relating_property_definition
