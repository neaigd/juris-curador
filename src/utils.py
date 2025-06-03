# src/utils.py
# -*- coding: utf-8 -*-
"""Módulo utilitário com funções auxiliares:
- Gerenciamento de configuração (cores, diretórios, formatos).
- Configuração de logging básico.
- Funções genéricas de manipulação de arquivos.
"""

import json
import yaml # Requires PyYAML, ensure it's in requirements.txt
import logging
import os
from typing import Dict, Any, Tuple, Optional

# --- Configuration Management ---

DEFAULT_CONFIG = {
    "directories": {
        "download": "juris_downloads",
        "annotated_pdfs": "juris_annotated",
        "zotero_exports": "juris_zotero_exports",
        "logs": "juris_logs"
    },
    "pdf_highlight_colors": {
        "primary": [1, 1, 0],  # Yellow (R, G, B - values from 0 to 1)
        "secondary": [0, 1, 1],  # Cyan
        "llm_identified": [0.8, 0.2, 0.8]  # Purple-ish
    },
    "output_formats": {
        "bibliography_style": "ABNT", # Currently only ABNT is implemented
        "zotero_json_indent": 4
    },
    "llm": {
        "api_key_env_var": "LLM_API_KEY", # Environment variable name for the API key
        "default_model": "gemini-pro" # Placeholder for LLM model selection
    },
    "logging":{
        "level": "INFO", # DEBUG, INFO, WARNING, ERROR, CRITICAL
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    }
}

