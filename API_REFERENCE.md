# AI Finance Assistant - API Reference Documentation

> Complete API documentation for developers integrating with AI Finance Assistant.

---

## Table of Contents
1. [Authentication](#authentication)
2. [Chat Endpoints](#chat-endpoints)
3. [Portfolio Endpoints](#portfolio-endpoints)
4. [Market Data Endpoints](#market-data-endpoints)
5. [Conversation Management](#conversation-management)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Code Examples](#code-examples)

---

## Base URL

```
Development:  http://localhost:8000
Production:   https://api.financeai.eu
```

---

## Authentication

All requests require authentication (JWT token or API key).

### Bearer Token Authentication

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.financeai.eu/api/chat
```

### API Key Authentication (Legacy)

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  https://api.financeai.eu/api/chat
```

---

## Chat Endpoints

### POST /api/chat

Send a chat message and receive AI-powered response with context awareness.

**Request:**
```json
{
  "message": "What is dollar-cost averaging?",
  "conversation_id": "conv-abc-123",
  "user_id": "user-xyz-789",
  "include_sources": true
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| message | string | Yes | User's chat message |
| conversation_id | string | No | UUID for multi-turn conversations. If omitted, new conversation created |
| user_id | string | No | User identifier for conversation history tracking |
| include_sources | boolean | No | Include knowledge base sources in response (default: true) |

**Response:**
```json
{
  "response": "Dollar-cost averaging is an investment strategy where...",
  "conversation_id": "conv-abc-123",
  "message_id": "msg-def-456",
  "timestamp": "2025-04-21T10:30:00Z",
  "sources": [
    "07_dca.md",
    "18_long_term_investing.md"
  ],
  "confidence": 0.92,
  "thinking_process": "Intent: education, Topics: [dca, investing]",
  "conversation_summary": "User learning about DCA and long-term strategies"
}
```

**Status Codes:**
- `200 OK` - Successful response
- `400 Bad Request` - Invalid message or parameters
- `401 Unauthorized` - Missing or invalid authentication
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

**Example:**

```bash
curl -X POST https://api.financeai.eu/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "message": "How do I build a diversified portfolio?",
    "conversation_id": "conv-user-1",
    "include_sources": true
  }'
```

---

### WebSocket /ws/chat/{conversation_id}

Real-time chat with streaming responses and persistent context.

**Connection:**
```javascript
const ws = new WebSocket(
  `wss://api.financeai.eu/ws/chat/conv-abc-123?token=JWT_TOKEN`
);

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "What's a Roth IRA?",
    user_id: "user-xyz"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data.response);
  console.log('Streaming:', data.type); // 'streaming' or 'complete'
};
```

**Message Types:**

| Type | Description | Data |
|------|-------------|------|
| user_message | User message received | {conversation_id, timestamp} |
| assistant_message | Complete response | {response, timestamp, sources} |
| error | Error occurred | {error: string} |

---

## Portfolio Endpoints

### POST /api/portfolio/analyze

Analyze a portfolio and generate visualizations.

**Request:**
```json
{
  "holdings": [
    {
      "symbol": "AAPL",
      "shares": 100,
      "purchase_price": 150.00
    },
    {
      "symbol": "BND",
      "shares": 50,
      "purchase_price": 80.00
    }
  ],
  "include_risk_analysis": true,
  "include_correlation": true
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| holdings | array | Yes | Array of holdings with symbol, shares, purchase_price |
| include_risk_analysis | boolean | No | Include risk metrics (default: true) |
| include_correlation | boolean | No | Include correlation matrix (default: true) |
| benchmark_symbol | string | No | Compare against benchmark (e.g., "SPY") |

**Response:**
```json
{
  "summary": {
    "total_value": 25000.00,
    "total_gain_loss": 1250.00,
    "gain_loss_percentage": 5.25,
    "currency": "USD"
  },
  "allocation": [
    {
      "name": "AAPL",
      "symbol": "AAPL",
      "value": 15000.00,
      "percentage": 60.0,
      "sector": "Technology"
    },
    {
      "name": "BND",
      "symbol": "BND",
      "value": 10000.00,
      "percentage": 40.0,
      "sector": "Bonds"
    }
  ],
  "risk_metrics": {
    "volatility": 0.18,
    "beta": 0.85,
    "sharpe_ratio": 1.2,
    "max_drawdown": 0.15
  },
  "correlation_matrix": {
    "assets": ["AAPL", "BND"],
    "matrix": [[1.0, -0.3], [-0.3, 1.0]]
  }
}
```

**Example:**

```bash
curl -X POST https://api.financeai.eu/api/portfolio/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "shares": 100, "purchase_price": 150},
      {"symbol": "BND", "shares": 50, "purchase_price": 80}
    ],
    "include_risk_analysis": true
  }'
```

---

### GET /api/portfolio/{portfolio_id}

Retrieve a previously saved portfolio.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| portfolio_id | string | Yes | Portfolio UUID |

**Response:**
```json
{
  "id": "portfolio-abc",
  "user_id": "user-xyz",
  "name": "My Retirement Portfolio",
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-04-21T10:30:00Z",
  "holdings": [...],
  "analysis": {...}
}
```

---

### PUT /api/portfolio/{portfolio_id}

Update an existing portfolio.

**Request:**
```json
{
  "name": "Updated Portfolio Name",
  "holdings": [...]
}
```

**Response:** Updated portfolio object (same as GET)

---

## Market Data Endpoints

### GET /api/market/{symbol}

Get current market data for a symbol.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Stock ticker (e.g., "AAPL") |
| interval | string | No | Data interval: "1d", "1wk", "1mo" (default: "1d") |
| period | string | No | Historical period: "1d", "5d", "1mo", "3mo", "6mo", "1y", "5y" (default: "1y") |

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_price": 175.50,
  "currency": "USD",
  "previous_close": 174.30,
  "open": 174.80,
  "high": 176.20,
  "low": 174.50,
  "volume": 52000000,
  "market_cap": 2750000000000,
  "pe_ratio": 28.5,
  "dividend_yield": 0.0045,
  "52_week_high": 199.62,
  "52_week_low": 124.17,
  "historical_data": [
    {
      "date": "2025-04-21",
      "open": 174.80,
      "high": 176.20,
      "low": 174.50,
      "close": 175.50,
      "volume": 52000000
    }
  ]
}
```

**Example:**

```bash
curl https://api.financeai.eu/api/market/AAPL?period=3mo \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

### GET /api/market/comparison

Compare multiple symbols side-by-side.

**Request:**
```
GET /api/market/comparison?symbols=AAPL,MSFT,GOOGL&metrics=price,pe_ratio,dividend_yield
```

**Response:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "comparison": [
    {
      "symbol": "AAPL",
      "price": 175.50,
      "pe_ratio": 28.5,
      "dividend_yield": 0.0045
    },
    {
      "symbol": "MSFT",
      "price": 418.75,
      "pe_ratio": 32.1,
      "dividend_yield": 0.0074
    }
  ]
}
```

---

## Conversation Management

### GET /api/conversations/{conversation_id}/history

Get full conversation history.

**Response:**
```json
{
  "conversation_id": "conv-abc-123",
  "messages": [
    {
      "role": "user",
      "content": "What is diversification?",
      "timestamp": "2025-04-21T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Diversification is...",
      "timestamp": "2025-04-21T10:00:05Z",
      "sources": ["03_diversification.md"],
      "confidence": 0.94
    }
  ],
  "metadata": {
    "intent": "education",
    "topics": ["diversification", "portfolio"],
    "message_count": 6,
    "created_at": "2025-04-21T09:50:00Z",
    "last_updated": "2025-04-21T10:30:00Z"
  }
}
```

---

### DELETE /api/conversations/{conversation_id}

Delete a conversation and its history.

**Response:**
```json
{
  "status": "success",
  "message": "Conversation deleted",
  "conversation_id": "conv-abc-123"
}
```

---

### POST /api/conversations/{conversation_id}/clear

Clear conversation messages but keep metadata.

**Response:**
```json
{
  "status": "success",
  "message": "Conversation history cleared",
  "metadata": {...}
}
```

---

### GET /api/users/{user_id}/conversations

Get all conversations for a user.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Max results (default: 10) |
| offset | integer | Pagination offset (default: 0) |
| sort | string | Sort by: "recent", "oldest", "topics" |

**Response:**
```json
{
  "user_id": "user-xyz",
  "conversations": [
    {
      "id": "conv-abc",
      "created_at": "2025-04-21T09:50:00Z",
      "intent": "education",
      "topics": ["diversification"],
      "message_count": 6
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

---

## Error Handling

### Error Response Format

All errors follow standard format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Message parameter is required",
    "details": {
      "field": "message",
      "reason": "must_not_be_empty"
    },
    "request_id": "req-abc-123"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_REQUEST | 400 | Invalid parameters or format |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Access denied |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMITED | 429 | Too many requests |
| SERVER_ERROR | 500 | Internal server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |

**Example Error:**

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after": 45
    }
  }
}
```

---

## Rate Limiting

API requests are rate-limited per user/API key.

**Default Limits:**
```
Free Tier:
- 100 requests/minute
- 1,000 requests/day
- 10 concurrent connections

Pro Tier:
- 1,000 requests/minute
- 100,000 requests/day
- 100 concurrent connections
```

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1713691445
Retry-After: 45
```

---

## Code Examples

### Python Client

```python
import requests
from datetime import datetime

class FinanceAIClient:
    def __init__(self, api_url, jwt_token):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
    
    def chat(self, message, conversation_id=None):
        """Send a chat message"""
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "include_sources": True
        }
        response = requests.post(
            f"{self.api_url}/api/chat",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_portfolio(self, holdings):
        """Analyze a portfolio"""
        payload = {
            "holdings": holdings,
            "include_risk_analysis": True
        }
        response = requests.post(
            f"{self.api_url}/api/portfolio/analyze",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_market_data(self, symbol, period="1y"):
        """Get market data for a symbol"""
        response = requests.get(
            f"{self.api_url}/api/market/{symbol}",
            params={"period": period},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = FinanceAIClient("https://api.financeai.eu", "YOUR_JWT_TOKEN")

# Chat
response = client.chat("What is dollar-cost averaging?")
print(response["response"])

# Portfolio analysis
holdings = [
    {"symbol": "AAPL", "shares": 100, "purchase_price": 150},
    {"symbol": "BND", "shares": 50, "purchase_price": 80}
]
analysis = client.analyze_portfolio(holdings)
print(f"Total Value: ${analysis['summary']['total_value']}")

# Market data
market = client.get_market_data("AAPL")
print(f"AAPL Price: ${market['current_price']}")
```

### JavaScript/TypeScript Client

```typescript
interface ChatRequest {
  message: string;
  conversation_id?: string;
  include_sources?: boolean;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: string[];
  confidence: number;
}

class FinanceAIClient {
  private apiUrl: string;
  private jwtToken: string;

  constructor(apiUrl: string, jwtToken: string) {
    this.apiUrl = apiUrl;
    this.jwtToken = jwtToken;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.apiUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async analyzePortfolio(holdings: any[]) {
    const response = await fetch(`${this.apiUrl}/api/portfolio/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ holdings })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  connectWebSocket(conversationId: string): WebSocket {
    return new WebSocket(
      `${this.apiUrl.replace('https', 'wss')}/ws/chat/${conversationId}?token=${this.jwtToken}`
    );
  }
}

