# Configuration

Root application configuration.

This class defines the complete configuration model for the application. It aggregates
settings for logging, internationalization (i18n), Redis and PostGIS database connections,
STAC data sources, TIN generation, and IFC export configuration. The configuration is
typically loaded from a YAML file using the `load()` class method, which supports
environment variable expansion.

### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| logging_level | `string` | ✅ | string |  | Logging level for the application (e.g., DEBUG, INFO, WARNING) |
| redis | `object` | ✅ | [RedisConfig](#redisconfig) |  | Redis configuration |
| db | `object` | ✅ | [DBConfig](#dbconfig) |  | Database configuration |
| stac | `object` | ✅ | [STACConfig](#stacconfig) |  | STAC configuration for external data sources |
| ifc | `object` | ✅ | [IFCConfig](#ifcconfig) |  | IFC (Industry Foundation Classes) export configuration |
| i18n | `object` or `null` |  | [I18nConfig](#i18nconfig) | `null` | Internationalization (i18n) configuration |
| tin | `object` |  | [TINConfig](#tinconfig) |  | TIN (Triangulated Irregular Network) generation configuration |


---

# Definitions

## AttributeConfig

Attribute mapping configuration

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| value | `string` | ✅ | string | Attribute value |

## BuildingAttributeConfig

Attribute mapping configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [BuildingSourceConfig](#buildingsourceconfig) | Source configuration for this attribute |

## BuildingEntity

Supported ifc entities for building entities

#### Type: `string`

**Possible Values:** `IFC_BUILDING`

## BuildingEntityConfig

Entity mapping configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [BuildingEntity](#buildingentity) |  | Type of entity |
| attributes | `array` |  | [BuildingAttributeConfig](#buildingattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [BuildingPropertyConfig](#buildingpropertyconfig) | `[]` | List of property mappings |
| building_parts | `array` |  | [BuildingPartConfig](#buildingpartconfig) | `[]` | List of building parts belonging to this building entity |

## BuildingFeatureType

Feature type configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the building |
| sql_path | `string` | ✅ | string |  | Path to SQL definition for the building feature type. Must return at least a column named 'egid'. |
| egid_xpath | `string` | ✅ | string |  | XPath expression to extract EGID identifier from city gml building entities |
| entity_mapping | `object` | ✅ | [BuildingEntityConfig](#buildingentityconfig) |  | Entity mapping configuration for the building |
| spatial_structure_mapping | `object` | ✅ | [BuildingSpatialEntityConfig](#buildingspatialentityconfig) |  | Spatial structure mapping for the building |
| group_mapping | `array` |  | [BuildingSourceConfig](#buildingsourceconfig) | `[]` | Group mappings for the building feature type |

## BuildingPartConfig

Building part configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [BuildingPartEntity](#buildingpartentity) |  | Type of entity |
| geometry_mapping | `object` or `null` |  | [GmlGeometryMapping](#gmlgeometrymapping) | `null` | Geometry mapping for the building part |
| color | `object` |  | [Color](#color) | `"white"` | Color assigned to the building part |

## BuildingPartEntity

Supported ifc entities for building part entities

#### Type: `string`

**Possible Values:** `IFC_WALL` or `IFC_SLAB` or `IFC_ROOF` or `IFC_SPACE` or `IFC_BUILDING_ELEMENT_PROXY`

## BuildingPropertyConfig

Property mapping configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [BuildingSourceConfig](#buildingsourceconfig) | Source configuration for this property |

## BuildingSource

Supported source types for properties and attributes in building feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL` or `CITY_GML`

## BuildingSourceConfig

Source configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [BuildingSource](#buildingsource) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## BuildingSpatialEntityConfig

Spatial structure mapping configuration for building feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [BuildingAttributeConfig](#buildingattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [BuildingPropertyConfig](#buildingpropertyconfig) | `[]` | List of property mappings |

## Color

Color configuration based on red, green, blue and alpha channels

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| r | `number` | ✅ | `0.0 <= x <= 1.0` |  | Red channel |
| g | `number` | ✅ | `0.0 <= x <= 1.0` |  | Green channel |
| b | `number` | ✅ | `0.0 <= x <= 1.0` |  | Blue channel |
| a | `number` |  | `0.0 <= x <= 1.0` | `0.0` | Alpha channel |

## DBConfig

Postgis connection configuration

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| dbname | `string` | ✅ | string | Database name |
| user | `string` | ✅ | string | Database username |
| host | `string` | ✅ | string | Database host address |
| port | `integer` | ✅ | integer | Database port number |
| password | `string` | ✅ | string | Database password |

## ExtrusionAttributeConfig

Attribute mapping configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [ExtrusionConfigSource](#extrusionconfigsource) | Source configuration for this attribute |

## ExtrusionConfigSource

Source configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [ExtrusionSource](#extrusionsource) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## ExtrusionEntity

Supported ifc entities for extrusion entities

#### Type: `string`

**Possible Values:** `IFC_PIPE_SEGMENT` or `IFC_DISTRIBUTION_FLOW_ELEMENT`

## ExtrusionEntityConfig

Entity mapping configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [ExtrusionEntity](#extrusionentity) |  | Type of entity |
| attributes | `array` |  | [ExtrusionAttributeConfig](#extrusionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ExtrusionPropertyConfig](#extrusionpropertyconfig) | `[]` | List of property mappings |

## ExtrusionEntityTypeConfig

Entity type mapping configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [ExtrusionAttributeConfig](#extrusionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ExtrusionPropertyConfig](#extrusionpropertyconfig) | `[]` | List of property mappings |

## ExtrusionFeatureType

Feature type configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the extrusion |
| entity_mapping | `object` | ✅ | [ExtrusionEntityConfig](#extrusionentityconfig) |  | Entity mapping configuration for the extrusion |
| spatial_structure_mapping | `object` | ✅ | [ExtrusionSpatialEntityConfig](#extrusionspatialentityconfig) |  | Spatial structure mapping for the projection |
| sql_path | `string` or `null` |  | string | `null` | Path to SQL definition for the extrusion feature type. Exact specification can be found in the configuration documentation. |
| entity_type_mapping | `object` or `null` |  | [ExtrusionEntityTypeConfig](#extrusionentitytypeconfig) | `null` | Entity type mapping configuration for the extrusion. (Only supported for entities with TypeObject) |
| group_mapping | `array` |  | [ExtrusionConfigSource](#extrusionconfigsource) | `[]` | Group mappings for the projection feature type |
| color | `object` |  | [Color](#color) | `"white"` | Color assigned to the extrusion feature type |

## ExtrusionPropertyConfig

Property mapping configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [ExtrusionConfigSource](#extrusionconfigsource) | Source configuration for this property |

## ExtrusionSource

Supported source types for properties and attributes in extrusion feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL`

## ExtrusionSpatialEntityConfig

Spatial structure mapping configuration for extrusion feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [ExtrusionAttributeConfig](#extrusionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ExtrusionPropertyConfig](#extrusionpropertyconfig) | `[]` | List of property mappings |

## GeoReferencing

Supported geo referencing methods

#### Type: `string`

**Possible Values:** `LO_GEO_REF_30` or `LO_GEO_REF_40` or `LO_GEO_REF_50`

## GmlGeometry

Supported gml geometry types

#### Type: `string`

**Possible Values:** `MULTI_SURFACE` or `SOLID` or `COMPOSITE_SOLID`

## GmlGeometryMapping

Geometry mapping for building part

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| xpath | `string` | ✅ | string | XPath expression to locate the building part geometry in source data |
| geometry | `string` | ✅ | [GmlGeometry](#gmlgeometry) | Referenced geometry type of the building part |

## GridSize

Available grid sizes for projections

#### Type: `number`

**Possible Values:** `0.5` or `2.0`

## GroupConfig

Group configuration for IFC export

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| path | `string` | ✅ | string | Path identifier for the group |
| entity_mapping | `object` | ✅ | [GroupEntityConfig](#groupentityconfig) | Entity mapping configuration for the group |

## GroupEntity

Supported ifc entities for groups

#### Type: `string`

**Possible Values:** `IFC_DISTRIBUTION_SYSTEM` or `IFC_DISTRIBUTION_CIRCUIT` or `IFC_BUILDING_BUILT_SYSTEM` or `IFC_STRUCTURAL_ANALYSIS_MODEL` or `IFC_ZONE`

## GroupEntityConfig

Entity mapping configuration for group

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [GroupEntity](#groupentity) |  | Type of entity |
| attributes | `array` |  | [AttributeConfig](#attributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [PropertyConfig](#propertyconfig) | `[]` | List of property mappings |

## I18nConfig

Internationalization (i18n) configuration

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| de | `string` or `null` |  | string | `null` | Path to the german translation file |
| fr | `string` or `null` |  | string | `null` | Path to the french translation string |
| it | `string` or `null` |  | string | `null` | Path to the italian translation string |

## IFCConfig

IFC export configuration

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| author | `string` | ✅ | string |  | Author of the IFC model |
| version | `string` | ✅ | string |  | IFC schema version |
| application_name | `string` | ✅ | string |  | Name of the application generating IFC |
| project_name | `string` | ✅ | string |  | Project name in IFC |
| geo_referencing | `string` | ✅ | [GeoReferencing](#georeferencing) |  | Georeferencing configuration for IFC |
| projection_feature_types | `array` |  | [ProjectionFeatureType](#projectionfeaturetype) | `[]` | List of projection feature type definitions |
| building_feature_types | `array` |  | [BuildingFeatureType](#buildingfeaturetype) | `[]` | List of building feature type definitions |
| extrusion_feature_types | `array` |  | [ExtrusionFeatureType](#extrusionfeaturetype) | `[]` | List of extrusion feature type definitions |
| groups | `array` |  | [GroupConfig](#groupconfig) | `[]` | List of group configurations for IFC |

## ProjectionAttributeConfig

Attribute mapping configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [ProjectionConfigSource](#projectionconfigsource) | Source configuration for this attribute |

## ProjectionConfigSource

Source configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [ProjectionSource](#projectionsource) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## ProjectionEntity

Supported ifc entities for projection entities

#### Type: `string`

**Possible Values:** `IFC_GEOGRAPHIC_ELEMENT` or `IFC_ANNOTATION` or `IFC_SITE` or `IFC_BUILDING` or `IFC_SPATIAL_ZONE`

## ProjectionEntityConfig

Entity mapping configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [ProjectionEntity](#projectionentity) |  | Type of entity |
| attributes | `array` |  | [ProjectionAttributeConfig](#projectionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ProjectionPropertyConfig](#projectionpropertyconfig) | `[]` | List of property mappings |

## ProjectionEntityTypeConfig

Entity type mapping configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [ProjectionAttributeConfig](#projectionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ProjectionPropertyConfig](#projectionpropertyconfig) | `[]` | List of property mappings |

## ProjectionFeatureType

Feature type configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the projection |
| sql_path | `string` | ✅ | string |  | Path to SQL definition for the projection feature type. Must return at least a column named 'wkt'. |
| entity_mapping | `object` | ✅ | [ProjectionEntityConfig](#projectionentityconfig) |  | Entity mapping configuration for the projection |
| spatial_structure_mapping | `object` | ✅ | [ProjectionSpatialEntityConfig](#projectionspatialentityconfig) |  | Spatial structure mapping for the projection |
| entity_type_mapping | `object` or `null` |  | [ProjectionEntityTypeConfig](#projectionentitytypeconfig) | `null` | Entity type mapping configuration for the projection. (Only supported for entities with TypeObject) |
| group_mapping | `array` |  | [ProjectionConfigSource](#projectionconfigsource) | `[]` | Group mappings for the projection feature type |
| color | `object` |  | [Color](#color) | `"white"` | Color assigned to the projection feature type |

## ProjectionPropertyConfig

Property mapping configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [ProjectionConfigSource](#projectionconfigsource) | Source configuration for this property |

## ProjectionSource

Supported source types for properties and attributes in projection feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL`

## ProjectionSpatialEntityConfig

Spatial structure mapping configuration for projection feature type

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [ProjectionAttributeConfig](#projectionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ProjectionPropertyConfig](#projectionpropertyconfig) | `[]` | List of property mappings |

## PropertyConfig

Property mapping configuration

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| value | `string` | ✅ | string | Property value |

## RedisConfig

Redis connection configuration

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| host | `string` | ✅ | string |  | Redis host address |
| port | `integer` | ✅ | integer |  | Redis port number |
| db | `object` | ✅ | [RedisDBConfig](#redisdbconfig) |  | Nested Redis database configuration |
| global_keyprefix | `string` or `null` |  | string | `null` | Optional global keyprefix for the Redis result backend |
| queue | `string` or `null` |  | string | `null` | Optional queue name for Celery tasks |

## RedisDBConfig

Redis databases configuration

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| celery_broker | `integer` | ✅ | `0 <= x ` | DB index for Celery broker |
| celery_backend | `integer` | ✅ | `0 <= x ` | DB index for Celery result backend |
| file_cache | `integer` | ✅ | `0 <= x ` | DB index for file cache |

## STACConfig

STAC URLs configuration for external data sources

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| dtm_items_url | `string` or `null` |  | string | `null` | URL to STAC items for DTM data |
| building_items_url | `string` or `null` |  | string | `null` | URL to STAC items for building data |

## TINConfig

TIN generation configuration

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| grid_size | `number` | ✅ | [GridSize](#gridsize) | TIN grid size |
| max_height_error | `number` | ✅ | `0.0 <= x <= 0.05` | Maximum allowed height error for TIN generation |


---

Markdown generated with [jsonschema-markdown](https://github.com/elisiariocouto/jsonschema-markdown).
