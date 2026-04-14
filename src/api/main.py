"""
FastAPI backend for Finnie.
Connect the React frontend to workflow, market, and portfolio services.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Any
import logging

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.config import get_settings
from src.workflow.langgraph_workflow import run_langgraph_workflow
from src.data.market_service import get_quote
from src.data.portfolio_service import (
    get_sample_portfolio, 
    get_user_portfolio, 
    save_portfolio, 
    update_portfolio, 
    delete_holding,
    calculate_portfolio_performance,
    analyze_allocation
)
from src.api.websocket_manager import manager
from src.api.background_tasks import start_quote_fetcher, stop_quote_fetcher

app = FastAPI(
    title="Finnie API",
    version="1.0.0",
    description="REST API for chat, market quotes, and portfolio.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    response: str
    agent: str
    sources: list[str] = []
    routing_confidence: float = 0.0


class QuoteRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)


class QuoteResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    currency: str = "USD"
    error: str | None = None


class PortfolioSummary(BaseModel):
    summary: str
    total_value: float = 50000.0
    allocation: dict[str, float] = {"stocks": 60, "bonds": 30, "cash": 10}


class PortfolioHolding(BaseModel):
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float | None = None


class PortfolioRequest(BaseModel):
    holdings: list[PortfolioHolding] = []


class PortfolioResponse(BaseModel):
    holdings: list[PortfolioHolding]
    total_value: float
    allocation: dict[str, float]
    last_updated: str = "Never"


class PortfolioPerformanceResponse(BaseModel):
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    allocation_chart: dict
    performance_chart: dict


class PortfolioAllocationResponse(BaseModel):
    current_allocation: dict[str, float]
    recommended_allocation: dict[str, float]
    allocation_chart: dict
    diversification_score: float


# --- Startup/Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup."""
    await start_quote_fetcher()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on server shutdown."""
    await stop_quote_fetcher()


# --- Routes ---
@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "app": get_settings().app_name}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await run_langgraph_workflow(request.message)
        return ChatResponse(
            response=result["response"],
            agent=result["agent"],
            sources=result.get("sources", []),
            routing_confidence=result.get("routing_confidence", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market/quote/{symbol}", response_model=QuoteResponse)
async def quote(symbol: str):
    symbol = symbol.upper().strip()
    if not symbol or len(symbol) > 10:
        raise HTTPException(status_code=400, detail="Invalid symbol")
    try:
        q = get_quote(symbol)
        if q.get("error"):
            return QuoteResponse(
                symbol=q["symbol"],
                price=0,
                change=0,
                change_percent=0,
                error=q["error"],
            )
        return QuoteResponse(
            symbol=q["symbol"],
            price=float(q.get("price", 0)),
            change=float(q.get("change", 0)),
            change_percent=float(q.get("change_percent", 0)),
            currency=q.get("currency", "USD"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/summary", response_model=PortfolioSummary)
async def portfolio_summary():
    summary = get_sample_portfolio()
    return PortfolioSummary(
        summary=summary,
        total_value=50000.0,
        allocation={"stocks": 60, "bonds": 30, "cash": 10},
    )


@app.post("/api/v1/portfolio", response_model=PortfolioResponse)
async def save_portfolio(request: PortfolioRequest):
    try:
        success = save_portfolio("default", request.holdings)
        if success:
            return PortfolioResponse(
                holdings=request.holdings,
                total_value=sum(h["quantity"] * h.get("avg_cost", 0) for h in request.holdings),
                allocation=_calculate_allocation(request.holdings),
                last_updated=datetime.now().isoformat(),
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save portfolio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    try:
        portfolio_data = get_user_portfolio("default")
        return PortfolioResponse(
                holdings=portfolio_data.get("holdings", []),
                total_value=portfolio_data.get("total_value", 0),
                allocation=portfolio_data.get("allocation", {}),
                last_updated=portfolio_data.get("last_updated", "Never"),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/portfolio", response_model=PortfolioResponse)
async def update_portfolio(request: PortfolioRequest):
    try:
        success = update_portfolio("default", request.holdings)
        if success:
            return PortfolioResponse(
                holdings=request.holdings,
                total_value=sum(h["quantity"] * h.get("avg_cost", 0) for h in request.holdings),
                allocation=_calculate_allocation(request.holdings),
                last_updated=datetime.now().isoformat(),
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update portfolio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/portfolio/{symbol}", response_model=PortfolioResponse)
async def delete_holding(symbol: str):
    try:
        success = delete_holding("default", symbol)
        if success:
            return PortfolioResponse(
                holdings=[],
                total_value=0,
                allocation={},
                last_updated=datetime.now().isoformat(),
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete holding")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/performance", response_model=PortfolioPerformanceResponse)
async def portfolio_performance(user_id: str = "default"):
    try:
        portfolio_data = get_user_portfolio(user_id)
        performance = calculate_portfolio_performance(portfolio_data)
        return PortfolioPerformanceResponse(**performance)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolio/allocation", response_model=PortfolioAllocationResponse)
async def portfolio_allocation(user_id: str = "default"):
    try:
        portfolio_data = get_user_portfolio(user_id)
        allocation = analyze_allocation(portfolio_data)
        return PortfolioAllocationResponse(**allocation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- WebSocket Routes ---
@app.websocket("/api/v1/ws/market")
async def websocket_market_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time market data updates.
    
    Clients can send:
    - {"type": "subscribe", "symbols": ["AAPL", "GOOGL"]}
    - {"type": "unsubscribe", "symbols": ["AAPL"]}
    
    Server sends:
    - {"type": "market_update", "symbol": "AAPL", "data": {...}}
    - {"type": "connection", "status": "connected"}
    """
    await manager.connect(websocket)
    logger.info(f"WebSocket client connected. Active connections: {manager.get_active_connections_count()}")
    
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"WebSocket message received: {data}")
            
            if data.get("type") == "subscribe":
                symbols = data.get("symbols", [])
                logger.info(f"Subscribing to: {symbols}")
                for symbol in symbols:
                    await manager.subscribe(websocket, symbol.upper())
                logger.info(f"Subscribed symbols. Total subscriptions: {manager.get_all_subscribed_symbols()}")
                    
            elif data.get("type") == "unsubscribe":
                symbols = data.get("symbols", [])
                logger.info(f"Unsubscribing from: {symbols}")
                for symbol in symbols:
                    await manager.unsubscribe(websocket, symbol.upper())
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected")
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


def _calculate_allocation(holdings: list[PortfolioHolding]) -> dict[str, float]:
    """Calculate portfolio allocation percentages."""
    if not holdings:
        return {}
    
    total_value = sum(h["quantity"] * h.get("avg_cost", 0) for h in holdings)
    allocation = {}
    
    for holding in holdings:
        allocation[holding.symbol] = (holding.quantity * holding.avg_cost) / total_value * 100 if total_value > 0 else 0
    
    return allocation


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
