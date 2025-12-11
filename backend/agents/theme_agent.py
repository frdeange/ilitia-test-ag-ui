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
    hero_emoji: str = Field(default="✨", description="Main emoji displayed in the hero section (e.g., ⚽ for sports, 🎸 for rock)")
    service_emojis: list[str] = Field(default=["🧠", "💻", "👥"], description="Three emojis for the service cards (AI, Development, Consulting)")
    background_image: str = Field(default="", description="URL to a background image for the hero section (optional, from Unsplash)")


@ai_function
def update_theme(theme: Theme) -> str:
    """Update the page theme with new colors, emojis, and styling.

    Use this to change the visual appearance of the page based on user preferences.
    Always provide ALL fields including hero_emoji, service_emojis, and optionally background_image.

    Args:
        theme: The complete theme configuration with all styling details including:
               - Colors (primary, secondary, background, card, text, accent)
               - font_family and mood/description
               - hero_emoji (main emoji in hero section)
               - service_emojis (list of 3 emojis for service cards)
               - background_image (optional URL for hero background)

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
   - "Fan del Real Madrid" → Colores blanco, púrpura, dorado + ⚽🏆⚡ + imagen de estadio
   - "Rockero / Heavy Metal" → Negro, rojo sangre, fuentes bold + 🎸🤘🔥 + imagen concierto
   - "Minimalista" → Blancos, grises suaves, clean + ✨🎯💡 + sin imagen
   - "Naturaleza" → Verdes, marrones, tonos tierra + 🌿🌲🍃 + imagen de bosque
   - "Cyberpunk" → Neón, púrpura, rosa eléctrico sobre negro + 🤖💜⚡ + imagen ciudad neón
   - "Elegante / Luxury" → Negro, dorado, blanco + ✨💎👔 + imagen abstracta elegante
   - "Deportivo" → Colores vibrantes, energéticos + 💪🏃⚡ + imagen deporte
   - "Anime / Gaming" → Rosa, cian, púrpura + 🎮🌸✨ + imagen anime/gaming
   
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
   - hero_emoji: Emoji principal grande en el hero (ej: ⚽, 🎸, 🌿)
   - service_emojis: EXACTAMENTE 3 emojis para las tarjetas de servicios [IA, Desarrollo, Consultoría]
   - background_image: URL de imagen de fondo (usar Unsplash, puede estar vacío "")

4. Los colores DEBEN ser en formato hexadecimal (#RRGGBB)

5. URLs de imágenes de fondo sugeridas (de Unsplash):
   - Real Madrid/Fútbol: "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200"
   - Rock/Concierto: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200"
   - Naturaleza/Bosque: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200"
   - Cyberpunk/Ciudad: "https://images.unsplash.com/photo-1545987796-200677ee1011?w=1200"
   - Elegante/Abstracto: "https://images.unsplash.com/photo-1557683316-973673baf926?w=1200"
   - Minimalista: "" (sin imagen)
   - Gaming: "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=1200"
   - Deporte: "https://images.unsplash.com/photo-1461896836934- voices-from-the-field?w=1200"

6. Después de actualizar el tema, responde con un mensaje breve y entusiasta confirmando el cambio

7. SIEMPRE responde en español

Ejemplos de respuesta:
- "¡Hala Madrid! ⚽🏆 He aplicado los colores del Real Madrid con emojis de fútbol y un estadio de fondo."
- "🎸🤘 ¡Rock and Roll! Tema oscuro con rojo sangre, emojis rockeros y un concierto de fondo."
- "🌿 Naturaleza pura. Tonos verdes, emojis naturales y un hermoso bosque de fondo."

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
