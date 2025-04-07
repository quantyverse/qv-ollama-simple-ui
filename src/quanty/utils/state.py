"""
State management for UI-specific aspects of the chat application.
"""

class ChatState:
    """
    Manages UI-specific state for the chat application.
    
    This complements the history management already provided by qv-ollama-sdk
    by tracking UI states like when a response is being generated and
    handling streaming responses before they're complete.
    """
    
    def __init__(self):
        self.is_thinking = False
        self.current_response = ""
    
    def start_thinking(self):
        """Set the state to indicate a response is being generated."""
        self.is_thinking = True
        self.current_response = ""
    
    def stop_thinking(self):
        """Reset the thinking state after response is complete."""
        self.is_thinking = False
        self.current_response = ""
    
    def update_current_response(self, chunk):
        """
        Add a new chunk to the current streaming response.
        
        Args:
            chunk: A text chunk from the streaming response
        """
        self.current_response += chunk
    
    def get_current_response(self):
        """
        Get the current in-progress response.
        
        Returns:
            The current streaming response text
        """
        return self.current_response

# Create a global instance
chat_state = ChatState() 