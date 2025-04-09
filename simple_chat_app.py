"""
Simple chat app based on NiceGUI's example, integrated with Ollama LLM.
"""
from datetime import datetime
from typing import List, Tuple
import sys
import os
import threading
import time
import ollama

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Ollama client directly
from qv_ollama_sdk import OllamaChatClient


from nicegui import ui, app
OLLAMA_MODEL = "gemma2:2b"  # Default model
SYSTEM_MESSAGE = "You are a helpful assistant that can answer questions and help with tasks."

# Message format: (user_id, text, timestamp)
messages: List[Tuple[str, str, str]] = []

# Constants for our chat
USER_ID = "user"
AI_ID = "assistant"

# For tracking AI response generation
is_thinking = False
current_response = ""  # Currently streaming response
message_completed = False  # Flag to indicate message just completed

# Threading lock for safe updates
update_lock = threading.Lock()

# Model data dictionary for binding
model_data = {'current_model': OLLAMA_MODEL}

# Custom CSS to remove the chat bubble triangles and ensure proper alignment
custom_css = """
/* Import Roboto font */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
/* Import Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* Apply Roboto to text elements but not icons */
body, input, button, div, span, p, h1, h2, h3, h4, h5, h6, label, textarea {
    font-family: 'Roboto', sans-serif !important;
}

/* Preserve Material Icons font */
.material-icons, .q-icon, .material-symbols-outlined {
    font-family: 'Material Icons', 'Material Symbols Outlined' !important;
}

/* Remove bubble triangles */
.q-message-text:before {
    display: none !important;
}

/* Ensure proper message alignment */
.q-message-sent {
    margin-left: auto !important;
    margin-right: 8px !important;
}

.q-message-received {
    margin-right: auto !important;
    margin-left: 8px !important;
}

/* Custom assistant message bubble color */
.q-message-received .q-message-text {
    background-color: #3bebff !important;
    color: white !important;
}

/* Make sure markdown content is visible */
.q-message-text .nicegui-markdown {
    width: 100%;
    color: inherit !important;
}

/* Style markdown code blocks */
.q-message-text pre {
    background-color: rgba(0, 0, 0, 0.1) !important;
    border-radius: 4px;
    padding: 8px !important;
    margin: 8px 0 !important;
    overflow-x: auto;
}

.q-message-text code {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 0.9em;
}

/* Custom header color */
.custom-header {
    background-color: #145068 !important;
}

/* Custom button color */
.custom-button {
    background-color: #145068 !important;
    color: white !important;
}

/* Add a bit more space between messages */
.q-message {
    margin-bottom: 8px !important;
}

/* Model list styling */
.model-list {
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 12px;
}

.model-item {
    padding: 8px 12px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.model-item:hover {
    background-color: rgba(20, 80, 104, 0.1);
}

.model-item.selected {
    background-color: rgba(20, 80, 104, 0.2);
    border-left: 4px solid #145068;
}

.model-item:last-child {
    border-bottom: none;
}

.model-name {
    font-weight: bold;
}

.model-meta {
    font-size: 0.8em;
    color: #666;
}

/* Header buttons */
.header-button {
    margin-left: 12px;
    background-color: #145068 !important;
    box-shadow: none !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: white !important;
}

/* Flat button with no elevation */
.q-btn--flat {
    box-shadow: none !important;
}

/* Badge for selected model */
.model-badge {
    padding: 2px 8px;
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.2);
    font-size: 0.8em;
    margin-left: 8px;
}
"""

# Function to get all available models
def get_available_models():
    try:
        models = ollama.list()
        return models.get('models', [])
    except Exception as e:
        print(f"Error fetching models: {str(e)}")
        return []

# Initialize the ollama client - this function will be called whenever model changes
def initialize_client(model_name=None):
    if model_name is None:
        model_name = model_data['current_model']
    
    # Create a new client with the selected model
    return OllamaChatClient(
        model_name=model_name,
        system_message=SYSTEM_MESSAGE
    )

# Initialize the client with default model
ollama_client = initialize_client()

@ui.refreshable
def model_list_component(dialog):
    """Display all available models with selection ability."""
    models = get_available_models()
    current_model = model_data['current_model']
    
    with ui.card().classes('w-full model-list'):
        with ui.row():
            ui.label('Available Models').classes('text-xl font-bold')
            ui.space()
            ui.button('Refresh', on_click=lambda: model_list_component.refresh(dialog), icon='refresh').props('flat').classes('custom-button')
            ui.button('Close', on_click=dialog.close, icon='close').props('flat')
            
        if models:
            for model in models:
                model_name = model.get('model', 'Unknown')
                is_selected = model_name == current_model
                
                # Function to select this model
                def select_model(model_to_select=model_name):
                    global ollama_client, messages
                    
                    # Only process if actually changing models
                    if model_to_select != model_data['current_model']:
                        # Update the model data - this will trigger the binding update
                        model_data['current_model'] = model_to_select
                        
                        # Clear the message history
                        messages.clear()
                        
                        # Update the client
                        ollama_client = initialize_client(model_to_select)
                        
                        # Refresh the chat display
                        chat_messages.refresh()
                        
                        # Show notification
                        ui.notify(f'Switched to model: {model_to_select}', color='positive')
                    
                    # Refresh this component to update selection indicators
                    model_list_component.refresh(dialog)
                    
                    # Close the dialog
                    dialog.close()
                
                with ui.card().classes(f'model-item {"selected" if is_selected else ""}').on('click', select_model):
                    with ui.row():
                        ui.label(model_name).classes('model-name')
                        if is_selected:
                            ui.label('ACTIVE').classes('text-positive text-bold q-ml-sm')
                    size_mb = model.get('size', 0) / (1024 * 1024)
                    ui.label(f"Size: {size_mb:.1f} MB").classes('model-meta')
        else:
            ui.label('No models found. Please install models using Ollama.').classes('p-4')

