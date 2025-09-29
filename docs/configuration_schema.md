# Configuration

JSON Schema missing a description, provide it using the `description` key in the root of the JSON document.

### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| logging_level | `string` | ✅ | string |  | Logging level for the application (e.g., DEBUG, INFO, WARNING) |
| redis | `object` | ✅ | [RedisConfig](#redisconfig) |  | Redis configuration |
| db | `object` | ✅ | [DBConfig](#dbconfig) |  | Database configuration |
| stac | `object` | ✅ | [STACConfig](#stacconfig) |  | STAC configuration for external data sources |
| tin | `object` | ✅ | [TINConfig](#tinconfig) |  | TIN (Triangulated Irregular Network) generation configuration |
| ifc | `object` | ✅ | [IFCConfig](#ifcconfig) |  | IFC (Industry Foundation Classes) export configuration |
| i18n | `object` or `null` |  | [I18nConfig](#i18nconfig) | `null` | Internationalization (i18n) configuration |


---

# Definitions

## AttributeConfig_BuildingSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [Source_BuildingSourceType_](#source_buildingsourcetype_) | Source configuration for this attribute |

## AttributeConfig_ProjectionSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [Source_ProjectionSourceType_](#source_projectionsourcetype_) | Source configuration for this attribute |

## AttributeConfig_StaticSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [Source_StaticSourceType_](#source_staticsourcetype_) | Source configuration for this attribute |

## BuildingEntityConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity_type | `string` | ✅ | [BuildingEntityType](#buildingentitytype) |  | Type of entity |
| attributes | `array` |  | [AttributeConfig_BuildingSourceType_](#attributeconfig_buildingsourcetype_) | `[]` | List of attribute mappings |
| properties | `array` |  | [PropertyConfig_BuildingSourceType_](#propertyconfig_buildingsourcetype_) | `[]` | List of property mappings |
| building_parts | `array` |  | [BuildingPartConfig](#buildingpartconfig) | `[]` | List of building parts belonging to this building entity |

## BuildingEntityType

Supported ifc entity types for building entities

#### Type: `string`

**Possible Values:** `IFC_BUILDING`

## BuildingFeatureType

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the building |
| sql_path | `string` | ✅ | string |  | Path to SQL definition for the building feature type |
| egid_xpath | `string` | ✅ | string |  | XPath expression to extract EGID identifier |
| entity_mapping | `object` | ✅ | [BuildingEntityConfig](#buildingentityconfig) |  | Entity mapping configuration for the building |
| spatial_structure_mapping | `object` | ✅ | [EntityConfig_SpatialEntityType_StaticSourceType_](#entityconfig_spatialentitytype_staticsourcetype_) |  | Spatial structure mapping for the building |
| group_mapping | `array` |  | [Source_BuildingSourceType_](#source_buildingsourcetype_) | `[]` | Group mappings for the building feature type |

## BuildingPartConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| xpath | `string` | ✅ | string | XPath to locate the building part element in source data |
| entity_mapping | `object` | ✅ | [EntityConfig_BuildingPartEntityType_BuildingSourceType_](#entityconfig_buildingpartentitytype_buildingsourcetype_) | Entity mapping configuration for the building part |
| color | `object` |  | [Color](#color) | Color assigned to the building part |

## BuildingPartEntityType

Supported ifc entity types for building part entities

#### Type: `string`

**Possible Values:** `IFC_WALL` or `IFC_SLAB` or `IFC_ROOF` or `IFC_SPACE`

## BuildingSourceType

Supported source types for properties and attributes in building feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL` or `CITY_GML`

## Color

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| r | `number` | ✅ | `0.0 <= x <= 1.0` |  | Red channel |
| g | `number` | ✅ | `0.0 <= x <= 1.0` |  | Green channel |
| b | `number` | ✅ | `0.0 <= x <= 1.0` |  | Blue channel |
| a | `number` |  | `0.0 <= x <= 1.0` | `0.0` | Alpha channel |

## DBConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| dbname | `string` | ✅ | string | Database name |
| user | `string` | ✅ | string | Database username |
| host | `string` | ✅ | string | Database host address |
| port | `integer` | ✅ | integer | Database port number |
| password | `string` | ✅ | string | Database password |

## EntityConfig_BuildingPartEntityType_BuildingSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity_type | `string` | ✅ | [BuildingPartEntityType](#buildingpartentitytype) |  | Type of entity |
| attributes | `array` |  | [AttributeConfig_BuildingSourceType_](#attributeconfig_buildingsourcetype_) | `[]` | List of attribute mappings |
| properties | `array` |  | [PropertyConfig_BuildingSourceType_](#propertyconfig_buildingsourcetype_) | `[]` | List of property mappings |

## EntityConfig_GroupEntityType_StaticSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity_type | `string` | ✅ | [GroupEntityType](#groupentitytype) |  | Type of entity |
| attributes | `array` |  | [AttributeConfig_StaticSourceType_](#attributeconfig_staticsourcetype_) | `[]` | List of attribute mappings |
| properties | `array` |  | [PropertyConfig_StaticSourceType_](#propertyconfig_staticsourcetype_) | `[]` | List of property mappings |

## EntityConfig_ProjectionEntityType_ProjectionSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity_type | `string` | ✅ | [ProjectionEntityType](#projectionentitytype) |  | Type of entity |
| attributes | `array` |  | [AttributeConfig_ProjectionSourceType_](#attributeconfig_projectionsourcetype_) | `[]` | List of attribute mappings |
| properties | `array` |  | [PropertyConfig_ProjectionSourceType_](#propertyconfig_projectionsourcetype_) | `[]` | List of property mappings |

## EntityConfig_SpatialEntityType_StaticSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity_type | `string` | ✅ | [SpatialEntityType](#spatialentitytype) |  | Type of entity |
| attributes | `array` |  | [AttributeConfig_StaticSourceType_](#attributeconfig_staticsourcetype_) | `[]` | List of attribute mappings |
| properties | `array` |  | [PropertyConfig_StaticSourceType_](#propertyconfig_staticsourcetype_) | `[]` | List of property mappings |

## FeatureTypesConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| projections | `array` | ✅ | [ProjectionFeatureType](#projectionfeaturetype) | List of projection feature type definitions |
| buildings | `array` | ✅ | [BuildingFeatureType](#buildingfeaturetype) | List of building feature type definitions |

## GeoReferencing

Supported geo referencing methods

#### Type: `string`

**Possible Values:** `LO_GEO_REF_30` or `LO_GEO_REF_40` or `LO_GEO_REF_50`

## GridSize

Available grid sizes for projections

#### Type: `number`

**Possible Values:** `0.5` or `2.0`

## GroupConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| path | `string` | ✅ | string | Path identifier for the group |
| entity_mapping | `object` | ✅ | [EntityConfig_GroupEntityType_StaticSourceType_](#entityconfig_groupentitytype_staticsourcetype_) | Entity mapping configuration for the group |

## GroupEntityType

Supported ifc entity types for groups

#### Type: `string`

**Possible Values:** `IFC_DISTRIBUTION_SYSTEM` or `IFC_DISTRIBUTION_CIRCUIT` or `IFC_BUILDING_SYSTEM` or `IFC_STRUCTURAL_ANALYSIS_MODEL` or `IFC_ZONE`

## I18nConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| de | `string` or `null` |  | string | `null` | Path to the german translation file |
| fr | `string` or `null` |  | string | `null` | Path to the french translation string |
| it | `string` or `null` |  | string | `null` | Path to the italian translation string |

## IFCConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| author | `string` | ✅ | string |  | Author of the IFC model |
| version | `string` | ✅ | string |  | IFC schema version |
| application_name | `string` | ✅ | string |  | Name of the application generating IFC |
| project_name | `string` | ✅ | string |  | Project name in IFC |
| geo_referencing | `string` | ✅ | [GeoReferencing](#georeferencing) |  | Georeferencing configuration for IFC |
| triangulation_representation_type | `string` | ✅ | [TriangulationRepresentationType](#triangulationrepresentationtype) |  | Triangulation representation type to use |
| feature_types | `object` | ✅ | [FeatureTypesConfig](#featuretypesconfig) |  | Configured feature types for IFC |
| groups | `array` |  | [GroupConfig](#groupconfig) | `[]` | List of group configurations for IFC |

## ProjectionEntityType

Supported ifc entity types for projection entities

#### Type: `string`

**Possible Values:** `IFC_GEOGRAPHIC_ELEMENT`

## ProjectionFeatureType

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the projection |
| sql_path | `string` | ✅ | string |  | Path to SQL definition for the projection feature type |
| entity_mapping | `object` | ✅ | [EntityConfig_ProjectionEntityType_ProjectionSourceType_](#entityconfig_projectionentitytype_projectionsourcetype_) |  | Entity mapping configuration for the projection |
| spatial_structure_mapping | `object` | ✅ | [EntityConfig_SpatialEntityType_StaticSourceType_](#entityconfig_spatialentitytype_staticsourcetype_) |  | Spatial structure mapping for the projection |
| group_mapping | `array` |  | [Source_ProjectionSourceType_](#source_projectionsourcetype_) | `[]` | Group mappings for the projection feature type |
| color | `object` |  | [Color](#color) |  | Color assigned to the projection feature type |

## ProjectionSourceType

Supported source types for properties and attributes in projection feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL`

## PropertyConfig_BuildingSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [Source_BuildingSourceType_](#source_buildingsourcetype_) | Source configuration for this property |

## PropertyConfig_ProjectionSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [Source_ProjectionSourceType_](#source_projectionsourcetype_) | Source configuration for this property |

## PropertyConfig_StaticSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [Source_StaticSourceType_](#source_staticsourcetype_) | Source configuration for this property |

## RedisConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| host | `string` | ✅ | string |  | Redis host address |
| port | `integer` | ✅ | integer |  | Redis port number |
| db | `object` | ✅ | [RedisDBConfig](#redisdbconfig) |  | Nested Redis database configuration |
| global_keyprefix | `string` or `null` |  | string | `null` | Optional global keyprefix for the Redis result backend |

## RedisDBConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| celery_broker | `integer` | ✅ | `0 <= x ` | DB index for Celery broker |
| celery_backend | `integer` | ✅ | `0 <= x ` | DB index for Celery result backend |
| file_cache | `integer` | ✅ | `0 <= x ` | DB index for file cache |

## STACConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| dtm_items_url | `string` or `null` |  | string | `null` | URL to STAC items for DTM data |
| building_items_url | `string` or `null` |  | string | `null` | URL to STAC items for building data |

## Source_BuildingSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [BuildingSourceType](#buildingsourcetype) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## Source_ProjectionSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [ProjectionSourceType](#projectionsourcetype) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## Source_StaticSourceType_

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [StaticSourceType](#staticsourcetype) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## SpatialEntityType

Supported ifc entity types for spatial entities

#### Type: `string`

**Possible Values:** `IFC_SITE`

## StaticSourceType

Static source types for properties and attributes

#### Type: `string`

**Possible Values:** `STATIC`

## TINConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| grid_size | `number` | ✅ | [GridSize](#gridsize) | TIN grid size |
| max_height_error | `number` | ✅ | `0.0 <= x <= 0.05` | Maximum allowed height error for TIN generation |

## TriangulationRepresentationType

Supported build methods for the triangulations in the ifc

#### Type: `string`

**Possible Values:** `TESSELLATION` or `BREP`


---

Markdown generated with [jsonschema-markdown](https://github.com/elisiariocouto/jsonschema-markdown).
