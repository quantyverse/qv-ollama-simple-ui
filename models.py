"""
Model management and configuration for the chat application.
"""
import ollama
from qv_ollama_sdk import OllamaChatClient
from typing import Dict, List

# Default model configuration
DEFAULT_MODEL = "gemma2:2b"
SYSTEM_MESSAGE = "You are a helpful assistant that can answer questions and help with tasks."

class ModelManager:
    def __init__(self):
        self.current_model = DEFAULT_MODEL
        self.model_data = {'current_model': DEFAULT_MODEL}
        self.client = self._initialize_client()

    def _initialize_client(self, model_name: str = None) -> OllamaChatClient:
        """Initialize the Ollama client with the specified model."""
        if model_name is None:
            model_name = self.model_data['current_model']
        
        return OllamaChatClient(
            model_name=model_name,
            system_message=SYSTEM_MESSAGE
        )

    def get_available_models(self) -> List[Dict]:
        """Get all available models from Ollama."""
        try:
            models = ollama.list()
            return models.get('models', [])
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            return []

    def switch_model(self, model_name: str) -> None:
        """Switch to a different model."""
        if model_name != self.model_data['current_model']:
            self.model_data['current_model'] = model_name
            self.current_model = model_name
            self.client = self._initialize_client(model_name)

    def get_client(self) -> OllamaChatClient:
        """Get the current Ollama client instance."""
        return self.client

    def get_model_data(self) -> Dict:
        """Get the current model data dictionary."""
        return self.model_data 