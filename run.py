import asyncio
import signal
import sys
import uvicorn
from typing import Any, Dict, Set
from app.main import app

class GracefulUvicorn(uvicorn.Server):
    """Uvicorn server with graceful shutdown"""
    
    def __init__(self, config: uvicorn.Config, active_connections: Set[Any]):
        super().__init__(config)
        self.active_connections = active_connections
        self._cleanup_event = asyncio.Event()

    async def shutdown(self, sockets: Set[Any] = None) -> None:
        """Cleanup tasks tied to the service's shutdown."""
        print("\nReceived shutdown signal, closing connections...")
        
        # Close all active connections
        for connection in self.active_connections:
            connection.close()
        self.active_connections.clear()
        
        await super().shutdown(sockets=sockets)

async def main():
    # Store active connections
    active_connections: Set[Any] = set()
    
    # Configure Uvicorn and Include app (this is the aplication from import)
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
    
    # Create and run server
    server = GracefulUvicorn(config=config, active_connections=active_connections)
    
    # Handle shutdown signals
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda s, f: asyncio.create_task(server.shutdown()))
    
    try:
        await server.serve()
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the server
    asyncio.run(main()) 