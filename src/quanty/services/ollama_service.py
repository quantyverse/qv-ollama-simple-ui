"""
Service for interacting with Ollama models via qv-ollama-sdk.
"""
from qv_ollama_sdk import OllamaChatClient
import traceback
import time
import logging

from src.quanty.config import OLLAMA_MODEL, SYSTEM_MESSAGE
from src.quanty.utils.state import chat_state

# Configure logging
logger = logging.getLogger(__name__)

class OllamaService:
    """
    Service for interacting with Ollama models.
    
    Acts as an adapter between qv-ollama-sdk and our UI,
    updating UI state and providing a simplified interface
    for UI components.
    """
    
    def __init__(self, model_name=OLLAMA_MODEL, system_message=SYSTEM_MESSAGE):
        """
        Initialize the service with configuration from config.py.
        
        Args:
            model_name: The Ollama model to use
            system_message: System prompt to use for the conversation
        """
        logger.info(f"Initializing OllamaService with model: {model_name}")
        try:
            self.client = OllamaChatClient(
                model_name=model_name,
                system_message=system_message
            )
            logger.info("OllamaChatClient initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OllamaChatClient: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def send_message(self, message):
        """
        Send a message and stream the response with UI state updates.
        
        Args:
            message: The user message to send
            
        Returns:
            The complete response text
        """
        logger.info(f"Sending message: '{message[:30]}...' (truncated)")
        
        # Set UI state to "thinking"
        chat_state.start_thinking()
        logger.debug("Set chat_state.is_thinking = True")
        
        try:
            # Try to send the message
            response = ""
            
            logger.debug("Starting streaming response")
            chunk_count = 0
            
            for chunk in self.client.stream_chat(message):
                chunk_count += 1
                response += chunk
                chat_state.update_current_response(chunk)
                
                # Add a small delay to prevent UI freezing
                time.sleep(0.01)
                
                # Log progress occasionally
                if chunk_count % 50 == 0:
                    logger.debug(f"Received {chunk_count} chunks, current length: {len(response)} chars")
            
            logger.info(f"Completed message, received {chunk_count} chunks, response length: {len(response)} chars")
            return response
        except Exception as e:
            # Handle any exceptions
            error_msg = f"Error communicating with Ollama: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Update the response with the error
            chat_state.update_current_response(f"\n\nError: {error_msg}")
            return error_msg
        finally:
            # Always reset UI state
            logger.debug("Set chat_state.is_thinking = False")
            chat_state.stop_thinking()
    
    def get_history(self):
        """
        Get the conversation history from the SDK.
        
        Returns:
            List of message dictionaries
        """
        try:
            history = self.client.get_history()
            logger.debug(f"Retrieved history with {len(history)} messages")
            return history
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            logger.error(traceback.format_exc())
            return []

# Create a global instance
logger.info("Creating global OllamaService instance")
ollama_service = OllamaService() 