"""
Main container component that combines chat history and message input.
"""
from nicegui import ui
import logging

from src.quanty.components.chat_history import chat_history
from src.quanty.components.message_input import message_input

# Configure logging
logger = logging.getLogger(__name__)

def chat_container():
    """
    Create the main chat container that combines all chat components.
    
    Returns:
        The main chat container UI element
    """
    logger.info("Creating chat container")
    
    # Create a simple column layout without nested cards
    container = ui.column().classes('w-full h-full gap-4')
    
    with container:
        # Connection status indicator for visibility
        ui.label('UI Ready').classes('text-center text-sm text-green-500')
        
        # Chat history area (takes most of the space)
        history_container = ui.column().classes('w-full flex-grow overflow-auto h-[60vh]')
        with history_container:
            chat_history()
        
        # Message input area at the bottom
        input_container = ui.column().classes('w-full mt-2')
        with input_container:
            message_input()
    
    # Log success
    logger.info("Chat container created successfully")
    return container 