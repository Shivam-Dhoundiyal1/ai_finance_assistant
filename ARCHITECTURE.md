# AI Finance Assistant - Architecture & System Design

> Comprehensive visual and textual documentation of system architecture, component relationships, and data flows.

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  React Frontend (TypeScript)                                          │   │
│  │  - Asset Allocation Charts (Pie Charts)                             │   │
│  │  - Risk Heatmaps (Bar Charts with Risk Scoring)                     │   │
│  │  - Correlation Matrix Visualization                                 │   │
│  │  - Multi-turn Chat Interface with Context                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │ HTTP/WebSocket
                                │ Axios + EventSource
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  FastAPI Server (Port 8000)                                          │   │
│  │  ├─ REST Endpoints (/api/chat, /api/market, /api/portfolio)        │   │
│  │  ├─ WebSocket Endpoints (/ws/chat/{conversation_id})               │   │
│  │  ├─ CORS Middleware (localhost:5173, :3000)                        │   │
│  │  └─ Request/Response Logging                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
    │  Conversation   │  │  Chat Routes    │  │ Market/Portfolio │
    │  Context Store  │  │  & Handlers     │  │ Data Endpoints   │
    └─────────────────┘  └────────┬────────┘  └──────────┬───────┘
                                  │                      │
                                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  LangGraph Workflow State Machine                                     │   │
│  │                                                                       │   │
│  │  ┌─────────────┐                                                   │   │
│  │  │   Router    │───Determines request type and optimal path       │   │
│  │  └──────┬──────┘                                                   │   │
│  │         │                                                           │   │
│  │    ┌────┴────┬──────────┬──────────┐                              │   │
│  │    ▼         ▼          ▼          ▼                              │   │
│  │ ┌─────┐ ┌──────┐ ┌────────┐ ┌───────┐                            │   │
│  │ │ RAG │ │Market│ │Finance │ │ Other │                            │   │
│  │ │Ret. │ │ Agg. │ │  Calc  │ │ Agents│                            │   │
│  │ └──┬──┘ └──┬───┘ └───┬────┘ └───┬───┘                            │   │
│  │    └───┬───┴────┬────┴───┬──────┘                                │   │
│  │        ▼        ▼        ▼                                        │   │
│  │  ┌──────────────────────────────┐                               │   │
│  │  │   LLM Node (gpt-4o-mini)      │                              │   │
│  │  │   - Context Injection         │                              │   │
│  │  │   - Response Generation       │                              │   │
│  │  │   - Chain-of-Thought          │                              │   │
│  │  └──────────┬───────────────────┘                               │   │
│  │             ▼                                                    │   │
│  │  ┌──────────────────────────────┐                               │   │
│  │  │   Response Formatter          │                              │   │
│  │  │   - Markdown Formatting       │                              │   │
│  │  │   - Confidence Scoring        │                              │   │
│  │  │   - Source Attribution        │                              │   │
│  │  └──────────────────────────────┘                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└───────────────┬──────────────────────────────────────────────────────────┘
                │
        ┌───────┼────────┬─────────────┬──────────────┐
        ▼       ▼        ▼             ▼              ▼
    ┌──────┐ ┌─────┐ ┌────────┐ ┌──────────┐  ┌──────────┐
    │ RAG  │ │Redis│ │PostgreS│ │yFinance  │  │ NewsAPI  │
    │Chroma│ │Cache│ │Database│ │& Alpha V.│  │& Webhooks│
    │  DB  │ │(5s) │ │Logs    │ │API       │  │          │
    └──────┘ └─────┘ └────────┘ └──────────┘  └──────────┘
```

---

## Component Deep Dives

### 1. Frontend Layer (React + TypeScript)

**Components:**
```
frontend/src/
├── components/
│   ├── AssetAllocationChart.tsx        # Pie chart for portfolio allocation
│   ├── RiskHeatmap.tsx                 # Risk visualization & metrics
│   ├── CorrelationMatrix.tsx           # Asset correlation heatmap
│   ├── ChatInterface.tsx               # Multi-turn chat with context
│   ├── ConversationHistory.tsx         # View past conversations
│   └── PortfolioAnalysis.tsx           # Integrated portfolio view
├── hooks/
│   ├── useChat.ts                      # Chat logic hook
│   ├── useConversation.ts              # Conversation management
│   └── usePortfolioData.ts             # Portfolio data fetching
├── pages/
│   ├── Chat.tsx                        # Chat interface page
│   ├── Portfolio.tsx                   # Portfolio analysis page
│   └── Dashboard.tsx                   # Main dashboard
└── api.ts                              # Axios client config
```

**Data Flow:**
```
User Input (Chat/Click)
    ↓
