# Architecture

## System architecture

### Context

The service cs2bim is designed with the following conceptual components:

![CS2BIM System Architecture](../uploads/system-architecture-context.jpg){#fig-system-architecture-context fig-align="left" width=65%}

| Component   | Description                                                                                                                                              |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| cs2bim      | Main component to transform feature types into IFC instances.<br>Including transformation algorithms, IFC serialisation, service task management etc.    |
| PostGIS/WKT | Database holding the GIS feature types. In current state, this is a PostGIS database.<br>The component cs2bim has a postgres connection to the database. |
| DTM         | Data store with Digital Terrain Model data. DTM data is expected in format XYZ. The cs2bim component gets the DTM data over a STAC API request.          |
| CityGML     | Data store with CityGML data. CityGML data is expected in version 2 of CityGML. The cs2bim component gets the CityGML data over a STAC API request.      |
| REST API    | REST API to interact with cs2bim: Start processing, get status of processing, get generated IFC file.                                                    |
| ili2pg      | External component to transform INTERLIS data into PostGIS. This must be done as a standalone pre process.                                               |

  
<br>
<br>
The following architectural enhancements are already being discussed and ***proposed as potential next steps*** for the
further development and improvement of the service:

![CS2BIM System Architecture, look ahead](../uploads/system-architecture-context-future.jpg){#fig-system-architecture-context-future fig-align="left" width=65%}

- Geopackage as additional data source format for GIS feature types.
    - Geopackage files could be stored locally (on the server) or could be accessed via STAC API
- DMT files stored locally (on the server)
- CityGML files stored locally (on the server)

These improvements would simplify the “local” execution of the service as a “standalone” application, as originally
intended.

### Internal

![CS2BIM System Architecture](../uploads/system-architecture-2.jpg){#fig-system-architecture-2}

#### Services

The system architecture is set up using three Docker services.

The api and worker services are built from a custom Docker image based on `python:3.10`, which contains the application
code base and all required dependencies. Both services share the same image but use different entry points. The redis
service is created using the standard `redis:7` image.

##### api

The entry point for this service is the `api.app` module. It is responsible for routing user requests. There are three
endpoints that let the user interact with the application:

- `POST /generate-model` – triggers the generation of an IFC model. Returns a `task_id` that can be used to track
  progress and retrieve the result.
- `GET /generation-state/{task_id}` – returns the current state of a generation task.
- `GET /generated-file/{task_id}` – returns the generated IFC file once the task is completed.

The service uses FastAPI as the web framework and Uvicorn as the ASGI server to host it.

##### worker

The entry point for the worker service is the `worker.app` module. The service runs a Celery instance that manages and
executes IFC model generation tasks. It connects to the required data sources (PostGIS database and SwissTopo STAC API)
that provide the data needed for model generation.

##### redis

The redis service serves two purposes: as the message broker for the worker service (managing task queues between api
and worker) and as the cache management layer, tracking which files are cached and whether cached files need to be
refreshed.

### Docker Volumes

To store data produced during run-time, the docker-compose file defines four Docker volumes:

- **redis_data** – persists all data stored in Redis. Prevents data loss on service rebuilds.
- **ifc** – stores generated IFC files.
- **logs** – stores log files for the api and worker services.
- **cache** – stores cached data fetched from external data sources.

### Volume Mappings

All configurable files are mapped from the host machine into the containers. This includes translation files (i18n), SQL
query files, and the application configuration (`config.yml`). This way they can be easily edited without rebuilding the
containers.