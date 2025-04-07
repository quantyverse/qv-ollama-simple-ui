"""
Simple chat app based on NiceGUI's example, integrated with Ollama LLM.
"""
from datetime import datetime
from typing import List, Tuple
import sys
import os
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Ollama service
from quanty.services.ollama_service import ollama_service

from nicegui import ui

# Message format: (user_id, avatar, text, timestamp)
messages: List[Tuple[str, str, str, str]] = []

# Constants for our chat
USER_ID = "user"
AI_ID = "assistant"
USER_AVATAR = "https://robohash.org/user?bgset=bg2"
AI_AVATAR = "https://robohash.org/assistant?bgset=bg2"

# For tracking states
is_thinking = False
needs_refresh = False  # Flag for when UI needs refreshing
last_update = 0  # Timestamp of last update
current_response = ""  # Currently streaming response

# Threading lock for safe updates
update_lock = threading.Lock()

@ui.refreshable
def chat_messages() -> None:
    """Display all chat messages."""
    global last_update
    
    # Update timestamp when refreshed
    last_update = time.time()
    
    if messages:
        for user_id, avatar, text, stamp in messages:
            ui.chat_message(text=text, stamp=stamp, avatar=avatar, sent=user_id == USER_ID)
    else:
        ui.label('No messages yet').classes('mx-auto my-36')
    
    # If AI is thinking, show current streaming response or thinking indicator
    if is_thinking:
        with update_lock:  # Safely access the current_response
            if current_response:
                # Show the streaming response as it's being generated
                ui.chat_message(
                    text=current_response,
                    stamp=datetime.now().strftime('%X'),
                    avatar=AI_AVATAR,
                    sent=False
                )
            else:
                # Show thinking indicator until first token arrives
                ui.chat_message(
                    text="Thinking...",
                    stamp=datetime.now().strftime('%X'),
                    avatar=AI_AVATAR,
                    sent=False
                )
    
    # Scroll to bottom
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')


@ui.page('/')
async def main():
    # Input element reference
    input_element = None
    
    # Function to handle streaming responses
    def handle_stream_chunk(chunk):
        """Handle a single chunk from the streaming response."""
        global current_response, needs_refresh
        
        # Update the current response with the new chunk
        with update_lock:
            # Append the chunk to our current response
            current_response += chunk
            # Set refresh flag
            needs_refresh = True
    
    # Background thread for getting AI response with streaming
    def get_ai_response_thread(message_text):
        """Function to run in a separate thread with streaming."""
        global is_thinking, needs_refresh, current_response
        
        try:
            # Reset current response
            with update_lock:
                current_response = ""
            
            # Use streaming API instead of regular chat
            full_response = ""
            for chunk in ollama_service.client.stream_chat(message_text):
                # Update the streaming display
                handle_stream_chunk(chunk)
                # Build the complete response
                full_response += chunk
                # Small delay to control refresh rate
                time.sleep(0.01)
            
            # Add the complete message to history
            ai_stamp = datetime.now().strftime('%X')
            messages.append((AI_ID, AI_AVATAR, full_response, ai_stamp))
        except Exception as e:
            # Add error message
            ai_stamp = datetime.now().strftime('%X')
            messages.append((AI_ID, AI_AVATAR, f"Error: {str(e)}", ai_stamp))
        finally:
            # Reset thinking state and current response
            with update_lock:
                is_thinking = False
                current_response = ""
                needs_refresh = True
    
    def send() -> None:
        """Send a message and trigger AI response in a background thread."""
        global is_thinking
        
        # Get message text
        message_text = input_element.value
        if not message_text or is_thinking:
            return
            
        # Clear input
        input_element.value = ''
        
        # Add user message
        stamp = datetime.now().strftime('%X')
        messages.append((USER_ID, USER_AVATAR, message_text, stamp))
        
        # Set thinking state
        is_thinking = True
        
        # Refresh chat to show user message and thinking indicator
        chat_messages.refresh()
        
        # Start a background thread to get AI response
        threading.Thread(target=get_ai_response_thread, args=(message_text,), daemon=True).start()
    
    # Timer function to check for updates - with faster refresh rate for streaming
    def check_updates():
        """Check if we need to refresh the UI."""
        global needs_refresh
        if needs_refresh:
            # Reset flag first to avoid race conditions
            with update_lock:
                needs_refresh = False
            # Refresh the UI
            chat_messages.refresh()
    
    # Header with title
    with ui.header().classes('bg-primary text-white'):
        ui.label('Quanty Chat').classes('text-xl')

    # Main content area
    with ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        await ui.context.client.connected()
        chat_messages()
        
        # Add timer to check for updates - faster refresh rate for streaming
        ui.timer(0.1, check_updates)  # 100ms for more responsive streaming

    # Footer with input area
    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar():
                ui.image(USER_AVATAR)
            input_element = ui.input(placeholder='Type your message...').props('rounded outlined input-class=mx-3').classes('flex-grow')
            ui.button('Send', on_click=send).props('icon=send')
            
        # Connect enter key to send
        input_element.on('keydown.enter', send)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title="Quanty Chat", port=8080)