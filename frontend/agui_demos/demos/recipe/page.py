"""
Recipe Demo Page

The main page component for the recipe generation demo.
"""

import reflex as rx

from .state import RecipeState
from .components import recipe_form, floating_chat
from ...shared import sidebar


def reset_button() -> rx.Component:
    """Button to reset recipe to default"""
    return rx.cond(
        RecipeState.has_recipe,
        rx.button(
            rx.hstack(
                rx.icon("rotate-ccw", size=14),
                rx.text("Nueva Receta"),
                spacing="2",
            ),
            variant="outline",
            color_scheme="gray",
            size="1",
            cursor="pointer",
            on_click=RecipeState.reset_recipe,
        ),
        rx.fragment(),
    )


def main_content() -> rx.Component:
    """Main content area with the recipe form"""
    return rx.box(
        rx.center(
            rx.vstack(
                # Header with reset button
                rx.hstack(
                    rx.text(
                        "Demo: Asistente de Recetas IA",
                        font_size="0.9rem",
                        color="#666",
                    ),
                    rx.spacer(),
                    reset_button(),
                    width="100%",
                    align="center",
                    margin_bottom="0.5rem",
                ),
                
                # Recipe form
                recipe_form(),
                
                spacing="2",
                width="100%",
                max_width="800px",
                padding="2rem",
            ),
            width="100%",
        ),
        width="100%",
        min_height="100vh",
        background="#f5f5f5",
        margin_left="240px",  # Space for sidebar
        padding_top="2rem",
        padding_right="420px",  # Space for chat panel when open
        display="flex",
        justify_content="center",
    )


def recipe_page() -> rx.Component:
    """Main recipe demo page component"""
    return rx.box(
        # Sidebar navigation
        sidebar(active_demo="recipe"),
        
        # Main content area
        main_content(),
        
        # Floating chat
        floating_chat(),
        
        min_height="100vh",
        background="#f5f5f5",
    )
