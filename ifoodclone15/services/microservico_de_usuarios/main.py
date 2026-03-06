"""
microservico_de_usuarios - Main Application
================================
Ponto de entrada do microserviço microservico_de_usuarios.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router


app = FastAPI(
    title="microservico_de_usuarios",
    description="Microserviço microservico_de_usuarios - DDD Architecture",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "microservico_de_usuarios"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "microservico_de_usuarios API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
