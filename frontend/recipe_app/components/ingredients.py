"""
Ingredients Components

Compact ingredient display components for quick reference.
"""

import reflex as rx

from ..state import RecipeState, Ingredient


def ingredient_badge(ingredient: Ingredient) -> rx.Component:
    """
    A compact badge showing a single ingredient.
    """
    return rx.badge(
        rx.hstack(
            rx.text(ingredient.icon, font_size="0.9rem"),
            rx.text(
                ingredient.amount,
                font_weight="bold",
                font_size="0.75rem",
            ),
            rx.text(
                ingredient.name,
                font_size="0.75rem",
            ),
            spacing="1",
        ),
        color_scheme="purple",
        variant="soft",
        radius="full",
        padding="0.25rem 0.75rem",
    )


def ingredients_list() -> rx.Component:
    """
    A compact horizontal list of ingredient badges.
    
    Great for showing ingredients at a glance.
    """
    return rx.cond(
        RecipeState.ingredient_count > 0,
        rx.box(
            rx.hstack(
                rx.icon("shopping-basket", size=16, color="#667eea"),
                rx.text(
                    f"{RecipeState.ingredient_count} ingredientes",
                    font_size="0.85rem",
                    font_weight="bold",
                    color="#667eea",
                ),
                spacing="1",
                align="center",
            ),
            rx.flex(
                rx.foreach(
                    RecipeState.recipe.ingredients,
                    ingredient_badge,
                ),
                flex_wrap="wrap",
                gap="0.5rem",
                margin_top="0.5rem",
            ),
            padding="1rem",
            background="white",
            border_radius="0.75rem",
            box_shadow="0 2px 10px rgba(0,0,0,0.05)",
        ),
        rx.fragment(),
    )


def ingredient_checklist() -> rx.Component:
    """
    A checklist-style ingredient display.
    
    Useful for shopping or prep tracking.
    """
    return rx.cond(
        RecipeState.ingredient_count > 0,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("clipboard-list", size=20, color="#667eea"),
                    rx.heading("Lista de Compras", size="4"),
                    spacing="2",
                    align="center",
                ),
                rx.divider(margin_y="0.5rem"),
                rx.vstack(
                    rx.foreach(
                        RecipeState.recipe.ingredients,
                        lambda ing: rx.hstack(
                            rx.checkbox(
                                size="2",
                            ),
                            rx.text(ing.icon, font_size="1rem"),
                            rx.text(
                                f"{ing.amount} {ing.name}",
                                font_size="0.9rem",
                            ),
                            spacing="2",
                            width="100%",
                            padding_y="0.25rem",
                        ),
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1rem",
        ),
        rx.fragment(),
    )


def compact_ingredient_summary() -> rx.Component:
    """
    A one-line summary of ingredients count.
    """
    return rx.cond(
        RecipeState.ingredient_count > 0,
        rx.hstack(
            rx.icon("list", size=14, color="gray"),
            rx.text(
                f"{RecipeState.ingredient_count} ingredientes necesarios",
                font_size="0.8rem",
                color="gray",
            ),
            spacing="1",
            align="center",
        ),
        rx.fragment(),
    )
