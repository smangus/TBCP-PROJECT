from fastapi import FastAPI, Request, HTTPException
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import your existing TBCP modules
# from your_module import your_functionality

app = FastAPI(
    title="Tech Bio C-Suite Copilot API",
    description="Comprehensive API for tech leader bio generation"
)

# Configure CORS for App Engine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "TBCP API is operational",
        "status": "ready"
    }

# Health check endpoint for App Engine
@app.get("/_ah/health")
async def health_check():
    return {"status": "healthy"}

# Example endpoint - replace with your actual bio generation logic
@app.get("/generate-bio")
async def generate_tech_bio(name: str = None):
    # TODO: Replace with actual bio generation from your TBCP project
    if not name:
        return {"error": "Name is required"}
    
    # Placeholder - integrate your actual bio generation logic
    return {
        "name": name,
        "bio": "Tech leader bio generation in progress"
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"An unexpected error occurred: {str(exc)}"}
    )

# Configure App Engine setup with both Uvicorn and Gunicorn compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Development server
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
else:
    # Production via Gunicorn
    # App Engine will look for 'app' variable
    pass
