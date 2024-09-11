import datetime
from ifcopenshell import file

from cs2bim.config.geo_referencing import GeoReferencing
from cs2bim.config.feature_class import FeatureClass
from cs2bim.ifc.ifc_utils import *
from cs2bim.ifc.ifc_model import IfcModel
from cs2bim.ifc.entity.ifc_spatial_structure import IfcSpatialStructureEntityType
from cs2bim.ifc.entity.ifc_element import IfcElementEntityType
from cs2bim.ifc.geometry.triangulation import Triangulation, TriangulationRepresentationType

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
    ):
        self.author = author
        self.version = version
        self.application_name = application_name
        self.project_name = project_name
        self.geo_referencing = geo_referencing
        self.triangulation_representation_type = triangulation_representation_type
        self.feature_classes = feature_classes

    def build(self, ifc_model: IfcModel) -> file:
        """Builds an ifcopenshell ifc file based on a model object"""
        logger.info(f"initialize new ifc writer for ifc '{ifc_model.file_name}'")
        ifc_file = file(schema=ifc_model.schema)
        ifc_file.wrapped_data.header.file_name.name = ifc_model.file_name

        logger.info(f"build ifc")
        person = add_ifc_person(ifc_file, self.author)
        organization = add_ifc_organization(ifc_file, self.author)
        person_and_organization = add_ifc_person_and_organization(ifc_file, person, organization)
        application = add_ifc_application(ifc_file, organization, self.version, self.application_name)
        owner_history = add_ifc_owner_history(
            ifc_file,
            person_and_organization,
            application,
            int(datetime.datetime.now().timestamp()),
        )
        length_unit = add_ifc_si_unit(ifc_file, "LENGTHUNIT", "METRE")
        area_unit = add_ifc_si_unit(ifc_file, "AREAUNIT", "SQUARE_METRE")
        volume_unit = add_ifc_si_unit(ifc_file, "VOLUMEUNIT", "CUBIC_METRE")
        degree_unit = add_ifc_si_unit(ifc_file, "PLANEANGLEUNIT", "RADIAN")
        plane_angle_measure = add_ifc_plane_angle_measure(ifc_file)
        measure_with_unit = add_ifc_measure_with_unit(ifc_file, plane_angle_measure, degree_unit)
        dimensional_exponents = add_ifc_dimensional_exponents(ifc_file)
        conversion_based_unit = add_ifc_conversion_based_unit(ifc_file, dimensional_exponents, measure_with_unit)
        unit_assignment = add_ifc_unit_assignment(ifc_file, length_unit, area_unit, volume_unit, conversion_based_unit)

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_40:
            context_location = add_ifc_cartesian_point(ifc_file, ifc_model.origin)
        else:
            context_location = add_ifc_cartesian_point(ifc_file, (0.0, 0.0, 0.0))
        axis_2_placement_3D = add_ifc_axis_2_placement_3D(ifc_file, context_location)
        representation_context = add_ifc_geometric_representation_context(ifc_file, axis_2_placement_3D)

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_50:
            projected_crs = add_ifc_projected_crs(ifc_file, length_unit)
            add_ifc_map_conversion(ifc_file, representation_context, projected_crs, ifc_model.origin)

        project = add_ifc_project(ifc_file, self.project_name, owner_history, representation_context, unit_assignment)

        if self.geo_referencing == GeoReferencing.LO_GEO_REF_30:
            site_location = add_ifc_cartesian_point(ifc_file, ifc_model.origin)
        else:
            site_location = add_ifc_cartesian_point(ifc_file, (0.0, 0.0, 0.0))
        axis = add_ifc_axis_2_placement_3D(ifc_file, site_location)
        local_placement = add_ifc_local_placement(ifc_file, axis)

        group_entities = {}
        spatial_structures_entities = {}
        for feature_class_key, elements in ifc_model.feature_classes.items():
            feature_class = self.feature_classes[feature_class_key]
            logger.info(f"FeatureClass {feature_class_key}: build ifc spatial structure")
            spatial_structure = feature_class.spatial_structure
            if not spatial_structure.get_key() in spatial_structures_entities:
                if spatial_structure.type == IfcSpatialStructureEntityType.IFC_SITE:
                    site = add_ifc_site(ifc_file, spatial_structure.name, owner_history, local_placement)
                    add_ifc_rel_aggregates(ifc_file, project, [site])
                    spatial_structures_entities[spatial_structure.get_key()] = site
                else:
                    raise Exception(
                        f"builing step for structure entity type {spatial_structure.type.name} not implemented"
                    )

            logger.info(f"FeatureClass {feature_class_key}: build ifc elements")
            values = feature_class.color_definition
            color = add_ifc_colour_rgb(ifc_file, values[0:3])
            shading = add_ifc_surface_style_shading(ifc_file, color, values[3])
            style_entity = add_ifc_surface_style(ifc_file, shading)

            element_entities = []
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
                        cartesian_point_list = add_ifc_cartesian_point_list_3D(ifc_file, vertices)
                        item = add_ifc_triangulated_face_set(ifc_file, cartesian_point_list, point_index_list)
                    elif representation_type == TriangulationRepresentationType.BREP:
                        vertex_dict = {}
                        faces = []
                        for triangle in element.geometry.triangles:
                            vertices = []
                            for vertex in triangle:
                                if vertex not in vertex_dict:
                                    vertex_dict[vertex] = add_ifc_cartesian_point(ifc_file, vertex)
                                vertices.append(vertex_dict[vertex])
                            poly_loop = add_ifc_poly_loop(ifc_file, vertices)
                            outer_bound = add_ifc_face_outer_bound(ifc_file, poly_loop)
                            face = add_ifc_face(ifc_file, outer_bound)
                            faces.append(face)
                        closed_shell = add_ifc_closed_shell(ifc_file, faces)
                        item = add_ifc_faceted_brep(ifc_file, closed_shell)
                    else:
                        raise Exception(
                            f"builing step for triangulation representation type {representation_type.name} not implemented"
                        )
                else:
                    raise Exception(f"builing step for geometry class {type(element.geometry)} not implemented")

                add_ifc_styled_item(ifc_file, item, style_entity)
                shape_representation = add_ifc_shape_representation(
                    ifc_file, representation_context, representation_type.value, item
                )
                product_definition_shape = add_ifc_product_definition_shape(ifc_file, shape_representation)
                if feature_class.entity_type == IfcElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
                    element_entity = add_ifc_geographic_element(ifc_file, element.name, element.description)
                else:
                    raise Exception(
                        f"builing step for feature class entity type {element.feature_class.entity_type.name} not implemented"
                    )
                element_entity.Representation = product_definition_shape

                for property_set in element.property_sets.values():
                    property_entites = []
                    for key, value in property_set.properties.items():
                        text = add_ifc_text(ifc_file, value)
                        property_entites.append(add_ifc_property_single_value(ifc_file, key, text))
                    property_set = add_ifc_property_set(ifc_file, property_set.name, property_entites)
                    add_ifc_rel_defines_by_properties(ifc_file, [element_entity], property_set)

                element_entities.append(element_entity)

            add_ifc_rel_aggregates(ifc_file, spatial_structures_entities[spatial_structure.get_key()], element_entities)

            logger.info(f"FeatureClass {feature_class_key}: build ifc groups")
            for group_definition in feature_class.groups:
                path = []
                for group in group_definition.split("."):
                    parent_group_path = ".".join(path)
                    path.append(group)
                    group_path = ".".join(path)
                    if not group_path in group_entities:
                        group_entities[group_path] = add_ifc_group(ifc_file, group)
                        if not parent_group_path == "":
                            add_ifc_rel_assigns_to_group(
                                ifc_file, [group_entities[group_path]], group_entities[parent_group_path]
                            )
                add_ifc_rel_assigns_to_group(ifc_file, element_entities, group_entities[group_definition])

        logger.info("completed ifc build")

        return ifc_file
