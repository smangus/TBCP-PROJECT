# app.py

import os
import time
import logging
import jwt
from typing import Dict, Any, List, Optional
import vertexai
from vertexai.preview import model_garden

vertexai.init(project="techbio-c-suite-copilot", location="us-central1")

model = model_garden.OpenModel("google/txgemma@txgemma-27b-chat")
endpoint = model.deploy(
  accept_eula=True,
  machine_type="a3-highgpu-2g",
  accelerator_type="NVIDIA_H100_80GB",
  accelerator_count=2,
  serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20250114_0916_RC00_maas",
  endpoint_display_name="google_txgemma-27b-chat-mg-one-click-deploy",
  model_display_name="google_txgemma-27b-chat-1744235813342",
)

# FastAPI and Web Frameworks
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the router workflow
from router.router_agent import create_copilot_app

# Import memory manager
from utils.memory_manager import memory_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Authentication dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create the FastAPI app
app = FastAPI(
    title="TechBio C-Suite CoPilot API", 
    description="AI-powered decision support for biotech executives using TxGemma for molecular reasoning",
    version="1.1.0"
)

# Set up CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://scriptome.ai", 
        "https://copilot.scriptome.ai", 
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the copilot application
copilot = create_copilot_app()

# Define the request models
class QueryRequest(BaseModel):
    query: str
    
class SearchRequest(BaseModel):
    query: str
    limit: int = 5

# Define the response models
class QueryResponse(BaseModel):
    response: str
    contributing_agents: List[str]
    agent_responses: Optional[Dict[str, str]] = None
    processing_time: Optional[float] = None
    user_context: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    id: str
    timestamp: str
    user_query: str
    synthesis_response: str
    selected_agents: List[str]
    
class SearchResponse(BaseModel):
    results: List[ConversationResponse]

class MemoryStatsResponse(BaseModel):
    agent_memory: Dict[str, Any]
    shared_memory: Dict[str, Any]
    conversations: Dict[str, Any]

def validate_token(token: str):
    """
    Token validation with comprehensive error handling
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            os.getenv('JWT_SECRET', 'default_secret_key_please_replace'), 
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid token provided")
        raise HTTPException(status_code=403, detail="Could not validate credentials")

# Create the API endpoint with optional authentication
@app.post("/api/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest, 
    background_tasks: BackgroundTasks,
    token: Optional[str] = Depends(oauth2_scheme)
):
    try:
        # Validate token if provided
        user_context = None
        if token:
            try:
                user_info = validate_token(token)
                user_context = {
                    "user_id": user_info.get('sub'),
                    "email": user_info.get('email'),
                    "name": user_info.get('name')
                }
            except HTTPException:
                # Log the authentication failure but don't block the query
                logger.warning("Authentication failed, proceeding without user context")
        
        # Record the start time for performance tracking
        start_time = time.time()
        
        # Prepare query with optional user context
        query_input = {
            "query": request.query,
            "user_context": user_context
        }
        
        # Process the query using the router workflow
        result = copilot(query_input)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Extract the response and agent information
        if isinstance(result, Dict):
            response = result.get("response", "")
            contributing_agents = result.get("selected_agents", [])
            agent_responses = result.get("agent_responses", {})
        else:
            response = result
            contributing_agents = ["unknown"]
            agent_responses = {}
        
        # Store conversation in memory manager (in background)
        background_tasks.add_task(
            memory_manager.record_conversation,
            user_query=request.query,
            agent_responses=agent_responses,
            synthesis_response=response,
            selected_agents=contributing_agents,
            user_context=user_context
        )
        
        # Update agent memories (in background)
        for agent_name in contributing_agents:
            if agent_name == "molecular_agent" and hasattr(agent_responses.get(agent_name, {}), "get"):
                # Extract and update molecular agent's memories if available
                agent_result = agent_responses.get(agent_name, {})
                if isinstance(agent_result, dict):
                    molecular_knowledge = agent_result.get("molecular_insights")
                    
                    if molecular_knowledge:
                        background_tasks.add_task(
                            memory_manager.update_agent_memory,
                            agent_name="molecular_agent",
                            memory_type="molecular_knowledge",
                            memory_data=molecular_knowledge
                        )
        
        # Create the response object with detailed information
        return QueryResponse(
            response=response, 
            contributing_agents=contributing_agents,
            agent_responses=agent_responses,
            processing_time=round(processing_time, 2),
            user_context=user_context
        )
    
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Add endpoint for searching similar queries
@app.post("/api/search", response_model=SearchResponse)
async def search_conversations(
    request: SearchRequest,
    token: Optional[str] = Depends(oauth2_scheme)
):
    try:
        # Validate token if provided
        user_context = None
        if token:
            try:
                user_info = validate_token(token)
                user_context = {
                    "user_id": user_info.get('sub'),
                    "email": user_info.get('email')
                }
            except HTTPException:
                logger.warning("Authentication failed during search")
        
        # Search for similar conversations
        results = memory_manager.search_conversations(
            query=request.query,
            limit=request.limit,
            user_context=user_context
        )
        
        # Format the results
        formatted_results = []
        for conv in results:
            formatted_results.append(ConversationResponse(
                id=conv["id"],
                timestamp=conv["timestamp"],
                user_query=conv["user_query"],
                synthesis_response=conv["synthesis_response"],
                selected_agents=conv["selected_agents"]
            ))
        
        return SearchResponse(results=formatted_results)
    
    except Exception as e:
        logger.error(f"Conversation search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

# Add endpoint to get memory statistics
@app.get("/api/memory/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(token: Optional[str] = Depends(oauth2_scheme)):
    try:
        # Optional token validation
        if token:
            validate_token(token)
        
        stats = memory_manager.get_memory_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Memory stats retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting memory stats: {str(e)}")

# Add endpoint to clear specific memory
@app.post("/api/memory/clear")
async def clear_memory(
    agent_name: Optional[str] = None, 
    memory_type: Optional[str] = None,
    token: Optional[str] = Depends(oauth2_scheme)
):
    try:
        # Validate token
        if token:
            user_info = validate_token(token)
        
        memory_manager.clear_memory(agent_name, memory_type)
        return JSONResponse(content={"message": "Memory cleared successfully"})
    
    except Exception as e:
        logger.error(f"Memory clearing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.1.0",
        "services": {
            "copilot": "running",
            "memory_manager": "operational"
        }
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
