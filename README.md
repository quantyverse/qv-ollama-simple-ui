# Simple Ollama Chat UI

A simple chat interface for interacting with Ollama LLM models.

## Features
- Chat with different Ollama models
- Real-time streaming responses
- Clean and modern UI
- Easy model switching

## Setup
1. Install Ollama: https://ollama.ai/
2. Install Python dependencies:
```bash
pip install nicegui ollama
```
3. Run the application:
```bash
python simple_chat_app.py
```

## Usage
- Type your message and press Enter or click Send
- Click "Models" to switch between different Ollama models
- Messages are displayed in real-time as they're generated

## Project Structure
- `simple_chat_app.py` - Main application
- `chat.py` - Chat functionality
- `models.py` - Model management
- `styles.py` - UI styling
- `config.py` - Configuration settings
