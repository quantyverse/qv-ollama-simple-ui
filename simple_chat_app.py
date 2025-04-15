"""
Simple chat application using Ollama LLM and NiceGUI.
Main entry point for the application.
"""
import sys
import os
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nicegui import ui
from styles import CHAT_STYLES
from models import ModelManager
from chat import ChatManager
from src.components.dialogs import DialogManager
from config import (
    APP_TITLE, APP_PORT, MAX_WIDTH, MARGIN_Y, MARGIN_X,
    MODEL_DIALOG_MIN_WIDTH, MODEL_DIALOG_MAX_WIDTH,
    NO_MODELS_FOUND_MSG, MODEL_SWITCH_SUCCESS_MSG
)

# UI refresh settings
UI_REFRESH_INTERVAL = 0.1  # UI refresh interval in seconds

def create_header(dialog_manager: DialogManager, model_manager: ModelManager) -> None:
    """Create the application header."""
    with ui.header().classes('custom-header text-white'):
        with ui.row().classes('w-full items-center'):
            ui.label(APP_TITLE).classes('text-xl')
            ui.label().bind_text_from(
                model_manager.get_model_data(), 
                'current_model',
                backward=lambda name: f"Model: {name}"
            ).classes('model-badge')
            ui.space()
            ui.button('Pull Model', on_click=dialog_manager.show_pull_dialog, icon='download').props('flat').classes('header-button')
            ui.button('Models', on_click=dialog_manager.show_models_dialog, icon='list').props('flat').classes('header-button')

def create_footer(chat_manager: ChatManager) -> tuple[ui.input, callable]:
    """Create the application footer with input area."""
    with ui.footer().classes('bg-white'), ui.column().classes(f'w-full max-w-{MAX_WIDTH} {MARGIN_X} {MARGIN_Y}'):
        with ui.row().classes('w-full no-wrap items-center'):
            input_element = ui.input(placeholder='Type your message...').props('rounded outlined input-class=mx-3').classes('flex-grow')
            ui.button('Send', on_click=lambda: send_message(input_element, chat_manager)).props('icon=send').classes('custom-button')
        input_element.on('keydown.enter', lambda: send_message(input_element, chat_manager))
        return input_element, lambda: send_message(input_element, chat_manager)

def send_message(input_element: ui.input, chat_manager: ChatManager) -> None:
    """Send a message and get AI response."""
    message_text = input_element.value
    if not message_text or chat_manager.is_thinking:
        return
        
    input_element.value = ''
    chat_manager.add_user_message(message_text)
    chat_manager.is_thinking = True
    chat_manager.message_completed = True
    chat_manager.chat_messages.refresh()
    threading.Thread(target=chat_manager.get_ai_response, args=(message_text,), daemon=True).start()

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