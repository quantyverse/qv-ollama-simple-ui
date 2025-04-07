"""
Component for entering and sending chat messages.
"""
from nicegui import ui
import traceback
import logging

from src.quanty.utils.state import chat_state
from src.quanty.services.ollama_service import ollama_service

# Configure logging
logger = logging.getLogger(__name__)

def message_input():
    """
    Create a message input component with send button.
    
    Returns:
        The message input container
    """
    logger.info("Initializing message input component")
    container = ui.column().classes('w-full')
    
    with container:
        # Status message for errors
        status = ui.label('').classes('text-red-500 text-sm h-6')
        
        # Create a row for the input and button
        with ui.row().classes('w-full items-end gap-2'):
            # Text input field
            text_input = ui.input(placeholder='Type your message...').classes('flex-grow')
            
            def send_message():
                """Send the current message if valid."""
                try:
                    message = text_input.value.strip()
                    
                    # Validate message and ensure we're not already processing
                    if not message:
                        status.text = 'Please enter a message'
                        return
                    
                    if chat_state.is_thinking:
                        status.text = 'Please wait for the previous response to complete'
                        return
                    
                    logger.info(f"Sending message: '{message[:30]}...' (truncated)")
                    
                    # Clear the input and status
                    text_input.value = ''
                    status.text = ''
                    
                    # Send the message to the Ollama service
                    ollama_service.send_message(message)
                    
                    # Scroll to bottom to show new message
                    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
                except Exception as e:
                    error_msg = f"Error sending message: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    status.text = error_msg
                    ui.notify(error_msg, type='negative', timeout=5000)
            
            # Send button
            send_btn = ui.button('Send', on_click=send_message).props('icon=send')
            
            # Test connection button
            def test_connection():
                """Test if Ollama is responding and show notification."""
                try:
                    logger.debug("Testing Ollama connection from message input")
                    history = ollama_service.get_history()
                    ui.notify(f"Connection OK. History has {len(history)} messages.", type='positive')
                    status.text = 'Connection successful'
                except Exception as e:
                    error_msg = f"Error testing connection: {str(e)}"
                    logger.error(error_msg)
                    ui.notify(error_msg, type='negative', timeout=5000)
                    status.text = error_msg
            
            ui.button('Test', on_click=test_connection, color='secondary')
            
            # Disable controls when thinking
            def update_disabled():
                """Update disabled state of input and button based on thinking state."""
                try:
                    disabled = chat_state.is_thinking
                    text_input.props(f'disable={str(disabled).lower()}')
                    send_btn.props(f'disable={str(disabled).lower()}')
                    
                    # Update status text when thinking
                    if disabled:
                        status.text = 'Assistant is thinking...'
                    elif status.text == 'Assistant is thinking...':
                        status.text = ''
                except Exception as e:
                    logger.error(f"Error updating disabled state: {str(e)}")
            
            # Check thinking state regularly
            ui.timer(0.5, update_disabled)  # Increased interval to reduce load
            
            # Allow pressing Enter to send message
            text_input.on('keydown.enter', send_message)
    
    return container 