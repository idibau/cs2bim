import os
import tempfile
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from config.configuration import Configuration
from config.geo_referencing import GeoReferencing


class TestConfiguration(unittest.TestCase):

    def test_load_valid_config(self):
        valid_config = """
            logging_level: INFO
            redis:
              host: "redis"
              port: 6379
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            db:
              dbname: "cs2bim"
              user: "postgres"
              host: "localhost"
              port: 5432
              password: "test_password"
            stac:
              dtm_items_url: "https://example.com/dtm"
              building_items_url: "https://example.com/buildings"
            tin:
              grid_size: 0.5
              max_height_error: 0.05
            ifc:
              author: "Test Author"
              version: "1.0"
              application_name: "test_app"
              project_name: "test_project"
              geo_referencing: LO_GEO_REF_50
              feature_types:
                projections:
                  - name: "test_projection"
                    sql_path: "/test/sql/test.sql"
                    entity_mapping:
                      entity_type: IFC_GEOGRAPHIC_ELEMENT
                    entity_type_mapping:
                    spatial_structure_mapping:
                      entity_type: IFC_SITE
                buildings:
                  - name: "test_building"
                    sql_path: "/test/sql/test.sql"
                    egid_xpath: ".//test"
                    entity_mapping:
                      entity_type: IFC_BUILDING
                      building_parts: []
                    entity_type_mapping:
                    spatial_structure_mapping:
                      entity_type: IFC_SITE
        """

        with patch("pathlib.Path.read_text", return_value=valid_config):
            config = Configuration.load("test_config.yml")
            self.assertEqual(config.logging_level, "INFO")
            self.assertEqual(config.redis.host, "redis")
            self.assertEqual(config.redis.port, 6379)
            self.assertEqual(config.db.dbname, "cs2bim")
            self.assertEqual(config.ifc.author, "Test Author")
            self.assertEqual(config.ifc.geo_referencing, GeoReferencing.LO_GEO_REF_50)

            self.assertEqual(len(config.ifc.feature_types.projections), 1)
            self.assertEqual(config.ifc.feature_types.projections[0].name, "test_projection")

            self.assertEqual(len(config.ifc.feature_types.buildings), 1)
            self.assertEqual(config.ifc.feature_types.buildings[0].name, "test_building")

    def test_load_with_environment_variables(self):
        config_with_env_vars = """
            logging_level: INFO
            redis:
              host: "${REDIS_HOST}"
              port: ${REDIS_PORT}
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            db:
              dbname: "cs2bim"
              user: "postgres"
              host: "localhost"
              port: 5432
              password: "${DB_PASSWORD}"
            stac:
              dtm_items_url: "https://example.com/dtm"
              building_items_url: "https://example.com/buildings"
            tin:
              grid_size: 0.5
              max_height_error: 0.05
            ifc:
              author: "${AUTHOR_NAME}"
              version: "1.0"
              application_name: "test_app"
              project_name: "test_project"
              geo_referencing: LO_GEO_REF_50
              feature_types:
                projections:
                  - name: "test_projection"
                    sql_path: "/test/sql/test.sql"
                    entity_mapping:
                      entity_type: IFC_GEOGRAPHIC_ELEMENT
                      attributes: []
                      properties: []
                    entity_type_mapping:
                      attributes: []
                      properties: []
                    spatial_structure_mapping:
                      entity_type: IFC_SITE
                      attributes: []
                      properties: []
                buildings: []
        """

        with patch.dict(os.environ, {
            "REDIS_HOST": "test-redis",
            "REDIS_PORT": "6380",
            "DB_PASSWORD": "secure_password",
            "AUTHOR_NAME": "Environment Author"
        }):
            with patch("pathlib.Path.read_text", return_value=config_with_env_vars):
                config = Configuration.load("test_config.yml")
                self.assertEqual(config.redis.host, "test-redis")
                self.assertEqual(config.redis.port, 6380)
                self.assertEqual(config.db.password, "secure_password")
                self.assertEqual(config.ifc.author, "Environment Author")

    def test_validation_error_missing_required_fields(self):
        incomplete_config = """
            logging_level: INFO
            redis:
              host: "redis"
              port: 6379
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            stac:
              dtm_items_url: "https://example.com/dtm"
              building_items_url: "https://example.com/buildings"
            tin:
              grid_size: 0.5
              max_height_error: 0.05
        """

        with patch("pathlib.Path.read_text", return_value=incomplete_config):
            with self.assertRaises(ValidationError):
                Configuration.load("test_config.yml")

    def test_conditional_validator_projections_without_dtm_url(self):
        invalid_config = """
            logging_level: INFO
            redis:
              host: "redis"
              port: 6379
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            db:
              dbname: "cs2bim"
              user: "postgres"
              host: "localhost"
              port: 5432
              password: "test_password"
            stac:
              # dtm_items_url fehlt!
              building_items_url: "https://example.com/buildings"
            tin:
              grid_size: 0.5
              max_height_error: 0.05
            ifc:
              author: "Test Author"
              version: "1.0"
              application_name: "test_app"
              project_name: "test_project"
              geo_referencing: LO_GEO_REF_50
              feature_types:
                projections:
                  - name: "test_projection"
                    sql_path: "/test/sql/test.sql"
                    entity_mapping:
                      entity_type: IFC_GEOGRAPHIC_ELEMENT
                      attributes: []
                      properties: []
                    entity_type_mapping:
                      attributes: []
                      properties: []
                    spatial_structure_mapping:
                      entity_type: IFC_SITE
                      attributes: []
                      properties: []
                buildings: []
        """

        with patch("pathlib.Path.read_text", return_value=invalid_config):
            with self.assertRaises(ValueError) as context:
                Configuration.load("test_config.yml")
            self.assertIn("stac.dtm_items_url is required", str(context.exception))

    def test_conditional_validator_buildings_without_building_url(self):
        invalid_config = """
            logging_level: INFO
            redis:
              host: "redis"
              port: 6379
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            db:
              dbname: "cs2bim"
              user: "postgres"
              host: "localhost"
              port: 5432
              password: "test_password"
            stac:
              dtm_items_url: "https://example.com/dtm"
              # building_items_url fehlt!
            tin:
              grid_size: 0.5
              max_height_error: 0.05
            ifc:
              author: "Test Author"
              version: "1.0"
              application_name: "test_app"
              project_name: "test_project"
              geo_referencing: LO_GEO_REF_50
              feature_types:
                projections: []
                buildings:
                  - name: "test_building"
                    sql_path: "/test/sql/test.sql"
                    egid_xpath: ".//test"
                    entity_mapping:
                      entity_type: IFC_BUILDING
                      attributes: []
                      properties: []
                      building_parts: []
                    entity_type_mapping:
                      attributes: []
                      properties: []
                    spatial_structure_mapping:
                      entity_type: IFC_SITE
                      attributes: []
                      properties: []
        """

        with patch("pathlib.Path.read_text", return_value=invalid_config):
            with self.assertRaises(ValueError) as context:
                Configuration.load("test_config.yml")
            self.assertIn("stac.building_items_url is required", str(context.exception))

    def test_load_with_actual_file(self):
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.yml', delete=False) as temp_file:
            temp_file.write("""
            logging_level: INFO
            redis:
              host: "redis"
              port: 6379
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            db:
              dbname: "cs2bim"
              user: "postgres"
              host: "localhost"
              port: 5432
              password: "test_password"
            stac:
              dtm_items_url: "https://example.com/dtm"
              building_items_url: "https://example.com/buildings"
            tin:
              grid_size: 0.5
              max_height_error: 0.05
            ifc:
              author: "Test Author"
              version: "1.0"
              application_name: "test_app"
              project_name: "test_project"
              geo_referencing: LO_GEO_REF_50
              feature_types:
                projections: []
                buildings: []
            """)

        try:
            config = Configuration.load(temp_file.name)
            self.assertEqual(config.logging_level, "INFO")
            self.assertEqual(config.redis.host, "redis")
            self.assertEqual(config.db.password, "test_password")
        finally:
            os.unlink(temp_file.name)

    def test_model_schema_validation_max_height_error(self):
        invalid_config = """
            logging_level: INFO
            redis:
              host: "redis"
              port: 6379
              db:
                celery_broker: 0
                celery_backend: 1
                file_cache: 2
            db:
              dbname: "cs2bim"
              user: "postgres"s
              host: "localhost"
              port: 5432
              password: "test_password"
            stac:
              dtm_items_url: "https://example.com/dtm"
              building_items_url: "https://example.com/buildings"
            tin:
              grid_size: 0.5
              max_height_error: 0.1  # Ungültiger Wert, sollte <= 0.05 sein
            ifc:
              author: "Test Author"
              version: "1.0"
              application_name: "test_app"
              project_name: "test_project"
              geo_referencing: LO_GEO_REF_50
              feature_types:
                projections: []
                buildings: []
        """

        with patch("pathlib.Path.read_text", return_value=invalid_config):
            with self.assertRaises(ValidationError):
                Configuration.load("test_config.yml")
