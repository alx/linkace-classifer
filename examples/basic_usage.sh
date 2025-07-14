#!/bin/bash

# Basic LinkAce Classifier Usage Examples

echo "🔗 LinkAce Classifier - Usage Examples"
echo "======================================"

# Example 1: Basic classification
echo -e "\n1. Basic Classification:"
echo "python linkace_classifier.py \\"
echo "  --api-url https://your-linkace.com/api/v2 \\"
echo "  --token YOUR_API_TOKEN \\"
echo "  --input-list 12 \\"
echo "  --classify-lists 1,2,3,4,5"

# Example 2: Dry run mode
echo -e "\n2. Dry Run Mode (Test Without Changes):"
echo "python linkace_classifier.py \\"
echo "  --api-url https://your-linkace.com/api/v2 \\"
echo "  --token YOUR_API_TOKEN \\"
echo "  --input-list 12 \\"
echo "  --classify-lists 1,2,3,4,5 \\"
echo "  --dry-run"

# Example 3: Custom confidence threshold
echo -e "\n3. Custom Confidence Threshold:"
echo "python linkace_classifier.py \\"
echo "  --api-url https://your-linkace.com/api/v2 \\"
echo "  --token YOUR_API_TOKEN \\"
echo "  --input-list 12 \\"
echo "  --classify-lists 1,2,3,4,5 \\"
echo "  --confidence-threshold 0.7"

# Example 4: Verbose output with CSV export
echo -e "\n4. Verbose Output with CSV Export:"
echo "python linkace_classifier.py \\"
echo "  --api-url https://your-linkace.com/api/v2 \\"
echo "  --token YOUR_API_TOKEN \\"
echo "  --input-list 12 \\"
echo "  --classify-lists 1,2,3,4,5 \\"
echo "  --verbose \\"
echo "  --output-file results.csv"

# Example 5: Custom Ollama model
echo -e "\n5. Custom Ollama Model:"
echo "python linkace_classifier.py \\"
echo "  --api-url https://your-linkace.com/api/v2 \\"
echo "  --token YOUR_API_TOKEN \\"
echo "  --input-list 12 \\"
echo "  --classify-lists 1,2,3,4,5 \\"
echo "  --ollama-model llama3.1:70b \\"
echo "  --ollama-url http://192.168.1.100:11434"

# Example 6: Using configuration file
echo -e "\n6. Using Configuration File:"
echo "# First, create config.json:"
echo "python config.py"
echo "# Edit config.json with your settings"
echo "# Then run:"
echo "python linkace_classifier.py --config config.json"

# Example 7: Environment variables
echo -e "\n7. Using Environment Variables:"
echo "export LINKACE_API_URL='https://your-linkace.com/api/v2'"
echo "export LINKACE_API_TOKEN='your-api-token'"
echo "export INPUT_LIST_ID=12"
echo "export CLASSIFY_LIST_IDS='1,2,3,4,5'"
echo "python linkace_classifier.py"

echo -e "\n✅ For more examples, check the README.md file!"