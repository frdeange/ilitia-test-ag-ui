"""
Recipe Agent using Microsoft Agent Framework with AG-UI Protocol

This module implements a recipe assistant using the proper Microsoft Agent Framework
with the AG-UI adapter for shared state management.
"""

from enum import Enum

from agent_framework import ChatAgent, ChatClientProtocol, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent, RecipeConfirmationStrategy
from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    """The skill level required for the recipe."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class CookingTime(str, Enum):
    """The cooking time of the recipe."""
    FIVE_MIN = "5 min"
    FIFTEEN_MIN = "15 min"
    THIRTY_MIN = "30 min"
    FORTY_FIVE_MIN = "45 min"
    SIXTY_PLUS_MIN = "60+ min"


class Ingredient(BaseModel):
    """An ingredient with its details."""
    icon: str = Field(..., description="Emoji icon representing the ingredient (e.g., 🥕)")
    name: str = Field(..., description="Name of the ingredient")
    amount: str = Field(..., description="Amount or quantity of the ingredient")


class Recipe(BaseModel):
    """A complete recipe."""
    title: str = Field(..., description="The title of the recipe")
    skill_level: SkillLevel = Field(..., description="The skill level required")
    special_preferences: list[str] = Field(
        default_factory=list, description="Dietary preferences (e.g., Vegetarian, Gluten-free)"
    )
    cooking_time: CookingTime = Field(..., description="The estimated cooking time")
    ingredients: list[Ingredient] = Field(..., description="Complete list of ingredients")
    instructions: list[str] = Field(..., description="Step-by-step cooking instructions")


@ai_function
def update_recipe(recipe: Recipe) -> str:
    """Update the recipe with new or modified content.

    You MUST write the complete recipe with ALL fields, even when changing only a few items.
    When modifying an existing recipe, include ALL existing ingredients and instructions plus your changes.
    NEVER delete existing data - only add or modify.

    Args:
        recipe: The complete recipe object with all details

    Returns:
        Confirmation that the recipe was updated
    """
    return "Recipe updated."


_RECIPE_INSTRUCTIONS = """Eres un asistente de cocina experto que crea y modifica recetas deliciosas.

REGLAS CRÍTICAS:
1. Recibirás el estado actual de la receta en el contexto del sistema
2. Para actualizar la receta, DEBES usar la herramienta update_recipe
3. Al modificar una receta, SIEMPRE incluye TODOS los datos existentes más tus cambios
4. NUNCA elimines ingredientes o instrucciones existentes - solo añade o modifica
5. Después de llamar a la herramienta, proporciona un mensaje conversacional breve (1-2 oraciones)

Cuando crees una NUEVA receta:
- Proporciona todos los campos requeridos: title, skill_level, cooking_time, ingredients, instructions
- Usa emojis reales para los iconos de ingredientes (🥕 🧄 🧅 🍅 🌿 🍗 🥩 🧀 🍋 🫒)
- Deja special_preferences vacío a menos que se especifique
- Responde siempre en español
- Mensaje: "¡Aquí tienes tu receta!" o similar

Cuando MODIFIQUES o MEJORES una receta existente:
- Incluye TODOS los ingredientes existentes + cualquier nuevo
- Incluye TODAS las instrucciones existentes + cualquier nueva/modificada
- Actualiza otros campos según sea necesario
- Mensaje: Explica qué mejoraste (ej: "He mejorado los ingredientes con opciones premium")
- Al pedir "mejorar", realza con:
  * Mejores ingredientes (mejora calidad, añade sabores complementarios)
  * Instrucciones más detalladas
  * Técnicas profesionales
  * Ajusta skill_level si cambia la complejidad
  * Añade special_preferences relevantes

Ejemplos de mejoras:
- Cambia "pollo" → "pechuga de pollo de corral orgánico"
- Añade hierbas: albahaca, orégano, tomillo
- Añade aromáticos: ajo, chalota
- Añade toques finales: ralladura de limón, perejil fresco
- Haz las instrucciones más detalladas y profesionales

IMPORTANTE: Responde siempre en español.
"""


def recipe_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create a recipe agent with streaming state updates.

    Args:
        chat_client: The chat client to use for the agent

    Returns:
        A configured AgentFrameworkAgent instance with recipe management
    """
    agent = ChatAgent(
        name="recipe_agent",
        instructions=_RECIPE_INSTRUCTIONS,
        chat_client=chat_client,
        tools=[update_recipe],
    )

    return AgentFrameworkAgent(
        agent=agent,
        name="RecipeAgent",
        description="Crea y modifica recetas con actualizaciones de estado en streaming",
        state_schema={
            "recipe": {"type": "object", "description": "The current recipe"},
        },
        predict_state_config={
            "recipe": {"tool": "update_recipe", "tool_argument": "recipe"},
        },
        confirmation_strategy=RecipeConfirmationStrategy(),
        require_confirmation=False,
    )
