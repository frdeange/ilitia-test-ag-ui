"""
Chat Interface Components

Chat UI for interacting with the recipe agent.
"""

import reflex as rx

from ..state import RecipeState, ChatMessage


def message_bubble(message: ChatMessage) -> rx.Component:
    """
    A single message bubble in the chat.
    
    User messages are aligned right with a blue background.
    Assistant messages are aligned left with a gray background.
    """
    is_user = message.role == "user"
    
    return rx.box(
        rx.box(
            rx.markdown(
                message.content,
                class_name="message-content",
            ),
            background=rx.cond(
                message.role == "user",
                "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "#f5f5f5"
            ),
            color=rx.cond(message.role == "user", "white", "black"),
            padding="0.75rem 1rem",
            border_radius="1rem",
            border_bottom_right_radius=rx.cond(message.role == "user", "0.25rem", "1rem"),
            border_bottom_left_radius=rx.cond(message.role == "user", "1rem", "0.25rem"),
            max_width="85%",
            box_shadow="0 2px 8px rgba(0,0,0,0.08)",
        ),
        display="flex",
        justify_content=rx.cond(message.role == "user", "flex-end", "flex-start"),
        width="100%",
        padding_y="0.25rem",
    )


def streaming_indicator() -> rx.Component:
    """Show streaming content while the agent is responding"""
    return rx.cond(
        RecipeState.is_streaming,
        rx.box(
            rx.box(
                rx.cond(
                    RecipeState.current_streaming_content != "",
                    rx.markdown(RecipeState.current_streaming_content),
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text("Pensando...", color="gray", font_size="0.9rem"),
                        spacing="2",
                    ),
                ),
                background="#f5f5f5",
                padding="0.75rem 1rem",
                border_radius="1rem",
                border_bottom_left_radius="0.25rem",
                max_width="85%",
                box_shadow="0 2px 8px rgba(0,0,0,0.08)",
            ),
            display="flex",
            justify_content="flex-start",
            width="100%",
            padding_y="0.25rem",
        ),
        rx.fragment(),
    )


def loading_indicator() -> rx.Component:
    """Show loading indicator when waiting for agent"""
    return rx.cond(
        RecipeState.is_loading & ~RecipeState.is_streaming,
        rx.center(
            rx.hstack(
                rx.spinner(size="2"),
                rx.text("Conectando con el chef...", color="gray"),
                spacing="2",
            ),
            padding="1rem",
        ),
        rx.fragment(),
    )


def error_alert() -> rx.Component:
    """Show error message if there's an error"""
    return rx.cond(
        RecipeState.has_error,
        rx.callout(
            RecipeState.error_message,
            icon="triangle-alert",
            color="red",
            margin_bottom="1rem",
        ),
        rx.fragment(),
    )


def chat_input() -> rx.Component:
    """Chat input field with send button"""
    return rx.hstack(
        rx.input(
            value=RecipeState.current_input,
            on_change=RecipeState.set_input,
            placeholder="Pide una receta... (ej: paella, tacos, lasaña)",
            width="100%",
            size="3",
            radius="full",
            on_key_down=RecipeState.handle_key_down,
        ),
        rx.button(
            rx.icon("send", size=20),
            on_click=RecipeState.send_message,
            disabled=RecipeState.is_loading,
            size="3",
            radius="full",
            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            cursor="pointer",
            _hover={"opacity": "0.9"},
        ),
        spacing="2",
        width="100%",
    )


def empty_chat_state() -> rx.Component:
    """Show when chat is empty"""
    return rx.center(
        rx.vstack(
            rx.icon("message-circle", size=48, color="#e0e0e0"),
            rx.text(
                "¡Hola! Soy tu asistente de cocina.",
                font_weight="bold",
                color="gray",
            ),
            rx.text(
                "Cuéntame qué te gustaría cocinar hoy.",
                color="#a0a0a0",
                font_size="0.9rem",
            ),
            spacing="2",
            align="center",
        ),
        padding="2rem",
        flex="1",
    )


def chat_interface() -> rx.Component:
    """
    Complete chat interface component.
    
    Includes:
    - Message history
    - Streaming indicator
    - Loading indicator
    - Error display
    - Input field
    """
    return rx.vstack(
        # Error alert at top
        error_alert(),
        
        # Chat messages area
        rx.box(
            rx.cond(
                RecipeState.message_count > 0,
                rx.vstack(
                    rx.foreach(RecipeState.messages, message_bubble),
                    streaming_indicator(),
                    loading_indicator(),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                empty_chat_state(),
            ),
            flex="1",
            overflow_y="auto",
            width="100%",
            padding="1rem",
            id="chat-messages",
        ),
        
        # Input area at bottom
        rx.box(
            chat_input(),
            width="100%",
            padding="1rem",
            border_top="1px solid #e0e0e0",
            background="white",
        ),
        
        spacing="0",
        width="100%",
        height="100%",
        background="white",
        border_radius="1rem",
        box_shadow="0 4px 20px rgba(0,0,0,0.08)",
        overflow="hidden",
    )
