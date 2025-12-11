"""
AG-UI Protocol Client for Reflex

This module provides a client for consuming AG-UI events via Server-Sent Events (SSE).
It handles the streaming connection and event parsing for the AG-UI protocol.
"""

import json
import asyncio
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Optional
from enum import Enum

import httpx


class AGUIEventType(str, Enum):
    """AG-UI Protocol Event Types"""
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    
    RAW = "RAW"
    CUSTOM = "CUSTOM"


@dataclass
class AGUIEvent:
    """Represents an AG-UI protocol event"""
    type: AGUIEventType
    data: dict[str, Any]
    timestamp: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "AGUIEvent":
        """Create an AGUIEvent from a dictionary"""
        event_type_str = data.get("type", "CUSTOM")
        try:
            event_type = AGUIEventType(event_type_str)
        except ValueError:
            event_type = AGUIEventType.CUSTOM
        
        return cls(
            type=event_type,
            data=data,
            timestamp=data.get("timestamp", "")
        )


@dataclass
class AGUIMessage:
    """Represents a chat message"""
    role: str
    content: str
    message_id: str = ""


@dataclass
class AGUIClientConfig:
    """Configuration for the AG-UI client"""
    base_url: str = "http://localhost:8888"
    endpoint: str = "/shared_state"
    timeout: float = 300.0  # 5 minutes timeout for long generations
    
    @property
    def full_url(self) -> str:
        return f"{self.base_url}{self.endpoint}"


class AGUIClient:
    """
    Client for consuming AG-UI protocol events from an agent backend.
    
    Usage:
        client = AGUIClient()
        async for event in client.run("Haz una receta de paella"):
            if event.type == AGUIEventType.TEXT_MESSAGE_CONTENT:
                print(event.data.get("content", ""), end="")
            elif event.type == AGUIEventType.STATE_SNAPSHOT:
                print(f"State: {event.data.get('state')}")
    """
    
    def __init__(self, config: Optional[AGUIClientConfig] = None):
        self.config = config or AGUIClientConfig()
        self._current_message_id: str = ""
        self._current_message_content: str = ""
    
    async def run(
        self,
        message: str,
        thread_id: str = "default",
        run_id: str = "",
        state: Optional[dict] = None
    ) -> AsyncIterator[AGUIEvent]:
        """
        Send a message to the agent and stream back AG-UI events.
        
        Args:
            message: The user message to send
            thread_id: Thread ID for conversation continuity
            run_id: Optional run ID
            state: Optional client state to send
            
        Yields:
            AGUIEvent objects as they arrive from the server
        """
        import uuid
        
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Prepare request payload (AG-UI format)
        payload = {
            "thread_id": thread_id,
            "run_id": run_id,
            "messages": [
                {"role": "user", "content": message}
            ],
            "state": state
        }
        
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            async with client.stream(
                "POST",
                self.config.full_url,
                json=payload,
                headers={
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json"
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        try:
                            data = json.loads(data_str)
                            event = AGUIEvent.from_dict(data)
                            
                            # Track message content
                            if event.type == AGUIEventType.TEXT_MESSAGE_START:
                                self._current_message_id = event.data.get("messageId", "")
                                self._current_message_content = ""
                            elif event.type == AGUIEventType.TEXT_MESSAGE_CONTENT:
                                self._current_message_content += event.data.get("content", "")
                            
                            yield event
                            
                        except json.JSONDecodeError:
                            # Skip malformed events
                            continue
    
    async def run_simple(
        self,
        message: str,
        thread_id: str = "default"
    ) -> AsyncIterator[AGUIEvent]:
        """
        Simplified run method using the /chat endpoint
        """
        payload = {
            "content": message,
            "thread_id": thread_id
        }
        
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.config.base_url}/chat",
                json=payload,
                headers={
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json"
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        try:
                            data = json.loads(data_str)
                            yield AGUIEvent.from_dict(data)
                        except json.JSONDecodeError:
                            continue
    
    async def reset(self, thread_id: str = "default") -> bool:
        """Reset the agent state for a thread"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.base_url}/reset/{thread_id}"
            )
            return response.status_code == 200
    
    async def health_check(self) -> bool:
        """Check if the agent backend is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.config.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


class AGUIEventHandler:
    """
    Helper class to handle AG-UI events with callbacks.
    
    Usage:
        handler = AGUIEventHandler()
        handler.on_text_content(lambda content: print(content, end=""))
        handler.on_state_snapshot(lambda state: update_ui(state))
        
        async for event in client.run("message"):
            handler.handle(event)
    """
    
    def __init__(self):
        self._handlers: dict[AGUIEventType, list[Callable]] = {}
    
    def on(self, event_type: AGUIEventType, callback: Callable) -> "AGUIEventHandler":
        """Register a callback for an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(callback)
        return self
    
    def on_text_content(self, callback: Callable[[str], None]) -> "AGUIEventHandler":
        """Register callback for text message content"""
        def wrapper(event_data: dict):
            callback(event_data.get("content", ""))
        return self.on(AGUIEventType.TEXT_MESSAGE_CONTENT, wrapper)
    
    def on_state_snapshot(self, callback: Callable[[dict], None]) -> "AGUIEventHandler":
        """Register callback for state snapshots"""
        def wrapper(event_data: dict):
            callback(event_data.get("state", {}))
        return self.on(AGUIEventType.STATE_SNAPSHOT, wrapper)
    
    def on_state_delta(self, callback: Callable[[list], None]) -> "AGUIEventHandler":
        """Register callback for state deltas"""
        def wrapper(event_data: dict):
            callback(event_data.get("delta", []))
        return self.on(AGUIEventType.STATE_DELTA, wrapper)
    
    def on_run_finished(self, callback: Callable[[], None]) -> "AGUIEventHandler":
        """Register callback for run completion"""
        def wrapper(event_data: dict):
            callback()
        return self.on(AGUIEventType.RUN_FINISHED, wrapper)
    
    def on_error(self, callback: Callable[[str], None]) -> "AGUIEventHandler":
        """Register callback for errors"""
        def wrapper(event_data: dict):
            callback(event_data.get("error", "Unknown error"))
        return self.on(AGUIEventType.RUN_ERROR, wrapper)
    
    def handle(self, event: AGUIEvent):
        """Handle an event by calling registered callbacks"""
        if event.type in self._handlers:
            for callback in self._handlers[event.type]:
                callback(event.data)


# Utility functions for synchronous contexts

def run_sync(
    message: str,
    base_url: str = "http://localhost:8888",
    thread_id: str = "default"
) -> dict:
    """
    Synchronous wrapper for running the agent.
    Returns the final state and collected messages.
    """
    import asyncio
    
    async def _run():
        config = AGUIClientConfig(base_url=base_url)
        client = AGUIClient(config)
        
        final_state = {}
        messages = []
        current_content = ""
        
        async for event in client.run(message, thread_id):
            if event.type == AGUIEventType.TEXT_MESSAGE_CONTENT:
                current_content += event.data.get("content", "")
            elif event.type == AGUIEventType.TEXT_MESSAGE_END:
                messages.append({"role": "assistant", "content": current_content})
                current_content = ""
            elif event.type == AGUIEventType.STATE_SNAPSHOT:
                final_state = event.data.get("state", {})
        
        return {"state": final_state, "messages": messages}
    
    return asyncio.run(_run())
