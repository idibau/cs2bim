# cs2bim

## Getting started



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
|tin.grid_size|float|0.5|0.5|
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

GeoReferencing -> tin2ifc.enum.geo_referencing.py\
TriangulationRepresentationType -> tin2ifc.enum.triangulation_representation_type.py\
ElementEntityType -> tin2ifc.enum.element_entity_type.py\
SpatialStructureEntityType -> tin2ifc.enum.spatial_structure_entity_type.py