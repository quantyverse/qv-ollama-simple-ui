"""
Chat functionality for the application.
Handles message management and UI components.
"""
from datetime import datetime
from typing import List, Tuple, Dict
import time
from nicegui import ui

from config import (
    USER_ID, AI_ID, STREAMING_DELAY
)
from models import ModelManager

class ChatManager:
    """Manages chat messages and UI components."""
    
    def __init__(self, model_manager: ModelManager):
        """Initialize chat manager with model manager."""
        self.model_manager = model_manager
        self.messages: List[Tuple[str, str, str]] = []
        self.is_thinking = False
        self.current_response = ""
        self.message_completed = False
        self.markdown_components: Dict[str, ui.markdown] = {}

    def add_user_message(self, text: str) -> None:
        """Add a user message to chat history."""
        stamp = datetime.now().strftime('%X')
        self.messages.append((USER_ID, text, stamp))

    def add_ai_message(self, text: str) -> None:
        """Add an AI message to chat history."""
        stamp = datetime.now().strftime('%X')
        self.messages.append((AI_ID, text, stamp))

    def clear_messages(self) -> None:
        """Clear all messages from chat history."""
        self.messages.clear()

    def update_streaming_content(self, text: str) -> None:
        """Update streaming response in UI."""
        if "streaming" in self.markdown_components:
            self.markdown_components["streaming"].content = text

    def get_ai_response(self, message_text: str) -> None:
        """Get AI response with streaming updates."""
        try:
            self.current_response = ""
            full_response = ""
            
            for chunk in self.model_manager.get_client().stream_chat(message_text):
                self.current_response += chunk
                self.update_streaming_content(self.current_response)
                full_response += chunk
                time.sleep(STREAMING_DELAY)
            
            self.is_thinking = False
            self.current_response = ""
            self.message_completed = True
            self.add_ai_message(full_response)
            
        except Exception as e:
            error_msg = str(e)
            self.is_thinking = False
            self.current_response = ""
            self.message_completed = True
            self.add_ai_message(f"Error: {error_msg}")

    @ui.refreshable
    def chat_messages(self) -> None:
        """Display chat messages in UI."""
        self.markdown_components = {}
        
        if self.messages:
            for i, (user_id, text, stamp) in enumerate(self.messages):
                if user_id == USER_ID:
                    ui.chat_message(text=text, stamp=stamp, avatar=None, sent=True)
                else:
                    with ui.chat_message(stamp=stamp, avatar=None, sent=False) as msg:
                        msg_id = f"message_{i}"
                        self.markdown_components[msg_id] = ui.markdown(text)
        else:
            ui.label('No messages yet').classes('mx-auto my-36')
        
        if self.is_thinking:
            response_text = self.current_response if self.current_response else "Thinking..."
            with ui.chat_message(stamp=datetime.now().strftime('%X'), avatar=None, sent=False) as msg:
                msg_id = "streaming"
                self.markdown_components[msg_id] = ui.markdown(response_text)
        
        if self.is_thinking or self.message_completed:
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
            self.message_completed = False 