// Usage
const client = new FinanceAIClient('https://api.financeai.eu', 'YOUR_JWT_TOKEN');

// Chat
const response = await client.chat({
  message: 'What is a Roth IRA?',
  conversation_id: 'conv-user-1'
});
console.log(response.response);

// WebSocket
const ws = client.connectWebSocket('conv-user-1');
ws.onmessage = (event) => {
  console.log('Response:', JSON.parse(event.data));
};
```

### cURL Examples

```bash
# Chat message
curl -X POST https://api.financeai.eu/api/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I start investing?",
    "include_sources": true
  }'

# Portfolio analysis
curl -X POST https://api.financeai.eu/api/portfolio/analyze \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"symbol": "AAPL", "shares": 100, "purchase_price": 150},
      {"symbol": "BND", "shares": 50, "purchase_price": 80}
    ]
  }'

# Market data
curl https://api.financeai.eu/api/market/AAPL?period=1y \
  -H "Authorization: Bearer $JWT_TOKEN"

# Conversation history
curl https://api.financeai.eu/api/conversations/conv-abc-123/history \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## SDKs & Libraries

### Official SDKs

- **Python**: `pip install financeai-sdk`
- **JavaScript/TypeScript**: `npm install @financeai/sdk`
- **Go**: `go get github.com/financeai/go-sdk`

### Community SDKs

- **Ruby**: `gem install financeai`
- **PHP**: `composer require financeai/php-sdk`

---

## Webhook Events

Subscribe to real-time events via webhooks.

**Event Types:**
- `portfolio.updated` - Portfolio changed
- `alert.triggered` - Alert threshold reached
- `market.alert` - Market condition alert
- `conversation.created` - New conversation started

**Webhook Payload:**
```json
{
  "event": "portfolio.updated",
  "timestamp": "2025-04-21T10:30:00Z",
  "data": {
    "portfolio_id": "portfolio-abc",
    "change_type": "holding_added",
    "changes": {...}
  }
}
```

---

## Support

- **Documentation**: https://docs.financeai.eu
- **Issues**: https://github.com/financeai/api/issues
- **Email**: support@financeai.eu
- **Status Page**: https://status.financeai.eu

---

**Last Updated**: April 2026 | **API Version**: 1.0.0
