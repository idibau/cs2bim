import logging

from config.configuration import config
from config.geo_referencing import GeoReferencing
from config.group_entity import GroupEntity
from config.projection_entity import ProjectionEntity
from core.ifc.ifc_file import IfcFile
from core.ifc.model.building import Building
from core.ifc.model.element import Element
from core.ifc.model.ifc_version import IfcVersion
from core.ifc.model.projection import Projection

logger = logging.getLogger(__name__)


class Model:
    """Class holding all variable data for creating the ifc"""

    def __init__(self, file_name: str, schema: IfcVersion, origin: tuple[float, float, float]) -> None:
        self.file_name = file_name
        self.schema = schema
        self.origin = origin
        self.projections: dict[str, list[Projection]] = {}
        self.buildings: dict[str, list[Building]] = {}

    def add_projections(self, feature_type_key: str, projections: list[Projection]) -> None:
        if not feature_type_key in self.projections:
            self.projections[feature_type_key] = []
        self.projections[feature_type_key].extend(projections)

    def add_buildings(self, feature_type_key: str, elements: list[Building]) -> None:
        if not feature_type_key in self.buildings:
            self.buildings[feature_type_key] = []
        self.buildings[feature_type_key].extend(elements)

    def map_to_ifc(self, language):
        logger.info(f"initialize new ifc writer for ifc '{self.file_name}'")
        ifc_file = IfcFile(self.schema.value, self.file_name, language)

        logger.info(f"build ifc")
        ifc_owner_history = ifc_file.create_ifc_owner_history(config.ifc.author, config.ifc.version,
                                                              config.ifc.application_name)
        ifc_length_unit = ifc_file.create_ifc_si_unit("LENGTHUNIT", "METRE")
        ifc_area_unit = ifc_file.create_ifc_si_unit("AREAUNIT", "SQUARE_METRE")
        ifc_volume_unit = ifc_file.create_ifc_si_unit("VOLUMEUNIT", "CUBIC_METRE")
        ifc_degree_unit = ifc_file.create_ifc_si_unit("PLANEANGLEUNIT", "RADIAN")
        ifc_unit_assignment = ifc_file.create_ifc_unit_assignment(ifc_length_unit, ifc_area_unit, ifc_volume_unit,
                                                                  ifc_degree_unit)

        geo_referencing = config.ifc.geo_referencing
        if geo_referencing == GeoReferencing.LO_GEO_REF_40:
            location = self.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_representation_context = ifc_file.create_ifc_geometric_representation_context(location)
        ifc_representation_sub_context = ifc_file.create_ifc_geometric_representation_sub_context(
            ifc_representation_context)
        if geo_referencing == GeoReferencing.LO_GEO_REF_50:
            ifc_file.create_ifc_map_conversion(ifc_length_unit, ifc_representation_context, self.origin)

        ifc_project = ifc_file.create_ifc_project(config.ifc.project_name, ifc_owner_history,
                                                  ifc_representation_context, ifc_unit_assignment)
        if geo_referencing == GeoReferencing.LO_GEO_REF_30:
            location = self.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_local_placement = ifc_file.create_ifc_local_placement(location)

        group_mappings = {}
        ifc_spatial_structures = {}

        projections_config = {p.name: p for p in config.ifc.feature_types.projections}
        for feature_type_key, elements in self.projections.items():
            logger.info(f"build FeatureType {feature_type_key}")
            feature_type = projections_config[feature_type_key]
            ifc_style = ifc_file.create_ifc_surface_style(feature_type.color)
            ifc_elements = []
            ifc_element_types = {}
            for element in elements:
                ifc_element = element.map_to_ifc(ifc_file, feature_type.entity_mapping.entity,
                                                 ifc_representation_sub_context, ifc_style)
                element.set_ifc_attributes(ifc_file, ifc_element)
                element.set_ifc_properties(ifc_file, ifc_element)
                ifc_elements.append(ifc_element)

                if element.element_type is not None:
                    if element.element_type not in ifc_element_types:
                        ifc_element_type = self.create_projection_ifc_element_type(ifc_file, element.element_type,
                                                                                   feature_type.entity_mapping.entity)
                        ifc_element_types[element.element_type] = (ifc_element_type, [])
                    ifc_element_types[element.element_type][1].append(ifc_element)

                if element.spatial_structure not in ifc_spatial_structures:
                    ifc_spatial_structure = self.create_ifc_spatial_structure(ifc_file, ifc_local_placement,
                                                                              ifc_project, element.spatial_structure)
                    ifc_spatial_structures[element.spatial_structure] = (ifc_spatial_structure, [], [])
                ifc_spatial_structures[element.spatial_structure][1].append(ifc_element)

                for group in element.groups:
                    if not group in group_mappings:
                        group_mappings[group] = []
                    group_mappings[group].append(ifc_element)

            for ifc_element_type, ifc_element_types in ifc_element_types.values():
                ifc_file.create_ifc_rel_defines_by_type(ifc_element_types, ifc_element_type)

        for feature_type_key, elements in self.buildings.items():
            logger.info(f"build FeatureType {feature_type_key}")
            ifc_elements = []
            for element in elements:
                ifc_element = element.map_to_ifc(ifc_file, ifc_local_placement, ifc_representation_sub_context)
                element.set_ifc_attributes(ifc_file, ifc_element)
                element.set_ifc_properties(ifc_file, ifc_element)
                ifc_elements.append(ifc_element)

                if element.spatial_structure not in ifc_spatial_structures:
                    ifc_spatial_structure = self.create_ifc_spatial_structure(ifc_file, ifc_local_placement,
                                                                              ifc_project, element.spatial_structure)
                    ifc_spatial_structures[element.spatial_structure] = (ifc_spatial_structure, [], [])
                ifc_spatial_structures[element.spatial_structure][2].append(ifc_element)

                for group in element.groups:
                    if not group in group_mappings:
                        group_mappings[group] = []
                    group_mappings[group].append(ifc_element)

        for ifc_spatial_structure, ifc_elements, ifc_spatial_elements in ifc_spatial_structures.values():
            if ifc_elements:
                ifc_file.create_ifc_rel_contained_in_spatial_structure(ifc_elements, ifc_spatial_structure)
            if ifc_spatial_elements:
                ifc_file.create_ifc_rel_aggregates(ifc_spatial_structure, ifc_spatial_elements)

        self.create_ifc_groups(ifc_file, group_mappings)
        logger.info("completed ifc build")
        return ifc_file

    def create_projection_ifc_element_type(self, ifc_file, element_type, projection_entity):
        if projection_entity == ProjectionEntity.IFC_GEOGRAPHIC_ELEMENT:
            ifc_element_type = ifc_file.create_ifc_geographic_element_type()
        elif projection_entity == ProjectionEntity.IFC_SPATIAL_ZONE:
            ifc_element_type = ifc_file.create_ifc_spatial_zone_type()
        else:
            raise NotImplementedError(
                f"building step for projection entity type {projection_entity.name} not implemented")
        element_type.set_ifc_attributes(ifc_file, ifc_element_type)
        element_type.set_ifc_properties(ifc_file, ifc_element_type)
        return ifc_element_type

    def create_ifc_spatial_structure(self, ifc_file, ifc_local_placement, ifc_project, spatial_structure_element):
        ifc_spatial_structure = ifc_file.create_ifc_site(ifc_local_placement, ifc_project)
        ifc_file.create_ifc_rel_aggregates(ifc_project, [ifc_spatial_structure])
        spatial_structure_element.set_ifc_attributes(ifc_file, ifc_spatial_structure)
        spatial_structure_element.set_ifc_properties(ifc_file, ifc_spatial_structure)
        return ifc_spatial_structure

    def create_ifc_groups(self, ifc_file, groups):
        ifc_groups = {}
        groups_config = {group.path: group for group in config.ifc.groups}
        for group_definition, ifc_group_elements in groups.items():
            path = []
            for group in group_definition.split("."):
                parent_group_path = ".".join(path)
                path.append(group)
                group_path = ".".join(path)
                if group_path in ifc_groups:
                    continue
                if group_path in groups_config:
                    group_config = groups_config[group_path]
                    if group_config.entity_mapping.entity == GroupEntity.IFC_DISTRIBUTION_SYSTEM:
                        ifc_group = ifc_file.create_ifc_distribution_system(group)
                    elif group_config.entity_mapping.entity == GroupEntity.IFC_DISTRIBUTION_CIRCUIT:
                        ifc_group = ifc_file.create_ifc_distribution_circuit(group)
                    elif group_config.entity_mapping.entity == GroupEntity.IFC_BUILDING_BUILT_SYSTEM:
                        if self.schema == IfcVersion.IFC4:
                            ifc_group = ifc_file.create_ifc_building_system(group)
                        else:
                            ifc_group = ifc_file.create_ifc_built_system(group)
                    elif group_config.entity_mapping.entity == GroupEntity.IFC_STRUCTURAL_ANALYSIS_MODEL:
                        ifc_group = ifc_file.create_ifc_structural_analysis_model(group)
                    elif group_config.entity_mapping.entity == GroupEntity.IFC_ZONE:
                        ifc_group = ifc_file.create_ifc_zone(group)
                    else:
                        raise NotImplementedError(
                            f"building step for ifc group entity {group_config.entity_mapping.entity.name} not implemented")
                    ifc_groups[group_path] = ifc_group

                    group_element = Element()
                    for attribute in group_config.entity_mapping.attributes:
                        group_element.add_attribute(attribute.attribute, attribute.value)
                    for p in group_config.entity_mapping.properties:
                        group_element.add_property(p.property_set, p.property, p.value)
                    group_element.set_ifc_attributes(ifc_file, ifc_group)
                    group_element.set_ifc_properties(ifc_file, ifc_group)
                else:
                    ifc_groups[group_path] = ifc_file.create_ifc_group(group)
                if not parent_group_path == "":
                    ifc_file.create_ifc_rel_assigns_to_group([ifc_groups[group_path]], ifc_groups[parent_group_path])
            ifc_file.create_ifc_rel_assigns_to_group(ifc_group_elements, ifc_groups[group_definition])