# Dictionary to store markdown components for streaming updates
markdown_components = {}
streaming_message = None

@ui.refreshable
def chat_messages() -> None:
    """Display all chat messages."""
    global markdown_components, streaming_message, message_completed
    
    # Clear the components dictionary at the start of refresh
    markdown_components = {}
    
    if messages:
        for i, (user_id, text, stamp) in enumerate(messages):
            if user_id == USER_ID:
                # User messages are simple text
                ui.chat_message(text=text, stamp=stamp, avatar=None, sent=True)
            else:
                # AI messages use markdown
                with ui.chat_message(stamp=stamp, avatar=None, sent=False) as msg:
                    # Create a markdown component and store it with a unique ID
                    msg_id = f"message_{i}"
                    markdown_components[msg_id] = ui.markdown(text)
    else:
        ui.label('No messages yet').classes('mx-auto my-36')
    
    # If AI is thinking, show current streaming response
    if is_thinking:
        with update_lock:
            response_text = current_response if current_response else "Thinking..."
            
            with ui.chat_message(stamp=datetime.now().strftime('%X'), avatar=None, sent=False) as msg:
                # Store the message container for later removal
                streaming_message = msg
                # Use a unique ID for the streaming component
                msg_id = "streaming"
                markdown_components[msg_id] = ui.markdown(response_text)
    
    # Scroll to bottom only while streaming or after user sends message
    if is_thinking or message_completed:
        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
        # Reset completion flag after scrolling
        message_completed = False


@ui.page('/')
async def main():
    # Add custom CSS to the page
    ui.add_head_html(f'<style>{custom_css}</style>')
    
    # Input element reference
    input_element = None
    
    # Create dialog for models
    models_dialog = ui.dialog()
    with models_dialog:
        with ui.card().classes('w-full').style('min-width: 500px; max-width: 90vw;'):
            model_list_component(models_dialog)
    
    # Function to open models dialog
    def show_models_dialog():
        models_dialog.open()
        model_list_component.refresh(models_dialog)
    
    # Function to update streaming content without full refresh
    def update_streaming_content(text):
        """Update the streaming response markdown content without refreshing."""
        if "streaming" in markdown_components:
            markdown_components["streaming"].content = text
    
    # Background thread for getting AI response with streaming
    def get_ai_response_thread(message_text):
        """Function to run in a separate thread with streaming."""
        global is_thinking, current_response, streaming_message, message_completed
        
        try:
            # Reset current response
            with update_lock:
                current_response = ""
            
            # Use streaming API
            full_response = ""
            for chunk in ollama_client.stream_chat(message_text):
                # Update the streaming display
                with update_lock:
                    current_response += chunk
                    # Update just the streaming markdown component
                    update_streaming_content(current_response)
                
                # Build the complete response
                full_response += chunk
                # Small delay to control refresh rate
                time.sleep(0.01)
            
            # Get the timestamp before we change state
            ai_stamp = datetime.now().strftime('%X')
            
            # Create a temporary copy of the full response
            final_response = full_response
            
            # Update our state variables in a thread-safe way
            with update_lock:
                # First reset thinking state to prevent the streaming message from reappearing
                is_thinking = False
                current_response = ""
                # Set completion flag to trigger one final scroll
                message_completed = True
                
                # Now add the message to history
                messages.append((AI_ID, final_response, ai_stamp))
            
        except Exception as e:
            # Add error message
            ai_stamp = datetime.now().strftime('%X')
            error_msg = str(e)
            
            # Update our state variables in a thread-safe way
            with update_lock:
                # Reset thinking state
                is_thinking = False
                current_response = ""
                # Set completion flag to trigger one final scroll
                message_completed = True
                
                # Add error message to history
                messages.append((AI_ID, f"Error: {error_msg}", ai_stamp))
    
    def send() -> None:
        """Send a message and trigger AI response in a background thread."""
        global is_thinking, message_completed
        
        # Get message text
        message_text = input_element.value
        if not message_text or is_thinking:
            return
            
        # Clear input
        input_element.value = ''
        
        # Add user message
        stamp = datetime.now().strftime('%X')
        messages.append((USER_ID, message_text, stamp))
        
        # Set thinking state
        is_thinking = True
        message_completed = True  # Trigger scroll for user message
        
        # Refresh chat to show user message and thinking indicator
        chat_messages.refresh()
        
        # Start a background thread to get AI response
        threading.Thread(target=get_ai_response_thread, args=(message_text,), daemon=True).start()
    
    # Header with title and model button
    with ui.header().classes('custom-header text-white'):
        with ui.row().classes('w-full items-center'):
            ui.label('QV Simple Ollama UI').classes('text-xl')
            # Create model label with binding from model_data
            ui.label().bind_text_from(
                model_data, 
                'current_model',
                backward=lambda name: f"Model: {name}"
            ).classes('model-badge')
            ui.space()
            ui.button('Models', on_click=show_models_dialog, icon='list').props('flat').classes('header-button')

    # Main content area 
    with ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        await ui.context.client.connected()
        chat_messages()
        
        # Simple timer for regular UI updates during streaming
        ui.timer(0.1, chat_messages.refresh)

    # Footer with input area
    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            input_element = ui.input(placeholder='Type your message...').props('rounded outlined input-class=mx-3').classes('flex-grow')
            ui.button('Send', on_click=send).props('icon=send').classes('custom-button')
            
        # Connect enter key to send
        input_element.on('keydown.enter', send)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title="QV Simple Ollama UI", port=8080)