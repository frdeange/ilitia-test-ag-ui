"""
Reflex State for Recipe App with AG-UI Protocol Integration

This module defines the application state and handles AG-UI events
to update the UI in real-time.
"""

import os
import asyncio
from typing import Any, Optional

import reflex as rx
from pydantic import BaseModel
from dotenv import load_dotenv

from .ag_ui_client import AGUIClient, AGUIClientConfig, AGUIEventType

# Load environment variables
load_dotenv()


class Ingredient(BaseModel):
    """Ingredient model for recipes (Agent Framework schema)"""
    icon: str = "🍽️"
    name: str = ""
    amount: str = ""


class Recipe(BaseModel):
    """Recipe model (Agent Framework schema)"""
    title: str = ""
    skill_level: str = "Beginner"  # Beginner, Intermediate, Advanced
    special_preferences: list[str] = []
    cooking_time: str = "30 min"  # 5 min, 15 min, 30 min, 45 min, 60+ min
    ingredients: list[Ingredient] = []
    instructions: list[str] = []


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = "user"
    content: str = ""


class RecipeState(rx.State):
    """
    Main application state for the recipe app.
    
    Handles:
    - Chat messages
    - Recipe data from AG-UI events
    - Loading/streaming states
    - Error handling
    """
    
    # Chat state
    messages: list[ChatMessage] = []
    current_input: str = ""
    
    # Recipe state (from AG-UI STATE_SNAPSHOT/STATE_DELTA)
    recipe: Recipe = Recipe()
    
    # UI state
    is_loading: bool = False
    is_streaming: bool = False
    current_streaming_content: str = ""
    error_message: str = ""
    
    # Agent configuration
    thread_id: str = "default"
    
    @rx.var
    def has_recipe(self) -> bool:
        """Check if we have a recipe to display"""
        return bool(self.recipe.title)
    
    @rx.var
    def has_error(self) -> bool:
        """Check if there's an error to display"""
        return bool(self.error_message)
    
    @rx.var
    def message_count(self) -> int:
        """Number of messages in chat"""
        return len(self.messages)
    
    @rx.var
    def ingredient_count(self) -> int:
        """Number of ingredients in current recipe"""
        return len(self.recipe.ingredients)
    
    def set_input(self, value: str):
        """Update the current input value"""
        self.current_input = value
    
    def clear_error(self):
        """Clear the error message"""
        self.error_message = ""
    
    def handle_key_down(self, key: str):
        """Handle key down events in the input field"""
        if key == "Enter":
            return RecipeState.send_message
    
    def reset_chat(self):
        """Reset the chat and recipe state"""
        self.messages = []
        self.recipe = Recipe()
        self.current_input = ""
        self.error_message = ""
        self.current_streaming_content = ""
    
    def _get_agent_url(self) -> str:
        """Get the agent backend URL from environment"""
        return os.getenv("AGENT_URL", "http://localhost:8888/shared_state")
    
    def _parse_agent_url(self) -> tuple[str, str]:
        """Parse base URL and endpoint from AGENT_URL"""
        url = self._get_agent_url()
        # Split into base and endpoint
        if "/shared_state" in url:
            base = url.replace("/shared_state", "")
            endpoint = "/shared_state"
        elif "/chat" in url:
            base = url.replace("/chat", "")
            endpoint = "/chat"
        else:
            base = url
            endpoint = "/shared_state"
        return base, endpoint
    
    async def send_message(self):
        """
        Send a message to the recipe agent and process AG-UI events.
        
        This method:
        1. Adds the user message to the chat
        2. Connects to the agent via SSE
        3. Processes AG-UI events to update state
        4. Handles streaming text content
        5. Updates recipe from STATE_SNAPSHOT/STATE_DELTA
        """
        if not self.current_input.strip():
            return
        
        user_message = self.current_input.strip()
        self.current_input = ""
        
        # Add user message to chat
        self.messages = self.messages + [
            ChatMessage(role="user", content=user_message)
        ]
        
        # Clear any previous error
        self.error_message = ""
        self.is_loading = True
        self.is_streaming = False
        self.current_streaming_content = ""
        
        yield  # Update UI immediately
        
        try:
            # Configure AG-UI client
            base_url, endpoint = self._parse_agent_url()
            config = AGUIClientConfig(base_url=base_url, endpoint=endpoint)
            client = AGUIClient(config)
            
            # Process events from the agent
            async for event in client.run(
                message=user_message,
                thread_id=self.thread_id
            ):
                # Handle different event types
                if event.type == AGUIEventType.RUN_STARTED:
                    self.is_loading = True
                    yield
                
                elif event.type == AGUIEventType.TEXT_MESSAGE_START:
                    self.is_streaming = True
                    self.current_streaming_content = ""
                    yield
                
                elif event.type == AGUIEventType.TEXT_MESSAGE_CONTENT:
                    content = event.data.get("content", "")
                    self.current_streaming_content += content
                    yield
                
                elif event.type == AGUIEventType.TEXT_MESSAGE_END:
                    # Add completed message to chat
                    if self.current_streaming_content:
                        self.messages = self.messages + [
                            ChatMessage(
                                role="assistant",
                                content=self.current_streaming_content
                            )
                        ]
                    self.is_streaming = False
                    self.current_streaming_content = ""
                    yield
                
                elif event.type == AGUIEventType.STATE_SNAPSHOT:
                    # Update recipe from state snapshot
                    state_data = event.data.get("state", {})
                    recipe_data = state_data.get("recipe", {})
                    
                    if recipe_data.get("title"):
                        self.recipe = Recipe(
                            title=recipe_data.get("title", ""),
                            skill_level=recipe_data.get("skill_level", "Beginner"),
                            special_preferences=recipe_data.get("special_preferences", []),
                            cooking_time=recipe_data.get("cooking_time", "30 min"),
                            ingredients=[
                                Ingredient(
                                    icon=ing.get("icon", "🍽️"),
                                    name=ing.get("name", ""),
                                    amount=ing.get("amount", "")
                                )
                                for ing in recipe_data.get("ingredients", [])
                            ],
                            instructions=recipe_data.get("instructions", []),
                        )
                    yield
                
                elif event.type == AGUIEventType.STATE_DELTA:
                    # Handle incremental state updates
                    delta = event.data.get("delta", [])
                    for op in delta:
                        if op.get("path") == "/recipe":
                            recipe_data = op.get("value", {})
                            if recipe_data:
                                self.recipe = Recipe(
                                    title=recipe_data.get("title", ""),
                                    skill_level=recipe_data.get("skill_level", "Beginner"),
                                    special_preferences=recipe_data.get("special_preferences", []),
                                    cooking_time=recipe_data.get("cooking_time", "30 min"),
                                    ingredients=[
                                        Ingredient(
                                            icon=ing.get("icon", "🍽️"),
                                            name=ing.get("name", ""),
                                            amount=ing.get("amount", "")
                                        )
                                        for ing in recipe_data.get("ingredients", [])
                                    ],
                                    instructions=recipe_data.get("instructions", []),
                                )
                    yield
                
                elif event.type == AGUIEventType.TOOL_CALL_START:
                    # Could show tool call indicator in UI
                    pass
                
                elif event.type == AGUIEventType.TOOL_CALL_END:
                    # Tool call completed
                    pass
                
                elif event.type == AGUIEventType.RUN_ERROR:
                    self.error_message = event.data.get("error", "Unknown error")
                    yield
                
                elif event.type == AGUIEventType.RUN_FINISHED:
                    self.is_loading = False
                    self.is_streaming = False
                    yield
        
        except Exception as e:
            self.error_message = f"Error connecting to agent: {str(e)}"
            self.is_loading = False
            self.is_streaming = False
            yield
    
    async def reset_agent(self):
        """Reset the agent state on the backend"""
        try:
            base_url, _ = self._parse_agent_url()
            config = AGUIClientConfig(base_url=base_url)
            client = AGUIClient(config)
            
            await client.reset(self.thread_id)
            self.reset_chat()
        except Exception as e:
            self.error_message = f"Error resetting agent: {str(e)}"
