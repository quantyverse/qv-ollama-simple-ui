"""
Simple chat application using Ollama LLM and NiceGUI.
Main entry point for the application.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nicegui import ui
from styles import CHAT_STYLES
from models import ModelManager
from chat import ChatManager
from config import (
    APP_TITLE, APP_PORT, MAX_WIDTH, MARGIN_Y, MARGIN_X,
    MODEL_DIALOG_MIN_WIDTH, MODEL_DIALOG_MAX_WIDTH,
    NO_MODELS_FOUND_MSG, MODEL_SWITCH_SUCCESS_MSG
)

# UI refresh settings
UI_REFRESH_INTERVAL = 0.1  # UI refresh interval in seconds

# Initialize managers
model_manager = ModelManager()
chat_manager = ChatManager(model_manager)

@ui.refreshable
def model_list_component(dialog):
    """Display available models in a dialog."""
    models = model_manager.get_available_models()
    current_model = model_manager.current_model
    
    with ui.card().classes('w-full model-list'):
        with ui.row():
            ui.label('Available Models').classes('text-xl font-bold')
            ui.space()
            ui.button('Refresh', on_click=lambda: model_list_component.refresh(dialog), icon='refresh').props('flat').classes('custom-button')
            ui.button('Close', on_click=dialog.close, icon='close').props('flat')
            
        if models:
            for model in models:
                model_name = model.get('model', 'Unknown')
                is_selected = model_name == current_model
                
                def select_model(model_to_select=model_name):
                    if model_to_select != model_manager.current_model:
                        model_manager.switch_model(model_to_select)
                        chat_manager.clear_messages()
                        chat_manager.chat_messages.refresh()
                        ui.notify(MODEL_SWITCH_SUCCESS_MSG.format(model_name=model_to_select), color='positive')
                    
                    model_list_component.refresh(dialog)
                    dialog.close()
                
                with ui.card().classes(f'model-item {"selected" if is_selected else ""}').on('click', select_model):
                    with ui.row():
                        ui.label(model_name).classes('model-name')
                        if is_selected:
                            ui.label('ACTIVE').classes('text-positive text-bold q-ml-sm')
                    size_mb = model.get('size', 0) / (1024 * 1024)
                    ui.label(f"Size: {size_mb:.1f} MB").classes('model-meta')
        else:
            ui.label(NO_MODELS_FOUND_MSG).classes('p-4')

@ui.page('/')
async def main():
    """Main application page with chat interface."""
    # Add custom CSS to the page
    ui.add_head_html(f'<style>{CHAT_STYLES}</style>')
    
    # Input element reference
    input_element = None
    
    # Create dialog for models
    models_dialog = ui.dialog()
    with models_dialog:
        with ui.card().classes('w-full').style(f'min-width: {MODEL_DIALOG_MIN_WIDTH}; max-width: {MODEL_DIALOG_MAX_WIDTH};'):
            model_list_component(models_dialog)
    
    def show_models_dialog():
        """Open the models selection dialog."""
        models_dialog.open()
        model_list_component.refresh(models_dialog)
    
    async def send() -> None:
        """Send a message and get AI response."""
        message_text = input_element.value
        if not message_text or chat_manager.is_thinking:
            return
            
        input_element.value = ''
        chat_manager.add_user_message(message_text)
        chat_manager.is_thinking = True
        chat_manager.message_completed = True
        chat_manager.chat_messages.refresh()
        await chat_manager.get_ai_response(message_text)
    
    # Header with title and model button
    with ui.header().classes('custom-header text-white'):
        with ui.row().classes('w-full items-center'):
            ui.label(APP_TITLE).classes('text-xl')
            ui.label().bind_text_from(
                model_manager.get_model_data(), 
                'current_model',
                backward=lambda name: f"Model: {name}"
            ).classes('model-badge')
            ui.space()
            ui.button('Models', on_click=show_models_dialog, icon='list').props('flat').classes('header-button')

    # Main content area 
    with ui.column().classes(f'w-full max-w-{MAX_WIDTH} {MARGIN_X} {MARGIN_Y}'):
        await ui.context.client.connected()
        chat_manager.chat_messages()
        ui.timer(UI_REFRESH_INTERVAL, chat_manager.chat_messages.refresh)

    # Footer with input area
    with ui.footer().classes('bg-white'), ui.column().classes(f'w-full max-w-{MAX_WIDTH} {MARGIN_X} {MARGIN_Y}'):
        with ui.row().classes('w-full no-wrap items-center'):
            input_element = ui.input(placeholder='Type your message...').props('rounded outlined input-class=mx-3').classes('flex-grow')
            ui.button('Send', on_click=send).props('icon=send').classes('custom-button')
        input_element.on('keydown.enter', send)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title=APP_TITLE, port=APP_PORT)