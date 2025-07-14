# LinkAce Classification API Documentation

## Overview

The LinkAce Classification API provides HTTP endpoints for classifying URLs using AI-powered analysis. The API accepts URLs and returns classification results with confidence scores and reasoning.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, no authentication is required for API access. Authentication may be added in future versions.

## Rate Limiting

- **Default Limit**: 60 requests per minute per IP address
- **Response Headers**: Rate limit information is not currently included in response headers
- **Rate Limit Exceeded**: Returns HTTP 429 with error message

## Content Type

All requests and responses use `application/json` content type.

## Endpoints

### 1. Classify URL

Classify a single URL and return matching classification lists with confidence scores.

**Endpoint**: `POST /classify`

**Request Body**:
```json
{
  "url": "https://example.com/page"
}
```

**Request Parameters**:
- `url` (string, required): The URL to classify. Must be a valid HTTP/HTTPS URL.

**Response** (HTTP 200):
```json
{
  "url": "https://example.com/page",
  "normalized_url": "https://example.com/page",
  "classifications": [
    {
      "list_id": 1,
      "confidence": 0.85,
      "reasoning": "Content matches technology articles pattern"
    },
    {
      "list_id": 3,
      "confidence": 0.92,
      "reasoning": "Similar to existing programming resources"
    }
  ],
  "timestamp": "2025-01-14T10:30:00Z",
  "processing_time_ms": 1250
}
```

**Response Fields**:
- `url`: Original URL from request
- `normalized_url`: Normalized version of the URL (if URL validation is enabled)
- `classifications`: Array of classification results
  - `list_id`: ID of the classification list
  - `confidence`: Confidence score (0.0 to 1.0)
  - `reasoning`: AI-generated explanation for the classification
- `timestamp`: ISO 8601 timestamp of classification
- `processing_time_ms`: Processing time in milliseconds (only in verbose mode)

**Error Responses**:

