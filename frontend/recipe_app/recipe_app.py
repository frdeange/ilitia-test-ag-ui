"""
Recipe App - Main Reflex Application

An interactive recipe generation app using AG-UI protocol
with Microsoft Agent Framework backend.
"""

import reflex as rx

from .state import RecipeState
from .components import sidebar, floating_chat, recipe_form


def main_content() -> rx.Component:
    """Main content area with the recipe form"""
    return rx.box(
        rx.center(
            recipe_form(),
            width="100%",
            max_width="800px",
            padding="2rem",
            padding_top="2rem",
        ),
        width="100%",
        min_height="100vh",
        background="#f5f5f5",
        margin_left="240px",  # Space for sidebar
        padding_top="2rem",  # Add space from top
        padding_right="420px",  # Space for chat panel when open
        display="flex",
        justify_content="center",
    )


def index() -> rx.Component:
    """Main page component"""
    return rx.box(
        # Sidebar navigation
        sidebar(),
        
        # Main content area
        main_content(),
        
        # Floating chat
        floating_chat(),
        
        min_height="100vh",
        background="#f5f5f5",
    )


# Custom styles
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
#chat-messages {
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

# Add the index page
app.add_page(index, title="🍳 AG-UI Recipe Demo")