React Hook (useChat)
    ↓
Axios API Call
    ↓
FastAPI Endpoint
    ↓
Response (JSON)
    ↓
Update Component State
    ↓
Re-render with New Data
```

### 2. API Layer (FastAPI)

**Endpoints:**

| Endpoint | Method | Purpose | Context |
|----------|--------|---------|---------|
| `/api/chat` | POST | Send chat message | Uses ConversationContext |
| `/ws/chat/{id}` | WebSocket | Real-time chat | Streaming context |
| `/api/conversations/{id}/history` | GET | Get conversation | Full context retrieval |
| `/api/conversations/{id}/clear` | POST | Clear messages | Keep metadata |
| `/api/market/{symbol}` | GET | Market data | yFinance + caching |
| `/api/portfolio/analyze` | POST | Portfolio analysis | Risk calculation |
| `/api/health` | GET | Server status | Health check |

**Request/Response Flow:**
```
FastAPI Request
    ↓
Middleware (CORS, Logging, Auth)
    ↓
Route Handler
    ↓
Retrieve/Create ConversationContext
    ↓
Call Workflow Orchestrator
    ↓
Receive Response
    ↓
Add to ConversationContext
    ↓
Save Context (in-memory/Redis)
    ↓
Return Response to Client
```

### 3. Conversation Context Manager

**Multi-turn Chat Flow:**

```
Message 1: "What's a diversified portfolio?"
    ↓
[Context: intent=education, topics=[diversification]]
    ↓
Agent Response (from knowledge base)
    ↓
Save Context + Message

Message 2: "How do I build one?"
    ↓
Retrieve Context (has topic memory)
    ↓
Inject Context: "User interested in diversification, now asking HOW"
    ↓
Agent Response (more practical, builds on prior context)
    ↓
Update Context + Message

Message 3: "What about my tech stocks?"
    ↓
Retrieve Context (knows about diversification interest)
    ↓
Inject Context: "User wants to diversify, specifically concerned about tech"
    ↓
Agent Response (tech-specific diversification advice)
    ↓
Update Context + Message
```

**Context Data Structure:**
```python
ConversationContext {
    conversation_id: str
    user_id: Optional[str]
    
    messages: List[ChatMessage]  # Full history
    detected_intent: str         # "portfolio_analysis", "tax_planning"
    detected_topics: List[str]   # ["stocks", "retirement", "diversification"]
    user_profile: dict           # {"age": 35, "risk_tolerance": "moderate"}
    
    Methods:
    - add_message()              # Add user/assistant message
    - get_conversation_summary() # Summarize for context injection
    - get_system_prompt_injection()  # Prepare context for LLM
    - extract_user_profile_updates() # Learn user info from messages
}
```

### 4. LangGraph Workflow Orchestration

**State Machine Flow:**

```
START
    ↓
input: ChatMessage + Context
    ↓
[ROUTER NODE]
  Analyzes message + context
  Determines best agent path
  Updates conversation intent/topics
    ↓
    ├─→ [RAG NODE] → Documents Retrieved
    ├─→ [MARKET NODE] → Market Data
    ├─→ [PORTFOLIO NODE] → Portfolio Calc
    └─→ [OTHER AGENTS] → Specialized Processing
    ↓
[ENRICHMENT NODE]
  Combines all data sources
  Prioritizes by relevance
  Adds source attribution
    ↓
[LLM NODE]
  Injects ConversationContext
  Provides enhanced system prompt
  Generates response with chain-of-thought
    ↓
[FORMATTER NODE]
  Markdown formatting
  Confidence scoring
  Source linking
    ↓
output: Formatted Response + Sources + Context Update
    ↓
END
```

**Key Enhancement with Context:**
```
Without Context:
  Router analyzes message → Agent selected → Response

With Context:
  Router analyzes message + conversation_summary + user_profile
    → Better agent selection
    → More relevant data retrieval
    → Contextually aware response
    → Conversation continuity
```

### 5. Knowledge Base (RAG System)

**Document Storage & Retrieval:**

```
Knowledge Files (50 documents)
    ↓
RecursiveCharacterTextSplitter
  - Chunk size: 800 chars
  - Overlap: 200 chars
  - Separators: ["\n\n", "\n", ". ", " ", ""]
    ↓
