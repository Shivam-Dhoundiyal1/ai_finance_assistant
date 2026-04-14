# Finnie

**Democratizing Financial Literacy Through Intelligent Conversational AI**

Capstone project: Applied Agentic AI for SWEs — Finnie.

## Architecture

**Data flow:**  
`User Query → Workflow Router → Appropriate Agent(s) → RAG Retrieval → LLM Processing → Response Generation → User Interface`

### Components

| Component        | Role                                                                 |
|-----------------|----------------------------------------------------------------------|
| **Workflow**     | Routes the user message to one of six specialized agents.            |
| **Agents**       | Finance Q&A, Portfolio Analysis, Market Analysis, Goal Planning, News Synthesizer, Tax Education. |
| **RAG**          | Retrieves relevant chunks from a vector store (Chroma) over financial knowledge. |
| **LLM**          | Generates responses (OpenAI or Gemini) with agent-specific prompts and context. |
| **Backend**      | FastAPI REST API: `/api/v1/chat`, `/api/v1/market/quote/:symbol`, `/api/v1/portfolio/summary`. |
| **Frontend**     | React (Vite) app: Chat, Portfolio, Market, About.                    |

### Project structure

```
ai_finance_assistant/
├── src/
│   ├── api/          # FastAPI app (chat, market, portfolio endpoints)
│   ├── agents/       # Six specialized agents
│   ├── core/         # Config and settings
│   ├── data/         # Knowledge markdown + market/portfolio services
│   ├── rag/          # Ingest, retriever, knowledge base
│   ├── web_app/      # (reserved)
│   ├── utils/        # Logging, helpers
│   └── workflow/     # Router and pipeline (route → RAG → LLM)
├── frontend/         # React (Vite + TypeScript) UI
├── tests/
├── config.yaml
├── requirements.txt
├── run_api.py        # Run FastAPI backend
├── run_ingest.py     # Ingest knowledge base
└── README.md
```

## Setup

### Backend (Python)

1. **Enter the project**
   ```bash
   cd ai_finance_assistant
   ```

2. **Virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**  
   Create a `.env` in the project root:
   ```env
   OPENAI_API_KEY=sk-...
   # Optional: GEMINI_API_KEY=... and LLM_PROVIDER=gemini
   ```

5. **Ingest the knowledge base** (once)
   ```bash
   python run_ingest.py
   ```

### Frontend (React)

1. **From project root**
   ```bash
   cd frontend
   npm install
   ```

## Run (backend + frontend connected)

1. **Start the API** (from project root)
   ```bash
   python run_api.py
   ```
   API runs at **http://127.0.0.1:8000**.

2. **Start the React app** (from `frontend/`)
   ```bash
   cd frontend
   npm run dev
   ```
   App runs at **http://localhost:5173**. Vite proxies `/api` to the backend, so the UI talks to the same origin.

3. Open **http://localhost:5173** in your browser. Use **Chat**, **Portfolio**, and **Market** tabs.

## Configuration

- **config.yaml** — App name, LLM provider/model, RAG paths, market provider, routing keywords.
- **.env** — Secrets: `OPENAI_API_KEY`, `GEMINI_API_KEY`. Environment variables override `config.yaml`.

## API (for the React frontend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/chat` | Body: `{ "message": "..." }` → `{ "response", "agent", "sources" }` |
| GET | `/api/v1/market/quote/{symbol}` | Stock quote |
| GET | `/api/v1/portfolio/summary` | Sample portfolio summary |

## Testing

```bash
pip install pytest
pytest tests/ -v
```

## Disclaimer

This project is for **educational purposes only**. It does not provide financial, tax, or legal advice. Consult a qualified professional for your situation.

## License

MIT (or as required by your course).
