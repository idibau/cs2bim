import os
import pytest
from pathlib import Path
from unittest.mock import patch

from config.configuration import Configuration
from config.geo_referencing import GeoReferencing


class TestConfiguration:

    @pytest.fixture
    def config_paths(self):
        base_path = Path(__file__).parent / "config"
        return {
            "base_config": base_path / "base_config.yml",
            "env_var_config": base_path / "env_config.yml",
            "invalid_projection_config": base_path / "invalid_projection_config.yml",
            "invalid_building_config": base_path / "invalid_building_config.yml"
        }

    def test_load_valid_config(self, config_paths):
        config = Configuration.load(config_paths["base_config"].as_posix())

        assert config.logging_level == "INFO"
        assert config.redis.host == "redis"
        assert config.redis.port == 6379
        assert config.redis.global_keyprefix == "prefix"
        assert config.db.dbname == "cs2bim"
        assert config.ifc.author == "Test Author"
        assert config.ifc.geo_referencing == GeoReferencing.LO_GEO_REF_50

        assert config.i18n.de == "de.yml"
        assert config.i18n.fr == "fr.yml"
        assert config.i18n.it == "it.yml"

    def test_environment_variable_substitution(self, config_paths):
        with patch.dict(os.environ, {
            "REDIS_HOST": "test-redis",
            "REDIS_PORT": "6380",
            "DB_USER": "test-user",
            "DB_PASSWORD": "secure_password"
        }):
            config = Configuration.load(config_paths["env_var_config"].as_posix())

            assert config.redis.host == "test-redis"
            assert config.redis.port == 6380
            assert config.db.user == "test-user"
            assert config.db.password == "secure_password"

    def test_conditional_validation_projections(self, config_paths):
        with pytest.raises(ValueError) as exc_info:
            Configuration.load(config_paths["invalid_projection_config"].as_posix())
        assert "stac.building_items_url is required" in str(exc_info.value)

    def test_conditional_validation_buildings(self, config_paths):
        with pytest.raises(ValueError) as exc_info:
            Configuration.load(config_paths["invalid_building_config"].as_posix())
        assert "stac.dtm_items_url is required" in str(exc_info.value)
