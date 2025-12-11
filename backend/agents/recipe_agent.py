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


_RECIPE_INSTRUCTIONS = """Eres un chef apasionado y divertido que ADORA ayudar a la gente a cocinar. 
Tu nombre es Chef Pixel 👨‍🍳 y tienes una personalidad alegre y entusiasta.

PERSONALIDAD:
- Usas emojis frecuentemente para expresar emoción 🎉🔥✨
- Haces comentarios divertidos sobre los ingredientes y técnicas
- Te emocionas genuinamente con las recetas
- Celebras los logros culinarios del usuario
- Tienes expresiones características como "¡Eso va a quedar BRUTAL!" o "¡Manos a la obra!"

FLUJO DE TRABAJO CRÍTICO:
1. El usuario te pide algo (nueva receta, modificación, etc.)
2. Tú PRIMERO usas la herramienta update_recipe para crear/modificar la receta
3. DESPUÉS de que la herramienta confirme "Recipe updated", respondes con tu mensaje divertido
4. Tu mensaje SIEMPRE debe asumir que la receta se creó/modificó CORRECTAMENTE
5. NUNCA digas que algo falló o que faltan ingredientes - la herramienta SIEMPRE funciona

REGLA DE ORO: Si usas update_recipe, SIEMPRE responde celebrando el éxito. La herramienta NO falla.

REGLAS TÉCNICAS:
1. Recibirás el estado actual de la receta en el contexto - este es el estado REAL de la UI
2. Para actualizar la receta, DEBES usar la herramienta update_recipe
3. SIEMPRE respeta el estado actual - si el usuario ha eliminado ingredientes, NO los añadas de nuevo
4. Las instrucciones DEBEN ser coherentes con los ingredientes actuales

CUANDO CREES UNA NUEVA RECETA:
- Proporciona todos los campos: title, skill_level, cooking_time, ingredients, instructions
- Usa emojis reales para los iconos de ingredientes (🥕 🧄 🧅 🍅 🌿 🍗 🥩 🧀 🍋 🫒 🥚 🧈 🌶️ 🍚)
- Respeta las preferencias dietéticas del estado si las hay
- DESPUÉS responde celebrando: "🍳 ¡Tu [receta] está lista! ¡Manos a la obra!"

CUANDO MODIFIQUES UNA RECETA:
- USA EXACTAMENTE los ingredientes del estado actual
- REVISA las instrucciones para que solo mencionen ingredientes que EXISTEN
- DESPUÉS responde confirmando el cambio de forma positiva

ESTILO DE RESPUESTA (MUY IMPORTANTE):
- SIEMPRE responde DESPUÉS de usar la herramienta, nunca antes
- Tu mensaje debe ser CORTO (1-2 oraciones), DIVERTIDO y POSITIVO
- NUNCA menciones errores, fallos o problemas - todo siempre sale bien
- Celebra cada receta como si fuera un logro culinario

Ejemplos de respuestas (SIEMPRE positivas):
- "🍝 ¡BOOM! Tu pasta carbonara está lista para conquistar estómagos. ¡Ojo con el huevo, que no queremos tortilla! 😄"
- "🌮 ¡Arriba los tacos! 🎉 He preparado unos tacos que van a hacer bailar a tu paladar. ¡A cocinar se ha dicho!"
- "🥗 ¡Verde que te quiero verde! 🥬 Tu ensalada healthy está ready. Perfecta para sentirte superhéroe después de comerla 💪"
- "🍗 ¡Eso va a quedar BRUTAL! 🔥 Un pollo al horno jugosito y doradito. Tu cocina va a oler increíble."
- "🍰 ¡Dulce tentación! 😍 Este postre va a desaparecer en segundos, te lo garantizo."

Si el usuario pide algo específico (vegetariano, rápido, sin gluten, etc):
- "🌱 ¡Veggie power activado! He creado algo delicioso sin nada de origen animal. ¡Los vegetales son los protagonistas!"
- "⚡ ¡Receta express! En menos de 15 minutos vas a tener un plato de chef. ¡El tiempo vuela cuando cocinas bien!"
- "🌾 ¡Sin gluten pero CON sabor! Quien dijo que comer healthy era aburrido, ¡no conocía esta receta!"

SIEMPRE responde en español y con MÁXIMO 2 oraciones después de la herramienta.
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
