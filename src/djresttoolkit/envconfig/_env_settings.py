import warnings
from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings[T: "EnvBaseSettings"](BaseSettings):
    """ "
    EnvBaseSettings is a base settings class for managing application configuration
    using both YAML files and environment variables.
    This class is designed to load configuration values from a YAML file first,
    and then override those values with environment variables if present. It supports
    nested configuration using a double underscore (`__`) as the delimiter in
    environment variable names, allowing for hierarchical settings.

    Class Attributes:
        env_file (str): The default filename for the environment variables file (default: ".env").
        yaml_file (str): The default filename for the YAML configuration file (default: ".environ.yaml").
        model_config (SettingsConfigDict): Configuration for environment variable parsing, including file encoding and nested delimiter.

    Methods:
        load(cls, *, env_file: str | None = None, ymal_file: str | None = None, warning: bool = True) -> "EnvBaseSettings":
            Loads configuration from a YAML file (if it exists), then overrides with environment variables.
            - env_file: Optional custom path to the .env file.
            - ymal_file: Optional custom path to the YAML file.
            - warning: If True, emits a warning if the YAML file is not found.
            Returns an instance of EnvBaseSettings with the loaded configuration.

    Usage:
        - Define your settings as subclasses of EnvBaseSettings.
        - Call `YourSettingsClass.load()` to load configuration from files and environment variables.
        - Supports nested configuration via double underscore in environment variable names (e.g., `DATABASE__HOST`).

    Raises:
        - UserWarning: If the YAML file is not found and `warning` is True.

    Example:
    ```python
        from djresttoolkit.envconfig import EnvBaseSettings
        
        class EnvSettings(EnvBaseSettings):
            debug: bool = False
            database_url: str
            
        settings = EnvSettings.load(warning=False)
    ```

    """

    env_file: ClassVar[str] = ".env"
    yaml_file: ClassVar[str] = ".environ.yaml"

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    @classmethod
    def load(
        cls: type[T],
        *,
        env_file: str | None = None,
        ymal_file: str | None = None,
        warning: bool = True,
    ) -> T:
        """Load from YAML first, then override with .env."""
        if env_file:
            cls.env_file = env_file
        if ymal_file:
            cls.yaml_file = ymal_file

        config_file = Path(cls.yaml_file)
        yaml_data: dict[str, Any] = {}
        if config_file.exists():
            with config_file.open("r") as f:
                yaml_data = yaml.safe_load(f) or {}
        elif warning:
            msg: str = f"Config file {config_file} not found, using only env vars."
            warnings.warn(msg, UserWarning, stacklevel=1)

        return cls(**yaml_data)
