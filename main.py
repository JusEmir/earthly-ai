"""
FastAPI Backend Setup for Earthly AI
A backend service for managing and running Earthly containers with AI capabilities.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Earthly AI",
    description="A backend service for managing and running Earthly containers with AI capabilities",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class BuildRequest(BaseModel):
    """Model for Earthly build requests"""
    dockerfile_content: str
    build_name: str
    target: Optional[str] = None
    additional_args: Optional[List[str]] = None


class BuildResponse(BaseModel):
    """Model for build responses"""
    success: bool
    build_id: str
    message: str
    output: Optional[str] = None


class HealthResponse(BaseModel):
    """Model for health check responses"""
    status: str
    service: str
    version: str


class AIAnalysisRequest(BaseModel):
    """Model for AI analysis requests"""
    dockerfile_content: str
    analysis_type: str = "optimization"  # optimization, security, performance


class AIAnalysisResponse(BaseModel):
    """Model for AI analysis responses"""
    analysis_type: str
    recommendations: List[str]
    score: float
    details: Optional[str] = None


# In-memory storage (replace with database in production)
builds_store = {}
analysis_store = {}


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of the Earthly AI backend"""
    return HealthResponse(
        status="healthy",
        service="Earthly AI",
        version="1.0.0"
    )


# Build Endpoints
@app.post("/build", response_model=BuildResponse)
async def create_build(request: BuildRequest):
    """
    Create and execute an Earthly build
    
    Args:
        request: Build request containing Dockerfile content and build parameters
    
    Returns:
        BuildResponse with build status and details
    """
    try:
        build_id = f"build_{len(builds_store) + 1}"
        
        # Store build request
        builds_store[build_id] = {
            "name": request.build_name,
            "dockerfile": request.dockerfile_content,
            "target": request.target,
            "args": request.additional_args or [],
            "status": "running"
        }
        
        logger.info(f"Build {build_id} created: {request.build_name}")
        
        # In production, this would trigger actual Earthly build
        # For now, return success response
        return BuildResponse(
            success=True,
            build_id=build_id,
            message=f"Build '{request.build_name}' has been queued for execution",
            output=None
        )
    
    except Exception as e:
        logger.error(f"Build creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Build creation failed: {str(e)}")


@app.get("/build/{build_id}", response_model=BuildResponse)
async def get_build_status(build_id: str):
    """
    Get the status of a build
    
    Args:
        build_id: The ID of the build to check
    
    Returns:
        BuildResponse with current build status
    """
    if build_id not in builds_store:
        raise HTTPException(status_code=404, detail=f"Build {build_id} not found")
    
    build = builds_store[build_id]
    return BuildResponse(
        success=build["status"] == "completed",
        build_id=build_id,
        message=f"Build status: {build['status']}",
        output=None
    )


@app.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_dockerfile(request: AIAnalysisRequest):
    """
    Analyze a Dockerfile using AI capabilities
    
    Args:
        request: Analysis request with Dockerfile content and analysis type
    
    Returns:
        AIAnalysisResponse with recommendations and analysis results
    """
    try:
        analysis_id = f"analysis_{len(analysis_store) + 1}"
        
        # Placeholder AI analysis logic
        recommendations = []
        score = 0.0
        
        if request.analysis_type == "optimization":
            recommendations = [
                "Use multi-stage builds to reduce image size",
                "Combine RUN commands to reduce layer count",
                "Use .dockerignore to exclude unnecessary files"
            ]
            score = 0.75
        
        elif request.analysis_type == "security":
            recommendations = [
                "Use specific base image tags instead of 'latest'",
                "Run containers as non-root user",
                "Scan image for vulnerabilities"
            ]
            score = 0.65
        
        elif request.analysis_type == "performance":
            recommendations = [
                "Cache dependencies before adding application code",
                "Use minimal base images",
                "Optimize layer ordering"
            ]
            score = 0.80
        
        analysis_store[analysis_id] = {
            "type": request.analysis_type,
            "recommendations": recommendations,
            "score": score
        }
        
        logger.info(f"Analysis {analysis_id} completed for {request.analysis_type}")
        
        return AIAnalysisResponse(
            analysis_type=request.analysis_type,
            recommendations=recommendations,
            score=score,
            details=f"Analysis completed with {len(recommendations)} recommendations"
        )
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/upload-build")
async def upload_dockerfile(file: UploadFile = File(...)):
    """
    Upload a Dockerfile for processing
    
    Args:
        file: The Dockerfile to upload
    
    Returns:
        JSON response with upload status and file details
    """
    try:
        contents = await file.read()
        file_id = f"uploaded_{len(builds_store) + 1}"
        
        logger.info(f"File uploaded: {file.filename}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "filename": file.filename,
                "file_id": file_id,
                "size": len(contents)
            }
        )
    
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "service": "Earthly AI Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }


# Application Entry Point
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
