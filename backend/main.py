"""
FastAPI Backend for Recipe Agent with AG-UI Protocol
"""

import json
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

from agents.recipe_agent import RecipeAgent

# Load environment variables
load_dotenv()

# Store agent instances per thread/session
agents: dict[str, RecipeAgent] = {}


def get_openai_client() -> AsyncOpenAI:
    """Create OpenAI client based on configuration"""
    # Check for Azure OpenAI first
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if azure_endpoint:
        from openai import AsyncAzureOpenAI
        return AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview"
        )
    
    # Default to OpenAI
    return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_model() -> str:
    """Get the model name based on configuration"""
    azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    if azure_deployment:
        return azure_deployment
    return os.getenv("OPENAI_MODEL", "gpt-4o")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🚀 Starting Recipe Agent Backend...")
    yield
    print("👋 Shutting down Recipe Agent Backend...")
    agents.clear()


app = FastAPI(
    title="Recipe Agent API",
    description="Interactive recipe generation using AG-UI protocol",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    """Request model for running the agent"""
    thread_id: str
    run_id: str
    messages: list[dict]
    state: dict | None = None


class Message(BaseModel):
    """Simple message model"""
    content: str
    thread_id: str = "default"


async def event_stream(agent: RecipeAgent, message: str) -> AsyncIterator[str]:
    """
    Generate Server-Sent Events from agent run
    
    Format: data: {json}\n\n
    """
    async for event in agent.run(message):
        # Format as SSE
        event_data = json.dumps(event)
        yield f"data: {event_data}\n\n"


@app.post("/shared_state")
async def run_shared_state(request: RunRequest):
    """
    AG-UI compatible endpoint for shared state protocol
    
    This endpoint receives messages and streams back AG-UI events via SSE.
    """
    thread_id = request.thread_id
    
    # Get or create agent for this thread
    if thread_id not in agents:
        client = get_openai_client()
        model = get_model()
        agents[thread_id] = RecipeAgent(client, model)
    
    agent = agents[thread_id]
    
    # Restore state if provided
    if request.state:
        # Update agent state from client state
        pass  # The agent maintains its own state
    
    # Get the last user message
    user_messages = [m for m in request.messages if m.get("role") == "user"]
    if not user_messages:
        return {"error": "No user message provided"}
    
    last_message = user_messages[-1].get("content", "")
    
    # Return SSE stream
    return StreamingResponse(
        event_stream(agent, last_message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/chat")
async def chat(message: Message):
    """
    Simple chat endpoint - alternative to full AG-UI protocol
    """
    thread_id = message.thread_id
    
    if thread_id not in agents:
        client = get_openai_client()
        model = get_model()
        agents[thread_id] = RecipeAgent(client, model)
    
    agent = agents[thread_id]
    
    return StreamingResponse(
        event_stream(agent, message.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@app.post("/reset/{thread_id}")
async def reset_thread(thread_id: str):
    """Reset agent state for a thread"""
    if thread_id in agents:
        agents[thread_id].reset()
        return {"status": "ok", "message": f"Thread {thread_id} reset"}
    return {"status": "ok", "message": "Thread not found (nothing to reset)"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "recipe-agent"}


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Recipe Agent API",
        "version": "1.0.0",
        "protocol": "AG-UI",
        "endpoints": {
            "shared_state": "/shared_state - AG-UI protocol endpoint",
            "chat": "/chat - Simple chat endpoint",
            "reset": "/reset/{thread_id} - Reset agent state",
            "health": "/health - Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8888))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
