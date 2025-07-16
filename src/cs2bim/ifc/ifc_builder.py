from ifcopenshell import file

from cs2bim.ifc.ifc_utils import *
from cs2bim.ifc.model.model import Model
from cs2bim.ifc.enum.geo_referencing import GeoReferencing
from cs2bim.ifc.enum.group_entity_type import GroupEntityType
from cs2bim.ifc.enum.element_entity_type import ElementEntityType
from cs2bim.ifc.enum.spatial_structure_entity_type import SpatialStructureEntityType
from cs2bim.ifc.enum.triangulation_representation_type import TriangulationRepresentationType
from cs2bim.ifc.geometry.triangulation import Triangulation
from cs2bim.ifc.config.feature_class import FeatureClass
from cs2bim.ifc.config.group_config import GroupConfig


logger = logging.getLogger(__name__)


class IfcBuilder:

    def __init__(
        self,
        author: str,
        version: str,
        application_name: str,
        project_name: str,
        geo_referencing: GeoReferencing,
        triangulation_representation_type: TriangulationRepresentationType,
        feature_classes: dict[str, FeatureClass],
        groups: dict[str, GroupConfig],
    ):
        self.author = author
        self.version = version
        self.application_name = application_name
        self.project_name = project_name
        self.geo_referencing = geo_referencing
        self.triangulation_representation_type = triangulation_representation_type
        self.feature_classes = feature_classes
        self.groups = groups

    def build(self, model: Model) -> file:
        """Builds an ifcopenshell ifc file based on a model object"""
        logger.info(f"initialize new ifc writer for ifc '{model.file_name}'")
        ifc_file = file(schema=model.schema.value)
        ifc_file.wrapped_data.header.file_name.name = model.file_name

        logger.info(f"build ifc")
        ifc_owner_history = add_ifc_owner_history(ifc_file, self.author, self.version, self.application_name)
        ifc_length_unit = add_ifc_si_unit(ifc_file, "LENGTHUNIT", "METRE")
        ifc_area_unit = add_ifc_si_unit(ifc_file, "AREAUNIT", "SQUARE_METRE")
        ifc_volume_unit = add_ifc_si_unit(ifc_file, "VOLUMEUNIT", "CUBIC_METRE")
        ifc_degree_unit = add_ifc_si_unit(ifc_file, "PLANEANGLEUNIT", "RADIAN")
        ifc_unit_assignment = add_ifc_unit_assignment(
            ifc_file, ifc_length_unit, ifc_area_unit, ifc_volume_unit, ifc_degree_unit
        )

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_40:
            location = model.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_representation_context = add_ifc_geometric_representation_context(ifc_file, location)
        ifc_representation_sub_context = add_ifc_geometric_representation_sub_context(ifc_file, ifc_representation_context)

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_50:
            add_ifc_map_conversion(ifc_file, ifc_length_unit, ifc_representation_context, model.origin)

        ifc_project = add_ifc_project(
            ifc_file, self.project_name, ifc_owner_history, ifc_representation_context, ifc_unit_assignment
        )

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_30:
            location = model.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_local_placement = add_ifc_local_placement(ifc_file, location)

        ifc_groups = {}
        ifc_spatial_structures = {}
        for feature_class_key, elements in model.feature_classes.items():
            feature_class = self.feature_classes[feature_class_key]
            logger.info(f"FeatureClass {feature_class_key}: build ifc spatial structure")
            spatial_structure_config = feature_class.spatial_structure
            if not spatial_structure_config.get_key() in ifc_spatial_structures:
                if spatial_structure_config.type == SpatialStructureEntityType.IFC_SITE:
                    ifc_site = add_ifc_site(ifc_file, ifc_local_placement, ifc_project)
                    ifc_spatial_structures[spatial_structure_config.get_key()] = ifc_site
                else:
                    raise Exception(
                        f"builing step for structure entity type {spatial_structure_config.type.name} not implemented"
                    )
                ifc_spatial_structure = ifc_spatial_structures[spatial_structure_config.get_key()]
                for attribute, value in spatial_structure_config.attributes.items():
                    if hasattr(ifc_spatial_structure, attribute):
                        setattr(ifc_spatial_structure, attribute, value)

            logger.info(f"FeatureClass {feature_class_key}: build ifc elements")
            ifc_style = add_ifc_surface_style(ifc_file, feature_class.color)

            groups = {}
            ifc_elements = []
            for element in elements:
                if isinstance(element.geometry, Triangulation):
                    representation_type = self.triangulation_representation_type
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
                        ifc_face_set = add_ifc_triangulated_face_set(ifc_file, vertices, point_index_list)
                    elif representation_type == TriangulationRepresentationType.BREP:
                        vertex_dict = {}
                        faces = []
                        for triangle in element.geometry.triangles:
                            vertices = []
                            for vertex in triangle:
                                if vertex not in vertex_dict:
                                    vertex_dict[vertex] = add_ifc_cartesian_point(ifc_file, vertex)
                                vertices.append(vertex_dict[vertex])
                            ifc_face = add_ifc_face(ifc_file, vertices)
                            faces.append(ifc_face)
                        ifc_face_set = add_ifc_faceted_brep(ifc_file, faces)
                    else:
                        raise Exception(
                            f"builing step for triangulation representation type {representation_type.name} not implemented"
                        )
                else:
                    raise Exception(f"builing step for geometry class {type(element.geometry)} not implemented")

                add_ifc_styled_item(ifc_file, ifc_face_set, ifc_style)

                product_definition_shape = add_ifc_product_definition_shape(
                    ifc_file, ifc_representation_sub_context, representation_type.value, ifc_face_set
                )
                ifc_local_placement = add_ifc_local_placement(ifc_file, (0.0, 0.0, 0.0))
                if feature_class.entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                    ifc_element = add_ifc_geographic_element(ifc_file, ifc_local_placement, product_definition_shape)
                else:
                    raise Exception(
                        f"builing step for feature class entity type {feature_class.entity_type.name} not implemented"
                    )
                for attribute, value in element.attributes.items():
                    if hasattr(ifc_element, attribute):
                        setattr(ifc_element, attribute, value)

                for property_set in element.property_sets.values():
                    property_entites = []
                    for key, value in property_set.properties.items():
                        property_entites.append(add_ifc_property_single_value(ifc_file, key, value))
                    add_ifc_property_set(ifc_file, property_set.name, property_entites, ifc_element)

                ifc_elements.append(ifc_element)

                for group in element.groups:
                    if not group in groups:
                        groups[group] = []
                    groups[group].append(ifc_element)

            add_ifc_rel_contained_in_spatial_structure(ifc_file, ifc_elements, ifc_spatial_structures[spatial_structure_config.get_key()])

            logger.info(f"FeatureClass {feature_class_key}: build ifc groups")
            for group_definition, ifc_group_elements in groups.items():
                path = []
                for group in group_definition.split("."):
                    parent_group_path = ".".join(path)
                    path.append(group)
                    group_path = ".".join(path)
                    if not group_path in ifc_groups:
                        if group_path in self.groups:
                            group_config = self.groups[group_definition]
                            if group_config.entity_type == GroupEntityType.IFC_DISTRIBUTION_SYSTEM:
                                ifc_groups[group_path] = add_ifc_distribution_system(ifc_file, group)
                            elif group_config.entity_type == GroupEntityType.IFC_DISTRIBUTION_CIRCUIT:
                                ifc_groups[group_path] = add_ifc_distribution_circuit(ifc_file, group)
                            elif group_config.entity_type == GroupEntityType.IFC_BUILDING_SYSTEM:
                                ifc_groups[group_path] = add_ifc_building_system(ifc_file, group)
                            elif group_config.entity_type == GroupEntityType.IFC_STRUCTURAL_ANALYSIS_MODEL:
                                ifc_groups[group_path] = add_ifc_structural_analysis_model(ifc_file, group)
                            elif group_config.entity_type == GroupEntityType.IFC_ZONE:
                                ifc_groups[group_path] = add_ifc_zone(ifc_file, group)
                            else:
                                raise Exception(
                                    f"builing step for ifc group entity {type(group_config.entity_type)} not implemented"
                                )
                            ifc_group = ifc_groups[group_path]
                            for attribute, value in group_config.attributes.items():
                                if hasattr(ifc_group, attribute):
                                    setattr(ifc_group, attribute, value)
                        else:
                            ifc_groups[group_path] = add_ifc_group(ifc_file, group)

                        if not parent_group_path == "":
                            add_ifc_rel_assigns_to_group(
                                ifc_file, [ifc_groups[group_path]], ifc_groups[parent_group_path]
                            )
                add_ifc_rel_assigns_to_group(ifc_file, ifc_group_elements, ifc_groups[group_definition])

        logger.info("completed ifc build")

        return ifc_file
