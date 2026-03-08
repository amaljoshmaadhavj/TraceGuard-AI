"""Configuration management for TraceGuard AI"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml


class Config:
    """Configuration loader and manager"""

    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load(cls, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config YAML file

        Returns:
            Configuration dictionary
        """
        if cls._config:
            return cls._config

        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"

        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            cls._config = yaml.safe_load(f) or {}

        return cls._config

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'embeddings.model')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        if not cls._config:
            cls.load()

        keys = key.split(".")
        value = cls._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @classmethod
    def set(cls, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key (dot-notation)
            value: Value to set
        """
        if not cls._config:
            cls.load()

        keys = key.split(".")
        config = cls._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get entire configuration"""
        if not cls._config:
            cls.load()
        return cls._config

    @classmethod
    def ensure_paths(cls):
        """Ensure all configured data directories exist"""
        if not cls._config:
            cls.load()

        paths = cls._config.get("paths", {})
        for path_key, path_value in paths.items():
            if path_value and not path_value.startswith("/"):  # Skip absolute paths in config
                Path(path_value).mkdir(parents=True, exist_ok=True)


def get_config(key: str = None, default: Any = None) -> Any:
    """Convenience function to get config value or entire config"""
    config = Config()
    if key is None:
        return config.get_all()
    return config.get(key, default)
