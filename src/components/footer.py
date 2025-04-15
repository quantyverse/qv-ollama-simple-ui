from nicegui import ui
from src.components.chat import ChatManager
from src.config.config import MAX_WIDTH, MARGIN_X, MARGIN_Y
import threading

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
