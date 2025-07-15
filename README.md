# 🔗 LinkAce Link Classifier

> AI-powered automatic link classification for LinkAce using Ollama

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![LinkAce](https://img.shields.io/badge/LinkAce-v2.1+-orange.svg)](https://www.linkace.org/)
[![Ollama](https://img.shields.io/badge/Ollama-compatible-purple.svg)](https://ollama.ai/)

Automatically classify links from a LinkAce input list into appropriate classification lists using AI-powered content analysis. The classifier uses Ollama for intelligent link classification with confidence scoring to ensure accurate categorization.

## ✨ Features

- **🤖 AI-Powered Classification**: Uses Ollama server for intelligent link analysis
- **🎯 Confidence Scoring**: Only moves links with high confidence scores (configurable threshold)
- **🔄 LinkAce Integration**: Seamlessly integrates with LinkAce API v2.1+
- **🧪 Dry Run Mode**: Test classifications without making actual changes
- **⚙️ Flexible Configuration**: CLI arguments, config files, and environment variables
- **📊 Comprehensive Logging**: Detailed progress tracking and classification reporting
- **💾 Export Results**: Save classification results to CSV or JSON formats
- **🛡️ Error Handling**: Robust error handling with automatic retry and rate limiting

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- LinkAce instance with API access
- Ollama server running locally or remotely

### Installation

#### Option 1: Install from source
1. **Clone the repository**:
   ```bash
   git clone https://github.com/alx/linkace-classifier.git
   cd linkace-classifier
   ```

2. **Install the package**:
   ```bash
   pip install .
   ```

#### Option 2: Development installation
```bash
git clone https://github.com/alx/linkace-classifier.git
cd linkace-classifier
pip install -e .
```

3. **Set up Ollama**:
   ```bash
   # Install Ollama (see https://ollama.ai/)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model
   ollama pull llama3.2
   
   # Start the server
   ollama serve
   ```

### Basic Usage

```bash
linkace-classifier \
  --api-url https://your-linkace.com/api/v2 \
  --token YOUR_API_TOKEN \
  --input-list 12 \
  --classify-lists 1,2,3,4,5
```

### Test with Dry Run

```bash
linkace-classifier \
  --api-url https://your-linkace.com/api/v2 \
  --token YOUR_API_TOKEN \
  --input-list 12 \
  --classify-lists 1,2,3,4,5 \
  --dry-run
```

## 📖 How It Works

1. **📥 Load Input List**: Fetches all links from the specified input list
2. **📚 Load Classification Context**: Retrieves links from classification lists for AI context
3. **🤖 AI Classification**: For each input link:
   - Analyzes link content, title, and metadata
   - Compares against existing links in classification lists
   - Generates confidence scores for each potential classification
4. **🎯 Threshold Filtering**: Only processes classifications above confidence threshold (default: 0.8)
5. **🔄 Link Movement**: Removes links from input list and adds to appropriate classification lists
6. **📊 Results**: Provides detailed summary of classifications and movements

## ⚙️ Configuration

### Command Line Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--api-url` | LinkAce API base URL | Yes |
| `--token` | LinkAce API token | Yes |
| `--input-list` | Input list ID to classify links from | Yes |
| `--classify-lists` | Comma-separated classification list IDs | Yes |
| `--config` | Configuration file path | No |
| `--ollama-url` | Ollama server URL (default: http://localhost:11434) | No |
| `--ollama-model` | Ollama model to use (default: llama3.2) | No |
| `--confidence-threshold` | Confidence threshold (default: 0.8) | No |
| `--dry-run` | Run in dry-run mode | No |
| `--verbose` | Enable verbose output | No |
| `--output-file` | Output file for results (CSV or JSON) | No |

### Configuration File

Create a `configs/config.json` file:

```json
{
  "linkace_api_url": "https://your-linkace.com/api/v2",
  "linkace_api_token": "your-api-token",
  "input_list_id": 12,
  "classify_list_ids": [1, 2, 3, 4, 5],
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "confidence_threshold": 0.8,
  "dry_run": false,
  "verbose": false
}
```

Generate a sample configuration:
```bash
python src/linkace_classifier/core/config.py
```

### Environment Variables

```bash
export LINKACE_API_URL="https://your-linkace.com/api/v2"
export LINKACE_API_TOKEN="your-api-token"
export INPUT_LIST_ID=12
export CLASSIFY_LIST_IDS="1,2,3,4,5"
export OLLAMA_URL="http://localhost:11434"
export CONFIDENCE_THRESHOLD=0.8
```

## 🔧 LinkAce API Integration

### Required API Endpoints

The classifier uses these LinkAce API v2.1+ endpoints:
- `GET /lists/{id}/links` - Retrieve all links from a specific list
- `GET /links/{id}` - Get detailed information about individual links
- `PUT /links/{id}` - Update link list assignments

### API Token Setup

1. Log into your LinkAce instance
2. Go to **User Settings** → **API Tokens**
3. Create a new token with appropriate permissions
4. Use the token in your configuration

## 🧪 Testing

Run the comprehensive test suite:
```bash
python tests/test_core.py
```

Run the demo with existing CSV data:
```bash
python scripts/demo_classifier.py
```

## 📊 Example Output

```
[2024-01-15 10:30:00] INFO: Starting LinkAce Link Classifier
✅ LinkAce API connection successful
✅ Ollama server connection successful
[2024-01-15 10:30:01] INFO: Loaded 25 links from input list
[2024-01-15 10:30:02] INFO: Loaded 150 total links from 5 classification lists
Progress: |██████████████████████████████████████████████████| 100.0% (25/25)

============================================================
📊 CLASSIFICATION SUMMARY
============================================================
Total links processed: 25
Links classified: 18
Links not classified: 7
Classification rate: 72.0%

Classifications by list:
  List 1: 8 links
  List 2: 5 links  
  List 3: 3 links
  List 4: 2 links

Confidence statistics:
  Average: 0.847
  Range: 0.801 - 0.923
============================================================
```

## 🔧 Advanced Usage

### Custom Ollama Models

```bash
linkace-classifier \
  --ollama-model llama3.1:70b \
  --ollama-url http://localhost:11434 \
  [other options]
```

### Batch Processing with Custom Threshold

```bash
linkace-classifier \
  --confidence-threshold 0.7 \
  --output-file results.csv \
  --verbose \
  [other options]
```

### Configuration File Usage

```bash
linkace-classifier --config configs/config.json
```

### HTTP API Server

Start the HTTP API server:
```bash
linkace-classifier-server --config configs/config.json --host 0.0.0.0 --port 8080
```

Make classification requests:
```bash
curl -X POST http://localhost:8080/classify \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/user/repo"}'
```

## 🛡️ Security Considerations

- **API Token Security**: Tokens are never logged or exposed in output
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Built-in rate limiting prevents API abuse
- **Safe Defaults**: Conservative defaults for all operations
- **Dry Run Testing**: Always test with `--dry-run` before production use

## 🚀 Performance & Scalability

- **Batch Processing**: Efficiently handles large link collections
- **Pagination Support**: Automatically handles paginated API responses
- **Memory Efficient**: Processes links in batches to manage memory usage
- **Rate Limiting**: Configurable delays between API calls
- **Progress Tracking**: Real-time progress indicators for long-running operations
- **Resumable Operations**: Graceful handling of interruptions

## 🤖 Supported Ollama Models

The classifier works with any Ollama model, but these are recommended:

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `llama3.2` | Fast | Good | Default choice |
| `llama3.1:70b` | Slow | Excellent | High-accuracy needs |
| `codellama:13b` | Medium | Good | Technical links |
| `mistral:7b` | Very Fast | Fair | Quick processing |

## 🐛 Troubleshooting

### Common Issues

**❌ LinkAce API Connection Failed**
```bash
❌ LinkAce API connection failed: 404 Client Error
```
- Verify your LinkAce URL and API token
- Ensure API token has necessary permissions
- Check LinkAce instance is running and accessible

**❌ Ollama Connection Failed**
```bash
❌ Ollama server connection failed
```
- Start Ollama server: `ollama serve`
- Verify server URL and port
- Check model availability: `ollama list`

**⚠️ No Classifications Above Threshold**
```bash
⚠️ No classifications above threshold
```
- Lower confidence threshold: `--confidence-threshold 0.7`
- Ensure classification lists have sufficient context links
- Verify input links are accessible and have content

**🔄 Rate Limiting Issues**
```bash
429 Too Many Requests
```
- Increase rate limit delay in configuration
- Use smaller batch sizes
- Check LinkAce instance rate limits

### Debug Mode

Enable detailed logging:
```bash
linkace-classifier --verbose [other options]
```

## 📁 Project Structure

```
linkace-classifier/
├── README.md                    # Project documentation
├── LICENSE                      # License file
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pyproject.toml              # Modern Python packaging
├── Dockerfile                   # Container setup
├── docker-compose.yml          # Container orchestration
├── src/
│   └── linkace_classifier/     # Main package
│       ├── __init__.py         # Package initialization
│       ├── core/               # Configuration, utilities, classifier
│       ├── api/                # LinkAce & Ollama clients
│       ├── http/               # Flask server
│       ├── cli/                # Command-line interfaces
│       ├── services/           # Classification service
│       └── validation/         # URL validation
├── tests/                      # Test files
├── configs/                    # Configuration files
├── scripts/                    # Demo and legacy scripts
├── docs/                       # Documentation
└── examples/                   # Usage examples
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python tests/test_core.py`
6. Submit a pull request

### Reporting Issues

Please use the [GitHub Issues](https://github.com/yourusername/linkace-classifier/issues) to report bugs or request features.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LinkAce](https://www.linkace.org/) - The excellent bookmark manager this tool integrates with
- [Ollama](https://ollama.ai/) - The AI inference engine powering intelligent classification

## 🌟 Support

- **Documentation**: Check this README and inline code documentation
- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/linkace-classifier/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/linkace-classifier/discussions)

---

**Made with ❤️ for the LinkAce community**
