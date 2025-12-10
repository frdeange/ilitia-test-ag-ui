"""
Recipe App - Main Reflex Application

An interactive recipe generation app using AG-UI protocol
with Microsoft Agent Framework backend.
"""

import reflex as rx

from .state import RecipeState
from .components import recipe_card, chat_interface, ingredients_list


def navbar() -> rx.Component:
    """Navigation bar with app title and reset button"""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("chef-hat", size=28, color="white"),
                rx.heading(
                    "Recetas Interactivas",
                    size="5",
                    color="white",
                    font_weight="bold",
                ),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.badge(
                    "AG-UI Protocol",
                    color_scheme="purple",
                    variant="soft",
                    radius="full",
                ),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Nueva Receta",
                    on_click=RecipeState.reset_agent,
                    variant="soft",
                    color_scheme="gray",
                    cursor="pointer",
                ),
                spacing="3",
                align="center",
            ),
            width="100%",
            padding_x="1.5rem",
            padding_y="1rem",
            align="center",
        ),
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        position="sticky",
        top="0",
        z_index="100",
        box_shadow="0 4px 20px rgba(0,0,0,0.15)",
    )


def main_content() -> rx.Component:
    """Main content area with chat and recipe card"""
    return rx.box(
        rx.hstack(
            # Left side: Chat interface
            rx.box(
                chat_interface(),
                width="45%",
                height="calc(100vh - 80px)",
                padding="1rem",
            ),
            
            # Right side: Recipe display
            rx.box(
                rx.vstack(
                    # Quick ingredients summary
                    ingredients_list(),
                    
                    # Full recipe card
                    recipe_card(),
                    
                    spacing="4",
                    width="100%",
                ),
                width="55%",
                height="calc(100vh - 80px)",
                padding="1rem",
                overflow_y="auto",
            ),
            
            width="100%",
            height="100%",
            spacing="0",
        ),
        width="100%",
        max_width="1600px",
        margin="0 auto",
    )


def mobile_content() -> rx.Component:
    """Mobile-friendly layout (stacked)"""
    return rx.vstack(
        # Chat at top
        rx.box(
            chat_interface(),
            width="100%",
            height="50vh",
            padding="0.5rem",
        ),
        
        # Recipe below
        rx.box(
            rx.vstack(
                ingredients_list(),
                recipe_card(),
                spacing="3",
                width="100%",
            ),
            width="100%",
            height="50vh",
            padding="0.5rem",
            overflow_y="auto",
        ),
        
        spacing="0",
        width="100%",
    )


def index() -> rx.Component:
    """Main page component"""
    return rx.box(
        navbar(),
        
        # Responsive layout
        rx.box(
            main_content(),
            display=["none", "none", "block", "block"],  # Hidden on mobile
        ),
        rx.box(
            mobile_content(),
            display=["block", "block", "none", "none"],  # Shown on mobile
        ),
        
        background="#f8f9fa",
        min_height="100vh",
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

/* Smooth scrolling for chat */
#chat-messages {
    scroll-behavior: smooth;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-bubble {
    animation: fadeIn 0.3s ease-out;
}

/* Recipe card animations */
@keyframes slideIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}

.recipe-card {
    animation: slideIn 0.4s ease-out;
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
app.add_page(index, title="🍳 Recetas Interactivas")
