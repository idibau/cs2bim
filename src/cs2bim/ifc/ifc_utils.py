import logging
from ifcopenshell import file, entity_instance, guid

logger = logging.getLogger(__name__)


def add_ifc_cartesian_point(ifc_file: file, coordinates: tuple[float, float, float]) -> entity_instance:
    return ifc_file.create_entity("IfcCartesianPoint", Coordinates=coordinates)


def add_ifc_person(ifc_file: file, given_name: str) -> entity_instance:
    return ifc_file.create_entity("IfcPerson", GivenName=given_name)


def add_ifc_organization(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcOrganization", Name=name)


def add_ifc_person_and_organization(
    ifc_file: file, the_person: entity_instance, the_organization: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcPersonAndOrganization",
        ThePerson=the_person,
        TheOrganization=the_organization,
    )


def add_ifc_application(
    ifc_file: file, application_developer: entity_instance, version: str, application_full_name: str
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcApplication",
        ApplicationDeveloper=application_developer,
        Version=version,
        ApplicationFullName=application_full_name,
    )


def add_ifc_owner_history(
    ifc_file: file,
    owning_user: entity_instance,
    owning_application: entity_instance,
    timestamp: float,
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcOwnerHistory",
        OwningUser=owning_user,
        OwningApplication=owning_application,
        ChangeAction="ADDED",
        LastModifiedDate=timestamp,
        CreationDate=timestamp,
    )


def add_ifc_axis_2_placement_3D(ifc_file: file, location: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcAxis2Placement3D", Location=location)


def add_ifc_geometric_representation_context(
    ifc_file: file, world_coordinate_system: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-05,
        WorldCoordinateSystem=world_coordinate_system,
    )


def add_ifc_projected_crs(ifc_file: file, map_unit: entity_instance) -> entity_instance:
    return ifc_file.create_entity(
        "IfcProjectedCRS",
        Name="EPSG:2056",
        Description="CH1903+ / LV95 -- Swiss CH1903+ / LV95",
        GeodeticDatum="CH1903+",
        VerticalDatum="LN02",
        MapProjection="CH1903+ / LV95",
        MapUnit=map_unit,
    )


def add_ifc_map_conversion(
    ifc_file: file,
    representation_context: entity_instance,
    projected_crs: entity_instance,
    origin: tuple[float, float, float],
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcMapConversion",
        SourceCRS=representation_context,
        TargetCRS=projected_crs,
        Eastings=origin[0],
        Northings=origin[1],
        OrthogonalHeight=origin[2],
        XAxisAbscissa=1,
        XAxisOrdinate=0,
    )


def add_ifc_si_unit(ifc_file: file, unit_type: str, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcSIUnit", UnitType=unit_type, Name=name)


def add_ifc_plane_angle_measure(ifc_file: file) -> entity_instance:
    return ifc_file.create_entity("IfcPlaneAngleMeasure", 0.017453292519943295)


def add_ifc_measure_with_unit(
    ifc_file: file, value_component: entity_instance, unit_component: entity_instance
) -> entity_instance:
    return ifc_file.create_entity("IfcMeasureWithUnit", ValueComponent=value_component, UnitComponent=unit_component)


def add_ifc_dimensional_exponents(ifc_file: file) -> entity_instance:
    return ifc_file.create_entity(
        "IfcDimensionalExponents",
        LengthExponent=0,
        MassExponent=0,
        TimeExponent=0,
        ElectricCurrentExponent=0,
        ThermodynamicTemperatureExponent=0,
        AmountOfSubstanceExponent=0,
        LuminousIntensityExponent=0,
    )


def add_ifc_conversion_based_unit(
    ifc_file: file, dimensions: entity_instance, conversion_factor: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcConversionBasedUnit",
        Dimensions=dimensions,
        UnitType="PLANEANGLEUNIT",
        Name="DEGREE",
        ConversionFactor=conversion_factor,
    )


def add_ifc_unit_assignment(
    ifc_file: file,
    length_unit: entity_instance,
    area_unit: entity_instance,
    volume_unit: entity_instance,
    conversion_based_unit: entity_instance,
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcUnitAssignment", Units=[length_unit, area_unit, volume_unit, conversion_based_unit]
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


def add_ifc_local_placement(ifc_file: file, relative_placement: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcLocalPlacement", RelativePlacement=relative_placement)


def add_ifc_site(
    ifc_file: file, name: str, owner_history: entity_instance, object_placement: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcSite", Name=name, GlobalId=guid.new(), OwnerHistory=owner_history, ObjectPlacement=object_placement
    )


def add_ifc_rel_aggregates(
    ifc_file: file, relating_object: entity_instance, related_objects: list[entity_instance]
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcRelAggregates",
        GlobalId=guid.new(),
        RelatingObject=relating_object,
        RelatedObjects=related_objects,
    )


def add_ifc_group(ifc_file: file, name: str) -> entity_instance:
    return ifc_file.create_entity("IfcGroup", GlobalId=guid.new(), Name=name)


def add_ifc_distribution_system(ifc_file: file, name: str, object_type: str, predefined_type: str) -> entity_instance:
    return ifc_file.create_entity(
        "IfcDistributionSystem", GlobalId=guid.new(), Name=name, ObjectType=object_type, PredefinedType=predefined_type
    )


def add_ifc_distribution_circuit(ifc_file: file, name: str, object_type: str, predefined_type: str) -> entity_instance:
    return ifc_file.create_entity(
        "IfcDistributionCircuit", GlobalId=guid.new(), Name=name, ObjectType=object_type, PredefinedType=predefined_type
    )


def add_ifc_building_system(ifc_file: file, name: str, object_type: str, predefined_type: str) -> entity_instance:
    return ifc_file.create_entity(
        "IfcBuildingSystem", GlobalId=guid.new(), Name=name, ObjectType=object_type, PredefinedType=predefined_type
    )


def add_ifc_structural_analysis_model(
    ifc_file: file, name: str, object_type: str, predefined_type: str
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcStructuralAnalysisModel",
        GlobalId=guid.new(),
        Name=name,
        ObjectType=object_type,
        PredefinedType=predefined_type,
    )


def add_ifc_zone(ifc_file: file, name: str, object_type: str) -> entity_instance:
    return ifc_file.create_entity("IfcZone", GlobalId=guid.new(), Name=name, ObjectType=object_type)


def add_ifc_rel_assigns_to_group(
    ifc_file: file, related_objects: list[entity_instance], group: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcRelAssignsToGroup", GlobalId=guid.new(), RelatedObjects=related_objects, RelatingGroup=group
    )


def add_ifc_face_outer_bound(ifc_file: file, bound: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcFaceOuterBound", Bound=bound, Orientation=True)


def add_ifc_face(ifc_file: file, bound: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcFace", Bounds=[bound])


def add_ifc_poly_loop(ifc_file: file, polygon: list[tuple[float, float, float]]) -> entity_instance:
    return ifc_file.create_entity("IfcPolyLoop", Polygon=polygon)


def add_ifc_closed_shell(ifc_file: file, cfs_faces: list[entity_instance]) -> entity_instance:
    return ifc_file.create_entity("IfcClosedShell", CfsFaces=cfs_faces)


def add_ifc_faceted_brep(ifc_file: file, outer: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcFacetedBrep", Outer=outer)


def add_ifc_shape_representation(
    ifc_file: file,
    context_of_items: entity_instance,
    representation_type: str,
    item: entity_instance,
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context_of_items,
        RepresentationIdentifier="Body",
        RepresentationType=representation_type,
        Items=[item],
    )


def add_ifc_product_definition_shape(ifc_file: file, representation: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcProductDefinitionShape", Representations=[representation])


def add_ifc_cartesian_point_list_3D(
    ifc_file: file,
    coord_list: list[tuple[float, float, float]],
) -> entity_instance:
    return ifc_file.create_entity("IfcCartesianPointList3D", CoordList=coord_list)


def add_ifc_triangulated_face_set(
    ifc_file: file, cartesian_point_list: entity_instance, coord_index: list[tuple[int, int, int]]
) -> entity_instance:
    return ifc_file.create_entity("IfcTriangulatedFaceSet", Coordinates=cartesian_point_list, CoordIndex=coord_index)


def add_ifc_geographic_element(ifc_file: file, name: str, description: str) -> entity_instance:
    return ifc_file.create_entity("IfcGeographicElement", GlobalId=guid.new(), Name=name, Description=description)


def add_ifc_colour_rgb(ifc_file: file, color: tuple[float, float, float]) -> entity_instance:
    return ifc_file.create_entity("IfcColourRgb", Red=color[0], Green=color[1], Blue=color[2])


def add_ifc_surface_style_shading(
    ifc_file: file, surface_colour: entity_instance, transparency: float
) -> entity_instance:
    return ifc_file.create_entity("IfcSurfaceStyleShading", SurfaceColour=surface_colour, Transparency=transparency)


def add_ifc_surface_style(ifc_file: file, style: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcSurfaceStyle", Side="BOTH", Styles=[style])


def add_ifc_styled_item(ifc_file: file, item: entity_instance, style: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcStyledItem", Item=item, Styles=[style])


def add_ifc_text(ifc_file: file, text: str) -> entity_instance:
    return ifc_file.create_entity("IfcText", text)


def add_ifc_rel_defines_by_properties(
    ifc_file: file, related_objects: list[entity_instance], property_set: entity_instance
) -> entity_instance:
    return ifc_file.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=guid.new(),
        RelatedObjects=related_objects,
        RelatingPropertyDefinition=property_set,
    )


def add_ifc_property_single_value(ifc_file: file, name: str, nominal_value: entity_instance) -> entity_instance:
    return ifc_file.create_entity("IfcPropertySingleValue", Name=name, NominalValue=nominal_value)


def add_ifc_property_set(ifc_file: file, name: str, has_properties: list[entity_instance]) -> entity_instance:
    return ifc_file.create_entity("IfcPropertySet", GlobalId=guid.new(), Name=name, HasProperties=has_properties)
