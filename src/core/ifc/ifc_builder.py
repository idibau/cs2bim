from config.configuration import config
from config.element_attribute import ElementAttribute
from config.element_entity_type import ElementEntityType
from config.geo_referencing import GeoReferencing
from config.group_entity_type import GroupEntityType
from config.source_type import SourceType
from config.spatial_structure_entity_type import SpatialStructureEntityType
from config.triangulation_representation_type import TriangulationRepresentationType
from core.ifc.ifc_entity_creator import *
from core.ifc.model.element import Element
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

    def build_ifc(self, model: Model) -> file:
        """Builds an ifcopenshell ifc file based on a model object"""
        logger.info(f"initialize new ifc writer for ifc '{model.file_name}'")
        ifc_file = file(schema=model.schema.value)
        ifc_file.wrapped_data.header.file_name.name = model.file_name

        logger.info(f"build ifc")
        ifc_owner_history = create_ifc_owner_history(ifc_file, self.author, self.version, self.application_name)
        ifc_length_unit = create_ifc_si_unit(ifc_file, "LENGTHUNIT", "METRE")
        ifc_area_unit = create_ifc_si_unit(ifc_file, "AREAUNIT", "SQUARE_METRE")
        ifc_volume_unit = create_ifc_si_unit(ifc_file, "VOLUMEUNIT", "CUBIC_METRE")
        ifc_degree_unit = create_ifc_si_unit(ifc_file, "PLANEANGLEUNIT", "RADIAN")
        ifc_unit_assignment = create_ifc_unit_assignment(
            ifc_file, ifc_length_unit, ifc_area_unit, ifc_volume_unit, ifc_degree_unit
        )

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_40:
            location = model.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_representation_context = create_ifc_geometric_representation_context(ifc_file, location)
        ifc_representation_sub_context = create_ifc_geometric_representation_sub_context(ifc_file,
                                                                                      ifc_representation_context)
        if self.geo_referencing == GeoReferencing.LO_GEO_REF_50:
            create_ifc_map_conversion(ifc_file, ifc_length_unit, ifc_representation_context, model.origin)

        ifc_project = create_ifc_project(
            ifc_file, self.project_name, ifc_owner_history, ifc_representation_context, ifc_unit_assignment
        )
        if self.geo_referencing == GeoReferencing.LO_GEO_REF_30:
            location = model.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_local_placement = create_ifc_local_placement(ifc_file, location)

        group_assignments = {}
        ifc_spatial_structures = {}
        self.build_building_feature_classes(ifc_file, ifc_local_placement, ifc_project, ifc_representation_sub_context,
                                            model, ifc_spatial_structures, group_assignments)
        self.build_clipped_terrain_feature_classes(ifc_file, ifc_local_placement, ifc_project,
                                                   ifc_representation_sub_context, model, ifc_spatial_structures,
                                                   group_assignments)
        self.build_groups(ifc_file, group_assignments)

        logger.info("completed ifc build")

        return ifc_file

    def build_clipped_terrain_feature_classes(self, ifc_file, ifc_local_placement, ifc_project,
                                              ifc_representation_sub_context, model, ifc_spatial_structures, groups):
        for feature_class_key, elements in model.clipped_terrains.items():
            logger.info(f"build FeatureClass {feature_class_key}")

            feature_class = self.clipped_terrain_config[feature_class_key]
            self.build_spatial_structure(ifc_file, ifc_local_placement, ifc_project, ifc_spatial_structures,
                                         feature_class.spatial_structure)

            ifc_style = create_ifc_surface_style(ifc_file, feature_class.color)
            ifc_elements = []
            for element in elements:
                representation_type = self.triangulation_representation_type
                if representation_type == TriangulationRepresentationType.TESSELLATION:
                    product_definition_shape = self.build_tessellation(ifc_file, ifc_representation_sub_context,
                                                                       ifc_style, element.triangles)
                elif representation_type == TriangulationRepresentationType.BREP:
                    product_definition_shape = self.build_brep(ifc_file, ifc_representation_sub_context, ifc_style,
                                                               element.triangles)
                else:
                    raise Exception(
                        f"building step for representation type {type(representation_type)} not implemented")

                ifc_local_placement = create_ifc_local_placement(ifc_file, (0.0, 0.0, 0.0))
                if feature_class.entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                    ifc_element = create_ifc_geographic_element(ifc_file, ifc_local_placement, product_definition_shape)
                else:
                    raise Exception(
                        f"building step for feature class entity type {feature_class.entity_type.name} not implemented for clipped terrain feature classes"
                    )

                self.set_ifc_attributes(ifc_element, element)
                self.set_ifc_properties(ifc_file, ifc_element, element)

                ifc_elements.append(ifc_element)

                for group in element.groups:
                    if not group in groups:
                        groups[group] = []
                    groups[group].append(ifc_element)

            create_ifc_rel_contained_in_spatial_structure(ifc_file, ifc_elements, ifc_spatial_structures[
                feature_class.spatial_structure.get_id()])

    def build_building_feature_classes(self, ifc_file, ifc_local_placement, ifc_project,
                                       ifc_representation_sub_context, model, ifc_spatial_structures, groups):
        for feature_class_key, elements in model.buildings.items():
            logger.info(f"build FeatureClass {feature_class_key}")

            feature_class = self.building_config[feature_class_key]
            self.build_spatial_structure(ifc_file, ifc_local_placement, ifc_project, ifc_spatial_structures,
                                         feature_class.spatial_structure)
            buildings = []
            for element in elements:
                ifc_building_parts = []
                for building_part in element.building_parts:
                    ifc_style = create_ifc_surface_style(ifc_file, building_part.color)
                    product_definition_shape = self.build_brep(ifc_file, ifc_representation_sub_context,
                                                               ifc_style, building_part.faces)
                    ifc_local_placement = create_ifc_local_placement(ifc_file, (0.0, 0.0, 0.0))
                    if building_part.entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                        ifc_element = create_ifc_geographic_element(ifc_file, ifc_local_placement,
                                                                 product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_ROOF:
                        ifc_element = create_ifc_roof(ifc_file, ifc_local_placement,
                                                   product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_SLAB:
                        ifc_element = create_ifc_slab(ifc_file, ifc_local_placement,
                                                   product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_WALL:
                        ifc_element = create_ifc_wall(ifc_file, ifc_local_placement,
                                                   product_definition_shape)
                    elif building_part.entity_type == ElementEntityType.IFC_SPACE:
                        ifc_element = create_ifc_space(ifc_file, ifc_local_placement,
                                                    product_definition_shape)
                    else:
                        raise Exception(
                            f"building step for feature class entity type {building_part.entity_type.name} not implemented for building feature classes"
                        )
                    self.set_ifc_attributes(ifc_element, building_part)
                    self.set_ifc_properties(ifc_file, ifc_element, building_part)
                    ifc_building_parts.append(ifc_element)

                ifc_building = create_ifc_building(ifc_file, ifc_local_placement)
                self.set_ifc_attributes(ifc_building, element)
                self.set_ifc_properties(ifc_file, ifc_building, element)

                create_ifc_rel_contained_in_spatial_structure(ifc_file, ifc_building_parts, ifc_building)
                buildings.append(ifc_building)

                for group in element.groups:
                    if not group in groups:
                        groups[group] = []
                    groups[group].append(ifc_building)

            create_ifc_rel_contained_in_spatial_structure(ifc_file, buildings, ifc_spatial_structures[
                feature_class.spatial_structure.get_id()])

    def build_tessellation(self, ifc_file, ifc_representation_sub_context, ifc_style, faces):
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
        ifc_face_set = create_ifc_triangulated_face_set(ifc_file, vertices, point_index_list)
        create_ifc_styled_item(ifc_file, ifc_face_set, ifc_style)
        product_definition_shape = create_ifc_product_definition_shape(
            ifc_file, ifc_representation_sub_context, "Tesselation", ifc_face_set
        )
        return product_definition_shape

    def build_brep(self, ifc_file, ifc_representation_sub_context, ifc_style, faces):
        vertex_dict = {}
        ifc_faces = []
        for polygon in faces:
            vertices = []
            for vertex in polygon:
                if vertex not in vertex_dict:
                    vertex_dict[vertex] = create_ifc_cartesian_point(ifc_file, vertex)
                vertices.append(vertex_dict[vertex])
            ifc_face = create_ifc_face(ifc_file, vertices)
            ifc_faces.append(ifc_face)
        ifc_face_set = create_ifc_faceted_brep(ifc_file, ifc_faces)
        create_ifc_styled_item(ifc_file, ifc_face_set, ifc_style)
        product_definition_shape = create_ifc_product_definition_shape(
            ifc_file, ifc_representation_sub_context, "Brep", ifc_face_set
        )
        return product_definition_shape

    def build_groups(self, ifc_file, groups):
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
                            ifc_groups[group_path] = create_ifc_distribution_system(ifc_file, group)
                        elif group_config.entity_type == GroupEntityType.IFC_DISTRIBUTION_CIRCUIT:
                            ifc_groups[group_path] = create_ifc_distribution_circuit(ifc_file, group)
                        elif group_config.entity_type == GroupEntityType.IFC_BUILDING_SYSTEM:
                            ifc_groups[group_path] = create_ifc_building_system(ifc_file, group)
                        elif group_config.entity_type == GroupEntityType.IFC_STRUCTURAL_ANALYSIS_MODEL:
                            ifc_groups[group_path] = create_ifc_structural_analysis_model(ifc_file, group)
                        elif group_config.entity_type == GroupEntityType.IFC_ZONE:
                            ifc_groups[group_path] = create_ifc_zone(ifc_file, group)
                        else:
                            raise Exception(
                                f"building step for ifc group entity {type(group_config.entity_type)} not implemented"
                            )
                        ifc_group = ifc_groups[group_path]

                        group_element = Element()
                        for attribute in group_config.attributes:
                            if attribute.source.type == SourceType.STATIC:
                                group_element.create_attribute(attribute.attribute, attribute.source.expression)
                        for p in group_config.properties:
                            if p.source.type == SourceType.STATIC:
                                group_element.create_property(p.property_set, p.property, p.source.expression)

                        self.set_ifc_attributes(ifc_group, group_element)
                        self.set_ifc_properties(ifc_file, ifc_group, group_element)
                    else:
                        ifc_groups[group_path] = create_ifc_group(ifc_file, group)

                    if not parent_group_path == "":
                        create_ifc_rel_assigns_to_group(
                            ifc_file, [ifc_groups[group_path]], ifc_groups[parent_group_path]
                        )
            create_ifc_rel_assigns_to_group(ifc_file, ifc_group_elements, ifc_groups[group_definition])

    def build_spatial_structure(self, ifc_file, ifc_local_placement, ifc_project, ifc_spatial_structures,
                                spatial_structure_config):
        if not spatial_structure_config.get_id() in ifc_spatial_structures:
            if spatial_structure_config.entity_type == SpatialStructureEntityType.IFC_SITE:
                ifc_site = create_ifc_site(ifc_file, ifc_local_placement, ifc_project)
                ifc_spatial_structures[spatial_structure_config.get_id()] = ifc_site
            else:
                raise Exception(
                    f"building step for structure entity type {spatial_structure_config.entity_type} not implemented"
                )
            ifc_spatial_structure = ifc_spatial_structures[spatial_structure_config.get_id()]

            spatial_structure_element = Element()
            for attribute in spatial_structure_config.attributes:
                if attribute.source.type == SourceType.STATIC:
                    spatial_structure_element.create_attribute(attribute.attribute, attribute.source.expression)
            for p in spatial_structure_config.properties:
                if p.source.type == SourceType.STATIC:
                    spatial_structure_element.create_property(p.property_set, p.property, p.source.expression)

            self.set_ifc_attributes(ifc_spatial_structure, spatial_structure_element)
            self.set_ifc_properties(ifc_file, ifc_spatial_structure, spatial_structure_element)

    def set_ifc_properties(self, ifc_file, ifc_element, element):
        for property_set in element.property_sets.values():
            ifc_property_single_values = []
            for key, value in property_set.properties.items():
                ifc_property_single_values.append(create_ifc_property_single_value(ifc_file, key, value))
            create_ifc_property_set(ifc_file, property_set.name, ifc_property_single_values, ifc_element)

    def set_ifc_attributes(self, ifc_element, element):
        for attribute, value in element.attributes.items():
            if attribute == ElementAttribute.NAME:
                ifc_attribute = "Name"
            elif attribute == ElementAttribute.DESCRIPTION:
                ifc_attribute = "Description"
            elif attribute == ElementAttribute.COMPOSITION_TYPE:
                ifc_attribute = "CompositionType"
            elif attribute == ElementAttribute.PREDEFINED_TYPE:
                ifc_attribute = "PredefinedType"
            elif attribute == ElementAttribute.OBJECT_TYPE:
                ifc_attribute = "ObjectType"
            elif attribute == ElementAttribute.LONGNAME:
                ifc_attribute = "LongName"
            else:
                raise Exception(f"building step for attribute type {attribute} not implemented")
            if hasattr(ifc_element, ifc_attribute):
                setattr(ifc_element, ifc_attribute, value)
