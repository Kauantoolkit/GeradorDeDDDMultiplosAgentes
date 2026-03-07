"""
Main entry point for the order service.
"""

import sys
from pathlib import Path

# Adiciona o diretório do serviço ao path
service_path = Path(__file__).parent
if str(service_path) not in sys.path:
    sys.path.insert(0, str(service_path))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router

app = FastAPI(
    title="Order Service",
    description="Microservice for order management",
    version="1.0.0"
)

# Serve static files (frontend)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Routes
app.include_router(router)


@app.get("/")
async def root():
    """Serve the frontend index.html"""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Order Service API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

