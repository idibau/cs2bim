# cs2bim

## Getting started

Build docker image
```console
docker build -t cs2bim-run -f Dockerfile . --rm
```
Run docker image
```console
docker run -e IFC_VERSION=[cs2bim.enum.ifc_version.IfcVersion] -e NAME=[str] -e BOUNDING_BOX=[str] -v .:/workspace/output --name cs2bim-run --rm cs2bim-run
```
The bounding box is provided as four numbers (epsg code (wgs84 or lv95) is configurable):\
bbox = min Longitude , min Latitude , max Longitude , max Latitude 

Examples:
- docker run -e IFC_VERSION="IFC4" -e NAME="Test" -e BOUNDING_BOX="8.619857,47.707097,8.621066,47.707740" -v .:/workspace/output --name cs2bim-run --rm cs2bim-run
- docker run -e IFC_VERSION="IFC4" -e NAME="Test" -e BOUNDING_BOX="8.627678,47.709467,8.630310,47.710234" -v .:/workspace/output --name cs2bim-run --rm cs2bim-run
- docker run -e IFC_VERSION="IFC4" -e NAME="Test" -e BOUNDING_BOX="8.626216,47.698555,8.626548,47.698647" -v .:/workspace/output --name cs2bim-run --rm cs2bim-run

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
|db.dbname|str|?|"cs2bim"|
|db.user|str|?|"postgres"|
|db.host|str|?|"host.docker.internal"|
|db.password|str|?|"xxx"|
|---|---|---|---|
|control.epsg_code|EPSGCode|LV95; WGS84|LV95|
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
|ifc.feature_classes.$FeatureClassKey.entity_type|ElementEntityType|IFC_GEOGRAPHIC_ELEMENT|IFC_GEOGRAPHIC_ELEMENT|
|ifc.feature_classes.$FeatureClassKey.spatial_structure.entity_type|SpatialStructureEntityType|IFC_SITE|IFC_SITE|
|ifc.feature_classes.$FeatureClassKey.spatial_structure.name|str|?|"Site"|
|ifc.feature_classes.$FeatureClassKey.groups|list[str]|?.?.?...|group_1.group_1_1.group_1_1_1|
|ifc.feature_classes.$FeatureClassKey.color_definition.r|float|0.0 - 1-0|0.1|
|ifc.feature_classes.$FeatureClassKey.color_definition.g|float|0.0 - 1-0|0.5|
|ifc.feature_classes.$FeatureClassKey.color_definition.b|float|0.0 - 1-0|0.5|
|ifc.feature_classes.$FeatureClassKey.color_definition.a|float|0.0 - 1-0|0.3|

### Types

EPSGCode -> cs2bim.enum.epsg_code.py
GeoReferencing -> tin2ifc.enum.geo_referencing.py\
TriangulationRepresentationType -> tin2ifc.enum.triangulation_representation_type.py\
ElementEntityType -> tin2ifc.enum.element_entity_type.py\
SpatialStructureEntityType -> tin2ifc.enum.spatial_structure_entity_type.py

## Code structure

### model

Builds an Ifc file using the ifcopenshell library based on a model object.

### service

There are two services available. A postgis service to query a postgis database and a swisstopo service to download terrain models.

### Postgis-Queries

- fetch_parcels(wkt)

```sql
WITH perimeter AS 
    (SELECT ST_GeomFromText('{wkt}', 2056) AS geom)                    
SELECT ST_AsText(ST_CurveToLine(geometrie)), nbident, nummer, egris_egrid 
FROM cs2bim.liegenschaft l
LEFT JOIN cs2bim.grundstueck g ON (l.liegenschaft_von = g.t_id)
JOIN perimeter ON ST_Intersects(l.geometrie, perimeter.geom)
```

- fetch_land_covers(wkt)

```sql
WITH perimeter AS 
    (SELECT ST_GeomFromText('{wkt}', 2056) AS geom)                    
SELECT ST_AsText(ST_CurveToLine(geometrie))
FROM cs2bim.boflaeche bb 
JOIN perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
WHERE bb.art = 'Gebaeude'
```

ST_GeomFromText -> Constructs a PostGIS ST_Geometry object \
ST_AsText -> Returns the OGC WKT representation of the geometry\
ST_CurveToLine ->  Converts a given geometry to a linear geometry\
ST_Intersects -> Returns true if two geometries intersect. Geometries intersect if they have any point in common.

### main.py

To execute the main function you need to provide three parameters as environment variables. IFC_VERSION, NAME and POLYGON.

1. Load configuration file
2. Create model
3. Build model
4. Save model