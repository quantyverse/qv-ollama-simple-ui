"""
Configuration and constants for the chat application.
"""

# Application settings
APP_TITLE = "QV Simple Ollama UI"
APP_PORT = 8080

# Chat settings
USER_ID = "user"
AI_ID = "assistant"

# Message format: (user_id, text, timestamp)
MESSAGE_FORMAT = "({user_id}, {text}, {timestamp})"

# UI settings
MAX_WIDTH = "3xl"  # Tailwind max-width class
MARGIN_Y = "my-6"  # Vertical margin class
MARGIN_X = "mx-auto"  # Horizontal margin class

# Model dialog settings
MODEL_DIALOG_MIN_WIDTH = "500px"
MODEL_DIALOG_MAX_WIDTH = "90vw"

# Streaming settings
STREAMING_DELAY = 0.01  # Delay between streaming chunks in seconds

# Error messages
NO_MODELS_FOUND_MSG = "No models found. Please install models using Ollama."
MODEL_SWITCH_SUCCESS_MSG = "Switched to model: {model_name}" 