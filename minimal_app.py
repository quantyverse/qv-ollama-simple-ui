"""
Minimal working chat application with NiceGUI.
"""
from nicegui import ui
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import from quanty
from quanty.services.ollama_service import ollama_service
from quanty.utils.state import chat_state

# Global state
messages = []
is_sending = False

# Main UI
def create_ui():
    # Simple header
    with ui.header().classes('justify-between'):
        ui.label('Quanty Chat').classes('text-2xl font-bold')
    
    # Main container
    with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
        # Messages area
        messages_container = ui.column().classes('w-full overflow-y-auto bg-gray-100 rounded p-4 mb-4').style('min-height: 400px')
        
        # Function to add a message to UI
        def add_message_to_ui(content, is_user=False):
            with messages_container:
                with ui.card().classes('w-full my-2 p-2'):
                    ui.label('You' if is_user else 'AI').classes('font-bold')
                    ui.label(content)
        
        # Add initial message
        add_message_to_ui('Hello! How can I help you today?')
        
        # Add existing messages if any
        for msg in messages:
            add_message_to_ui(msg['content'], msg['is_user'])
        
        # Input area
        with ui.row().classes('w-full'):
            text_input = ui.input(placeholder='Type your message...').classes('flex-grow')
            
            async def send_message():
                global is_sending  # Moved to beginning of function
                
                # Get message text
                content = text_input.value
                if not content or is_sending:
                    return
                
                # Clear input
                text_input.value = ''
                
                # Show user message
                messages.append({'content': content, 'is_user': True})
                add_message_to_ui(content, is_user=True)
                
                # Set sending state
                is_sending = True
                send_button.disable()
                
                try:
                    # Send to Ollama
                    response = ollama_service.send_message(content)
                    
                    # Show response
                    messages.append({'content': response, 'is_user': False})
                    add_message_to_ui(response)
                except Exception as e:
                    # Show error
                    error_msg = f"Error: {str(e)}"
                    add_message_to_ui(error_msg)
                    logger.error(error_msg)
                
                # Reset sending state
                is_sending = False
                send_button.enable()
            
            # Create send button
            send_button = ui.button('Send', on_click=send_message)
            send_button.props('icon=send')

# Start the app
ui.run(title='Quanty Chat', port=8080)
create_ui() 