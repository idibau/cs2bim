import logging

from config.geo_referencing import GeoReferencing
from config.group_entity_type import GroupEntityType
from config.spatial_structure_entity_type import SpatialStructureEntityType
from core.ifc.ifc_file import IfcFile
from core.ifc.model.building import Building
from core.ifc.model.clipped_terrain import ClippedTerrain
from core.ifc.model.element import Element
from core.ifc.model.ifc_version import IfcVersion

logger = logging.getLogger(__name__)


class Model:
    """Class holding all variable data for creating the ifc"""

    def __init__(self, ifc_config, file_name: str, schema: IfcVersion, origin: tuple[float, float, float]) -> None:
        self.ifc_config = ifc_config
        self.file_name = file_name
        self.schema = schema
        self.origin = origin

        self.clipped_terrains: dict[str, list[ClippedTerrain]] = {}
        self.buildings: dict[str, list[Building]] = {}

    def add_clipped_terrains(self, feature_class_key: str, clipped_terrains: list[ClippedTerrain]) -> None:
        if not feature_class_key in self.clipped_terrains:
            self.clipped_terrains[feature_class_key] = []
        self.clipped_terrains[feature_class_key].extend(clipped_terrains)

    def add_buildings(self, feature_class_key: str, elements: list[Building]) -> None:
        if not feature_class_key in self.buildings:
            self.buildings[feature_class_key] = []
        self.buildings[feature_class_key].extend(elements)

    def map_to_ifc(self):
        logger.info(f"initialize new ifc writer for ifc '{self.file_name}'")
        ifc_file = IfcFile(self.schema.value, self.file_name)

        logger.info(f"build ifc")
        author = self.ifc_config.author
        version = self.ifc_config.version
        application_name = self.ifc_config.application_name
        ifc_owner_history = ifc_file.create_ifc_owner_history(author, version, application_name)
        ifc_length_unit = ifc_file.create_ifc_si_unit("LENGTHUNIT", "METRE")
        ifc_area_unit = ifc_file.create_ifc_si_unit("AREAUNIT", "SQUARE_METRE")
        ifc_volume_unit = ifc_file.create_ifc_si_unit("VOLUMEUNIT", "CUBIC_METRE")
        ifc_degree_unit = ifc_file.create_ifc_si_unit("PLANEANGLEUNIT", "RADIAN")
        ifc_unit_assignment = ifc_file.create_ifc_unit_assignment(ifc_length_unit, ifc_area_unit, ifc_volume_unit,
                                                                  ifc_degree_unit)

        geo_referencing = self.ifc_config.geo_referencing
        if geo_referencing == GeoReferencing.LO_GEO_REF_40:
            location = self.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_representation_context = ifc_file.create_ifc_geometric_representation_context(location)
        ifc_representation_sub_context = ifc_file.create_ifc_geometric_representation_sub_context(
            ifc_representation_context)
        if geo_referencing == GeoReferencing.LO_GEO_REF_50:
            ifc_file.create_ifc_map_conversion(ifc_length_unit, ifc_representation_context, self.origin)

        project_name = self.ifc_config.project_name
        ifc_project = ifc_file.create_ifc_project(project_name, ifc_owner_history, ifc_representation_context,
                                                  ifc_unit_assignment)
        if geo_referencing == GeoReferencing.LO_GEO_REF_30:
            location = self.origin
        else:
            location = (0.0, 0.0, 0.0)
        ifc_local_placement = ifc_file.create_ifc_local_placement(location)


        clipped_terrain_config = {ct.name: ct for ct in self.ifc_config.clipped_terrain}
        group_assignments = {}
        ifc_spatial_structures = {}
        for feature_class_key, elements in self.clipped_terrains.items():
            logger.info(f"build FeatureClass {feature_class_key}")
            feature_class = clipped_terrain_config[feature_class_key]
            spatial_structure_id = feature_class.spatial_structure.get_id()
            if not spatial_structure_id in ifc_spatial_structures:
                ifc_spatial_structure = self.build_spatial_structure(ifc_file, ifc_local_placement, ifc_project,
                                                                     feature_class.spatial_structure)
                ifc_spatial_structures[spatial_structure_id] = ifc_spatial_structure
            ifc_style = ifc_file.create_ifc_surface_style(feature_class.color)
            ifc_elements = []
            for element in elements:
                triangulation_representation_type = self.ifc_config.triangulation_representation_type
                ifc_element = element.map_to_ifc(ifc_file, feature_class.entity_type, ifc_representation_sub_context,
                                                 ifc_style, triangulation_representation_type)
                ifc_elements.append(ifc_element)
                for group in element.groups:
                    if not group in group_assignments:
                        group_assignments[group] = []
                    group_assignments[group].append(ifc_element)
            ifc_file.create_ifc_rel_contained_in_spatial_structure(ifc_elements, ifc_spatial_structures[
                feature_class.spatial_structure.get_id()])

        building_config = {b.name: b for b in self.ifc_config.building}
        for feature_class_key, elements in self.buildings.items():
            logger.info(f"build FeatureClass {feature_class_key}")
            feature_class = building_config[feature_class_key]
            spatial_structure_id = feature_class.spatial_structure.get_id()
            if not spatial_structure_id in ifc_spatial_structures:
                ifc_spatial_structure = self.build_spatial_structure(ifc_file, ifc_local_placement, ifc_project,
                                                                     feature_class.spatial_structure)
                ifc_spatial_structures[spatial_structure_id] = ifc_spatial_structure
            buildings = []
            for element in elements:
                ifc_building = element.map_to_ifc(ifc_file, ifc_local_placement, ifc_representation_sub_context)
                buildings.append(ifc_building)
                for group in element.groups:
                    if not group in group_assignments:
                        group_assignments[group] = []
                    group_assignments[group].append(ifc_building)
            ifc_file.create_ifc_rel_contained_in_spatial_structure(buildings, ifc_spatial_structures[
                feature_class.spatial_structure.get_id()])

        self.build_groups(ifc_file, group_assignments)
        logger.info("completed ifc build")
        return ifc_file

    def build_spatial_structure(self, ifc_file, ifc_local_placement, ifc_project, spatial_structure_config):
        if spatial_structure_config.entity_type == SpatialStructureEntityType.IFC_SITE:
            ifc_spatial_structure = ifc_file.create_ifc_site(ifc_local_placement, ifc_project)
        else:
            raise Exception(
                f"building step for structure entity type {spatial_structure_config.entity_type} not implemented")
        spatial_structure_element = Element.from_static_element_config(spatial_structure_config)
        spatial_structure_element.set_ifc_attributes(ifc_spatial_structure)
        spatial_structure_element.set_ifc_properties(ifc_file, ifc_spatial_structure)
        return ifc_spatial_structure

    def build_groups(self, ifc_file, groups):
        ifc_groups = {}
        groups_config = {group.path: group for group in self.ifc_config.groups}
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
                    if group_config.entity_type == GroupEntityType.IFC_DISTRIBUTION_SYSTEM:
                        ifc_groups[group_path] = ifc_file.create_ifc_distribution_system(group)
                    elif group_config.entity_type == GroupEntityType.IFC_DISTRIBUTION_CIRCUIT:
                        ifc_groups[group_path] = ifc_file.create_ifc_distribution_circuit(group)
                    elif group_config.entity_type == GroupEntityType.IFC_BUILDING_SYSTEM:
                        ifc_groups[group_path] = ifc_file.create_ifc_building_system(group)
                    elif group_config.entity_type == GroupEntityType.IFC_STRUCTURAL_ANALYSIS_MODEL:
                        ifc_groups[group_path] = ifc_file.create_ifc_structural_analysis_model(group)
                    elif group_config.entity_type == GroupEntityType.IFC_ZONE:
                        ifc_groups[group_path] = ifc_file.create_ifc_zone(group)
                    else:
                        raise Exception(
                            f"building step for ifc group entity {type(group_config.entity_type)} not implemented")
                    ifc_group = ifc_groups[group_path]

                    group_element = Element.from_static_element_config(group_config)
                    group_element.set_ifc_attributes(ifc_group)
                    group_element.set_ifc_properties(ifc_file, ifc_group)
                else:
                    ifc_groups[group_path] = ifc_file.create_ifc_group(group)
                if not parent_group_path == "":
                    ifc_file.create_ifc_rel_assigns_to_group([ifc_groups[group_path]], ifc_groups[parent_group_path])
            ifc_file.create_ifc_rel_assigns_to_group(ifc_group_elements, ifc_groups[group_definition])
