"""
Reflex State for Theme Personalization Demo with AG-UI Protocol Integration

This module defines the theme state and handles AG-UI events
to update the UI styling in real-time.
"""

import os
import asyncio
import hashlib
import json
from typing import Any, Optional

import reflex as rx
from pydantic import BaseModel
from dotenv import load_dotenv

from ...shared.ag_ui_client import AGUIClient, AGUIClientConfig, AGUIEventType

# Load environment variables
load_dotenv()


class Theme(BaseModel):
    """Theme configuration model for page personalization"""
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    background_color: str = "#f5f5f5"
    card_background: str = "#ffffff"
    text_color: str = "#333333"
    accent_color: str = "#f97316"
    font_family: str = "Inter"
    mood: str = "Corporativo - Ilitia"
    description: str = "Tema por defecto con los colores corporativos de Ilitia"


class ThemeChatMessage(BaseModel):
    """Chat message model for theme demo"""
    role: str = "user"
    content: str = ""


class ThemeState(rx.State):
    """
    Theme personalization state.
    
    Handles:
    - Chat messages for theme customization
    - Theme data from AG-UI events
    - Loading/streaming states
    """
    
    # Chat state
    messages: list[ThemeChatMessage] = []
    current_input: str = ""
    
    # Theme state (from AG-UI STATE_SNAPSHOT/STATE_DELTA)
    theme: Theme = Theme()
    _last_theme_hash: str = ""
    
    # UI state
    is_loading: bool = False
    is_streaming: bool = False
    current_streaming_content: str = ""
    error_message: str = ""
    chat_open: bool = False
    
    # Agent configuration
    thread_id: str = "theme-default"
    
    @rx.var
    def has_theme(self) -> bool:
        """Check if we have a customized theme"""
        return self.theme.mood != "Corporativo - Ilitia"
    
    @rx.var
    def gradient_style(self) -> str:
        """CSS gradient from primary to secondary colors"""
        return f"linear-gradient(135deg, {self.theme.primary_color} 0%, {self.theme.secondary_color} 100%)"
    
    @rx.var
    def message_count(self) -> int:
        """Number of messages in chat"""
        return len(self.messages)
    
    def set_input(self, value: str):
        """Update the current input value"""
        self.current_input = value
    
    def clear_error(self):
        """Clear the error message"""
        self.error_message = ""
    
    def toggle_chat(self):
        """Toggle the floating chat panel open/closed"""
        self.chat_open = not self.chat_open

    def handle_key_down(self, key: str):
        """Handle key down events in the input field"""
        if key == "Enter":
            return ThemeState.send_message
    
    def reset_theme(self):
        """Reset to default theme"""
        self.theme = Theme()
        self.messages = []
        self.current_input = ""
        self._last_theme_hash = ""
    
    def _get_agent_url(self) -> str:
        """Get the theme agent backend URL from environment"""
        base_url = os.getenv("AGENT_URL", "http://localhost:8888/shared_state")
        # Replace shared_state with theme_state for theme agent
        return base_url.replace("/shared_state", "/theme_state")
    
    def _build_state_for_agent(self) -> dict:
        """Build the current state to send to the agent"""
        return {
            "theme": self.theme.model_dump()
        }
    
    async def send_message(self):
        """Send a message to the theme agent and process AG-UI events"""
        if not self.current_input.strip():
            return
        
        user_message = self.current_input.strip()
        self.current_input = ""
        
        # Add user message to chat
        self.messages = self.messages + [
            ThemeChatMessage(role="user", content=user_message)
        ]
        
        self.is_loading = True
        self.is_streaming = False
        self.current_streaming_content = ""
        self.error_message = ""
        
        # Open chat if not open
        if not self.chat_open:
            self.chat_open = True
        
        yield
        
        try:
            agent_url = self._get_agent_url()
            print(f"🎨 Theme Agent URL: {agent_url}")
            
            config = AGUIClientConfig(
                base_url=agent_url.rsplit("/", 1)[0],
                endpoint=f"/{agent_url.rsplit('/', 1)[1]}",
                timeout=120.0,
            )
            print(f"🎨 Config: base={config.base_url}, endpoint={config.endpoint}")
            
            client = AGUIClient(config)
            
            # Current state to send
            current_state = self._build_state_for_agent()
            
            async for event in client.run(
                message=user_message,
                thread_id=self.thread_id,
                state=current_state,
            ):
                if event.type == AGUIEventType.TEXT_MESSAGE_START:
                    self.is_streaming = True
                    self.current_streaming_content = ""
                    yield
                    
                elif event.type == AGUIEventType.TEXT_MESSAGE_CONTENT:
                    # Handle both 'delta' and 'content' keys
                    delta = event.data.get("delta", event.data.get("content", ""))
                    self.current_streaming_content += delta
                    yield
                    
                elif event.type == AGUIEventType.TEXT_MESSAGE_END:
                    if self.current_streaming_content:
                        self.messages = self.messages + [
                            ThemeChatMessage(
                                role="assistant",
                                content=self.current_streaming_content
                            )
                        ]
                    self.is_streaming = False
                    self.current_streaming_content = ""
                    yield
                    
                elif event.type == AGUIEventType.STATE_SNAPSHOT:
                    # Process theme state update
                    snapshot_data = event.data.get("snapshot", event.data.get("state", {}))
                    theme_data = snapshot_data.get("theme")
                    
                    if theme_data and isinstance(theme_data, dict):
                        # Check if theme actually changed
                        theme_content = json.dumps(theme_data, sort_keys=True)
                        current_hash = hashlib.md5(theme_content.encode()).hexdigest()
                        
                        if current_hash != self._last_theme_hash:
                            old_mood = self.theme.mood
                            self._last_theme_hash = current_hash
                            
                            # Update theme
                            self.theme = Theme(
                                primary_color=theme_data.get("primary_color", self.theme.primary_color),
                                secondary_color=theme_data.get("secondary_color", self.theme.secondary_color),
                                background_color=theme_data.get("background_color", self.theme.background_color),
                                card_background=theme_data.get("card_background", self.theme.card_background),
                                text_color=theme_data.get("text_color", self.theme.text_color),
                                accent_color=theme_data.get("accent_color", self.theme.accent_color),
                                font_family=theme_data.get("font_family", self.theme.font_family),
                                mood=theme_data.get("mood", self.theme.mood),
                                description=theme_data.get("description", self.theme.description),
                            )
                    yield
                    
                elif event.type == AGUIEventType.RUN_ERROR:
                    error = event.data.get("error", "Error desconocido")
                    self.error_message = f"Error: {error}"
                    yield
                    
                elif event.type == AGUIEventType.RUN_FINISHED:
                    self.is_loading = False
                    self.is_streaming = False
                    yield
                    
        except Exception as e:
            self.error_message = f"Error de conexión: {str(e)}"
            print(f"🎨 ERROR: {e}")
            self.is_loading = False
            self.is_streaming = False
            yield
            yield
