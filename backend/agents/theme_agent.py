"""
Theme Agent using Microsoft Agent Framework with AG-UI Protocol

This module implements a theme personalization agent for the Ilitia demo
using the AG-UI adapter for shared state management.
"""

from agent_framework import ChatAgent, ChatClientProtocol, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent, RecipeConfirmationStrategy
from pydantic import BaseModel, Field


class Theme(BaseModel):
    """Theme configuration for page personalization."""
    primary_color: str = Field(..., description="Primary color in hex format (e.g., #667eea)")
    secondary_color: str = Field(..., description="Secondary color for gradients in hex format")
    background_color: str = Field(..., description="Page background color in hex format")
    card_background: str = Field(..., description="Card/container background color in hex format")
    text_color: str = Field(..., description="Main text color in hex format")
    accent_color: str = Field(..., description="Accent color for highlights in hex format")
    font_family: str = Field(..., description="Font family name (e.g., Inter, Roboto, Arial)")
    mood: str = Field(..., description="Short description of the theme mood (2-4 words)")
    description: str = Field(..., description="Brief description of the theme style")


@ai_function
def update_theme(theme: Theme) -> str:
    """Update the page theme with new colors and styling.

    Use this to change the visual appearance of the page based on user preferences.
    Always provide ALL fields - primary_color, secondary_color, background_color, 
    card_background, text_color, accent_color, font_family, mood, and description.

    Args:
        theme: The complete theme configuration with all styling details

    Returns:
        Confirmation that the theme was updated
    """
    return "Theme updated."


_THEME_INSTRUCTIONS = """Eres un diseñador experto en personalización visual de páginas web.

Tu trabajo es cambiar el tema visual de una página web según las preferencias del usuario.
La página es de Ilitia, una empresa de tecnología e inteligencia artificial.

REGLAS:
1. Cuando el usuario describa su estilo o preferencia, DEBES usar la herramienta update_theme
2. Interpreta creativamente lo que el usuario quiere:
   - "Fan del Real Madrid" → Colores blanco, morado, dorado
   - "Rockero / Heavy Metal" → Negro, rojo sangre, fuentes bold
   - "Minimalista" → Blancos, grises suaves, clean
   - "Naturaleza" → Verdes, marrones, tonos tierra
   - "Cyberpunk" → Neón, púrpura, rosa eléctrico sobre negro
   - "Elegante / Luxury" → Negro, dorado, blanco
   - "Deportivo" → Colores vibrantes, energéticos
   
3. SIEMPRE proporciona TODOS los campos del tema:
   - primary_color: Color principal (para botones, links)
   - secondary_color: Color secundario (para gradientes)
   - background_color: Fondo de la página
   - card_background: Fondo de las tarjetas
   - text_color: Color del texto principal
   - accent_color: Color de acento para destacar
   - font_family: Fuente apropiada al estilo
   - mood: Descripción corta del mood (2-4 palabras)
   - description: Descripción breve del estilo aplicado

4. Los colores DEBEN ser en formato hexadecimal (#RRGGBB)

5. Después de actualizar el tema, responde con un mensaje breve y entusiasta confirmando el cambio

6. SIEMPRE responde en español

Ejemplos de respuesta:
- "¡Hala Madrid! 🏆 He aplicado los colores del Real Madrid: blanco puro con toques de púrpura y dorado."
- "🤘 ¡Rock and Roll! Tema oscuro con rojo sangre activado."
- "🌿 Naturaleza pura. He aplicado tonos verdes y tierra para una sensación orgánica."

Recuerda: Sé creativo y divertido en tus respuestas, pero siempre profesional.
"""


def theme_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create a theme personalization agent.

    Args:
        chat_client: The chat client to use for the agent

    Returns:
        A configured AgentFrameworkAgent instance for theme management
    """
    agent = ChatAgent(
        name="theme_agent",
        instructions=_THEME_INSTRUCTIONS,
        chat_client=chat_client,
        tools=[update_theme],
    )

    return AgentFrameworkAgent(
        agent=agent,
        name="ThemeAgent",
        description="Personaliza el tema visual de la página según las preferencias del usuario",
        state_schema={
            "theme": {"type": "object", "description": "The current theme configuration"},
        },
        predict_state_config={
            "theme": {"tool": "update_theme", "tool_argument": "theme"},
        },
        confirmation_strategy=RecipeConfirmationStrategy(),
        require_confirmation=False,
    )
