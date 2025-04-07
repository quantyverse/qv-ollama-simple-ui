"""
Ultra basic chat app with minimal features
"""
from nicegui import ui
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the service
from quanty.services.ollama_service import ollama_service

# Add a container with scrolling for the messages
with ui.card().classes('w-full h-[400px] overflow-auto p-4') as scroll_container:
    # Simple column to show messages
    messages_area = ui.column().classes('w-full gap-2')  # Added gap for spacing
    
    # Simple welcome message
    with messages_area:
        ui.label('Welcome to Quanty Chat!').classes('text-lg font-bold')

# Status indicator
status_text = ui.label('').classes('italic text-sm text-gray-500')

# Basic input and button in a row for better alignment
with ui.row().classes('w-full items-end gap-2'):
    text_input = ui.input('Message').classes('flex-grow')
    button = ui.button('Send').classes('bg-blue-500')

# Simple send function
def send():
    message = text_input.value
    if not message:
        return
        
    # Immediately clear input so user sees the change
    text_input.value = ""
    
    # Immediately display user message with clear separation
    with messages_area:
        ui.label(f"You: {message}").classes('font-bold text-blue-600 p-2 rounded bg-blue-50')
    
    # Force UI update to ensure message is visible
    ui.update()
    
    # Scroll to bottom to show new message
    ui.run_javascript(f"document.querySelector('.overflow-auto').scrollTop = document.querySelector('.overflow-auto').scrollHeight")
    
    # Disable button while processing - do this after showing the message
    button.disable()
    
    # Visual indicator that AI is thinking (with its own UI element)
    status_text.text = "Assistant is thinking..."
    thinking_indicator = None
    with messages_area:
        thinking_indicator = ui.label("Assistant is thinking...").classes('text-gray-500 italic p-2')
    
    # Force another UI update and scroll to ensure thinking indicator is visible
    ui.update()
    ui.run_javascript(f"document.querySelector('.overflow-auto').scrollTop = document.querySelector('.overflow-auto').scrollHeight")
    
    try:
        # Get response
        response = ollama_service.send_message(message)
        
        # Remove thinking indicator
        if thinking_indicator:
            thinking_indicator.delete()
        
        # Show AI response as a separate, clearly distinguished message
        with messages_area:
            ui.label(f"AI: {response}").classes('text-green-600 p-2 rounded bg-green-50')
        
        # Clear status
        status_text.text = ""
        
        # Scroll to bottom again to show AI response
        ui.run_javascript(f"document.querySelector('.overflow-auto').scrollTop = document.querySelector('.overflow-auto').scrollHeight")
    except Exception as e:
        # Remove thinking indicator
        if thinking_indicator:
            thinking_indicator.delete()
            
        # Show error
        with messages_area:
            ui.label(f"Error: {str(e)}").classes('text-red-500 p-2 rounded bg-red-50')
        
        # Update status
        status_text.text = "Error occurred"
    
    # Re-enable button
    button.enable()

# Connect button to function
button.on_click(send)

# Also connect Enter key to send
def on_key(e):
    if hasattr(e, 'key') and e.key == 'Enter':
        send()

# Try different event names that might be supported
try:
    text_input.on('keydown', on_key)
except:
    try:
        text_input.on('keypress', on_key)
    except:
        pass  # Ignore if neither works

# Start the app
ui.run(port=8080, title="Quanty Chat") 