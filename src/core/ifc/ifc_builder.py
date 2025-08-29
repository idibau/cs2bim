from config.configuration import config
from config.element_entity_type import ElementEntityType
from config.geo_referencing import GeoReferencing
from config.group_entity_type import GroupEntityType
from config.spatial_structure_entity_type import SpatialStructureEntityType
from config.triangulation_representation_type import TriangulationRepresentationType
from core.ifc.ifc_utils import *
from core.ifc.model.model import Model

logger = logging.getLogger(__name__)


class IfcBuilder:

    def __init__(self):
        self.author = config.ifc.author
        self.version = config.ifc.version
        self.application_name = config.ifc.application_name
        self.project_name = config.ifc.project_name
        self.geo_referencing = config.ifc.geo_referencing
        self.triangulation_representation_type = config.ifc.triangulation_representation_type
        self.clipped_terrain_config = config.ifc.clipped_terrain
        self.building_config = config.ifc.building
        self.groups_config = config.ifc.groups

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
        ifc_representation_sub_context = add_ifc_geometric_representation_sub_context(ifc_file,
                                                                                      ifc_representation_context)
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

        group_assignments = {}
        ifc_spatial_structures = {}
        self.create_building_feature_classes(ifc_file, ifc_local_placement, ifc_project, ifc_representation_sub_context,
                                             model, ifc_spatial_structures, group_assignments)
        self.create_clipped_terrain_feature_classes(ifc_file, ifc_local_placement, ifc_project,
                                                    ifc_representation_sub_context, model, ifc_spatial_structures,
                                                    group_assignments)
        self.create_groups(ifc_file, group_assignments)

        logger.info("completed ifc build")

        return ifc_file

    def create_clipped_terrain_feature_classes(self, ifc_file, ifc_local_placement, ifc_project,
                                               ifc_representation_sub_context, model, ifc_spatial_structures, groups):
        for feature_class_key, elements in model.clipped_terrains.items():
            feature_class = self.clipped_terrain_config[feature_class_key]
            logger.info(f"FeatureClass {feature_class_key}: build ifc spatial structure")
            self.create_spatial_structure(ifc_file, ifc_local_placement, ifc_project, ifc_spatial_structures,
                                          feature_class.spatial_structure)

            logger.info(f"FeatureClass {feature_class_key}: build ifc elements")
            ifc_style = add_ifc_surface_style(ifc_file, feature_class.color)
            ifc_elements = []
            for element in elements:
                representation_type = self.triangulation_representation_type
                if representation_type == TriangulationRepresentationType.TESSELLATION:
                    product_definition_shape = self.create_tessellation(ifc_file, ifc_representation_sub_context,
                                                                        ifc_style, element.triangles)
                elif representation_type == TriangulationRepresentationType.BREP:
                    product_definition_shape = self.create_brep(ifc_file, ifc_representation_sub_context, ifc_style,
                                                                element.triangles)
                else:
                    raise Exception(
                        f"building step for representation type {type(representation_type)} not implemented")

                ifc_local_placement = add_ifc_local_placement(ifc_file, (0.0, 0.0, 0.0))
                if feature_class.entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                    ifc_element = add_ifc_geographic_element(ifc_file, ifc_local_placement, product_definition_shape)
                else:
                    raise Exception(
                        f"building step for feature class entity type {feature_class.entity_type.name} not implemented for clipped terrain feature classes"
                    )

                self.add_attributes(ifc_element, element)
                self.add_properties(ifc_file, ifc_element, element)

                ifc_elements.append(ifc_element)

                for group in element.groups:
                    if not group in groups:
                        groups[group] = []
                    groups[group].append(ifc_element)

            add_ifc_rel_contained_in_spatial_structure(ifc_file, ifc_elements, ifc_spatial_structures[
                feature_class.spatial_structure.get_id()])

    def create_building_feature_classes(self, ifc_file, ifc_local_placement, ifc_project,
                                        ifc_representation_sub_context, model, ifc_spatial_structures, groups):
        for feature_class_key, elements in model.buildings.items():
            feature_class = self.building_config[feature_class_key]
            self.create_spatial_structure(ifc_file, ifc_local_placement, ifc_project, ifc_spatial_structures,
                                          feature_class.spatial_structure)
            buildings = []
            for element in elements:
                ifc_building_parts = []
                for building_part in element.building_parts:
                    ifc_style = add_ifc_surface_style(ifc_file, building_part.color)
                    product_definition_shape = self.create_brep(ifc_file, ifc_representation_sub_context,
                                                                ifc_style, building_part.faces)
                    ifc_local_placement = add_ifc_local_placement(ifc_file, (0.0, 0.0, 0.0))
                    if building_part.entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                        ifc_element = add_ifc_geographic_element(ifc_file, ifc_local_placement,
                                                                 product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_ROOF:
                        ifc_element = add_ifc_roof(ifc_file, ifc_local_placement,
                                                   product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_SLAB:
                        ifc_element = add_ifc_slab(ifc_file, ifc_local_placement,
                                                   product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_WALL:
                        ifc_element = add_ifc_wall(ifc_file, ifc_local_placement,
                                                   product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_SPACE:
                        ifc_element = add_ifc_space(ifc_file, ifc_local_placement,
                                                    product_definition_shape)
                    else:
                        raise Exception(
                            f"building step for feature class entity type {building_part.entity_type.name} not implemented for building feature classes"
                        )

                    self.add_attributes(ifc_element, building_part)
                    self.add_properties(ifc_file, ifc_element, building_part)

                    ifc_building_parts.append(ifc_element)

                ifc_building = add_ifc_building(ifc_file, ifc_local_placement)

                self.add_attributes(ifc_building, element)
                self.add_properties(ifc_file, ifc_building, element)

                add_ifc_rel_contained_in_spatial_structure(ifc_file, ifc_building_parts, ifc_building)
                buildings.append(ifc_building)

                for group in element.groups:
                    if not group in groups:
                        groups[group] = []
                    groups[group].append(ifc_building)

            add_ifc_rel_contained_in_spatial_structure(ifc_file, buildings, ifc_spatial_structures[
                feature_class.spatial_structure.get_id()])

    def create_tessellation(self, ifc_file, ifc_representation_sub_context, ifc_style, faces):
        vertices_dict = {}
        vertices = []
        for triangle in faces:
            for vertex in triangle:
                if not vertex in vertices_dict:
                    vertices_dict[vertex] = len(vertices) + 1
                    vertices.append(vertex)
        point_index_list = [
            tuple(vertices_dict[v] for v in triangle) for triangle in faces
        ]
        ifc_face_set = add_ifc_triangulated_face_set(ifc_file, vertices, point_index_list)
        add_ifc_styled_item(ifc_file, ifc_face_set, ifc_style)
        product_definition_shape = add_ifc_product_definition_shape(
            ifc_file, ifc_representation_sub_context, "Tesselation", ifc_face_set
        )
        return product_definition_shape

    def create_brep(self, ifc_file, ifc_representation_sub_context, ifc_style, faces):
        vertex_dict = {}
        ifc_faces = []
        for polygon in faces:
            vertices = []
            for vertex in polygon:
                if vertex not in vertex_dict:
                    vertex_dict[vertex] = add_ifc_cartesian_point(ifc_file, vertex)
                vertices.append(vertex_dict[vertex])
            ifc_face = add_ifc_face(ifc_file, vertices)
            ifc_faces.append(ifc_face)
        ifc_face_set = add_ifc_faceted_brep(ifc_file, ifc_faces)
        add_ifc_styled_item(ifc_file, ifc_face_set, ifc_style)
        product_definition_shape = add_ifc_product_definition_shape(
            ifc_file, ifc_representation_sub_context, "Brep", ifc_face_set
        )
        return product_definition_shape

    def create_groups(self, ifc_file, groups):
        ifc_groups = {}
        for group_definition, ifc_group_elements in groups.items():
            path = []
            for group in group_definition.split("."):
                parent_group_path = ".".join(path)
                path.append(group)
                group_path = ".".join(path)
                if not group_path in ifc_groups:
                    if group_path in self.groups_config:
                        group_config = self.groups_config[group_definition]
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
                                f"building step for ifc group entity {type(group_config.entity_type)} not implemented"
                            )
                        ifc_group = ifc_groups[group_path]
                        for attribute in group_config.attributes:
                            if hasattr(ifc_group, attribute.name):
                                setattr(ifc_group, attribute.name, attribute.value)
                    else:
                        ifc_groups[group_path] = add_ifc_group(ifc_file, group)

                    if not parent_group_path == "":
                        add_ifc_rel_assigns_to_group(
                            ifc_file, [ifc_groups[group_path]], ifc_groups[parent_group_path]
                        )
            add_ifc_rel_assigns_to_group(ifc_file, ifc_group_elements, ifc_groups[group_definition])

    def add_properties(self, ifc_file, ifc_element, element):
        for property_set in element.property_sets.values():
            ifc_property_single_values = []
            for key, value in property_set.properties.items():
                ifc_property_single_values.append(add_ifc_property_single_value(ifc_file, key, value))
            add_ifc_property_set(ifc_file, property_set.name, ifc_property_single_values, ifc_element)

    def add_attributes(self, ifc_element, element):
        for attribute, value in element.attributes.items():
            if hasattr(ifc_element, attribute):
                setattr(ifc_element, attribute, value)

    def create_spatial_structure(self, ifc_file, ifc_local_placement, ifc_project, ifc_spatial_structures,
                                 spatial_structure_config):
        if not spatial_structure_config.get_id() in ifc_spatial_structures:
            if spatial_structure_config.entity_type == SpatialStructureEntityType.IFC_SITE:
                ifc_site = add_ifc_site(ifc_file, ifc_local_placement, ifc_project)
                ifc_spatial_structures[spatial_structure_config.get_id()] = ifc_site
            else:
                raise Exception(
                    f"building step for structure entity type {spatial_structure_config.entity_type} not implemented"
                )
            ifc_spatial_structure = ifc_spatial_structures[spatial_structure_config.get_id()]
            for attribute in spatial_structure_config.attributes:
                if hasattr(ifc_spatial_structure, attribute.name):
                    setattr(ifc_spatial_structure, attribute.name, attribute.value)
