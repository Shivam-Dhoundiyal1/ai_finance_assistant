# AI Finance Assistant - Multi-Agent System using LangGraph

**A production-style AI system that demonstrates intelligent multi-agent architecture for financial queries with optimized performance and clean execution paths.**

## Overview

This AI Finance Assistant showcases a sophisticated multi-agent system built with LangGraph that intelligently routes user queries to specialized agents while maintaining high performance through optimized execution paths.

The system handles four main query types:
- **General chat & greetings** (fast path)
- **Financial knowledge & concepts** (deep path with RAG)
- **Real-time market data** (optimized path)
- **Portfolio analysis** (deep path with critic validation)

## Architecture

### Multi-Agent Workflow

The system uses LLM-based semantic routing to direct queries to appropriate specialist agents:

```
User Query
    |
    v
Router (LLM-based classification)
    |
    +-- llm (general queries) --> Fast Path: Router -> LLM -> Response
    |
    +-- data_enrichment (market data) --> Optimized: Router -> Data -> LLM -> Response  
    |
    +-- rag (knowledge) --> Deep Path: Router -> RAG -> Data -> LLM -> Critic -> Response
    |
    +-- portfolio (analysis) --> Deep Path: Router -> RAG -> Data -> LLM -> Critic -> Response
```

### Components

- **Router**: LLM-powered intent classification with confidence scoring
- **RAG System**: Retrieval-augmented generation with ChromaDB and sentence-transformers
- **Data Enrichment**: Real-time market data integration via yfinance
- **Specialized Agents**: Finance Q&A, Market Analysis, Portfolio Management
- **Critic System**: Response validation with confidence thresholds
- **Lazy Loading**: Memory-optimized embedding model caching

## Key Features

### Performance Optimizations
- **83% faster** simple queries through conditional routing
- **67% faster** data queries by skipping unnecessary RAG
- **Reduced memory usage** via lazy embedding loading
- **Intelligent execution paths** based on query complexity

### Advanced Capabilities
- **Semantic routing** with confidence-based fallback
- **Conditional RAG execution** (only when needed)
- **Smart retry logic** with critic confidence thresholds
- **Execution trace visibility** for system observability
- **Memory optimization** for serverless deployment

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Workflow**: LangGraph, LangChain
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace sentence-transformers
- **Market Data**: yfinance API
- **LLM APIs**: OpenAI, Google Gemini
- **Frontend**: React + TypeScript (optional)

## Performance Metrics

| Query Type | Before | After | Improvement |
|------------|--------|-------|-------------|
| Simple greetings | 6+ seconds | ~1 second | **83% faster** |
| Data queries | 6+ seconds | ~2 seconds | **67% faster** |
| Execution steps (greetings) | 5-6 steps | 3 steps | **50% fewer** |

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key (or Gemini)

### Setup

```bash
# Clone and setup
git clone <repository>
cd ai_finance_assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Initialize knowledge base
python run_ingest.py

# Start the API server
python run_api.py
```

### API Usage

```bash
# Start the server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## API Examples

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is diversification?"}'
```

### Market Data
```bash
curl "http://localhost:8000/api/v1/market/quote/AAPL"
```

### Portfolio Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/portfolio" \
  -H "Content-Type: application/json" \
  -d '{"holdings": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}]}'
```

## Deployment Notes

### Memory Optimization
- **Lazy loading**: Embeddings model loaded once, cached globally
- **Conditional execution**: Skip heavy components for simple queries
- **Serverless ready**: Optimized for 512MB-1GB RAM environments

### Performance Features
- **Fast path routing**: Direct LLM execution for simple queries
- **Smart caching**: Vector store and embeddings cached in memory
- **Bounded execution**: Max retry limits prevent infinite loops

## Project Structure

```
ai_finance_assistant/
|
src/
|   api/                    # FastAPI endpoints
|   workflow/               # LangGraph workflow and nodes
|   data/                   # Market and portfolio services
|   rag/                    # RAG system and knowledge base
|   core/                   # Configuration and utilities
|
requirements.txt           # Python dependencies
run_api.py                # API server entry point
run_ingest.py             # Knowledge base ingestion
.env.example              # Environment configuration template
```

## Configuration

### Environment Variables (.env.example)
```bash
# Primary LLM
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Alternative LLM
GOOGLE_API_KEY=your_gemini_key_here
GOOGLE_MODEL=gemini-2.0-flash

# RAG Configuration
RAG_TOP_K=5
CHROMA_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## System Behavior

### Execution Modes
- **Fast Mode**: `Router -> LLM -> Response` (greetings, simple chat)
- **Optimized Mode**: `Router -> Data -> LLM -> Response` (market queries)
- **Deep Mode**: `Router -> RAG -> Data -> LLM -> Critic -> Response` (knowledge, portfolio)

### Response Quality
- **Critic validation** ensures response relevance and completeness
- **Confidence thresholds** prevent unnecessary retries
- **Execution traces** provide system observability

## Disclaimer

**This project is for educational purposes only and does not provide financial advice.** All financial information should be verified with professional advisors.

---

*Built with modern AI engineering practices to demonstrate production-ready multi-agent systems.*
