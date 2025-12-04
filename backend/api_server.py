"""FastAPI backend server for real-time market data streaming."""

import os
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set

from backend.store import MarketStore
from backend.stream_worker import start_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Real-Time Market Streamer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global market store and worker
store: MarketStore = None
worker_thread = None
active_connections: Set[WebSocket] = set()


@app.on_event("startup")
async def startup_event():
    """Initialize market data store and worker on startup."""
    global store, worker_thread

    # Check if mock mode is requested
    use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() in ('true', '1', 'yes')

    logger.info(f"Starting market data worker (mock_mode={use_mock})")
    store = MarketStore(max_metrics=1000, max_trades=50)
    worker_thread = start_worker(store, symbol="btcusdt", use_mock=use_mock)
    logger.info("Market data worker started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down market data worker")
    # Close all active WebSocket connections
    for connection in list(active_connections):
        await connection.close()
    active_connections.clear()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Real-Time Market Streamer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/snapshot")
async def get_snapshot():
    """Get current market data snapshot."""
    if store is None:
        return {"error": "Store not initialized"}

    snapshot = store.snapshot()
    return snapshot


@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming real-time market data."""
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"WebSocket client connected. Total connections: {len(active_connections)}")

    try:
        # Send initial snapshot
        snapshot = store.snapshot()
        await websocket.send_json(snapshot)

        # Stream updates every 500ms
        while True:
            await asyncio.sleep(0.5)

            # Get latest snapshot
            snapshot = store.snapshot()

            # Send to client
            await websocket.send_json(snapshot)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
