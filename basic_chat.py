"""
Extremely basic chat UI that only uses button interaction
"""
from nicegui import ui
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the service
from quanty.services.ollama_service import ollama_service

# Run the app
def main():
    # Basic UI
    ui.label('Quanty Chat').style('font-weight: bold')
    
    # Message display
    messages_area = ui.column().style('width: 100%; min-height: 300px; border: 1px solid #ccc; padding: 8px')
    
    # Initial message
    with messages_area:
        ui.label('Welcome to Quanty Chat!')
    
    # Simple input
    input_box = ui.input('Your message')
    
    # Simple button
    button = ui.button('Send')
    
    # Send message
    def send_message():
        text = input_box.value
        if not text:
            return
            
        # Clear input
        input_box.value = ''
        
        # Add user message
        with messages_area:
            ui.label(f'You: {text}')
        
        # Disable button during processing
        button.disable()
        
        try:
            # Get response
            response = ollama_service.send_message(text)
            
            # Add AI message
            with messages_area:
                ui.label(f'AI: {response}')
        except Exception as e:
            # Show error
            with messages_area:
                ui.label(f'Error: {str(e)}')
        
        # Re-enable button
        button.enable()
    
    # Connect button
    button.on_click(send_message)

# Start app
ui.run(title='Basic Chat')
main() 