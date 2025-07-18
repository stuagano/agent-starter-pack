import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes_pdf import router as pdf_router
from routes_lists import router as lists_router
from routes_calendar import router as calendar_router

# Environment variables for Cloud Run
PORT = int(os.environ.get("PORT", 8080))

app = FastAPI(
    title="Penny Assistant API", 
    version="1.0.0",
    description="Backend API for Penny Assistant - PDF processing, lists, and calendar integration"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pdf_router, prefix="/api/v1", tags=["pdf"])
app.include_router(lists_router, prefix="/api/v1", tags=["lists"])
app.include_router(calendar_router, prefix="/api/v1", tags=["calendar"])

@app.get("/healthz")
def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok", "service": "penny-assistant-backend"}

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Penny Assistant Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "pdf": "/api/v1/pdf/upload",
            "lists": "/api/v1/lists",
            "calendar": "/api/v1/calendar/events"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT) 