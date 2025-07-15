#!/usr/bin/env python3
"""
CLI Entry Point for LinkAce Classifier HTTP Server

Main command-line interface for running the HTTP API server
"""

import sys
import os

# Add the package to Python path if running as script
if __name__ == "__main__":
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up to src directory
    src_dir = os.path.dirname(os.path.dirname(script_dir))
    # Add to Python path
    sys.path.insert(0, src_dir)

    from linkace_classifier.cli.server import main as server_main
else:
    from .server import main as server_main


def main():
    """Main entry point for the HTTP server CLI"""
    try:
        server_main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
