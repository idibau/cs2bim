# cs2bim

## Getting started

Build docker image
```console
docker build -t cs2bim-run -f Dockerfile . --rm
```
Run docker image
```console
docker run -e IFC_VERSION=[cs2bim.enum.ifc_version.IfcVersion] -e NAME=[str] -e POLYGON=[wkt] -v .:/workspace/output --name cs2bim-run --rm cs2bim-run
```
The polygon must be a valid wkt string in LV95.

Examples:
- docker run -e IFC_VERSION="IFC4" -e NAME="Test" -e POLYGON="POLYGON((2689114 1285136,2689143 1285192,2689170 1285159,2689114 1285136))" -v .:/workspace/output --name cs2bim-run --rm cs2bim-run

After you run the docker container successfully there will be new output ifc file inside the folder from where you started the container.

Important: If you change the config.yml, the container must be rebuild to make it work.

## Getting started dev

Build and run docker container or build and open cotainer with VSCode
```console
docker-compose -f docker-compose-dev.yml up 
```
Install pip packages (Run in container at /workspace)
```console
pip install --no-cache-dir --upgrade -r /workspace/requirements.txt
```

## Configuration

Some properties of this python project can be configured using the config.yaml file.

### Structure

| Key | Type | Values | Example |
|---|---|---|---|
|logging_level|str|NOTSET; DEBUG; INFO; WARN; ERROR; CRITICAL|"cs2bim"|
|---|---|---|---|
|db.dbname|str|?|"cs2bim"|
|db.user|str|?|"postgres"|
|db.host|str|?|"host.docker.internal"|
|db.port|int|?|5432|
|db.password|str|?|"xxx"|
|db.schema|str|?|"cs2bim"|
|---|---|---|---|
|swisstopo.stac_api|str|?|"https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items"|
|---|---|---|---|
|tin.grid_size|float|0.5;2|0.5|
|tin.max_height_error|float|TODO|0.05|
|---|---|---|---|
|ifc.author|str|?|"author"|
|ifc.version|str|?|"1.0"|
|ifc.application_name|str|?|"cs2bim"|
|ifc.project_name|str|?|"Project A"|
|ifc.geo_referencing|GeoReferencing|LO_GEO_REF_30; LO_GEO_REF_40; LO_GEO_REF_50|LO_GEO_REF_30|
|ifc.triangulation_representation_type|TriangulationRepresentationType|TESSELLATION; BREP|BREP|
|ifc.feature_classes.$FeatureClassKey.element_name_column|str|?|"name_column"|
|ifc.feature_classes.$FeatureClassKey.properties.$ListElement.name|str|?|"Property"|
|ifc.feature_classes.$FeatureClassKey.properties.$ListElement.column|str|?|"property_column"|
|ifc.feature_classes.$FeatureClassKey.properties.$ListElement.set|str|?|"PropertySet"|
|ifc.feature_classes.$FeatureClassKey.entity_type|IfcElementEntityType|IFC_GEOGRAPHIC_ELEMENT|IFC_GEOGRAPHIC_ELEMENT|
|ifc.feature_classes.$FeatureClassKey.spatial_structure.entity_type|IfcSpatialStructureEntityType|IFC_SITE|IFC_SITE|
|ifc.feature_classes.$FeatureClassKey.spatial_structure.name|str|?|"Site"|
|ifc.feature_classes.$FeatureClassKey.group_columns|list[str]|?|"group_column"|
|ifc.feature_classes.$FeatureClassKey.color_definition.r|float|0.0 - 1-0|0.1|
|ifc.feature_classes.$FeatureClassKey.color_definition.g|float|0.0 - 1-0|0.5|
|ifc.feature_classes.$FeatureClassKey.color_definition.b|float|0.0 - 1-0|0.5|
|ifc.feature_classes.$FeatureClassKey.color_definition.a|float|0.0 - 1-0|0.3|

### Types

EPSGCode -> cs2bim.enum.epsg_code.py
GeoReferencing -> cs2bim.config.geo_referencing.py\
TriangulationRepresentationType -> cs2bim.geometry.triangulation.py\
IfcElementEntityType -> cs2bim.ifc.entity.ifc_element.py\
IfcSpatialStructureEntityType -> cs2bim.ifc.entity.ifc_spatial_structure.py

### Postgis-Queries

For each feature class you have to provide a sql for querying the data. At the moment terrain data is the only supported type of data for feature classes. This type requiers the sql to take a polyon wkt as parameter "%(polygon)s" and return a column named "wkt" with wkt string values. To guarantee a correct processing it is important to check that the sql also delivers all columns that are additionally configured for the according feature class. This can be a column for the entity names, properties or groups.

When defining a group you can use "." to create nested group structures.

Example:
config.yaml
```yaml
...
feature_class_x:
      sql: "sql/feature_class_x.sql"
      element_name_column: "name_column"
      properties:
        - name: "Property"
          column: "property_column"
          set: "ProperttySetName" 
      group_columns:
        - "group"
...
```
sql/feature_class_x.sql
```sql
with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(geometrie, 1)) as wkt,
    nbident as name_column,
    nummer as property_column,
    CASE 
        WHEN x THEN 'Amtliche Vermessung.Feature-Klassen.x' 
        ELSE 'Amtliche Vermessung.Feature-Klassen.y'
    END as group
from
    cs2bim.liegenschaft l
    left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
    join perimeter on ST_Intersects(geometrie, perimeter.geom)
```


Useful postgis functions:

ST_GeomFromText -> Constructs a PostGIS ST_Geometry object \
ST_AsText -> Returns the OGC WKT representation of the geometry\
ST_CurveToLine ->  Converts a given geometry to a linear geometry\
ST_Intersects -> Returns true if two geometries intersect. Geometries intersect if they have any point in common.
ST_Contains -> Returns true if the first geometry contains the second.

## Code structure

### model

Builds an Ifc file using the ifcopenshell library based on a model object.

### service

There are two services available. A postgis service to query a postgis database and a swisstopo service to download terrain models.

### main.py

To execute the main function you need to provide three parameters as environment variables. IFC_VERSION, NAME and POLYGON.

1. Load configuration file
2. Create model
3. Build model
4. Save model