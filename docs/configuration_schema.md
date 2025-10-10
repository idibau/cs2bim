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

## BuildingAttributeConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [__main____BuildingSource](#__main____buildingsource) | Source configuration for this attribute |

## BuildingEntity

Supported ifc entity types for building entities

#### Type: `string`

**Possible Values:** `IFC_BUILDING`

## BuildingEntityConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [BuildingEntity](#buildingentity) |  | Type of entity |
| attributes | `array` |  | [BuildingAttributeConfig](#buildingattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [BuildingPropertyConfig](#buildingpropertyconfig) | `[]` | List of property mappings |
| building_parts | `array` |  | [BuildingPartConfig](#buildingpartconfig) | `[]` | List of building parts belonging to this building entity |

## BuildingFeatureType

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the building |
| sql_path | `string` | ✅ | string |  | Path to SQL definition for the building feature type |
| egid_xpath | `string` | ✅ | string |  | XPath expression to extract EGID identifier from city gml building entities |
| entity_mapping | `object` | ✅ | [BuildingEntityConfig](#buildingentityconfig) |  | Entity mapping configuration for the building |
| spatial_structure_mapping | `object` | ✅ | [BuildingSpatialEntityConfig](#buildingspatialentityconfig) |  | Spatial structure mapping for the building |
| group_mapping | `array` |  | [__main____BuildingSource](#__main____buildingsource) | `[]` | Group mappings for the building feature type |

## BuildingPartConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [BuildingPartEntity](#buildingpartentity) |  | Type of entity |
| geometry_mapping | `object` or `null` |  | [GmlGeometryMapping](#gmlgeometrymapping) | `null` | Geometry mapping for the building part |
| color | `object` |  | [Color](#color) |  | Color assigned to the building part |

## BuildingPartEntity

Supported ifc entity types for building part entities

#### Type: `string`

**Possible Values:** `IFC_WALL` or `IFC_SLAB` or `IFC_ROOF` or `IFC_BUILDING_ELEMENT_PROXY`

## BuildingPropertyConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [__main____BuildingSource](#__main____buildingsource) | Source configuration for this property |

## BuildingSpatialEntityConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [BuildingAttributeConfig](#buildingattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [BuildingPropertyConfig](#buildingpropertyconfig) | `[]` | List of property mappings |

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

## GmlGeometry

Supported gml geometry types

#### Type: `string`

**Possible Values:** `MULTI_SURFACE` or `SOLID` or `COMPOSITE_SOLID`

## GmlGeometryMapping

No description provided for this model.

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

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| path | `string` | ✅ | string | Path identifier for the group |
| entity_mapping | `object` | ✅ | [GroupEntityConfig](#groupentityconfig) | Entity mapping configuration for the group |

## GroupEntity

Supported ifc entity types for groups

#### Type: `string`

**Possible Values:** `IFC_DISTRIBUTION_SYSTEM` or `IFC_DISTRIBUTION_CIRCUIT` or `IFC_BUILDING_BUILT_SYSTEM` or `IFC_STRUCTURAL_ANALYSIS_MODEL` or `IFC_ZONE`

## GroupEntityConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [GroupEntity](#groupentity) |  | Type of entity |
| attributes | `array` |  | [StaticAttributeConfig](#staticattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [StaticPropertyConfig](#staticpropertyconfig) | `[]` | List of property mappings |

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
| feature_types | `object` | ✅ | [FeatureTypesConfig](#featuretypesconfig) |  | Configured feature types for IFC |
| groups | `array` |  | [GroupConfig](#groupconfig) | `[]` | List of group configurations for IFC |

## ProjectionAttributeConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| source | `object` | ✅ | [__main____ProjectionSource](#__main____projectionsource) | Source configuration for this attribute |

## ProjectionEntity

Supported ifc entity types for projection entities

#### Type: `string`

**Possible Values:** `IFC_GEOGRAPHIC_ELEMENT`

## ProjectionEntityConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| entity | `string` | ✅ | [ProjectionEntity](#projectionentity) |  | Type of entity |
| attributes | `array` |  | [ProjectionAttributeConfig](#projectionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ProjectionPropertyConfig](#projectionpropertyconfig) | `[]` | List of property mappings |

## ProjectionEntityTypeConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [ProjectionAttributeConfig](#projectionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ProjectionPropertyConfig](#projectionpropertyconfig) | `[]` | List of property mappings |

## ProjectionFeatureType

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Feature type name for the projection |
| sql_path | `string` | ✅ | string |  | Path to SQL definition for the projection feature type |
| entity_mapping | `object` | ✅ | [ProjectionEntityConfig](#projectionentityconfig) |  | Entity mapping configuration for the projection |
| spatial_structure_mapping | `object` | ✅ | [ProjectionSpatialEntityConfig](#projectionspatialentityconfig) |  | Spatial structure mapping for the projection |
| entity_type_mapping | `object` or `null` |  | [ProjectionEntityTypeConfig](#projectionentitytypeconfig) | `null` | Entity type mapping configuration for the projection |
| group_mapping | `array` |  | [__main____ProjectionSource](#__main____projectionsource) | `[]` | Group mappings for the projection feature type |
| color | `object` |  | [Color](#color) |  | Color assigned to the projection feature type |

## ProjectionPropertyConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| source | `object` | ✅ | [__main____ProjectionSource](#__main____projectionsource) | Source configuration for this property |

## ProjectionSpatialEntityConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| attributes | `array` |  | [ProjectionAttributeConfig](#projectionattributeconfig) | `[]` | List of attribute mappings |
| properties | `array` |  | [ProjectionPropertyConfig](#projectionpropertyconfig) | `[]` | List of property mappings |

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

## StaticAttributeConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| attribute | `string` | ✅ | string | Attribute name (Only applied if the attribute exists on the entity) |
| value | `string` | ✅ | string | Attribute value |

## StaticPropertyConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| property | `string` | ✅ | string | Property name |
| property_set | `string` | ✅ | string | Property set name |
| value | `string` | ✅ | string | Property value |

## TINConfig

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| grid_size | `number` | ✅ | [GridSize](#gridsize) | TIN grid size |
| max_height_error | `number` | ✅ | `0.0 <= x <= 0.05` | Maximum allowed height error for TIN generation |

## __main____BuildingSource

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [config__building_source__BuildingSource](#config__building_source__buildingsource) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## __main____ProjectionSource

No description provided for this model.

#### Type: `object`

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| type | `string` | ✅ | [config__projection_source__ProjectionSource](#config__projection_source__projectionsource) | Type of the data source |
| expression | `string` | ✅ | string | Expression defining the source data |

## config__building_source__BuildingSource

Supported source types for properties and attributes in building feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL` or `CITY_GML`

## config__projection_source__ProjectionSource

Supported source types for properties and attributes in projection feature types

#### Type: `string`

**Possible Values:** `STATIC` or `SQL`


---

Markdown generated with [jsonschema-markdown](https://github.com/elisiariocouto/jsonschema-markdown).
