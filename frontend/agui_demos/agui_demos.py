"""
AG-UI Demos - Main Reflex Application

A collection of demos showcasing the AG-UI protocol
with Microsoft Agent Framework backend.
"""

import reflex as rx

from .demos.recipe import recipe_page, RecipeState
from .demos.theme import theme_page, ThemeState


# Custom styles shared across demos
STYLES = """
/* Message content styles */
.message-content p {
    margin: 0;
}

.message-content ul, .message-content ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.message-content code {
    background: rgba(0,0,0,0.1);
    padding: 0.1rem 0.3rem;
    border-radius: 0.25rem;
    font-size: 0.9em;
}

/* Smooth scrolling */
#chat-messages, #theme-chat-messages {
    scroll-behavior: smooth;
}

/* Loading dots animation */
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
    40% { transform: translateY(-6px); opacity: 1; }
}

.loading-dot {
    animation: bounce 1.4s infinite ease-in-out both;
}

.dot-1 { animation-delay: -0.32s; }
.dot-2 { animation-delay: -0.16s; }
.dot-3 { animation-delay: 0s; }

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-bubble {
    animation: fadeIn 0.3s ease-out;
}
"""


# Create the Reflex app
app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

# Add pages
app.add_page(recipe_page, route="/", title="🍳 AG-UI Recipe Demo")
app.add_page(theme_page, route="/theme", title="🎨 AG-UI Theme Demo - Ilitia")
