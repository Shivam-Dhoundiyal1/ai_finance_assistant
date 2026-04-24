# AI Finance Assistant - Project Setup Guide

> Complete step-by-step guide to get the AI Finance Assistant running on your local machine.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [IDE Setup (VS Code)](#ide-setup-vs-code)

---

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 5GB free (for Python packages, node_modules, Chroma DB)
- **Internet**: Required for downloading dependencies and LLM API calls

### Required Software
- **Python**: 3.11+ ([Download](https://www.python.org/downloads/))
- **Node.js**: 18+ ([Download](https://nodejs.org/))
- **Git**: Latest version ([Download](https://git-scm.com/))
- **Code Editor**: VS Code recommended ([Download](https://code.visualstudio.com/))

### Verify Installations
```bash
# Check Python version
python --version  # Should show 3.11+

# Check Node.js version
node --version    # Should show v18+
npm --version     # Should show 9+

# Check Git
git --version
```

---

## Project Structure

```
ai_finance_assistant/
├── src/                          # Python backend source code
│   ├── agents/                   # Multi-agent orchestration
│   │   ├── finance_qa.py        # General finance Q&A agent
│   │   ├── market.py            # Market analysis agent
│   │   ├── portfolio.py         # Portfolio analysis agent
│   │   ├── news.py              # Financial news agent
│   │   ├── tax.py               # Tax education agent
│   │   └── goal_planning.py     # Financial goal planning agent
│   ├── workflow/                 # LangGraph workflow orchestration
│   │   ├── langgraph_workflow.py # Main state machine
│   │   ├── langgraph_nodes.py   # Workflow nodes (router, RAG, LLM, etc)
│   │   ├── intelligent_router.py # Request routing logic
│   │   └── state.py             # Workflow state definitions
│   ├── api/                      # FastAPI REST & WebSocket endpoints
│   │   ├── main.py              # FastAPI app, routes
│   │   └── websocket_manager.py # WebSocket connection handling
│   ├── rag/                      # Retrieval-Augmented Generation
│   │   ├── knowledge_base.py    # Knowledge base configuration
│   │   ├── ingest.py            # Document ingestion into Chroma
│   │   ├── retriever.py         # Vector database retrieval
│   │   └── knowledge/           # Financial education documents (50 files)
│   ├── data/                     # Data services
│   │   ├── market_service.py    # yFinance integration
│   │   ├── portfolio_service.py # Portfolio analytics
│   │   ├── knowledge/           # Knowledge base documents
│   │   └── portfolios/          # User portfolio data
│   ├── core/                     # Core configuration
│   │   └── config.py            # Settings & pydantic models
│   └── utils/                    # Utilities
│       └── logging.py           # Logging setup
├── frontend/                     # React/TypeScript frontend
│   ├── src/
│   │   ├── App.tsx              # Main React component
│   │   ├── api.ts               # Axios API client
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   └── main.tsx             # React entry point
│   ├── vite.config.ts           # Vite build configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   └── package.json             # Node.js dependencies
├── tests/                        # Test suite
│   ├── conftest.py              # pytest fixtures
│   ├── test_agents.py           # Agent tests
│   ├── test_api.py              # API endpoint tests
│   ├── test_rag.py              # RAG system tests
│   ├── test_workflow.py         # Workflow tests
│   └── test_services.py         # Data service tests
├── data/                         # Data directory
│   └── chroma/                  # Chroma vector database (created during setup)
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
├── pytest.ini                   # pytest configuration
└── .env.example                 # Environment variables template
```

---

## Backend Setup

### Step 1: Clone or Create Project Directory
```bash
# If cloning from GitHub
git clone https://github.com/yourusername/ai_finance_assistant.git
cd ai_finance_assistant

# Or create new directory if starting fresh
mkdir ai_finance_assistant
cd ai_finance_assistant
```

### Step 2: Create Python Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv financeAI

# Activate virtual environment
financeAI\Scripts\activate

# Verify activation (you should see (financeAI) prefix in terminal)
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv financeAI

# Activate virtual environment
source financeAI/bin/activate

# Verify activation (you should see (financeAI) prefix in terminal)
```

### Step 3: Install Python Dependencies

```bash
# Ensure pip is updated
python -m pip install --upgrade pip

# Install all dependencies from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|langchain|chroma|pydantic)"
```

**Key Dependencies Installed:**
- `fastapi`: Web framework for REST API
- `langchain`: LLM framework with agents
- `langgraph`: State machine for orchestration
- `pydantic`: Data validation and settings
- `chromadb`: Vector database for RAG
- `sentence-transformers`: Embedding model
- `pyyaml`: Configuration parsing
- `python-dotenv`: Environment variable loading
- `pytest`: Testing framework

### Step 4: Set Up Environment Variables

```bash
# Copy template to .env
cp .env.example .env

# Edit .env with your API keys
# On Windows: notepad .env
# On macOS/Linux: nano .env (or your preferred editor)
```

**Required API Keys:**
- `OPENAI_API_KEY`: Get from [OpenAI API](https://platform.openai.com/api-keys)
- `GOOGLE_API_KEY` (optional): Get from [Google AI Studio](https://aistudio.google.com/)

**Example .env Setup:**
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
VITE_API_URL=http://localhost:8000
```

### Step 5: Ingest Knowledge Base Documents

The knowledge base documents (50 financial education files) need to be indexed into Chroma:

```bash
# Run ingestion script
python run_ingest.py

# Expected output:
# Loading weights: 100%|██████████| 103/103 [00:00<00:00, 3000.00it/s]
# Ingested 495 chunks into the knowledge base.

# This creates data/chroma/chroma.sqlite3 with indexed documents
```

### Step 6: Verify Backend Setup

```bash
# Run pytest to check if all dependencies work
pytest tests/ -v

# Or run a quick API startup test
python -c "from src.api.main import app; print('✓ FastAPI app loads successfully')"
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Node.js Dependencies

```bash
# Install npm packages
npm install

# Verify installation
npm list | head -20
```

**Key Dependencies:**
- `react`: UI library
- `typescript`: Type safety
- `vite`: Build tool
- `tailwindcss`: CSS framework
- `axios`: HTTP client
- `recharts`: Data visualization (for charts)

### Step 3: Build Tailwind CSS (if needed)

```bash
# Tailwind should build automatically via Vite
# But you can manually build if needed:
npx tailwindcss -i ./src/index.css -o ./src/output.css
```

### Step 4: Verify Frontend Setup

```bash
# Check if Vite can build the project
npm run build

# Expected output:
# ✓ xxx modules transformed
# dist/index.html    x.xx kB
# dist/assets/...
```

---

## Running the Application

### Terminal 1: Start Backend API Server

```bash
# Make sure you're in the project root and virtual env is activated
cd c:\Users\Asus\Desktop\ai_finance_assistant  # Or your project path

# Activate virtual environment (if not already activated)
financeAI\Scripts\activate  # Windows
# source financeAI/bin/activate  # macOS/Linux

# Start FastAPI server
python run_api.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

### Terminal 2: Start Frontend Development Server

```bash
# Navigate to frontend directory
cd frontend

# Start Vite dev server
npm run dev

# Expected output:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

### Access the Application

Open your browser and visit:
- **Frontend**: `http://localhost:5173`
- **API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)

### Test the Chat Feature

1. Go to `http://localhost:5173`
2. Type a finance question: "What is a diversified portfolio?"
3. Click Send
4. Backend agents process the query:
   - Intelligent Router analyzes intent
   - RAG retriever fetches relevant knowledge documents
   - LLM generates response using context
   - Response appears in chat

---

## Testing

### Run All Tests

```bash
# Activate virtual environment first
financeAI\Scripts\activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Key Features

```bash
# Test RAG retrieval
pytest tests/test_rag.py -v

# Test agent routing
pytest tests/test_router.py -v

# Test API endpoints
pytest tests/test_api.py -v

# Test workflow orchestration
pytest tests/test_workflow.py -v
```

### Manual API Testing

```bash
# Test chat endpoint (using curl or Postman)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is dollar-cost averaging?",
    "chat_history": []
  }'

# Expected response:
# {
#   "response": "Dollar-cost averaging is an investment strategy...",
#   "sources": ["07_dca.md"],
#   "reasoning": "Retrieved relevant knowledge from documents..."
# }
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:**
```bash
# Make sure you're in the project root (ai_finance_assistant/)
# and virtual environment is activated
echo $PYTHONPATH  # Should be empty or show current directory

# Or run with PYTHONPATH set
PYTHONPATH=. python run_api.py
```

### Issue: "OPENAI_API_KEY not found"

**Solution:**
```bash
# Verify .env file exists in project root
ls -la .env  # macOS/Linux
dir .env    # Windows

# Check .env has correct format
cat .env | grep OPENAI

# Verify it's being loaded (should print your key, not None)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key loaded' if os.getenv('OPENAI_API_KEY') else 'Key not found')"
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Option 1: Kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Option 2: Change port in .env
# Set SERVER_PORT=8001 and restart
```

### Issue: "Failed to download embedding model"

**Solution:**
```bash
# Usually "all-MiniLM-L6-v2" downloads from HuggingFace Hub
# If internet is slow, pre-download manually:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Set HuggingFace offline mode in code if needed
```

### Issue: "Chroma database not found or empty"

**Solution:**
```bash
# Re-ingest knowledge base documents
python run_ingest.py

# Verify documents were ingested
python -c "from src.rag.retriever import RAGRetriever; r = RAGRetriever(); print(f'Documents in DB: {r.get_knowledge_base_stats()}')"
```

### Issue: Frontend won't connect to backend

**Solution:**
```bash
# Verify backend is running on correct port
curl http://localhost:8000  # Should return "Invalid request" or 404, not connection error

# Check CORS configuration in src/core/config.py
# CORS_ORIGINS should include http://localhost:5173

# Check .env VITE_API_URL matches backend URL
grep VITE_API_URL .env  # Should show http://localhost:8000
```

---

## IDE Setup (VS Code)

### Recommended Extensions

Install these extensions for better development experience:

1. **Python** (Microsoft) - Python language support
2. **Pylance** - Python type checking and IntelliSense
3. **FastAPI** - FastAPI snippets and documentation
4. **REST Client** - Test API endpoints directly in VS Code
5. **Thunder Client** - Postman alternative for API testing
6. **ES7+ React/Redux/React-Native snippets** - Frontend development
7. **Tailwind CSS IntelliSense** - Tailwind autocompletion
8. **Prettier** - Code formatting

### Python Interpreter Configuration

1. Open Command Palette: `Ctrl+Shift+P`
2. Search for "Python: Select Interpreter"
3. Choose `./financeAI/Scripts/python.exe` (Windows) or `./financeAI/bin/python` (macOS/Linux)

### Launch Configurations

Create `.vscode/launch.json` for debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v"
      ],
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### Git Ignore Configuration

The `.gitignore` should include:
```
financeAI/
node_modules/
dist/
.env
.env.local
__pycache__/
*.pyc
.pytest_cache/
data/chroma/
```

---

## Next Steps

1. **Test the Application**: Send chat messages and verify end-to-end workflow
2. **Review Knowledge Base**: Check `src/data/knowledge/` for available documents
3. **Explore API Documentation**: Visit `http://localhost:8000/docs`
4. **Run Tests**: Ensure all tests pass with `pytest tests/ -v`
5. **Read Code Comments**: Review agent and workflow implementations
6. **Customize**: Modify agents, add new knowledge documents, or enhance UI

---

## Common Commands Reference

```bash
# Backend
python run_api.py              # Start API server
python run_ingest.py           # Ingest knowledge base
pytest tests/ -v               # Run tests
python -m pytest tests/test_agents.py -v  # Test specific module

# Frontend
npm run dev                    # Start dev server
npm run build                  # Build for production
npm run preview                # Preview production build

# Environment
source financeAI/bin/activate  # Activate venv (macOS/Linux)
financeAI\Scripts\activate     # Activate venv (Windows)
deactivate                     # Deactivate venv
```

---

## Support & Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **React/TypeScript**: https://react-typescript-cheatsheet.netlify.app/
- **Vite**: https://vitejs.dev/
- **Tailwind CSS**: https://tailwindcss.com/

---

**Last Updated**: 2025 | **For**: Development Setup
