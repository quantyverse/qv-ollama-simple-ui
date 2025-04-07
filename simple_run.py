"""
Simplified run script for the Quanty chat application.
"""
import sys
import os
import logging
from nicegui import ui

# Configure simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)
logger.info(f"Added {src_path} to Python path")

# Import the service
try:
    from quanty.services.ollama_service import ollama_service
except Exception as e:
    logger.error(f"Error importing: {str(e)}")
    print(f"ERROR: {str(e)}")
    sys.exit(1)

# Global state
messages = []
is_sending = False

def main():
    """Main application entry point."""
    print("\n============================")
    print("   Starting Quanty Chat    ")
    print("============================\n")
    
    # Header
    with ui.header():
        ui.label('Quanty Chat').classes('text-2xl font-bold')
    
    # Main container
    with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
        # Chat area
        messages_area = ui.column().classes('w-full p-4 bg-gray-100 rounded')
        
        # Function to add a message to the UI
        def add_message(text, is_user=False):
            with messages_area:
                with ui.row().classes('w-full my-2'):
                    color = 'blue-100' if is_user else 'gray-100'
                    with ui.card().classes(f'bg-{color} p-2'):
                        ui.label(f"{'You' if is_user else 'Assistant'}:").classes('font-bold')
                        ui.label(text)
        
        # Add welcome message
        add_message("Hello! I'm your assistant. How can I help you?")
        
        # Status indicator
        status = ui.label('').classes('text-sm text-gray-500')
        
        # Input area
        with ui.row().classes('w-full mt-4'):
            input_box = ui.input(placeholder='Type your message here...').classes('flex-grow')
            
            # Send message function
            def send():
                global is_sending  # Moved to beginning of function
                
                if not input_box.value or is_sending:
                    return
                
                # Get message
                message = input_box.value
                input_box.value = ''
                
                # Show user message
                add_message(message, is_user=True)
                
                # Set sending state
                is_sending = True
                send_btn.disable()
                status.text = 'Assistant is thinking...'
                
                try:
                    # Send to Ollama
                    response = ollama_service.send_message(message)
                    
                    # Show response
                    add_message(response)
                except Exception as e:
                    logger.error(f"Error sending message: {str(e)}")
                    status.text = f'Error: {str(e)}'
                
                # Reset state
                is_sending = False
                send_btn.enable()
                status.text = ''
                
            # Create send button  
            send_btn = ui.button('Send', on_click=send).props('icon=send')
            
            # Handle enter press
            def on_enter(e):
                if e.key == 'Enter' and not is_sending:
                    send()
            
            input_box.on('keydown', on_enter)

    # Run the app
    ui.run(title='Quanty Chat', port=8080)

if __name__ == '__main__':
    main() 