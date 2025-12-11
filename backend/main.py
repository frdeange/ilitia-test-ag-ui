"""
FastAPI Backend for AG-UI Demos with Microsoft Agent Framework

Uses Microsoft Agent Framework with AG-UI adapter for proper integration.
Provides endpoints for Recipe and Theme agents.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint
from agent_framework.openai import OpenAIChatClient

from agents.recipe_agent import recipe_agent
from agents.theme_agent import theme_agent

# Load environment variables
load_dotenv()


def get_chat_client():
    """Create OpenAI/Azure chat client based on configuration"""
    # Check for Azure OpenAI first
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    if azure_endpoint:
        from agent_framework.azure import AzureOpenAIChatClient

        return AzureOpenAIChatClient(
            endpoint=azure_endpoint,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        )

    # Default to OpenAI
    return OpenAIChatClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_id=os.getenv("OPENAI_MODEL", "gpt-4o"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🚀 Starting AG-UI Demos Backend (Microsoft Agent Framework)...")
    print("   📍 Recipe Agent: /shared_state")
    print("   📍 Theme Agent:  /theme_state")
    yield
    print("👋 Shutting down AG-UI Demos Backend...")


app = FastAPI(
    title="AG-UI Demos API",
    description="Interactive demos using Microsoft Agent Framework with AG-UI protocol",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create chat client
chat_client = get_chat_client()

# Register Recipe Agent endpoint
recipe_ag = recipe_agent(chat_client)
add_agent_framework_fastapi_endpoint(app, recipe_ag, "/shared_state")

# Register Theme Agent endpoint
theme_ag = theme_agent(chat_client)
add_agent_framework_fastapi_endpoint(app, theme_ag, "/theme_state")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agui-demos", "framework": "microsoft-agent-framework"}


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AG-UI Demos API",
        "version": "2.0.0",
        "framework": "Microsoft Agent Framework",
        "protocol": "AG-UI",
        "agents": {
            "recipe": "/shared_state - Recipe generation agent",
            "theme": "/theme_state - Theme personalization agent",
        },
        "endpoints": {
            "health": "/health - Health check",
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8888))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
    )