HuggingFaceEmbeddings (all-MiniLM-L6-v2)
  - 384-dimensional vectors
  - ~150k vector DB entries
    ↓
Chroma Vector Database
  - Persistent storage: data/chroma/
  - Collection: "finance_knowledge"
  - Metadata: source file, section, relevance
    ↓
RAG Retriever (Top-K + Min Similarity)
  - Top K: 5 documents
  - Min score: 0.3 (30% relevance)
  - Reranked by relevance
    ↓
Context Injection
  - Best matches → System prompt
  - Source attribution
  - Confidence scores
```

---

## Data Flow Diagrams

### Chat Message Flow (Request → Response)

```
┌─────────────────────────────────────────────────────────┐
│ 1. USER SENDS MESSAGE                                   │
│    Frontend: "How do I diversify my portfolio?"         │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 2. API ENDPOINT (/api/chat)                             │
│    - Extract message & conversation_id                  │
│    - Create/retrieve ConversationContext                │
│    - Add user message to history                        │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 3. CONVERSATION CONTEXT PROCESSING                      │
│    - Detect intent: "education" + "portfolio_advice"    │
│    - Extract topics: ["diversification", "portfolio"]   │
│    - Update user profile if new info detected           │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 4. WORKFLOW ORCHESTRATION (LangGraph)                   │
│    - Router: Select best agent path                     │
│    - Path: RAG (education) + Market (current data)      │
└──────────────┬──────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    ┌────────┐   ┌──────────┐
    │RAG Ret.│   │Market API│
    │5 docs  │   │latest    │
    │80K ch. │   │prices    │
    └──┬─────┘   └────┬─────┘
       │              │
       └──────┬───────┘
              ▼
┌─────────────────────────────────────────────────────────┐
│ 5. LLM CONTEXT INJECTION                                │
│                                                         │
│    System Prompt includes:                              │
│    - Conversation history (last 3 exchanges)            │
│    - Detected topics: diversification                   │
│    - RAG documents (5 best matches)                     │
│    - User profile (age, risk tolerance if known)        │
│    - Context: "Building on prior discussion of..."      │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 6. LLM RESPONSE GENERATION                              │
│    gpt-4o-mini with enhanced context                    │
│    → 2000-char response                                 │
│    → References knowledge base docs                     │
│    → Acknowledges conversation context                 │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 7. RESPONSE FORMATTING                                  │
│    - Add source attribution                             │
│    - Calculate confidence (0.9/1.0)                     │
│    - Markdown formatting                                │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 8. CONTEXT PERSISTENCE                                  │
│    - Add assistant response to history                  │
│    - Save updated context                               │
│    - Store in conversation store                        │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 9. RESPONSE SENT TO FRONTEND                            │
│    {                                                    │
│      "response": "Diversification is...",               │
│      "conversation_id": "abc-123",                      │
│      "sources": ["03_diversification.md"],              │
│      "thinking_process": "Context: building on...",     │
│      "conversation_summary": "User learning about..."   │
│    }                                                    │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 10. FRONTEND UPDATE                                     │
│     - Display response in chat                          │
│     - Show sources below message                        │
│     - Keep conversation_id for next message             │
│     - Update conversation history in sidebar            │
└─────────────────────────────────────────────────────────┘
```

### Portfolio Analysis Flow

```
User: "Analyze my portfolio"
    ↓
API: POST /api/portfolio/analyze
    ↓
[Market Data Aggregation]
  - Fetch current prices (yFinance)
  - Get historical data (1-year)
  - Calculate metrics
    ↓
[Portfolio Calculation]
  - Total value
  - Allocation %
  - Sector exposure
  - Risk metrics (volatility, beta)
  - Correlations
    ↓
[Visualization Data Preparation]
  - AssetAllocationChart data
  - RiskHeatmap data
  - CorrelationMatrix data
    ↓
[Response]
  {
    "total_value": $125000,
    "allocation": [
      {"name": "Stocks", "value": 75000, "percentage": "60%"},
      {"name": "Bonds", "value": 37500, "percentage": "30%"},
      {"name": "Cash", "value": 12500, "percentage": "10%"}
    ],
    "risk_metrics": [...],
    "correlation_matrix": [...]
  }
    ↓
