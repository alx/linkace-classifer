#!/usr/bin/env python3
"""
CLI Entry Point for LinkAce Classifier

Main command-line interface for running the LinkAce classifier
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

    from linkace_classifier.core.classifier import main as classifier_main
else:
    from ..core.classifier import main as classifier_main


def main():
    """Main entry point for the classifier CLI"""
    try:
        classifier_main()
    except KeyboardInterrupt:
        print("\n\nClassifier interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
