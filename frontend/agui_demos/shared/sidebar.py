"""
Sidebar Component - Demo Navigation Menu

A sidebar showing available demos in the application.
"""

import reflex as rx


def demo_item(title: str, description: str, icon: str, href: str, is_active: bool = False) -> rx.Component:
    """A single demo item in the sidebar"""
    return rx.link(
        rx.box(
            rx.hstack(
                rx.icon(icon, size=18, color="#667eea" if is_active else "#666"),
                rx.vstack(
                    rx.text(
                        title,
                        font_weight="600" if is_active else "500",
                        font_size="0.9rem",
                        color="#333" if is_active else "#666",
                    ),
                    rx.text(
                        description,
                        font_size="0.75rem",
                        color="#999",
                        line_height="1.3",
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="0.75rem",
            border_radius="0.5rem",
            background="rgba(102, 126, 234, 0.1)" if is_active else "transparent",
            border_left=f"3px solid {'#667eea' if is_active else 'transparent'}",
            cursor="pointer",
            _hover={
                "background": "rgba(102, 126, 234, 0.05)" if not is_active else "rgba(102, 126, 234, 0.1)",
            },
            width="100%",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def sidebar(active_demo: str = "recipe") -> rx.Component:
    """
    Main sidebar component with demo navigation.
    
    Args:
        active_demo: The currently active demo ("recipe" or "theme")
    
    Shows available demos that can be selected.
    """
    return rx.box(
        rx.vstack(
            # App title
            rx.hstack(
                rx.icon("sparkles", size=24, color="#667eea"),
                rx.text(
                    "AG-UI Demos",
                    font_weight="bold",
                    font_size="1.1rem",
                    color="#333",
                ),
                spacing="2",
                align="center",
                padding="1rem",
                border_bottom="1px solid #eee",
                width="100%",
            ),
            
            # Demos section
            rx.box(
                rx.text(
                    "DEMOS",
                    font_size="0.7rem",
                    font_weight="600",
                    color="#999",
                    letter_spacing="0.05em",
                    padding_x="0.75rem",
                    padding_top="1rem",
                    padding_bottom="0.5rem",
                ),
                
                # Recipe Assistant
                demo_item(
                    title="Asistente de Recetas",
                    description="Crea y mejora recetas con IA",
                    icon="chef-hat",
                    href="/",
                    is_active=(active_demo == "recipe"),
                ),
                
                # Page Personalizer (Ilitia)
                demo_item(
                    title="Personalizador Ilitia",
                    description="Personaliza el tema con IA",
                    icon="palette",
                    href="/theme",
                    is_active=(active_demo == "theme"),
                ),
                
                width="100%",
                padding_x="0.5rem",
            ),
            
            rx.spacer(),
            
            # Footer
            rx.box(
                rx.hstack(
                    rx.text(
                        "Microsoft Agent Framework",
                        font_size="0.7rem",
                        color="#999",
                    ),
                    rx.badge(
                        "AG-UI",
                        color_scheme="purple",
                        variant="soft",
                        size="1",
                    ),
                    spacing="2",
                    align="center",
                ),
                padding="1rem",
                border_top="1px solid #eee",
                width="100%",
            ),
            
            spacing="0",
            height="100%",
            width="100%",
        ),
        width="240px",
        min_width="240px",
        height="100vh",
        background="white",
        border_right="1px solid #eee",
        position="fixed",
        left="0",
        top="0",
        z_index="50",
    )
