"""
Recipe Form Component

Interactive form for creating and editing recipes.
Supports bidirectional sync with the AI agent.
"""

import reflex as rx

from ..state import RecipeState, Ingredient


# Available options - Spanish labels
COOKING_TIMES = ["5 min", "15 min", "30 min", "45 min", "60+ min"]
SKILL_LEVELS = ["Principiante", "Intermedio", "Avanzado"]
DIETARY_PREFERENCES = [
    "Alta Proteína",
    "Bajo en Carbohidratos",
    "Picante",
    "Económico",
    "Un Solo Plato",
    "Vegetariano",
    "Vegano",
]


def time_selector() -> rx.Component:
    """Dropdown for cooking time selection"""
    return rx.hstack(
        rx.icon("clock", size=16, color="#666"),
        rx.select(
            COOKING_TIMES,
            value=RecipeState.recipe.cooking_time,
            on_change=RecipeState.set_cooking_time,
            size="2",
        ),
        spacing="2",
        align="center",
    )


def skill_selector() -> rx.Component:
    """Dropdown for skill level selection"""
    return rx.hstack(
        rx.icon("chef-hat", size=16, color="#666"),
        rx.select(
            SKILL_LEVELS,
            value=RecipeState.recipe.skill_level,
            on_change=RecipeState.set_skill_level,
            size="2",
        ),
        spacing="2",
        align="center",
    )


def dietary_preferences() -> rx.Component:
    """Section for dietary preferences"""
    return rx.box(
        rx.text(
            "Preferencias Dietéticas",
            font_weight="600",
            font_size="0.9rem",
            color="#333",
            margin_bottom="0.5rem",
        ),
        rx.hstack(
            rx.checkbox(
                "Alta Proteína",
                checked=RecipeState.recipe.special_preferences.contains("Alta Proteína"),
                on_change=RecipeState.toggle_preference("Alta Proteína"),
                size="2",
            ),
            rx.checkbox(
                "Bajo en Carbohidratos",
                checked=RecipeState.recipe.special_preferences.contains("Bajo en Carbohidratos"),
                on_change=RecipeState.toggle_preference("Bajo en Carbohidratos"),
                size="2",
            ),
            rx.checkbox(
                "Picante",
                checked=RecipeState.recipe.special_preferences.contains("Picante"),
                on_change=RecipeState.toggle_preference("Picante"),
                size="2",
            ),
            rx.checkbox(
                "Económico",
                checked=RecipeState.recipe.special_preferences.contains("Económico"),
                on_change=RecipeState.toggle_preference("Económico"),
                size="2",
            ),
            rx.checkbox(
                "Un Solo Plato",
                checked=RecipeState.recipe.special_preferences.contains("Un Solo Plato"),
                on_change=RecipeState.toggle_preference("Un Solo Plato"),
                size="2",
            ),
            rx.checkbox(
                "Vegetariano",
                checked=RecipeState.recipe.special_preferences.contains("Vegetariano"),
                on_change=RecipeState.toggle_preference("Vegetariano"),
                size="2",
            ),
            rx.checkbox(
                "Vegano",
                checked=RecipeState.recipe.special_preferences.contains("Vegano"),
                on_change=RecipeState.toggle_preference("Vegano"),
                size="2",
            ),
            spacing="4",
            flex_wrap="wrap",
        ),
        width="100%",
    )


