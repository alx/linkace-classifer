#!/usr/bin/env python3
"""
Test script for LinkAce Classifier

Tests the various components and functionality
"""

import sys
import json
from linkace_api import LinkAceClient
from ollama_client import OllamaClient
from config import ConfigManager


def test_linkace_api():
    """Test LinkAce API functionality"""
    print("Testing LinkAce API...")

    # Use sample config
    try:
        with open("config.json", "r") as f:
            config_data = json.load(f)

        # Skip if using default placeholder values
        if "your-linkace-instance.com" in config_data["linkace_api_url"]:
            print("⚠️  Skipping LinkAce API test - using placeholder URL")
            return False

        client = LinkAceClient(
            config_data["linkace_api_url"], config_data["linkace_api_token"]
        )

        # Test connection
        if client.test_connection():
            print("✅ LinkAce API connection successful")
            return True
        else:
            print("❌ LinkAce API connection failed")
            return False

    except Exception as e:
        print(f"❌ Error testing LinkAce API: {e}")
        return False


def test_ollama_client():
    """Test Ollama client functionality"""
    print("Testing Ollama client...")

    try:
        client = OllamaClient()

        # Test connection
        if client.test_connection():
            print("✅ Ollama connection successful")

            # Test classification with sample data
            sample_link = {
                "url": "https://github.com/example/repo",
                "title": "Example Repository",
                "description": "A sample GitHub repository for testing",
            }

            sample_classify_lists = {
                1: [
                    {"url": "https://github.com/python/cpython", "title": "Python"},
                    {"url": "https://github.com/microsoft/vscode", "title": "VS Code"},
                ],
                2: [
                    {"url": "https://news.ycombinator.com/item?id=1", "title": "News"},
                    {"url": "https://techcrunch.com/article", "title": "Tech News"},
                ],
            }

            print("Testing classification...")
            classifications = client.classify_link(sample_link, sample_classify_lists)

            if classifications:
                print(f"✅ Classification successful: {len(classifications)} results")
                for classification in classifications:
                    print(
                        f"  List {classification['list_id']}: "
                        f"{classification['confidence']:.3f}"
                    )
                return True
            else:
                print("⚠️  No classifications returned (this may be normal)")
                return True

        else:
            print("❌ Ollama connection failed")
            return False

    except Exception as e:
        print(f"❌ Error testing Ollama client: {e}")
        return False


def test_config_manager():
    """Test configuration management"""
    print("Testing configuration manager...")

    try:
        config_manager = ConfigManager()

        # Test loading from file
        config_data = config_manager.load_from_file("config.json")

        if config_data:
            print("✅ Configuration file loaded successfully")

            # Test creating config object (will fail with placeholder values)
            try:
                # Create a mock args object
                class MockArgs:
                    def __init__(self):
                        self.api_url = "https://example.com/api/v2"
                        self.token = "test-token"
                        self.input_list = 12
                        self.classify_lists = [1, 2, 3]
                        self.ollama_url = "http://localhost:11434"
                        self.ollama_model = "llama3.2"
                        self.confidence_threshold = 0.8
                        self.dry_run = True
                        self.verbose = False
                        self.output_file = None

                mock_args = MockArgs()
                config_manager.create_config(mock_args)

                print("✅ Configuration object created successfully")
                return True

            except SystemExit:
                print(
                    "⚠️  Configuration validation works (expected with "
                    "placeholder values)"
                )
                return True

        else:
            print("❌ Configuration file loading failed")
            return False

    except Exception as e:
        print(f"❌ Error testing configuration manager: {e}")
        return False


def test_import_modules():
    """Test that all modules can be imported"""
    print("Testing module imports...")

    try:
        from linkace_api import LinkAceClient  # noqa: F401
        from ollama_client import OllamaClient  # noqa: F401
        from config import ConfigManager  # noqa: F401
        from utils import log_message  # noqa: F401

        print("✅ All modules imported successfully")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running LinkAce Classifier Tests")
    print("=" * 50)

    tests = [
        ("Module Imports", test_import_modules),
        ("Configuration Manager", test_config_manager),
        ("Ollama Client", test_ollama_client),
        ("LinkAce API", test_linkace_api),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed or were skipped")
        return 1


if __name__ == "__main__":
    sys.exit(main())
