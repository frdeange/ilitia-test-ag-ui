"""
Recipe Agent using Microsoft Agent Framework
Based on AG-UI protocol for interactive recipes
"""

import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from openai import AsyncOpenAI


@dataclass
class Ingredient:
    """Represents a recipe ingredient"""
    name: str
    quantity: str
    unit: str
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit
        }


@dataclass
class Recipe:
    """Represents a recipe"""
    title: str = ""
    description: str = ""
    ingredients: list[Ingredient] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    prep_time: str = ""
    cook_time: str = ""
    servings: int = 4
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "ingredients": [i.to_dict() for i in self.ingredients],
            "instructions": self.instructions,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "servings": self.servings
        }


@dataclass
class RecipeState:
    """Shared state for the recipe agent"""
    recipe: Recipe = field(default_factory=Recipe)
    messages: list[dict] = field(default_factory=list)
    is_generating: bool = False
    
    def to_dict(self) -> dict:
        return {
            "recipe": self.recipe.to_dict(),
            "messages": self.messages,
            "is_generating": self.is_generating
        }


class RecipeAgent:
    """
    Recipe generation agent using Microsoft Agent Framework patterns
    with AG-UI protocol support
    """
    
    SYSTEM_PROMPT = """Eres un chef experto y asistente de cocina. Tu trabajo es ayudar a crear recetas deliciosas y detalladas.

Cuando el usuario pida una receta:
1. Primero, proporciona un título atractivo para la receta
2. Luego una descripción breve
3. Lista todos los ingredientes con cantidades exactas
4. Proporciona instrucciones paso a paso claras
5. Incluye tiempos de preparación y cocción

Responde siempre en español y sé entusiasta sobre la cocina.

IMPORTANTE: Cuando generes una receta, usa la herramienta 'update_recipe' para actualizar el estado con la información de la receta."""

    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "update_recipe",
                "description": "Actualiza la receta con la información proporcionada",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Título de la receta"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción breve de la receta"
                        },
                        "ingredients": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "quantity": {"type": "string"},
                                    "unit": {"type": "string"}
                                },
                                "required": ["name", "quantity", "unit"]
                            },
                            "description": "Lista de ingredientes"
                        },
                        "instructions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Pasos de la receta"
                        },
                        "prep_time": {
                            "type": "string",
                            "description": "Tiempo de preparación (ej: '15 minutos')"
                        },
                        "cook_time": {
                            "type": "string",
                            "description": "Tiempo de cocción (ej: '30 minutos')"
                        },
                        "servings": {
                            "type": "integer",
                            "description": "Número de porciones"
                        }
                    },
                    "required": ["title", "description", "ingredients", "instructions"]
                }
            }
        }
    ]

    def __init__(self, openai_client: AsyncOpenAI, model: str = "gpt-4o"):
        self.client = openai_client
        self.model = model
        self.state = RecipeState()
    
    def _handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """Handle tool calls from the LLM"""
        if tool_name == "update_recipe":
            # Update the recipe state
            self.state.recipe = Recipe(
                title=arguments.get("title", ""),
                description=arguments.get("description", ""),
                ingredients=[
                    Ingredient(
                        name=ing.get("name", ""),
                        quantity=ing.get("quantity", ""),
                        unit=ing.get("unit", "")
                    )
                    for ing in arguments.get("ingredients", [])
                ],
                instructions=arguments.get("instructions", []),
                prep_time=arguments.get("prep_time", ""),
                cook_time=arguments.get("cook_time", ""),
                servings=arguments.get("servings", 4)
            )
            return {"success": True, "message": "Receta actualizada correctamente"}
        
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def run(self, user_message: str) -> AsyncIterator[dict]:
        """
        Run the agent and yield AG-UI protocol events
        
        Events yielded:
        - RUN_STARTED
        - TEXT_MESSAGE_START
        - TEXT_MESSAGE_CONTENT (multiple)
        - TEXT_MESSAGE_END
        - TOOL_CALL_START
        - TOOL_CALL_END
        - STATE_SNAPSHOT
        - STATE_DELTA
        - RUN_FINISHED
        """
        import uuid
        
        run_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # Emit RUN_STARTED
        yield {
            "type": "RUN_STARTED",
            "runId": run_id,
            "timestamp": self._timestamp()
        }
        
        self.state.is_generating = True
        self.state.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Emit initial STATE_SNAPSHOT
        yield {
            "type": "STATE_SNAPSHOT",
            "state": self.state.to_dict(),
            "timestamp": self._timestamp()
        }
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            *self.state.messages
        ]
        
        try:
            # Call LLM with streaming
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.TOOLS,
                stream=True
            )
            
            # Emit TEXT_MESSAGE_START
            yield {
                "type": "TEXT_MESSAGE_START",
                "messageId": message_id,
                "role": "assistant",
                "timestamp": self._timestamp()
            }
            
            full_content = ""
            tool_calls_data = {}
            
            async for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                
                if delta:
                    # Handle text content
                    if delta.content:
                        full_content += delta.content
                        yield {
                            "type": "TEXT_MESSAGE_CONTENT",
                            "messageId": message_id,
                            "content": delta.content,
                            "timestamp": self._timestamp()
                        }
                    
                    # Handle tool calls
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            tc_id = tc.index
                            if tc_id not in tool_calls_data:
                                tool_calls_data[tc_id] = {
                                    "id": tc.id or str(uuid.uuid4()),
                                    "name": "",
                                    "arguments": ""
                                }
                            
                            if tc.function:
                                if tc.function.name:
                                    tool_calls_data[tc_id]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_calls_data[tc_id]["arguments"] += tc.function.arguments
            
            # Emit TEXT_MESSAGE_END
            yield {
                "type": "TEXT_MESSAGE_END",
                "messageId": message_id,
                "timestamp": self._timestamp()
            }
            
            # Process tool calls if any
            for tc_id, tc_data in tool_calls_data.items():
                tool_call_id = str(uuid.uuid4())
                
                # Emit TOOL_CALL_START
                yield {
                    "type": "TOOL_CALL_START",
                    "toolCallId": tool_call_id,
                    "toolName": tc_data["name"],
                    "timestamp": self._timestamp()
                }
                
                # Execute tool
                try:
                    arguments = json.loads(tc_data["arguments"])
                    result = self._handle_tool_call(tc_data["name"], arguments)
                    
                    # Emit STATE_DELTA after recipe update
                    if tc_data["name"] == "update_recipe":
                        yield {
                            "type": "STATE_DELTA",
                            "delta": [
                                {
                                    "op": "replace",
                                    "path": "/recipe",
                                    "value": self.state.recipe.to_dict()
                                }
                            ],
                            "timestamp": self._timestamp()
                        }
                    
                except json.JSONDecodeError:
                    result = {"error": "Invalid JSON in tool arguments"}
                
                # Emit TOOL_CALL_END
                yield {
                    "type": "TOOL_CALL_END",
                    "toolCallId": tool_call_id,
                    "result": result,
                    "timestamp": self._timestamp()
                }
            
            # Store assistant message
            if full_content:
                self.state.messages.append({
                    "role": "assistant",
                    "content": full_content
                })
        
        except Exception as e:
            yield {
                "type": "RUN_ERROR",
                "error": str(e),
                "timestamp": self._timestamp()
            }
        
        finally:
            self.state.is_generating = False
            
            # Emit final STATE_SNAPSHOT
            yield {
                "type": "STATE_SNAPSHOT",
                "state": self.state.to_dict(),
                "timestamp": self._timestamp()
            }
            
            # Emit RUN_FINISHED
            yield {
                "type": "RUN_FINISHED",
                "runId": run_id,
                "timestamp": self._timestamp()
            }
    
    def _timestamp(self) -> str:
        """Get current ISO timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def reset(self):
        """Reset the agent state"""
        self.state = RecipeState()
