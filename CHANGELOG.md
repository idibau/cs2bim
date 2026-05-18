# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-05-18

### Added

- Support for selective feature type export

## [1.0.0] - 2026-05-13

### Added

- Initial release of the CS2BIM service
- REST API (FastAPI) for submitting IFC model generation requests
- Asynchronous task processing via Celery worker with Redis as message broker
- PostGIS integration for reading cadastral survey data
- STAC service integration for fetching external geodata
- Geometry processors for projection, extrusion, and building generation
- TIN-based terrain model processing for 3D surface generation
- IFC export using IfcOpenShell
- YAML-based configuration for feature type and IFC entity mapping
- Multi-language output support
- Docker-based deployment with dedicated containers for API, worker, and Redis