def ingredient_card(ingredient: Ingredient, index: int) -> rx.Component:
    """A single ingredient card - editable"""
    return rx.box(
        rx.hstack(
            rx.text(ingredient.icon, font_size="1.5rem"),
            rx.vstack(
                rx.input(
                    value=ingredient.name,
                    on_change=lambda v: RecipeState.update_ingredient_name(index, v),
                    placeholder="Nombre del ingrediente",
                    variant="soft",
                    size="1",
                    width="100%",
                    class_name="ingredient-name-input",
                ),
                rx.input(
                    value=ingredient.amount,
                    on_change=lambda v: RecipeState.update_ingredient_amount(index, v),
                    placeholder="Cantidad",
                    variant="soft",
                    size="1",
                    width="100%",
                    class_name="ingredient-amount-input",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        padding="0.75rem",
        background="#f9f9f9",
        border_radius="0.5rem",
        border="1px solid #eee",
        min_width="180px",
        max_width="200px",
        class_name="ingredient-card",
    )


def ingredients_section() -> rx.Component:
    """Section for ingredients"""
    return rx.box(
        rx.hstack(
            rx.text(
                "Ingredientes",
                font_weight="600",
                font_size="0.9rem",
                color="#333",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=14),
                "Añadir Ingrediente",
                variant="outline",
                color_scheme="orange",
                size="1",
                cursor="pointer",
                on_click=RecipeState.add_empty_ingredient,
            ),
            width="100%",
            align="center",
            margin_bottom="0.75rem",
        ),
        rx.flex(
            rx.foreach(
                RecipeState.recipe.ingredients,
                lambda ing, idx: ingredient_card(ing, idx),
            ),
            gap="0.75rem",
            flex_wrap="wrap",
        ),
        width="100%",
    )


def instruction_step(instruction: str, index: int) -> rx.Component:
    """A single instruction step - editable"""
    return rx.hstack(
        rx.box(
            rx.text(
                index + 1,
                font_weight="bold",
                color="white",
                font_size="0.75rem",
            ),
            background="linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
            border_radius="50%",
            width="24px",
            height="24px",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.text_area(
            value=instruction,
            on_change=lambda val: RecipeState.update_instruction(index, val),
            width="100%",
            min_height="60px",
            resize="vertical",
            font_size="0.85rem",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def instructions_section() -> rx.Component:
    """Section for cooking instructions"""
    return rx.box(
        rx.hstack(
            rx.text(
                "Instrucciones",
                font_weight="600",
                font_size="0.9rem",
                color="#333",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=14),
                "Añadir Paso",
                variant="outline",
                color_scheme="orange",
                size="1",
                cursor="pointer",
                on_click=RecipeState.add_empty_instruction,
            ),
            width="100%",
            align="center",
            margin_bottom="0.75rem",
        ),
        rx.vstack(
            rx.foreach(
                RecipeState.recipe.instructions,
                lambda inst, idx: instruction_step(inst, idx),
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def improve_button() -> rx.Component:
    """Button to improve recipe with AI"""
    return rx.center(
        rx.button(
            rx.cond(
                RecipeState.is_loading,
                rx.hstack(
                    rx.spinner(size="1", color="white"),
                    rx.text("Mejorando..."),
                    spacing="2",
                ),
                rx.hstack(
                    rx.icon("sparkles", size=18),
                    rx.text("Mejorar con IA"),
                    spacing="2",
                ),
            ),
            size="3",
            background="linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
            color="white",
            cursor="pointer",
            disabled=RecipeState.is_loading,
            on_click=RecipeState.improve_with_ai,
            _hover={"opacity": "0.9"},
            padding_x="2rem",
        ),
        width="100%",
        margin_top="1.5rem",
    )


def recipe_form() -> rx.Component:
    """
    Main recipe form component.
    
    Interactive form that syncs with the AI agent.
    """
    return rx.box(
        rx.vstack(
            # Title - editable
            rx.input(
                value=RecipeState.recipe.title,
                on_change=RecipeState.set_title,
                placeholder="Crea tu Receta",
                font_size="1.5rem",
                font_weight="bold",
                variant="soft",
                width="100%",
                size="3",
            ),
            
            # Time and skill selectors
            rx.hstack(
                time_selector(),
                skill_selector(),
                spacing="4",
                margin_y="0.75rem",
            ),
            
            rx.divider(margin_y="0.5rem"),
            
            # Dietary preferences
            dietary_preferences(),
            
            rx.divider(margin_y="0.75rem"),
            
            # Ingredients
            ingredients_section(),
            
            rx.divider(margin_y="0.75rem"),
            
            # Instructions
            instructions_section(),
            
            # Improve button
            improve_button(),
            
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="1.5rem",
        background="white",
        border_radius="1rem",
        box_shadow="0 4px 20px rgba(0,0,0,0.08)",
        width="100%",
        max_width="700px",
    )
