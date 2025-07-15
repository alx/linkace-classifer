#!/usr/bin/env python3
"""
Server Launcher for LinkAce Classifier API

Main entry point for starting the HTTP API server
"""

import sys
import signal
import argparse

from ..core.config import ConfigManager, ClassifierConfig
from ..http.server import ClassificationAPIServer
from ..core.utils import log_message


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log_message("Received shutdown signal, stopping server...", "INFO")
    sys.exit(0)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="LinkAce Classification API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config.json
  %(prog)s --host 0.0.0.0 --port 8080
  %(prog)s --config config.json --host 0.0.0.0 --port 8080 --debug
        """,
    )

    # Configuration
    parser.add_argument("--config", help="Configuration file path (JSON format)")

    # Server settings
    parser.add_argument(
        "--host", default="localhost", help="Server host address (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Server port number (default: 5000)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    # LinkAce API settings
    parser.add_argument("--api-url", help="LinkAce API base URL")
    parser.add_argument("--api-token", help="LinkAce API token")
    parser.add_argument(
        "--classify-lists",
        type=lambda x: [int(i.strip()) for i in x.split(",")],
        help="Comma-separated list of classification list IDs",
    )

    # Ollama settings
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)",
    )

    # Other settings
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.8,
        help="Confidence threshold for classification (default: 0.8)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-cors", action="store_true", help="Disable CORS support")
    parser.add_argument(
        "--no-url-validation", action="store_true", help="Disable URL validation"
    )

    return parser.parse_args()


def create_config_from_args(args) -> ClassifierConfig:
    """Create configuration from command-line arguments"""
    config_manager = ConfigManager()

    # Start with defaults
    config_dict = {
        "server_host": args.host,
        "server_port": args.port,
        "server_debug": args.debug,
        "enable_cors": not args.no_cors,
        "enable_url_validation": not args.no_url_validation,
        "ollama_url": args.ollama_url,
        "ollama_model": args.ollama_model,
        "confidence_threshold": args.confidence_threshold,
        "verbose": args.verbose,
        "input_list_id": 1,  # Default value, not used for API server
        "dry_run": False,
        "enable_accessibility_check": False,
        "request_timeout": 30.0,
        "max_requests_per_minute": 60,
    }

    # Load from configuration file if provided
    if args.config:
        file_config = config_manager.load_from_file(args.config)
        config_dict.update(file_config)

    # Load from environment variables
    env_config = config_manager.load_from_env()
    config_dict.update(env_config)

    # Override with command-line arguments
    if args.api_url:
        config_dict["linkace_api_url"] = args.api_url
    if args.api_token:
        config_dict["linkace_api_token"] = args.api_token
    if args.classify_lists:
        config_dict["classify_list_ids"] = args.classify_lists

    # Validate required fields for API server
    required_fields = ["linkace_api_url", "linkace_api_token", "classify_list_ids"]

    missing_fields = []
    for field in required_fields:
        if field not in config_dict or config_dict[field] is None:
            missing_fields.append(field)

    if missing_fields:
        print("❌ Missing required configuration for API server:")
        for field in missing_fields:
            print(f"  - {field}")
        print("\nProvide these via:")
        print("  - Command-line arguments (--api-url, --api-token, --classify-lists)")
        print("  - Configuration file (--config config.json)")
        print(
            "  - Environment variables (LINKACE_API_URL, LINKACE_API_TOKEN, CLASSIFY_LIST_IDS)"
        )
        sys.exit(1)

    # Validate URL format
    if not config_dict["linkace_api_url"].startswith(("http://", "https://")):
        print("❌ LinkAce API URL must start with http:// or https://")
        sys.exit(1)

    # Validate lists
    if (
        not isinstance(config_dict["classify_list_ids"], list)
        or len(config_dict["classify_list_ids"]) == 0
    ):
        print("❌ classify_list_ids must be a non-empty list")
        sys.exit(1)

    try:
        return ClassifierConfig(**config_dict)
    except TypeError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)


def test_services(config: ClassifierConfig) -> bool:
    """Test connectivity to external services"""
    from ..api.linkace import LinkAceClient
    from ..api.ollama import OllamaClient

    print("🔍 Testing service connectivity...")

    # Test LinkAce API
    try:
        linkace_client = LinkAceClient(config.linkace_api_url, config.linkace_api_token)
        if linkace_client.test_connection():
            print("✅ LinkAce API connection successful")
        else:
            print("❌ LinkAce API connection failed")
            return False
    except Exception as e:
        print(f"❌ LinkAce API error: {e}")
        return False

    # Test Ollama
    try:
        ollama_client = OllamaClient(config.ollama_url, config.ollama_model)
        if ollama_client.test_connection():
            print("✅ Ollama server connection successful")
        else:
            print("❌ Ollama server connection failed")
            return False
    except Exception as e:
        print(f"❌ Ollama server error: {e}")
        return False

    print("✅ All service connections successful")
    return True


def print_server_info(config: ClassifierConfig):
    """Print server startup information"""
    print("\n" + "=" * 60)
    print("🚀 LinkAce Classification API Server")
    print("=" * 60)
    print(f"Server URL: http://{config.server_host}:{config.server_port}")
    print(f"Debug Mode: {config.server_debug}")
    print(f"CORS Enabled: {config.enable_cors}")
    print(f"URL Validation: {config.enable_url_validation}")
    print(f"Rate Limit: {config.max_requests_per_minute} requests/minute")
    print(f"Confidence Threshold: {config.confidence_threshold}")
    print(f"Classification Lists: {config.classify_list_ids}")
    print("\n📋 Available Endpoints:")
    print(f"  POST   http://{config.server_host}:{config.server_port}/classify")
    print(f"  GET    http://{config.server_host}:{config.server_port}/status")
    print(f"  GET    http://{config.server_host}:{config.server_port}/summary")
    print(f"  GET    http://{config.server_host}:{config.server_port}/health")
    print("\n💡 Example Request:")
    print(
        f"  curl -X POST http://{config.server_host}:{config.server_port}/classify \\"
    )
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"url": "https://github.com/user/repo"}\'')
    print("\n" + "=" * 60)


def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Parse command-line arguments
    args = parse_arguments()

    try:
        # Create configuration
        config = create_config_from_args(args)

        # Print configuration if verbose
        if config.verbose:
            print_server_info(config)

        # Test service connectivity
        if not test_services(config):
            print("\n❌ Service connectivity tests failed")
            print(
                "Please check your configuration and ensure all services are running:"
            )
            print(f"  - LinkAce API: {config.linkace_api_url}")
            print(f"  - Ollama server: {config.ollama_url}")
            sys.exit(1)

        # Create and start server
        log_message("Initializing API server...", "INFO")
        server = ClassificationAPIServer(config)

        if not config.verbose:
            print_server_info(config)

        print(f"\n🎉 Server starting... Press Ctrl+C to stop")
        server.run()

    except KeyboardInterrupt:
        log_message("Server stopped by user", "INFO")
    except Exception as e:
        log_message(f"Server error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