*Bad Request (HTTP 400)*:
```json
{
  "error": "Missing required field: url",
  "code": 400,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

*Invalid URL (HTTP 422)*:
```json
{
  "error": "Invalid URL format",
  "code": 422,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

*Rate Limited (HTTP 429)*:
```json
{
  "error": "Rate limit exceeded",
  "code": 429,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

*Server Error (HTTP 500)*:
```json
{
  "error": "Classification service error",
  "code": 500,
  "timestamp": "2025-01-14T10:30:00Z"
}
```

### 2. Service Status

Get the current status of the classification service and external dependencies.

**Endpoint**: `GET /status`

**Response** (HTTP 200):
```json
{
  "service": "LinkAce Classification Service",
  "timestamp": "2025-01-14T10:30:00Z",
  "linkace_api": "connected",
  "ollama": "connected",
  "classification_lists": {
    "count": 5,
    "total_links": 1250,
    "cache_status": "fresh"
  }
}
```

**Response Fields**:
- `service`: Service name and version
- `timestamp`: Current timestamp
- `linkace_api`: LinkAce API connection status (`connected`, `disconnected`, `error`)
- `ollama`: Ollama server connection status (`connected`, `disconnected`, `error`)
- `classification_lists`: Information about loaded classification lists
  - `count`: Number of classification lists
  - `total_links`: Total number of links across all lists
  - `cache_status`: Cache status (`fresh`, `stale`, `empty`)

### 3. Classification Summary

Get a summary of available classification lists and their contents.

**Endpoint**: `GET /summary`

**Response** (HTTP 200):
```json
{
  "total_lists": 5,
  "lists": [
    {
      "list_id": 1,
      "link_count": 245,
      "domains": ["github.com", "stackoverflow.com", "dev.to", "medium.com"]
    },
    {
      "list_id": 2,
      "link_count": 189,
      "domains": ["news.ycombinator.com", "techcrunch.com", "arstechnica.com"]
    }
  ]
}
```

**Response Fields**:
- `total_lists`: Total number of classification lists
- `lists`: Array of list information
  - `list_id`: Classification list ID
  - `link_count`: Number of links in the list
  - `domains`: Sample of unique domains in the list (up to 10)

### 4. Health Check

Simple health check endpoint for monitoring and load balancers.

**Endpoint**: `GET /health`

**Response** (HTTP 200):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-14T10:30:00Z"
}
```

## Example Usage

### Using cURL

**Classify a URL**:
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/user/repo"}'
```

**Check service status**:
```bash
curl http://localhost:5000/status
```

**Get classification summary**:
```bash
curl http://localhost:5000/summary
```

### Using Python requests

```python
import requests

# Classify a URL
response = requests.post('http://localhost:5000/classify', 
                        json={'url': 'https://github.com/user/repo'})

if response.status_code == 200:
    result = response.json()
    print(f"URL: {result['url']}")
    print(f"Classifications: {len(result['classifications'])}")
    for classification in result['classifications']:
        print(f"  List {classification['list_id']}: {classification['confidence']:.3f}")
else:
    print(f"Error: {response.status_code} - {response.json()['error']}")

# Check service status
status_response = requests.get('http://localhost:5000/status')
status = status_response.json()
print(f"LinkAce API: {status['linkace_api']}")
print(f"Ollama: {status['ollama']}")
```

### Using JavaScript fetch

```javascript
// Classify a URL
fetch('http://localhost:5000/classify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({url: 'https://github.com/user/repo'})
})
.then(response => response.json())
.then(data => {
  console.log('Classifications:', data.classifications);
})
.catch(error => {
  console.error('Error:', error);
});
```

## Configuration

The API server behavior can be configured through:

### Command Line Arguments

```bash
python run_server.py --host 0.0.0.0 --port 8080 --debug
```

### Configuration File

```bash
python run_server.py --config config.json
```

Example `config.json`:
```json
{
  "linkace_api_url": "https://your-linkace.com/api/v2",
  "linkace_api_token": "your-token-here",
  "classify_list_ids": [1, 2, 3, 4, 5],
  "server_host": "0.0.0.0",
  "server_port": 5000,
  "confidence_threshold": 0.8,
  "enable_cors": true,
  "enable_url_validation": true,
  "max_requests_per_minute": 60
}
```

### Environment Variables

```bash
export LINKACE_API_URL="https://your-linkace.com/api/v2"
export LINKACE_API_TOKEN="your-token-here"
export CLASSIFY_LIST_IDS="1,2,3,4,5"
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="5000"
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request format or missing required fields |
| 404 | Not Found | Endpoint not found |
| 405 | Method Not Allowed | HTTP method not supported for endpoint |
| 422 | Unprocessable Entity | Invalid URL format or content |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error or external service failure |
| 503 | Service Unavailable | External service (LinkAce/Ollama) unavailable |

## Performance Notes

- **Caching**: Classification lists are cached for 5 minutes to improve performance
- **Concurrency**: The server supports concurrent requests using Flask's threaded mode
- **Timeouts**: Requests have a default timeout of 30 seconds
- **Rate Limiting**: Implemented per-IP address to prevent abuse

## Security Considerations

- **Input Validation**: All URLs are validated before processing
- **Rate Limiting**: Prevents abuse and DoS attacks
- **CORS**: Can be disabled for security if not needed
- **No Authentication**: Currently no authentication required (consider adding for production)

## Monitoring

- Use `/health` endpoint for basic health checks
- Use `/status` endpoint for detailed service status
- Monitor response times and error rates
- Check external service connectivity (LinkAce API, Ollama)

## Troubleshooting

### Common Issues

1. **503 Service Unavailable**: Check LinkAce API and Ollama connectivity
2. **429 Rate Limited**: Reduce request frequency or increase rate limits
3. **422 Invalid URL**: Ensure URLs include protocol (http:// or https://)
4. **500 Server Error**: Check server logs for detailed error information

### Debug Mode

Enable debug mode for detailed logging:
```bash
python run_server.py --debug
```

### Verbose Mode

Enable verbose mode for additional response information:
```bash
python run_server.py --verbose
```