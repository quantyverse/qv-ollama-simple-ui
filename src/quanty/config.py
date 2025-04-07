"""
Configuration settings for the chat application.
"""
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ollama client settings
OLLAMA_MODEL = "gemma2:2b"  # Default model
OLLAMA_FALLBACK_MODELS = ["gemma:7b", "llama2:7b", "mistral:7b"]  # Fallback models if default not available
SYSTEM_MESSAGE = "You are a helpful assistant."

# UI settings
TITLE = "Quanty Chat"
CHAT_WIDTH = "800px"

logger.info(f"Config loaded with model: {OLLAMA_MODEL}")
logger.info(f"Fallback models available: {OLLAMA_FALLBACK_MODELS}")
