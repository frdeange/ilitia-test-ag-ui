"""
Demo Cards Component

Sample cards to demonstrate theme changes for Ilitia.
"""

import reflex as rx

from ..state import ThemeState


def hero_section() -> rx.Component:
    """Hero section with Ilitia branding"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("sparkles", size=40, color="white"),
                rx.text(
                    "Ilitia",
                    font_size="2.5rem",
                    font_weight="bold",
                    color="white",
                ),
                spacing="3",
                align="center",
            ),
            rx.text(
                ThemeState.theme.mood,
                font_size="1.2rem",
                color="rgba(255,255,255,0.9)",
                font_weight="500",
            ),
            rx.text(
                ThemeState.theme.description,
                font_size="0.9rem",
                color="rgba(255,255,255,0.7)",
                text_align="center",
                max_width="500px",
            ),
            spacing="3",
            align="center",
            padding="3rem",
        ),
        background=ThemeState.gradient_style,
        border_radius="1rem",
        width="100%",
        box_shadow="0 10px 40px rgba(0,0,0,0.15)",
    )


def service_card(icon: str, title: str, description: str) -> rx.Component:
    """A service card component"""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=28, color="white"),
                padding="1rem",
                border_radius="0.75rem",
                background=ThemeState.gradient_style,
            ),
            rx.text(
                title,
                font_size="1.1rem",
                font_weight="600",
                color=ThemeState.theme.text_color,
            ),
            rx.text(
                description,
                font_size="0.85rem",
                color="#666",
                text_align="center",
                line_height="1.5",
            ),
            spacing="3",
            align="center",
            padding="1.5rem",
        ),
        background=ThemeState.theme.card_background,
        border_radius="1rem",
        box_shadow="0 4px 20px rgba(0,0,0,0.08)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "0 8px 30px rgba(0,0,0,0.12)",
        },
        style={"transition": "all 0.3s ease"},
        flex="1",
        min_width="200px",
    )


def stat_card(value: str, label: str) -> rx.Component:
    """A statistics card"""
    return rx.box(
        rx.vstack(
            rx.text(
                value,
                font_size="2rem",
                font_weight="bold",
                background=ThemeState.gradient_style,
                background_clip="text",
                style={"-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"},
            ),
            rx.text(
                label,
                font_size="0.85rem",
                color="#666",
            ),
            spacing="1",
            align="center",
        ),
        background=ThemeState.theme.card_background,
        padding="1.5rem 2rem",
        border_radius="1rem",
        box_shadow="0 4px 20px rgba(0,0,0,0.08)",
        flex="1",
        min_width="150px",
    )


def testimonial_card(quote: str, author: str, role: str) -> rx.Component:
    """A testimonial card"""
    return rx.box(
        rx.vstack(
            rx.icon("quote", size=24, color=ThemeState.theme.primary_color),
            rx.text(
                quote,
                font_size="0.95rem",
                color=ThemeState.theme.text_color,
                font_style="italic",
                text_align="center",
                line_height="1.6",
            ),
            rx.divider(width="50px", border_color=ThemeState.theme.primary_color),
            rx.vstack(
                rx.text(
                    author,
                    font_weight="600",
                    font_size="0.9rem",
                    color=ThemeState.theme.text_color,
                ),
                rx.text(
                    role,
                    font_size="0.8rem",
                    color="#666",
                ),
                spacing="0",
                align="center",
            ),
            spacing="3",
            align="center",
            padding="2rem",
        ),
        background=ThemeState.theme.card_background,
        border_radius="1rem",
        box_shadow="0 4px 20px rgba(0,0,0,0.08)",
        border_left=f"4px solid {ThemeState.theme.primary_color}",
        width="100%",
    )


def cta_button() -> rx.Component:
    """Call to action button"""
    return rx.button(
        rx.hstack(
            rx.text("Comenzar Ahora"),
            rx.icon("arrow-right", size=18),
            spacing="2",
        ),
        size="3",
        background=ThemeState.gradient_style,
        color="white",
        cursor="pointer",
        _hover={"opacity": "0.9", "transform": "scale(1.02)"},
        style={"transition": "all 0.2s ease"},
        padding_x="2rem",
    )


def demo_cards() -> rx.Component:
    """
    Collection of demo cards to showcase theme changes.
    """
    return rx.vstack(
        # Hero Section
        hero_section(),
        
        # Services Section
        rx.box(
            rx.text(
                "Nuestros Servicios",
                font_size="1.5rem",
                font_weight="bold",
                color=ThemeState.theme.text_color,
                margin_bottom="1rem",
            ),
            rx.flex(
                service_card(
                    "brain",
                    "Inteligencia Artificial",
                    "Soluciones de IA personalizadas para tu negocio",
                ),
                service_card(
                    "code",
                    "Desarrollo Software",
                    "Aplicaciones modernas con las últimas tecnologías",
                ),
                service_card(
                    "users",
                    "Consultoría",
                    "Asesoramiento experto para tu transformación digital",
                ),
                gap="1.5rem",
                flex_wrap="wrap",
                justify="center",
            ),
            width="100%",
            padding_y="2rem",
        ),
        
        # Stats Section
        rx.box(
            rx.flex(
                stat_card("+150", "Proyectos"),
                stat_card("+50", "Clientes"),
                stat_card("+10", "Años"),
                stat_card("24/7", "Soporte"),
                gap="1rem",
                flex_wrap="wrap",
                justify="center",
            ),
            width="100%",
            padding_y="1rem",
        ),
        
        # Testimonial
        rx.box(
            rx.text(
                "Lo que dicen nuestros clientes",
                font_size="1.5rem",
                font_weight="bold",
                color=ThemeState.theme.text_color,
                margin_bottom="1rem",
                text_align="center",
            ),
            testimonial_card(
                "Ilitia transformó completamente nuestra manera de trabajar. Su equipo de IA nos ayudó a automatizar procesos que antes nos tomaban días.",
                "María García",
                "CTO, TechCorp",
            ),
            width="100%",
            max_width="600px",
            padding_y="2rem",
        ),
        
        # CTA
        rx.center(
            cta_button(),
            width="100%",
            padding_y="2rem",
        ),
        
        spacing="4",
        width="100%",
        align="center",
    )
