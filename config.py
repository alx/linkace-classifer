#!/usr/bin/env python3
"""
Configuration Management for LinkAce Classifier

Handles configuration loading from environment variables, config files,
and command-line arguments
"""

import os
import json
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ClassifierConfig:
    """Configuration for the LinkAce classifier"""

    # LinkAce API settings
    linkace_api_url: str
    linkace_api_token: str

    # List configuration
    input_list_id: int
    classify_list_ids: List[int]

    # Ollama settings
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Classification settings
    confidence_threshold: float = 0.8

    # Operation settings
    dry_run: bool = False
    verbose: bool = False

    # Rate limiting
    api_rate_limit: float = 0.1  # seconds between API calls

    # Output settings
    log_level: str = "INFO"
    output_file: Optional[str] = None
    
    # HTTP Server settings
    server_host: str = "localhost"
    server_port: int = 5000
    server_debug: bool = False
    enable_cors: bool = True
    
    # API settings
    enable_url_validation: bool = True
    enable_accessibility_check: bool = False
    request_timeout: float = 30.0
    max_requests_per_minute: int = 60


class ConfigManager:
    """Manages configuration loading from various sources"""

    def __init__(self):
        self.config = None

    def load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}

        # LinkAce API settings
        if os.getenv("LINKACE_API_URL"):
            config["linkace_api_url"] = os.getenv("LINKACE_API_URL")
        if os.getenv("LINKACE_API_TOKEN"):
            config["linkace_api_token"] = os.getenv("LINKACE_API_TOKEN")

        # List configuration
        if os.getenv("INPUT_LIST_ID"):
            config["input_list_id"] = int(os.getenv("INPUT_LIST_ID"))
        if os.getenv("CLASSIFY_LIST_IDS"):
            config["classify_list_ids"] = [
                int(x.strip()) for x in os.getenv("CLASSIFY_LIST_IDS").split(",")
            ]

        # Ollama settings
        if os.getenv("OLLAMA_URL"):
            config["ollama_url"] = os.getenv("OLLAMA_URL")
        if os.getenv("OLLAMA_MODEL"):
            config["ollama_model"] = os.getenv("OLLAMA_MODEL")

        # Classification settings
        if os.getenv("CONFIDENCE_THRESHOLD"):
            config["confidence_threshold"] = float(os.getenv("CONFIDENCE_THRESHOLD"))

        # Operation settings
        if os.getenv("DRY_RUN"):
            config["dry_run"] = os.getenv("DRY_RUN").lower() in ("true", "1", "yes")
        if os.getenv("VERBOSE"):
            config["verbose"] = os.getenv("VERBOSE").lower() in ("true", "1", "yes")
            
        # HTTP Server settings
        if os.getenv("SERVER_HOST"):
            config["server_host"] = os.getenv("SERVER_HOST")
        if os.getenv("SERVER_PORT"):
            config["server_port"] = int(os.getenv("SERVER_PORT"))
        if os.getenv("SERVER_DEBUG"):
            config["server_debug"] = os.getenv("SERVER_DEBUG").lower() in ("true", "1", "yes")
        if os.getenv("ENABLE_CORS"):
            config["enable_cors"] = os.getenv("ENABLE_CORS").lower() in ("true", "1", "yes")

        return config

    def load_from_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            print(f"✅ Loaded configuration from {config_file}")
            return config
        except FileNotFoundError:
            print(f"⚠️  Configuration file {config_file} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing configuration file {config_file}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading configuration file {config_file}: {e}")
            return {}

    def load_from_args(self, args) -> Dict[str, Any]:
        """Load configuration from command-line arguments"""
        config = {}

        # Required arguments
        if hasattr(args, "api_url") and args.api_url:
            config["linkace_api_url"] = args.api_url
        if hasattr(args, "token") and args.token:
            config["linkace_api_token"] = args.token
        if hasattr(args, "input_list") and args.input_list:
            config["input_list_id"] = args.input_list
        if hasattr(args, "classify_lists") and args.classify_lists:
            config["classify_list_ids"] = args.classify_lists

        # Optional arguments
        if hasattr(args, "ollama_url") and args.ollama_url:
            config["ollama_url"] = args.ollama_url
        if hasattr(args, "ollama_model") and args.ollama_model:
            config["ollama_model"] = args.ollama_model
        if hasattr(args, "confidence_threshold") and args.confidence_threshold:
            config["confidence_threshold"] = args.confidence_threshold
        if hasattr(args, "dry_run") and args.dry_run:
            config["dry_run"] = args.dry_run
        if hasattr(args, "verbose") and args.verbose:
            config["verbose"] = args.verbose
        if hasattr(args, "output_file") and args.output_file:
            config["output_file"] = args.output_file

        return config

    def create_config(self, args=None, config_file: str = None) -> ClassifierConfig:
        """
        Create a complete configuration by merging sources

        Priority order (highest to lowest):
        1. Command-line arguments
        2. Configuration file
        3. Environment variables
        4. Default values

        Args:
            args: Parsed command-line arguments
            config_file: Path to configuration file

        Returns:
            Complete configuration object
        """
        # Start with default values
        config_dict = {
            "ollama_url": "http://localhost:11434",
            "ollama_model": "llama3.2",
            "confidence_threshold": 0.8,
            "dry_run": False,
            "verbose": False,
            "api_rate_limit": 0.1,
            "log_level": "INFO",
        }

        # Load from environment variables
        env_config = self.load_from_env()
        config_dict.update(env_config)

        # Load from configuration file
        if config_file:
            file_config = self.load_from_file(config_file)
            config_dict.update(file_config)

        # Load from command-line arguments
        if args:
            args_config = self.load_from_args(args)
            config_dict.update(args_config)

        # Validate required settings
        required_fields = [
            "linkace_api_url",
            "linkace_api_token",
            "input_list_id",
            "classify_list_ids",
        ]

        missing_fields = []
        for field in required_fields:
            if field not in config_dict or config_dict[field] is None:
                missing_fields.append(field)

        if missing_fields:
            print("❌ Missing required configuration fields:")
            for field in missing_fields:
                print(f"  - {field}")
            print(
                "\nProvide these via command-line arguments, environment "
                "variables, or config file."
            )
            sys.exit(1)

        # Validate URL format
        if not config_dict["linkace_api_url"].startswith(("http://", "https://")):
            print("❌ LinkAce API URL must start with http:// or https://")
            sys.exit(1)

        # Validate confidence threshold
        if not 0.0 <= config_dict["confidence_threshold"] <= 1.0:
            print("❌ Confidence threshold must be between 0.0 and 1.0")
            sys.exit(1)

        # Validate list IDs
        if (
            not isinstance(config_dict["classify_list_ids"], list)
            or len(config_dict["classify_list_ids"]) == 0
        ):
            print("❌ classify_list_ids must be a non-empty list")
            sys.exit(1)

        # Create configuration object
        try:
            self.config = ClassifierConfig(**config_dict)
            return self.config
        except TypeError as e:
            print(f"❌ Configuration error: {e}")
            sys.exit(1)

    def save_config(self, config: ClassifierConfig, config_file: str):
        """Save configuration to file"""
        config_dict = {
            "linkace_api_url": config.linkace_api_url,
            "linkace_api_token": config.linkace_api_token,
            "input_list_id": config.input_list_id,
            "classify_list_ids": config.classify_list_ids,
            "ollama_url": config.ollama_url,
            "ollama_model": config.ollama_model,
            "confidence_threshold": config.confidence_threshold,
            "dry_run": config.dry_run,
            "verbose": config.verbose,
            "api_rate_limit": config.api_rate_limit,
            "log_level": config.log_level,
            "output_file": config.output_file,
        }

        try:
            with open(config_file, "w") as f:
                json.dump(config_dict, f, indent=2)
            print(f"✅ Configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving configuration to {config_file}: {e}")

    def print_config(self, config: ClassifierConfig):
        """Print current configuration"""
        print("📋 Current Configuration:")
        print(f"  LinkAce API URL: {config.linkace_api_url}")
        print(f"  API Token: {config.linkace_api_token[:20]}...")
        print(f"  Input List ID: {config.input_list_id}")
        print(f"  Classify List IDs: {config.classify_list_ids}")
        print(f"  Ollama URL: {config.ollama_url}")
        print(f"  Ollama Model: {config.ollama_model}")
        print(f"  Confidence Threshold: {config.confidence_threshold}")
        print(f"  Dry Run: {config.dry_run}")
        print(f"  Verbose: {config.verbose}")
        print()


def create_sample_config_file():
    """Create a sample configuration file"""
    sample_config = {
        "linkace_api_url": "https://your-linkace-instance.com/api/v2",
        "linkace_api_token": "your-api-token-here",
        "input_list_id": 12,
        "classify_list_ids": [1, 2, 3, 4, 5],
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3.2",
        "confidence_threshold": 0.8,
        "dry_run": False,
        "verbose": False,
        "server_host": "localhost",
        "server_port": 5000,
        "server_debug": False,
        "enable_cors": True,
        "enable_url_validation": True,
        "enable_accessibility_check": False,
        "request_timeout": 30.0,
        "max_requests_per_minute": 60
    }

    with open("config.json", "w") as f:
        json.dump(sample_config, f, indent=2)

    print("✅ Sample configuration file created as config.json")
    print("Edit this file with your actual settings before running the classifier.")


if __name__ == "__main__":
    # Create sample config file when run directly
    create_sample_config_file()
