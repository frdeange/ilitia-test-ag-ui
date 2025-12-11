"""
Reflex Configuration for AG-UI Demos
"""

import os
import reflex as rx

config = rx.Config(
    app_name="agui_demos",
    title="🚀 AG-UI Demos | Microsoft Agent Framework",
    description="Demos interactivas del protocolo AG-UI con Microsoft Agent Framework",
    
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
