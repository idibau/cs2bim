# Mapping Principles

## Basics 
To convert a typical geodataset to IFC, both semantic mappings and geometric conversions must be defined, see figure below.  

![Mapping Principles Overview ([@schildknecht2025IntegrationLandAdministration])](../uploads/mapping-principle-overview.jpg){#fig-mapping-principles-overview}

In [@schildknecht2025IntegrationLandAdministration], the various semantic and geometric mappings are described and discussed in detail.  

The semantic mapping implemented with cs2bim comprises five mapping levels (see also figure below):

- Entity mapping
- Property mapping
- EntityType mapping
- Spatial structure mapping
- Group mapping

![Mapping Principles Entities](../uploads/mapping-principle-entity.jpg){#fig-mapping-principles-entity fig-align="left" width=75%}

<br>
<br>
The geometric conversion is shown schematically in the figure below. Based on the defined conversion type, an IFC geometry is generated from the geometry of the geodata instance and assigned to the generated IFC instance. This process always involves at least one geometry type conversion from a WKT definition to an IFC definition. Depending on the source dataset, additional processing of the geometry may also occur — e.g., from 2D to 3D.  

![Mapping Principles Geometry](../uploads/mapping-principle-geometry.jpg){#fig-mapping-principles-geometry fig-align="left" width=75%}



## Principles