Frontend renders visualizations
```

---

## Scalability & Performance Considerations

### Current Setup (Development)
- **Throughput**: ~100 req/sec per instance
- **Response Time**: <2s for RAG queries
- **Concurrent Users**: 50-100

### For EU Production Scale

**Horizontal Scaling:**
```
┌──────────────────────────────────────────┐
│         Load Balancer (ALB)              │
│    (Distribute across availability zones)│
└──────────────┬──────────────────────────┘
       ┌───────┴───────┬────────────┐
       ▼               ▼            ▼
   ┌────────┐     ┌────────┐  ┌────────┐
   │Backend │     │Backend │  │Backend │
   │ Pod 1  │     │ Pod 2  │  │ Pod 3+ │
   └───┬────┘     └───┬────┘  └───┬────┘
       │              │           │
       └──────────────┼───────────┘
                      │ (Read Replicas)
                      ▼
              ┌──────────────┐
              │ PostgreSQL DB│ (eu-west-1)
              │ Multi-AZ     │
              └──────────────┘
```

**Caching Strategy:**
- Redis for session/context (5 min TTL)
- Browser caching for assets (1 hour)
- CDN for static files (Cloudflare)
- Market data cache (5 min)

**Database Optimization:**
- Connection pooling (PgBouncer, 20-50 connections)
- Indexes on frequently queried fields
- Query result caching (Redis)
- Read replicas for analytics

---

## Deployment Architecture

### Docker Compose (Local Development)
```
docker-compose up
├── postgres (5432)
├── redis (6379)
├── chroma (8001)
├── backend (8000)
└── frontend (3000)
```

### ECS Cluster (Production AWS eu-west-1)
```
ALB (Application Load Balancer)
├── ECS Service: Backend
│   └── Task Definition (Fargate)
│       ├── Backend Container
│       └── CloudWatch Logs
├── ECS Service: Frontend
│   └── Task Definition (Fargate)
│       ├── Frontend Container
│       └── CloudWatch Logs
└── RDS
    ├── PostgreSQL (Primary)
    └── Read Replica
```

---

## Security Architecture

```
┌─────────────────────────────────────────────┐
│            Internet / Client                 │
└────────────────────┬────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ CloudFlare / WAF      │
          │ - DDoS protection     │
          │ - Rate limiting       │
          │ - Geo-blocking        │
          └──────────┬────────────┘
                     │ (HTTPS/TLS 1.3)
                     ▼
          ┌──────────────────────┐
          │ AWS ALB              │
          │ - SSL/TLS termination│
          │ - Health checks      │
          └──────────┬────────────┘
                     │ (Internal)
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │VPC           │    │VPC           │
    │ Backend      │    │ Backend      │
    │ (Security    │    │ (Security    │
    │  Group)      │    │  Group)      │
    └──────┬───────┘    └──────┬───────┘
           │                   │
           └─────────┬─────────┘
                     │
           ┌─────────┴──────────┐
           │  RDS PostgreSQL    │
           │  (Encryption       │
           │   at rest)         │
           └────────────────────┘

Key Security Measures:
- API authentication (JWT tokens)
- Rate limiting (100 req/min per IP)
- Input validation & sanitization
- SQL injection prevention (parameterized queries)
- XSS protection (CSP headers)
- CSRF token validation
- Secrets management (AWS Secrets Manager)
- Audit logging (all requests logged with timestamps)
```

---

## Monitoring & Observability

```
Application Metrics → Prometheus
                    ↓
                  Grafana Dashboards
                    ├── API Latency
                    ├── Error Rates
                    ├── LLM Token Usage
                    ├── RAG Query Times
                    └── Resource Usage

Application Logs → CloudWatch / ELK
                 ├── Request logs
                 ├── Error logs
                 ├── LLM calls
                 └── RAG retrievals

Alerts:
- Backend unavailable (5 min)
- Error rate > 5%
- Response time > 5s
- RAG retrieval failure
```

---

## Future Architecture Enhancements

1. **GraphQL API** - More flexible queries instead of REST
2. **Event-Driven Architecture** - Message queue (RabbitMQ/Kafka) for async processing
3. **Service Mesh** (Istio) - Better service-to-service communication
4. **OpenTelemetry** - Distributed tracing across services
5. **Multi-Region Deployment** - EU (primary) + US (backup)
6. **Advanced Caching** - Varnish/Nginx reverse proxy
7. **ML Pipeline** - Train custom models on user feedback
8. **GraphQL Subscriptions** - Real-time portfolio updates

---

**Last Updated**: April 2026 | **For**: EU Remote Developers
