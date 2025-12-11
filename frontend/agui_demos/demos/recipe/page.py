"""
Recipe Demo Page

The main page component for the recipe generation demo.
"""

import reflex as rx

from .state import RecipeState
from .components import recipe_form, floating_chat
from ...shared import sidebar


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
