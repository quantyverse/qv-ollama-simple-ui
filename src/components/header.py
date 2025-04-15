from nicegui import ui
from src.services.models import ModelManager
from components.dialogs import DialogManager
from src.config.config import APP_TITLE

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
