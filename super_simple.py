"""
Super simple chat application with absolutely minimal UI
"""
from nicegui import ui
import sys
import os

# Basic setup - just add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Ollama service
from quanty.services.ollama_service import ollama_service

# Main function
def main():
    # Title
    ui.label('Quanty Chat').style('font-size: 24px; font-weight: bold;')
    
    # Chat display - using a simple div instead of textarea
    with ui.card().style('width: 100%; height: 300px; overflow-y: auto; padding: 10px;'):
        chat_container = ui.column()
        
        # Add welcome message
        with chat_container:
            ui.label("Welcome! Type a message below to chat with the assistant.")
    
    # Input field
    message_input = ui.input(placeholder='Type your message here')
    
    # Button without any fancy icons or classes
    send_button = ui.button('Send')
    
    # Simple is_busy flag
    busy = False
    
    # Function to add message to chat
    def add_message(text, is_user=False):
        with chat_container:
            sender = "You" if is_user else "AI"
            ui.label(f"{sender}: {text}")
    
    # Actual functionality
    def on_send():
        nonlocal busy
        
        # Don't allow multiple sends
        if busy:
            return
            
        # Get message
        message = message_input.value
        if not message:
            return
            
        # Clear input
        message_input.value = ""
        
        # Add to display
        add_message(message, is_user=True)
        
        # Set busy
        busy = True
        send_button.disable()
        
        try:
            # Get response
            response = ollama_service.send_message(message)
            
            # Add to display
            add_message(response)
        except Exception as e:
            # Show error
            add_message(f"Error: {str(e)}")
        
        # Reset state
        busy = False
        send_button.enable()
    
    # Connect function to button
    send_button.on_click(on_send)
    
    # Handle Enter key press using a proper approach for this version of NiceGUI
    # Using keypress event directly on the form rather than keydown event
    with ui.element('script').bind_content_from(message_input, 'value'):
        '''
        element.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                // Use the Quasar UI framework's API to call the button click handler
                document.querySelector('button').click();
            }
        });
        '''
        
# Run the app
ui.run(title='Super Simple Chat')
main() 