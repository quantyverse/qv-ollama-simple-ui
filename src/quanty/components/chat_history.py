"""
Component for displaying the chat conversation history.
"""
from nicegui import ui
import traceback
import logging

from src.quanty.services.ollama_service import ollama_service
from src.quanty.utils.state import chat_state
from src.quanty.components.message_bubble import message_bubble, update_message_content

# Configure logging
logger = logging.getLogger(__name__)

class ChatHistory:
    """Component that displays the conversation history with streaming support."""
    
    def __init__(self):
        """Initialize the chat history component."""
        logger.info("Initializing ChatHistory component")
        # Create a scrollable container with visible border for debugging
        self.container = ui.column().classes('w-full gap-2 overflow-y-auto border border-gray-200 p-2 min-h-[300px]')
        self.streaming_message = None
        self.last_content = ""
        self.is_first_update = True
        self.last_history_count = 0
        
        # Create a test message to verify UI is working
        with self.container:
            self.status_label = ui.label("Chat interface initialized. Waiting for messages...").classes('italic text-gray-500 text-center p-4')
            
            # Add a visible debug counter
            self.debug_counter = ui.label("Messages: 0").classes('text-xs text-gray-400 text-center')
        
        # Start the update timer
        logger.debug("Starting update timer")
        ui.timer(0.5, self.update)
    
    def update(self):
        """Update the chat history display based on current state."""
        try:
            logger.debug("ChatHistory update triggered")
            
            history = ollama_service.get_history()
            current_response = chat_state.get_current_response()
            is_thinking = chat_state.is_thinking
            
            # Update debug counter
            self.debug_counter.text = f"Messages: {len(history)} | Streaming: {is_thinking}"
            
            # Log the current state
            logger.debug(f"History: {len(history)} messages, is_thinking: {is_thinking}, current_response length: {len(current_response) if current_response else 0}")
            
            # Force rebuild if history length changed or first update
            if self.is_first_update or len(history) != self.last_history_count:
                logger.info(f"History count changed from {self.last_history_count} to {len(history)} - rebuilding")
                self._rebuild_all_messages(history, current_response, is_thinking)
                self.is_first_update = False
                self.last_history_count = len(history)
                return
                
            # Check if we need to update the streaming message
            if is_thinking:
                if not self.streaming_message:
                    # Clear the initial status message if it's still there
                    if self.status_label and self.status_label in self.container.children:
                        self.status_label.delete()
                        self.status_label = None
                    
                    # Create new streaming message
                    logger.debug("Creating new streaming message")
                    self.streaming_message = message_bubble(
                        content=current_response or "Thinking...",
                        is_user=False,
                        is_streaming=True
                    )
                    self.last_content = current_response
                    # Add to container explicitly
                    self.container.append(self.streaming_message)
                elif current_response != self.last_content:
                    # Update existing streaming message
                    try:
                        logger.debug(f"Updating streaming message, new length: {len(current_response)}")
                        update_message_content(self.streaming_message, current_response)
                        self.last_content = current_response
                    except Exception as e:
                        logger.error(f"Error updating message: {str(e)}")
                        logger.error(traceback.format_exc())
                        
                        # On error, force a rebuild
                        self._rebuild_all_messages(history, current_response, is_thinking)
            else:
                # If thinking stopped and we had a streaming message, refresh the whole view
                if self.streaming_message:
                    logger.info("Thinking stopped, rebuilding messages")
                    # Remove the streaming message
                    if self.streaming_message in self.container.children:
                        self.streaming_message.delete()
                    self.streaming_message = None
                    self._rebuild_all_messages(history, "", False)
        except Exception as e:
            # Handle any exceptions in the update method
            logger.error(f"Error in ChatHistory.update: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Add error directly to UI for visibility
            try:
                with self.container:
                    ui.label(f"Error: {str(e)}").classes('text-red-500')
            except:
                pass
    
    def _rebuild_all_messages(self, history, current_response, is_thinking):
        """Rebuild all messages from scratch."""
        try:
            logger.debug(f"Rebuilding all messages - history size: {len(history)}")
            
            # Clear the container but keep debug counter
            temp_counter = self.debug_counter
            self.container.clear()
            
            with self.container:
                # Add back the debug counter
                self.debug_counter = temp_counter
                
                # Show a message if history is empty
                if not history:
                    self.status_label = ui.label("No messages yet. Type something below to start.").classes('italic text-gray-500 text-center p-4')
                else:
                    self.status_label = None
                
                # Add all messages from history with explicit content logging
                for i, msg in enumerate(history):
                    is_user = msg.get('role') == 'user'
                    content = msg.get('content', '')
                    logger.debug(f"Adding message {i+1}: role={msg.get('role')}, content={content[:30]}{'...' if len(content) > 30 else ''}")
                    
                    bubble = message_bubble(
                        content=content,
                        is_user=is_user
                    )
                    # No need to append, already in container due to "with self.container:"
                
                # Add streaming message if needed
                if is_thinking and current_response:
                    logger.debug(f"Adding streaming message, length: {len(current_response)}")
                    self.streaming_message = message_bubble(
                        content=current_response,
                        is_user=False,
                        is_streaming=True
                    )
                    self.last_content = current_response
                else:
                    self.streaming_message = None
        except Exception as e:
            logger.error(f"Error rebuilding messages: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Add an error message to make it visible something went wrong
            with self.container:
                ui.label(f"Error displaying messages: {str(e)}").classes('text-red-500')

def chat_history():
    """
    Create and return a chat history component.
    
    Returns:
        The chat history UI element
    """
    logger.info("Creating chat history component")
    history = ChatHistory()
    return history.container 