"""
Dialog management for the chat application.
Handles all dialog-related functionality and UI components.
"""
from nicegui import ui
from typing import Callable

from src.services.models import ModelManager
from src.components.chat import ChatManager
from src.config.config import (
    MODEL_DIALOG_MIN_WIDTH, MODEL_DIALOG_MAX_WIDTH,
    NO_MODELS_FOUND_MSG, MODEL_SWITCH_SUCCESS_MSG
)

class DialogManager:
    """Manages application dialogs and their state."""
    def __init__(self, model_manager: ModelManager, chat_manager: ChatManager):
        self.model_manager = model_manager
        self.chat_manager = chat_manager
        
        # Create dialogs
        self.models_dialog = ui.dialog()
        self.pull_dialog = ui.dialog()
        
        # Initialize dialog components
        self._init_models_dialog()
        self._init_pull_dialog()
    
    def _init_models_dialog(self):
        """Initialize the models selection dialog."""
        with self.models_dialog:
            with ui.card().classes('w-full').style(f'min-width: {MODEL_DIALOG_MIN_WIDTH}; max-width: {MODEL_DIALOG_MAX_WIDTH};'):
                self.model_list_component(self.models_dialog)
    
    def _init_pull_dialog(self):
        """Initialize the pull model dialog."""
        with self.pull_dialog:
            with ui.card().classes('w-full').style(f'min-width: {MODEL_DIALOG_MIN_WIDTH}; max-width: {MODEL_DIALOG_MAX_WIDTH};'):
                with ui.column().classes('w-full'):
                    ui.label('Pull New Model').classes('text-xl font-bold')
                    self.model_input = ui.input(placeholder='Enter model name (e.g. llama2)').classes('w-full')
                    self.progress_bar = ui.linear_progress().classes('w-full')
                    self.status_label = ui.label('').classes('text-sm')
                    
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Cancel', on_click=self.pull_dialog.close).props('flat')
                        ui.button('Pull', on_click=self._pull_model).props('flat').classes('custom-button')
    
    @ui.refreshable
    def model_list_component(self, dialog):
        """Display available models in a dialog."""
        models = self.model_manager.get_available_models()
        current_model = self.model_manager.current_model
        
        with ui.card().classes('w-full model-list'):
            with ui.row():
                ui.label('Available Models').classes('text-xl font-bold')
                ui.space()
                ui.button('Refresh', on_click=lambda: self.model_list_component.refresh(dialog), icon='refresh').props('flat').classes('custom-button')
                ui.button('Close', on_click=dialog.close, icon='close').props('flat')
                
            if models:
                for model in models:
                    model_name = model.get('model', 'Unknown')
                    is_selected = model_name == current_model
                    
                    def select_model(model_to_select=model_name):
                        if model_to_select != self.model_manager.current_model:
                            self.model_manager.switch_model(model_to_select)
                            self.chat_manager.clear_messages()
                            self.chat_manager.chat_messages.refresh()
                            ui.notify(MODEL_SWITCH_SUCCESS_MSG.format(model_name=model_to_select), color='positive')
                        
                        self.model_list_component.refresh(dialog)
                        dialog.close()
                    
                    with ui.card().classes(f'model-item {"selected" if is_selected else ""}').on('click', select_model):
                        with ui.row().classes('w-full items-center'):
                            with ui.column():
                                ui.label(model_name).classes('model-name')
                                if is_selected:
                                    ui.label('ACTIVE').classes('text-positive text-bold q-ml-sm')
                                size_mb = model.get('size', 0) / (1024 * 1024)
                                ui.label(f"Size: {size_mb:.1f} MB").classes('model-meta')
                            ui.space()
                            if not is_selected:  # Don't show delete button for active model
                                def delete_model(model_to_delete=model_name):
                                    if self.model_manager.delete_model(model_to_delete):
                                        ui.notify(f"Model {model_to_delete} deleted successfully", color='positive')
                                        self.model_list_component.refresh(dialog)
                                    else:
                                        ui.notify(f"Failed to delete model {model_to_delete}", color='negative')
                                
                                ui.button(icon='delete', on_click=delete_model).props('flat dense').classes('text-negative')
            else:
                ui.label(NO_MODELS_FOUND_MSG).classes('p-4')
    
    def _update_progress(self, progress: float, status: str):
        """Update pull progress bar and status."""
        self.progress_bar.value = progress
        self.status_label.set_text(status)
    
    def _pull_model(self):
        """Handle model pulling."""
        model_name = self.model_input.value.strip()
        if not model_name:
            ui.notify('Please enter a model name', color='negative')
            return
        
        def pull_thread():
            if self.model_manager.pull_model(model_name, self._update_progress):
                ui.notify(f'Model {model_name} pulled successfully', color='positive')
                self.model_list_component.refresh(self.models_dialog)
                self.pull_dialog.close()
            else:
                ui.notify(f'Failed to pull model {model_name}', color='negative')
        
        import threading
        threading.Thread(target=pull_thread, daemon=True).start()
    
    def show_models_dialog(self):
        """Open the models selection dialog."""
        self.models_dialog.open()
        self.model_list_component.refresh(self.models_dialog)
    
    def show_pull_dialog(self):
        """Open the pull model dialog."""
        self.pull_dialog.open() 