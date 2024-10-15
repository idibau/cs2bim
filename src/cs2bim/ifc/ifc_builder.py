from ifcopenshell import file

from cs2bim.config.configuration import config
from cs2bim.config.geo_referencing import GeoReferencing
from cs2bim.config.feature_class import FeatureClass
from cs2bim.ifc.ifc_utils import *
from cs2bim.ifc.ifc_model import IfcModel
from cs2bim.ifc.entity.ifc_group import IfcGroup
from cs2bim.ifc.entity.ifc_spatial_structure import IfcSpatialStructureEntityType
from cs2bim.ifc.entity.ifc_element import IfcElementEntityType
from cs2bim.ifc.entity.ifc_group import IfcGroupEntityType
from cs2bim.geometry.triangulation import Triangulation, TriangulationRepresentationType


logger = logging.getLogger(__name__)


class IfcBuilder:

    def __init__(self):
        pass

    def build(self, ifc_model: IfcModel) -> file:
        """Builds an ifcopenshell ifc file based on a model object"""
        logger.info(f"initialize new ifc writer for ifc '{ifc_model.file_name}'")
        ifc_file = file(schema=ifc_model.schema)
        ifc_file.wrapped_data.header.file_name.name = ifc_model.file_name

        logger.info(f"build ifc")
        owner_history = add_ifc_owner_history(ifc_file, config.author, config.version, config.application_name)
        length_unit = add_ifc_si_unit(ifc_file, "LENGTHUNIT", "METRE")
        area_unit = add_ifc_si_unit(ifc_file, "AREAUNIT", "SQUARE_METRE")
        volume_unit = add_ifc_si_unit(ifc_file, "VOLUMEUNIT", "CUBIC_METRE")
        degree_unit = add_ifc_si_unit(ifc_file, "PLANEANGLEUNIT", "RADIAN")
        unit_assignment = add_ifc_unit_assignment(ifc_file, length_unit, area_unit, volume_unit, degree_unit)

        if config.geo_referencing == GeoReferencing.LO_GEO_REF_40:
            location = ifc_model.origin
        else:
            location = (0.0, 0.0, 0.0)
        representation_context = add_ifc_geometric_representation_context(ifc_file, location)

        if config.geo_referencing == GeoReferencing.LO_GEO_REF_50:
            add_ifc_map_conversion(ifc_file, length_unit, representation_context, ifc_model.origin)

        project = add_ifc_project(ifc_file, config.project_name, owner_history, representation_context, unit_assignment)

        if config.geo_referencing == GeoReferencing.LO_GEO_REF_30:
            location = ifc_model.origin
        else:
            location = (0.0, 0.0, 0.0)
        local_placement = add_ifc_local_placement(ifc_file, location)

        group_entities = {}
        spatial_structures_entities = {}
        for feature_class_key, elements in ifc_model.feature_classes.items():
            feature_class = config.feature_classes[feature_class_key]
            logger.info(f"FeatureClass {feature_class_key}: build ifc spatial structure")
            spatial_structure = feature_class.spatial_structure
            if not spatial_structure.get_key() in spatial_structures_entities:
                if spatial_structure.type == IfcSpatialStructureEntityType.IFC_SITE:
                    site = add_ifc_site(ifc_file, owner_history, local_placement, project)
                    spatial_structures_entities[spatial_structure.get_key()] = site
                else:
                    raise Exception(
                        f"builing step for structure entity type {spatial_structure.type.name} not implemented"
                    )
                spatial_structures_entity = spatial_structures_entities[spatial_structure.get_key()]
                for attribute, value in spatial_structure.attributes.items():
                    if hasattr(spatial_structures_entity, attribute):
                        setattr(spatial_structures_entity, attribute, value)

            logger.info(f"FeatureClass {feature_class_key}: build ifc elements")
            style_entity = add_ifc_surface_style(ifc_file, feature_class.color_definition)

            groups = {}
            element_entities = []
            for element in elements:
                if isinstance(element.geometry, Triangulation):
                    representation_type = config.triangulation_representation_type
                    if representation_type == TriangulationRepresentationType.TESSELLATION:
                        vertices_dict = {}
                        vertices = []
                        for triangle in element.geometry.triangles:
                            for vertex in triangle:
                                if not vertex in vertices_dict:
                                    vertices_dict[vertex] = len(vertices) + 1
                                    vertices.append(vertex)
                        point_index_list = [
                            tuple(vertices_dict[v] for v in triangle) for triangle in element.geometry.triangles
                        ]
                        item = add_ifc_triangulated_face_set(ifc_file, vertices, point_index_list)
                    elif representation_type == TriangulationRepresentationType.BREP:
                        vertex_dict = {}
                        faces = []
                        for triangle in element.geometry.triangles:
                            vertices = []
                            for vertex in triangle:
                                if vertex not in vertex_dict:
                                    vertex_dict[vertex] = add_ifc_cartesian_point(ifc_file, vertex)
                                vertices.append(vertex_dict[vertex])
                            face = add_ifc_face(ifc_file, vertices)
                            faces.append(face)
                        item = add_ifc_faceted_brep(ifc_file, faces)
                    else:
                        raise Exception(
                            f"builing step for triangulation representation type {representation_type.name} not implemented"
                        )
                else:
                    raise Exception(f"builing step for geometry class {type(element.geometry)} not implemented")

                add_ifc_styled_item(ifc_file, item, style_entity)

                product_definition_shape = add_ifc_product_definition_shape(
                    ifc_file, representation_context, representation_type.value, item
                )
                if feature_class.entity_type == IfcElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                    element_entity = add_ifc_geographic_element(ifc_file, product_definition_shape)
                else:
                    raise Exception(
                        f"builing step for feature class entity type {feature_class.entity_type.name} not implemented"
                    )
                for attribute, value in element.attributes.items():
                    if hasattr(element_entity, attribute):
                        setattr(element_entity, attribute, value)

                for property_set in element.property_sets.values():
                    property_entites = []
                    for key, value in property_set.properties.items():
                        property_entites.append(add_ifc_property_single_value(ifc_file, key, value))
                    property_set = add_ifc_property_set(ifc_file, property_set.name, property_entites, element_entity)

                element_entities.append(element_entity)

                for group in element.groups:
                    if not group in groups:
                        groups[group] = []
                    groups[group].append(element_entity)

            add_ifc_rel_aggregates(ifc_file, spatial_structures_entities[spatial_structure.get_key()], element_entities)

            logger.info(f"FeatureClass {feature_class_key}: build ifc groups")
            for group_definition, group_element_entities in groups.items():
                path = []
                for group in group_definition.split("."):
                    parent_group_path = ".".join(path)
                    path.append(group)
                    group_path = ".".join(path)
                    if not group_path in group_entities:
                        if group_path in config.groups:
                            ifc_group = config.groups[group_definition]
                            if ifc_group.entity_type == IfcGroupEntityType.IFC_DISTRIBUTION_SYSTEM:
                                group_entities[group_path] = add_ifc_distribution_system(ifc_file, group)
                            elif ifc_group.entity_type == IfcGroupEntityType.IFC_DISTRIBUTION_CIRCUIT:
                                group_entities[group_path] = add_ifc_distribution_circuit(ifc_file, group)
                            elif ifc_group.entity_type == IfcGroupEntityType.IFC_BUILDING_SYSTEM:
                                group_entities[group_path] = add_ifc_building_system(ifc_file, group)
                            elif ifc_group.entity_type == IfcGroupEntityType.IFC_STRUCTURAL_ANALYSIS_MODEL:
                                group_entities[group_path] = add_ifc_structural_analysis_model(ifc_file, group)
                            elif ifc_group.entity_type == IfcGroupEntityType.IFC_ZONE:
                                group_entities[group_path] = add_ifc_zone(ifc_file, group)
                            else:
                                raise Exception(
                                    f"builing step for ifc group entity {type(ifc_group.entity_type)} not implemented"
                                )
                            group_entity = group_entities[group_path]
                            for attribute, value in ifc_group.attributes.items():
                                if hasattr(group_entity, attribute):
                                    setattr(group_entity, attribute, value)
                        else:
                            group_entities[group_path] = add_ifc_group(ifc_file, group)

                        if not parent_group_path == "":
                            add_ifc_rel_assigns_to_group(
                                ifc_file, [group_entities[group_path]], group_entities[parent_group_path]
                            )
                add_ifc_rel_assigns_to_group(ifc_file, group_element_entities, group_entities[group_definition])

        logger.info("completed ifc build")

        return ifc_file
