import logging

from config.configuration import config
from config.geo_referencing import GeoReferencing
from config.group_entity_type import GroupEntityType
from config.spatial_entity_type import SpatialEntityType
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
            spatial_structure_id = feature_type.spatial_structure_mapping.get_id()
            if not spatial_structure_id in ifc_spatial_structures:
                ifc_spatial_structure = self.build_spatial_structure(ifc_file, ifc_local_placement, ifc_project,
                                                                     feature_type.spatial_structure_mapping)
                ifc_spatial_structures[spatial_structure_id] = ifc_spatial_structure
            ifc_style = ifc_file.create_ifc_surface_style(feature_type.color)
            ifc_elements = []
            for element in elements:
                ifc_element = element.map_to_ifc(ifc_file, feature_type.entity_mapping.entity_type,
                                                 ifc_representation_sub_context,
                                                 ifc_style)
                ifc_elements.append(ifc_element)
                for group in element.groups:
                    if not group in group_mappings:
                        group_mappings[group] = []
                    group_mappings[group].append(ifc_element)
            ifc_file.create_ifc_rel_contained_in_spatial_structure(ifc_elements, ifc_spatial_structures[
                feature_type.spatial_structure_mapping.get_id()])

        buildings_config = {b.name: b for b in config.ifc.feature_types.buildings}
        for feature_type_key, elements in self.buildings.items():
            logger.info(f"build FeatureType {feature_type_key}")
            feature_type = buildings_config[feature_type_key]
            spatial_structure_id = feature_type.spatial_structure_mapping.get_id()
            if not spatial_structure_id in ifc_spatial_structures:
                ifc_spatial_structure = self.build_spatial_structure(ifc_file, ifc_local_placement, ifc_project,
                                                                     feature_type.spatial_structure_mapping)
                ifc_spatial_structures[spatial_structure_id] = ifc_spatial_structure
            buildings = []
            for element in elements:
                ifc_element = element.map_to_ifc(ifc_file, ifc_local_placement, ifc_representation_sub_context)
                buildings.append(ifc_element)
                for group in element.groups:
                    if not group in group_mappings:
                        group_mappings[group] = []
                    group_mappings[group].append(ifc_element)
            ifc_file.create_ifc_rel_aggregates(ifc_spatial_structures[feature_type.spatial_structure_mapping.get_id()],
                                               buildings)

        self.build_groups(ifc_file, group_mappings)
        logger.info("completed ifc build")
        return ifc_file

    def build_spatial_structure(self, ifc_file, ifc_local_placement, ifc_project, spatial_structure_config):
        if spatial_structure_config.entity_type == SpatialEntityType.IFC_SITE:
            ifc_spatial_structure = ifc_file.create_ifc_site(ifc_local_placement, ifc_project)
        else:
            raise NotImplementedError(
                f"building step for structure entity type {spatial_structure_config.entity_type} not implemented")
        spatial_structure_element = Element.from_static_element_config(spatial_structure_config)
        spatial_structure_element.set_ifc_attributes(ifc_file, ifc_spatial_structure)
        spatial_structure_element.set_ifc_properties(ifc_file, ifc_spatial_structure)
        return ifc_spatial_structure

    def build_groups(self, ifc_file, groups):
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
                    group_config = groups_config[group_definition]
                    if group_config.entity_mapping.entity_type == GroupEntityType.IFC_DISTRIBUTION_SYSTEM:
                        ifc_groups[group_path] = ifc_file.create_ifc_distribution_system(group)
                    elif group_config.entity_mapping.entity_type == GroupEntityType.IFC_DISTRIBUTION_CIRCUIT:
                        ifc_groups[group_path] = ifc_file.create_ifc_distribution_circuit(group)
                    elif group_config.entity_mapping.entity_type == GroupEntityType.IFC_BUILDING_BUILT_SYSTEM:
                        if self.schema == IfcVersion.IFC4:
                            ifc_groups[group_path] = ifc_file.create_ifc_building_system(group)
                        else:
                            ifc_groups[group_path] = ifc_file.create_ifc_built_system(group)
                    elif group_config.entity_mapping.entity_type == GroupEntityType.IFC_STRUCTURAL_ANALYSIS_MODEL:
                        ifc_groups[group_path] = ifc_file.create_ifc_structural_analysis_model(group)
                    elif group_config.entity_mapping.entity_type == GroupEntityType.IFC_ZONE:
                        ifc_groups[group_path] = ifc_file.create_ifc_zone(group)
                    else:
                        raise NotImplementedError(
                            f"building step for ifc group entity {group_config.entity_mapping.entity_type.name} not implemented")
                    ifc_group = ifc_groups[group_path]

                    group_element = Element.from_static_element_config(group_config.entity_mapping)
                    group_element.set_ifc_attributes(ifc_file, ifc_group)
                    group_element.set_ifc_properties(ifc_file, ifc_group)
                else:
                    ifc_groups[group_path] = ifc_file.create_ifc_group(group)
                if not parent_group_path == "":
                    ifc_file.create_ifc_rel_assigns_to_group([ifc_groups[group_path]], ifc_groups[parent_group_path])
            ifc_file.create_ifc_rel_assigns_to_group(ifc_group_elements, ifc_groups[group_definition])
