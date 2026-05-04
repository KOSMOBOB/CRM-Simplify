from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.database import engine, Base
from app.routers import auth, contacts, leads, deals, tasks, activities

settings = get_settings()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        description="CRM Platform API with contact management, lead tracking, deal pipeline, and automation",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc) if settings.debug else "Unknown error"}
        )
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(contacts.router, prefix="/api/v1")
    app.include_router(leads.router, prefix="/api/v1")
    app.include_router(deals.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(activities.router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "app": settings.app_name}
    
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


app = create_application()


# Create tables on startup (for development)
@app.on_event("startup")
async def on_startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