_config: Dict[str, Any] = {} # In-memory cache for configuration

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Loads configuration from a YAML file. If not found, uses defaults
    and attempts to save a default config.yaml.
    """
    global _config
    if _config: # Return cached config if already loaded
        return _config

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
            _config = DEFAULT_CONFIG.copy() # Start with defaults
            # Deep update defaults with loaded config
            if loaded_config: # Ensure loaded_config is not None
                for key, value in loaded_config.items():
                    if isinstance(value, dict) and isinstance(_config.get(key), dict):
                        _config[key].update(value)
                    else:
                        _config[key] = value
            print(f"INFO: Configuration loaded from {config_path}")
        except Exception as e:
            print(f"WARNING: Could not load config from {config_path}: {e}. Using default configuration.")
            _config = DEFAULT_CONFIG.copy()
    else:
        print(f"INFO: Configuration file {config_path} not found. Using default configuration and creating a template.")
        _config = DEFAULT_CONFIG.copy()
        try:
            # Attempt to save a default config file for the user
            ensure_directory_exists(os.path.dirname(config_path) or '.')
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(DEFAULT_CONFIG, f, allow_unicode=True, sort_keys=False, indent=2)
            print(f"INFO: Default configuration template saved to {config_path}. Please review and customize it.")
        except Exception as e:
            print(f"WARNING: Could not save default configuration template to {config_path}: {e}")

    # Ensure all default directories exist after loading config
    for dir_key, dir_path in _config.get("directories", {}).items():
        ensure_directory_exists(dir_path) # This might print before logger is set if called early

    return _config

def get_config() -> Dict[str, Any]:
    """Returns the currently loaded configuration. Loads defaults if not yet loaded."""
    if not _config:
        return load_config()
    return _config

def get_highlight_colors() -> Dict[str, Tuple[float, float, float]]:
    """
    Returns the PDF highlight colors from config.
    Ensures RGB values are tuples of floats (0-1 range).
    """
    cfg = get_config()
    colors_dict = cfg.get("pdf_highlight_colors", DEFAULT_CONFIG["pdf_highlight_colors"])

    # Validate and convert format if necessary (e.g., from list to tuple)
    valid_colors = {}
    for name, color_val in colors_dict.items():
        if isinstance(color_val, list) and len(color_val) == 3 and all(isinstance(c, (int, float)) for c in color_val):
            # Normalize to 0-1 float if they seem to be in 0-255 range by mistake
            if any(c > 1 for c in color_val):
                valid_colors[name] = tuple(max(0.0, min(1.0, c/255.0)) for c in color_val)
            else:
                valid_colors[name] = tuple(float(c) for c in color_val)
        elif isinstance(color_val, tuple) and len(color_val) == 3 and all(isinstance(c, (int, float)) for c in color_val):
             if any(c > 1 for c in color_val): # Normalize if needed
                valid_colors[name] = tuple(max(0.0, min(1.0, c/255.0)) for c in color_val)
             else:
                valid_colors[name] = tuple(float(c) for c in color_val)
        else:
            print(f"WARNING: Invalid color format for '{name}' in config. Using default yellow.")
            valid_colors[name] = DEFAULT_CONFIG["pdf_highlight_colors"]["primary"]

    return valid_colors


# --- Logging Setup ---

def setup_logging(log_dir: Optional[str] = None,
                  level_str: Optional[str] = None,
                  log_format: Optional[str] = None,
                  date_fmt: Optional[str] = None,
                  log_to_console: bool = True,
                  log_to_file: bool = True,
                  log_filename: str = "juris_curador.log"
                  ) -> logging.Logger:
    """
    Configures basic logging for the application.
    Returns the root logger.
    """
    # Use get_config() to ensure config is loaded before accessing logging settings
    # This avoids issues if setup_logging is called before explicit load_config
    app_config = get_config()
    cfg = app_config.get("logging", DEFAULT_CONFIG["logging"])

    log_level_str = level_str or cfg.get("level", "INFO")
    log_format_str = log_format or cfg.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_datefmt_str = date_fmt or cfg.get("datefmt", "%Y-%m-%d %H:%M:%S")

    numeric_level = getattr(logging, log_level_str.upper(), logging.INFO)

    formatter = logging.Formatter(log_format_str, datefmt=log_datefmt_str)

    logger = logging.getLogger("juris_curador")
    logger.setLevel(numeric_level)

    # Clear existing handlers only if re-configuring the *same* logger instance
    # This check helps if setup_logging might be called multiple times.
    if logger.hasHandlers():
        logger.handlers.clear()

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_to_file:
        # Use configured log directory, falling back to default if not in config
        _log_dir_from_config = app_config.get("directories", {}).get("logs", DEFAULT_CONFIG["directories"]["logs"])
        _log_dir = log_dir or _log_dir_from_config

        ensure_directory_exists(_log_dir) # ensure_directory_exists uses print, safe here
        file_handler = logging.FileHandler(os.path.join(_log_dir, log_filename), encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if log_to_console or log_to_file:
        # Check if logger has handlers before logging, to avoid "No handlers" warning if both are false
        if logger.hasHandlers():
             logger.info(f"Logging initialized for 'juris_curador'. Level: {log_level_str}. Console: {log_to_console}, File: {log_to_file} (in '{_log_dir if log_to_file else 'N/A'}')")
        else:
            print(f"NOTICE: Logging for 'juris_curador' is not configured to output to console or file.")

    return logger

# --- File System Utilities ---

def ensure_directory_exists(dir_path: str) -> None:
    """
    Ensures that a directory exists; if not, creates it.
    Args:
        dir_path (str): The path to the directory.
    """
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            # Using print here as logger might not be configured when this is first called by load_config
            print(f"INFO: Created directory: {dir_path}")
        except OSError as e:
            print(f"ERROR: Could not create directory {dir_path}: {e}")
            raise

# Example usage and initial setup:
if __name__ == '__main__':
    # 1. Load configuration (this will also create default directories if they don't exist)
    # It will also attempt to create a default 'config.yaml' if not found.
    config = load_config()
    # If config.yaml was just created, default logging settings from DEFAULT_CONFIG will be used by setup_logging()
    # If config.yaml existed, its logging settings will be used.

    # 2. Setup logging using loaded/default configuration
    # The logger is named 'juris_curador'
    logger = setup_logging()
    # All subsequent logging calls will use this configuration.

    logger.info("\n--- Configuration Loaded (as seen by logger) ---")
    # Use json.dumps for pretty printing dicts in logs if desired
    logger.info(f"Config content: {json.dumps(config, indent=2)}")


    logger.info("\n--- Logger '%s' Initialized ---", logger.name)
    logger.debug("This is a debug message (will not show if level is INFO by default).")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

    logger.info("\n--- Testing Utilities ---")

    test_dir_key = "download" # Use a key from config.directories
    test_dir_from_config = config.get("directories", {}).get(test_dir_key)

    if test_dir_from_config:
        test_subdir = os.path.join(test_dir_from_config, "test_subdir_utils")
        logger.info(f"Ensuring test subdirectory exists: {test_subdir}")
        ensure_directory_exists(test_subdir) # This uses print for its own "Created directory" message
        if os.path.exists(test_subdir):
            logger.info(f"Test subdirectory {test_subdir} exists or was created.")
            try:
                if not os.listdir(test_subdir): # Only remove if empty
                    os.rmdir(test_subdir)
                    logger.info(f"Cleaned up empty test subdirectory: {test_subdir}")
                else:
                    logger.info(f"Test subdirectory {test_subdir} not empty, not removing.")
            except OSError as e:
                logger.warning(f"Could not remove test_subdir {test_subdir} (might not be empty or permission issue): {e}")
        else:
            logger.error(f"Test subdirectory {test_subdir} was NOT created.")
    else:
        logger.error(f"Directory key '{test_dir_key}' not found in config.")


    highlight_colors = get_highlight_colors()
    logger.info(f"Primary highlight color from config: {highlight_colors.get('primary')}")

    download_path = config.get("directories", {}).get("download")
    logger.info(f"Download directory from config: {download_path}")

    logger.info("\nUtils module example finished. Check 'config.yaml' and logs in '%s'.", config.get("directories",{}).get("logs","juris_logs"))
