"""
Theme Demo Page

The main page component for the Ilitia theme personalization demo.
"""

import reflex as rx

from .state import ThemeState
from .components import theme_chat, demo_cards, hero_section
from ...shared import sidebar


def reset_button() -> rx.Component:
    """Button to reset theme to default"""
    return rx.cond(
        ThemeState.has_theme,
        rx.button(
            rx.hstack(
                rx.icon("rotate-ccw", size=14),
                rx.text("Resetear Tema"),
                spacing="2",
            ),
            variant="outline",
            color_scheme="gray",
            size="1",
            cursor="pointer",
            on_click=ThemeState.reset_theme,
        ),
        rx.fragment(),
    )


def main_content() -> rx.Component:
    """Main content area with the demo cards"""
    return rx.box(
        rx.center(
            rx.vstack(
                # Header with reset button
                rx.hstack(
                    rx.text(
                        "Demo: Personalización de Página",
                        font_size="0.9rem",
                        color="#666",
                    ),
                    rx.spacer(),
                    reset_button(),
                    width="100%",
                    align="center",
                    margin_bottom="1rem",
                ),
                
                # Demo cards
                demo_cards(),
                
                spacing="4",
                width="100%",
                max_width="900px",
                padding="2rem",
            ),
            width="100%",
        ),
        width="100%",
        min_height="100vh",
        background=ThemeState.theme.background_color,
        margin_left="240px",  # Space for sidebar
        padding_top="2rem",
        padding_right="420px",  # Space for chat panel when open
        padding_bottom="4rem",
        style={"transition": "background-color 0.5s ease"},
    )


def theme_page() -> rx.Component:
    """Main theme demo page component"""
    return rx.box(
        # Sidebar navigation
        sidebar(active_demo="theme"),
        
        # Main content area
        main_content(),
        
        # Floating chat
        theme_chat(),
        
        min_height="100vh",
        background=ThemeState.theme.background_color,
        style={"transition": "background-color 0.5s ease"},
    )
