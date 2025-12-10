"""
Reflex Configuration for Recipe App
"""

import os
import reflex as rx

# Detect if running in a forwarded port environment
api_url = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="recipe_app",
    title="🍳 Recetas Interactivas | AG-UI",
    description="Genera recetas deliciosas con IA usando el protocolo AG-UI",
    
    # Frontend configuration
    frontend_port=3000,
    
    # Backend configuration
    backend_port=8000,
    api_url=api_url,
    
    # Disable default plugins that are not explicitly configured
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Tailwind configuration
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "primary": {
                        "50": "#f5f3ff",
                        "100": "#ede9fe",
                        "500": "#667eea",
                        "600": "#764ba2",
                        "700": "#6d28d9",
                    }
                }
            }
        }
    },
)
