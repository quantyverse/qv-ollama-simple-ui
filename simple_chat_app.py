"""
Simple chat application using Ollama LLM and NiceGUI.
Main entry point for the application.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nicegui import ui
from src.styles.styles import CHAT_STYLES
from src.services.models import ModelManager
from src.components.chat import ChatManager
from src.components.dialogs import DialogManager
from src.components.header import create_header
from src.components.footer import create_footer
from src.config.config import (
    APP_TITLE, APP_PORT, MAX_WIDTH, MARGIN_Y, MARGIN_X
)

# UI refresh settings
UI_REFRESH_INTERVAL = 0.1  # UI refresh interval in seconds

@ui.page('/')
def main():
    """Main application page with chat interface."""
    # Add custom CSS to the page
    ui.add_head_html(f'<style>{CHAT_STYLES}</style>')
    
    # Initialize managers
    model_manager = ModelManager()
    chat_manager = ChatManager(model_manager)
    dialog_manager = DialogManager(model_manager, chat_manager)
    
    # Create header
    create_header(dialog_manager, model_manager)
    
    # Main content area 
    with ui.column().classes(f'w-full max-w-{MAX_WIDTH} {MARGIN_X} {MARGIN_Y}'):
        chat_manager.chat_messages()
        ui.timer(UI_REFRESH_INTERVAL, chat_manager.chat_messages.refresh)
    
    # Create footer
    create_footer(chat_manager)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title=APP_TITLE, port=APP_PORT)