"""
Theme Chat Component

Floating chat for theme personalization.
"""

import reflex as rx

from ..state import ThemeState, ThemeChatMessage


def message_bubble(message: ThemeChatMessage) -> rx.Component:
    """A single message bubble in the chat"""
    return rx.box(
        rx.box(
            rx.markdown(
                message.content,
                class_name="message-content",
            ),
            background=rx.cond(
                message.role == "user",
                ThemeState.gradient_style,
                "#f5f5f5"
            ),
            color=rx.cond(message.role == "user", "white", "black"),
            padding="0.6rem 0.9rem",
            border_radius="0.75rem",
            border_bottom_right_radius=rx.cond(message.role == "user", "0.2rem", "0.75rem"),
            border_bottom_left_radius=rx.cond(message.role == "user", "0.75rem", "0.2rem"),
            max_width="90%",
            font_size="0.85rem",
            box_shadow="0 1px 4px rgba(0,0,0,0.06)",
        ),
        display="flex",
        justify_content=rx.cond(message.role == "user", "flex-end", "flex-start"),
        width="100%",
        padding_y="0.15rem",
    )


def loading_indicator() -> rx.Component:
    """Show loading dots when waiting for response"""
    return rx.cond(
        ThemeState.is_loading & ~ThemeState.is_streaming,
        rx.box(
            rx.box(
                rx.hstack(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="50%",
                        background="#888",
                        class_name="loading-dot dot-1",
                    ),
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="50%",
                        background="#888",
                        class_name="loading-dot dot-2",
                    ),
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="50%",
                        background="#888",
                        class_name="loading-dot dot-3",
                    ),
                    spacing="1",
                ),
                background="#f5f5f5",
                padding="0.8rem 1rem",
                border_radius="0.75rem",
                border_bottom_left_radius="0.2rem",
                box_shadow="0 1px 4px rgba(0,0,0,0.06)",
            ),
            display="flex",
            justify_content="flex-start",
            width="100%",
            padding_y="0.15rem",
        ),
        rx.fragment(),
    )


def streaming_indicator() -> rx.Component:
    """Show streaming content while the agent is responding"""
    return rx.cond(
        ThemeState.is_streaming,
        rx.box(
            rx.box(
                rx.cond(
                    ThemeState.current_streaming_content != "",
                    rx.markdown(
                        ThemeState.current_streaming_content,
                        font_size="0.85rem",
                    ),
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text("Pensando...", color="gray", font_size="0.8rem"),
                        spacing="2",
                    ),
                ),
                background="#f5f5f5",
                padding="0.6rem 0.9rem",
                border_radius="0.75rem",
                border_bottom_left_radius="0.2rem",
                max_width="90%",
                box_shadow="0 1px 4px rgba(0,0,0,0.06)",
            ),
            display="flex",
            justify_content="flex-start",
            width="100%",
            padding_y="0.15rem",
        ),
        rx.fragment(),
    )


def chat_input() -> rx.Component:
    """Chat input field with send button"""
    return rx.hstack(
        rx.input(
            value=ThemeState.current_input,
            on_change=ThemeState.set_input,
            placeholder="Describe tu estilo... (ej: fan del Real Madrid)",
            width="100%",
            size="2",
            radius="large",
            on_key_down=ThemeState.handle_key_down,
        ),
        rx.icon_button(
            rx.icon("arrow-up", size=16),
            on_click=ThemeState.send_message,
            disabled=ThemeState.is_loading,
            size="2",
            radius="full",
            background=ThemeState.gradient_style,
            cursor="pointer",
        ),
        spacing="2",
        width="100%",
        padding="0.75rem",
        border_top="1px solid #eee",
    )


def chat_panel() -> rx.Component:
    """The chat panel content"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.text(
                    "Personaliza tu Página",
                    font_weight="600",
                    font_size="0.95rem",
                ),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("x", size=16),
                    on_click=ThemeState.toggle_chat,
                    variant="ghost",
                    size="1",
                    cursor="pointer",
                ),
                width="100%",
                padding="0.75rem 1rem",
                border_bottom="1px solid #eee",
                align="center",
            ),
            
            # Welcome message
            rx.box(
                rx.hstack(
                    rx.text("🎨", font_size="0.85rem"),
                    rx.text(
                        "Dime tu estilo y personalizaré la página para ti",
                        font_size="0.85rem",
                        color="#666",
                    ),
                    spacing="1",
                ),
                padding="0.75rem 1rem",
                background="#f9f9f9",
                border_bottom="1px solid #eee",
                width="100%",
            ),
            
            # Messages area
            rx.box(
                rx.vstack(
                    rx.foreach(ThemeState.messages, message_bubble),
                    loading_indicator(),
                    streaming_indicator(),
                    spacing="1",
                    align="start",
                    width="100%",
                    padding="0.5rem",
                ),
                id="theme-chat-messages",
                flex="1",
                overflow_y="auto",
                width="100%",
            ),
            
            # Input
            chat_input(),
            
            spacing="0",
            height="100%",
            width="100%",
        ),
        width="min(400px, 90vw)",
        height="min(650px, 70vh)",
        max_width="400px",
        max_height="800px",
        background="white",
        border_radius="1rem",
        box_shadow="0 10px 40px rgba(0,0,0,0.15)",
        overflow="hidden",
        position="fixed",
        bottom="90px",
        right="24px",
        z_index="1000",
    )


def floating_chat_button() -> rx.Component:
    """The floating button to toggle chat"""
    return rx.box(
        rx.icon_button(
            rx.icon("message-circle", size=24),
            size="4",
            radius="full",
            background=ThemeState.gradient_style,
            box_shadow="0 4px 20px rgba(102, 126, 234, 0.4)",
            cursor="pointer",
            on_click=ThemeState.toggle_chat,
            _hover={
                "transform": "scale(1.05)",
                "box_shadow": "0 6px 25px rgba(102, 126, 234, 0.5)",
            },
            style={"transition": "all 0.2s ease"},
        ),
        position="fixed",
        bottom="24px",
        right="24px",
        z_index="1000",
    )


def theme_chat() -> rx.Component:
    """
    Complete floating chat component for theme personalization.
    """
    return rx.fragment(
        # Chat panel (shown when open)
        rx.cond(
            ThemeState.chat_open,
            chat_panel(),
            rx.fragment(),
        ),
        
        # Floating button (changes icon when open)
        rx.cond(
            ThemeState.chat_open,
            rx.fragment(),
            floating_chat_button(),
        ),
    )
