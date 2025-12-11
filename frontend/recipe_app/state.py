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


# Helper function to map skill level from English to Spanish
def _map_skill_level(skill: str) -> str:
    """Map skill level from English to Spanish"""
    mapping = {
        "beginner": "Principiante",
        "intermediate": "Intermedio", 
        "advanced": "Avanzado",
        "principiante": "Principiante",
        "intermedio": "Intermedio",
        "avanzado": "Avanzado",
    }
    return mapping.get(skill.lower(), "Intermedio") if skill else "Intermedio"


class Ingredient(BaseModel):
    """Ingredient model for recipes (Agent Framework schema)"""
    icon: str = "🍽️"
    name: str = ""
    amount: str = ""


class Recipe(BaseModel):
    """Recipe model (Agent Framework schema)"""
    title: str = ""
    skill_level: str = "Intermedio"  # Principiante, Intermedio, Avanzado
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
    chat_open: bool = False  # For floating chat
    
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
    
    def set_title(self, value: str):
        """Update recipe title"""
        self.recipe = Recipe(
            title=value,
            skill_level=self.recipe.skill_level,
            special_preferences=self.recipe.special_preferences,
            cooking_time=self.recipe.cooking_time,
            ingredients=self.recipe.ingredients,
            instructions=self.recipe.instructions,
        )
    
    def clear_error(self):
        """Clear the error message"""
        self.error_message = ""
    
    def toggle_chat(self):
        """Toggle the floating chat panel open/closed"""
        self.chat_open = not self.chat_open
    
    def set_cooking_time(self, value: str):
        """Update cooking time"""
        self.recipe = Recipe(
            title=self.recipe.title,
            skill_level=self.recipe.skill_level,
            special_preferences=self.recipe.special_preferences,
            cooking_time=value,
            ingredients=self.recipe.ingredients,
            instructions=self.recipe.instructions,
        )
    
    def set_skill_level(self, value: str):
        """Update skill level"""
        self.recipe = Recipe(
            title=self.recipe.title,
            skill_level=value,
            special_preferences=self.recipe.special_preferences,
            cooking_time=self.recipe.cooking_time,
            ingredients=self.recipe.ingredients,
            instructions=self.recipe.instructions,
        )
    
    def preference_checked(self, preference: str) -> bool:
        """Check if a preference is selected"""
        return preference in self.recipe.special_preferences
    
    def toggle_preference(self, preference: str):
        """Toggle a dietary preference on/off"""
        current_prefs = list(self.recipe.special_preferences)
        if preference in current_prefs:
            current_prefs.remove(preference)
        else:
            current_prefs.append(preference)
        
        self.recipe = Recipe(
            title=self.recipe.title,
            skill_level=self.recipe.skill_level,
            special_preferences=current_prefs,
            cooking_time=self.recipe.cooking_time,
            ingredients=self.recipe.ingredients,
            instructions=self.recipe.instructions,
        )
    
    def add_empty_ingredient(self):
        """Add an empty ingredient slot"""
        new_ingredients = list(self.recipe.ingredients)
        new_ingredients.append(Ingredient(icon="🍽️", name="", amount=""))
        
        self.recipe = Recipe(
            title=self.recipe.title,
            skill_level=self.recipe.skill_level,
            special_preferences=self.recipe.special_preferences,
            cooking_time=self.recipe.cooking_time,
            ingredients=new_ingredients,
            instructions=self.recipe.instructions,
        )
    
    def add_empty_instruction(self):
        """Add an empty instruction step"""
        new_instructions = list(self.recipe.instructions)
        new_instructions.append("")
        
        self.recipe = Recipe(
            title=self.recipe.title,
            skill_level=self.recipe.skill_level,
            special_preferences=self.recipe.special_preferences,
            cooking_time=self.recipe.cooking_time,
            ingredients=self.recipe.ingredients,
            instructions=new_instructions,
        )
    
    def update_instruction(self, index: int, value: str):
        """Update an instruction at a specific index"""
        new_instructions = list(self.recipe.instructions)
        if 0 <= index < len(new_instructions):
            new_instructions[index] = value
            
            self.recipe = Recipe(
                title=self.recipe.title,
                skill_level=self.recipe.skill_level,
                special_preferences=self.recipe.special_preferences,
                cooking_time=self.recipe.cooking_time,
                ingredients=self.recipe.ingredients,
                instructions=new_instructions,
            )
    
    def update_ingredient_name(self, index: int, value: str):
        """Update an ingredient's name at a specific index"""
        new_ingredients = list(self.recipe.ingredients)
        if 0 <= index < len(new_ingredients):
            old_ing = new_ingredients[index]
            new_ingredients[index] = Ingredient(
                icon=old_ing.icon,
                name=value,
                amount=old_ing.amount,
            )
            
            self.recipe = Recipe(
                title=self.recipe.title,
                skill_level=self.recipe.skill_level,
                special_preferences=self.recipe.special_preferences,
                cooking_time=self.recipe.cooking_time,
                ingredients=new_ingredients,
                instructions=self.recipe.instructions,
            )
    
    def update_ingredient_amount(self, index: int, value: str):
        """Update an ingredient's amount at a specific index"""
        new_ingredients = list(self.recipe.ingredients)
        if 0 <= index < len(new_ingredients):
            old_ing = new_ingredients[index]
            new_ingredients[index] = Ingredient(
                icon=old_ing.icon,
                name=old_ing.name,
                amount=value,
            )
            
            self.recipe = Recipe(
                title=self.recipe.title,
                skill_level=self.recipe.skill_level,
                special_preferences=self.recipe.special_preferences,
                cooking_time=self.recipe.cooking_time,
                ingredients=new_ingredients,
                instructions=self.recipe.instructions,
            )

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
            
            # Prepare the current recipe state to send
            current_state = {
                "recipe": {
                    "title": self.recipe.title,
                    "skill_level": self.recipe.skill_level,
                    "special_preferences": self.recipe.special_preferences,
                    "cooking_time": self.recipe.cooking_time,
                    "ingredients": [
                        {"icon": ing.icon, "name": ing.name, "amount": ing.amount}
                        for ing in self.recipe.ingredients
                    ],
                    "instructions": list(self.recipe.instructions),
                }
            }
            
            # Process events from the agent
            async for event in client.run(
                message=user_message,
                thread_id=self.thread_id,
                state=current_state
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
                        old_title = self.recipe.title
                        new_title = recipe_data.get("title", "")
                        
                        self.recipe = Recipe(
                            title=new_title,
                            skill_level=_map_skill_level(recipe_data.get("skill_level", "Intermediate")),
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
                        
                        # Add summary message to chat
                        num_ingredients = len(recipe_data.get("ingredients", []))
                        num_instructions = len(recipe_data.get("instructions", []))
                        
                        if old_title and old_title != new_title:
                            summary = f"He actualizado la receta a **{new_title}** con {num_ingredients} ingredientes y {num_instructions} pasos."
                        elif old_title:
                            summary = f"He mejorado la receta **{new_title}**. Ahora tiene {num_ingredients} ingredientes y {num_instructions} pasos."
                        else:
                            summary = f"He creado la receta **{new_title}** con {num_ingredients} ingredientes y {num_instructions} pasos."
                        
                        self.messages = self.messages + [
                            ChatMessage(role="assistant", content=summary)
                        ]
                    yield
                
                elif event.type == AGUIEventType.STATE_DELTA:
                    # Handle incremental state updates
                    delta = event.data.get("delta", [])
                    for op in delta:
                        if op.get("path") == "/recipe":
                            recipe_data = op.get("value", {})
                            if recipe_data:
                                old_title = self.recipe.title
                                new_title = recipe_data.get("title", "")
                                
                                self.recipe = Recipe(
                                    title=new_title,
                                    skill_level=_map_skill_level(recipe_data.get("skill_level", "Intermediate")),
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
                                
                                # Add summary message to chat
                                num_ingredients = len(recipe_data.get("ingredients", []))
                                num_instructions = len(recipe_data.get("instructions", []))
                                
                                if old_title and old_title != new_title:
                                    summary = f"He actualizado la receta a **{new_title}** con {num_ingredients} ingredientes y {num_instructions} pasos."
                                elif old_title:
                                    summary = f"He mejorado la receta **{new_title}**. Ahora tiene {num_ingredients} ingredientes y {num_instructions} pasos."
                                else:
                                    summary = f"He creado la receta **{new_title}** con {num_ingredients} ingredientes y {num_instructions} pasos."
                                
                                self.messages = self.messages + [
                                    ChatMessage(role="assistant", content=summary)
                                ]
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

    async def improve_with_ai(self):
        """
        Send the current recipe state to the agent for improvement.
        
        The state is sent in the request payload, and the agent reads it
        from the context. We just send a simple message asking for improvement.
        """
        # Simple message - the agent reads the state from the request
        message = "Mejora esta receta"
        
        # If we have a recipe title, be more specific
        if self.recipe.title:
            message = f"Mejora la receta de {self.recipe.title}"
        
        # Set as current input and send
        self.current_input = message
        
        # Call send_message (which will send the state in the payload)
        async for _ in self.send_message():
            yield
