"""
Recipe Card Component

A beautiful card displaying the generated recipe with all details.
"""

import reflex as rx

from ..state import RecipeState


def time_badge(label: str, time: str) -> rx.Component:
    """A badge showing cooking time"""
    return rx.hstack(
        rx.icon("clock", size=16, color="orange"),
        rx.text(label, font_weight="bold", font_size="0.8rem"),
        rx.text(time, font_size="0.8rem", color="gray"),
        spacing="1",
        align="center",
    )


def skill_badge(skill_level: str) -> rx.Component:
    """A badge showing skill level"""
    return rx.hstack(
        rx.icon("chef-hat", size=16, color="purple"),
        rx.text(skill_level, font_size="0.8rem", color="gray"),
        spacing="1",
        align="center",
    )


def preference_badge(preference: str) -> rx.Component:
    """A badge for dietary preferences"""
    return rx.badge(
        preference,
        color_scheme="green",
        variant="soft",
        radius="full",
    )


def instruction_item(instruction: str, index: int) -> rx.Component:
    """A single instruction step"""
    return rx.hstack(
        rx.box(
            rx.text(f"{index + 1}", font_weight="bold", color="white", font_size="0.8rem"),
            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            border_radius="50%",
            width="28px",
            height="28px",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.text(instruction, font_size="0.95rem", line_height="1.6"),
        spacing="3",
        align="start",
        width="100%",
    )


def recipe_card() -> rx.Component:
    """
    Main recipe card component.
    
    Displays the full recipe with:
    - Title and description
    - Time and servings badges
    - Ingredients list
    - Step-by-step instructions
    """
    return rx.cond(
        RecipeState.has_recipe,
        rx.card(
            rx.vstack(
                # Header with title
                rx.box(
                    rx.heading(
                        RecipeState.recipe.title,
                        size="6",
                        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        background_clip="text",
                        style={"-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"},
                    ),
                    width="100%",
                ),
                
                # Time, skill level and preferences badges
                rx.hstack(
                    time_badge("Tiempo:", RecipeState.recipe.cooking_time),
                    skill_badge(RecipeState.recipe.skill_level),
                    spacing="4",
                    flex_wrap="wrap",
                    margin_y="0.5rem",
                ),
                
                # Special preferences
                rx.cond(
                    RecipeState.recipe.special_preferences.length() > 0,
                    rx.flex(
                        rx.foreach(
                            RecipeState.recipe.special_preferences,
                            preference_badge,
                        ),
                        gap="0.5rem",
                        flex_wrap="wrap",
                        margin_bottom="0.5rem",
                    ),
                    rx.fragment(),
                ),
                
                rx.divider(margin_y="0.5rem"),
                
                # Ingredients section
                rx.box(
                    rx.hstack(
                        rx.icon("shopping-basket", size=20, color="#667eea"),
                        rx.heading("Ingredientes", size="4"),
                        spacing="2",
                        align="center",
                    ),
                    rx.box(
                        rx.foreach(
                            RecipeState.recipe.ingredients,
                            lambda ing: rx.hstack(
                                rx.text(ing.icon, font_size="1.2rem"),
                                rx.text(
                                    ing.amount,
                                    font_weight="bold",
                                    display="inline",
                                ),
                                rx.text(ing.name, display="inline"),
                                spacing="2",
                                padding_y="0.3rem",
                            ),
                        ),
                        margin_top="0.75rem",
                    ),
                    width="100%",
                ),
                
                rx.divider(margin_y="0.5rem"),
                
                # Instructions section
                rx.box(
                    rx.hstack(
                        rx.icon("chef-hat", size=20, color="#667eea"),
                        rx.heading("Instrucciones", size="4"),
                        spacing="2",
                        align="center",
                    ),
                    rx.vstack(
                        rx.foreach(
                            RecipeState.recipe.instructions,
                            lambda inst, idx: instruction_item(inst, idx),
                        ),
                        spacing="3",
                        margin_top="0.75rem",
                        align="start",
                        width="100%",
                    ),
                    width="100%",
                ),
                
                spacing="4",
                align="start",
                width="100%",
            ),
            padding="1.5rem",
            border_radius="1rem",
            box_shadow="0 10px 40px rgba(0,0,0,0.1)",
            background="white",
            width="100%",
        ),
        # Empty state when no recipe
        rx.center(
            rx.vstack(
                rx.icon("book-open", size=64, color="#e0e0e0"),
                rx.text(
                    "Pide una receta para comenzar",
                    color="gray",
                    font_size="1.1rem",
                ),
                rx.text(
                    'Prueba: "Haz una receta de paella valenciana"',
                    color="#a0a0a0",
                    font_size="0.9rem",
                    font_style="italic",
                ),
                spacing="3",
                align="center",
            ),
            padding="3rem",
            border="2px dashed #e0e0e0",
            border_radius="1rem",
            width="100%",
            min_height="300px",
        ),
    )
