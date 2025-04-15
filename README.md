# Simple Ollama Chat UI

A simple chat interface for interacting with Ollama LLM models. This project serves as a starting point for building chat applications with Ollama and NiceGUI.

## Features
- Chat with different Ollama models
- Real-time streaming responses
- Clean and modern UI
- Easy model switching
- Download Ollama models

## Setup
1. Install Ollama: https://ollama.com/
2. Install Python dependencies (using either pip or uv):
```bash
# Using pip
pip install nicegui ollama qv_ollama_sdk

# Using uv (faster)
uv add nicegui ollama qv_ollama_sdk
```
3. Run the application:
```bash
python simple_chat_app.py

# using uv
uv run simple_chat_app.py
```

## Usage
- Type your message and press Enter or click Send
- Click "Models" to switch between different Ollama models
- Messages are displayed in real-time as they're generated

## Troubleshooting
- If you encounter connection issues, ensure Ollama is running
- Check that you have the required models downloaded in Ollama
- For UI issues, try clearing your browser cache

## Project Structure
```
src/
├── components/     # UI components
│   ├── chat.py     # Chat interface
│   ├── dialogs.py  # Dialog windows
│   ├── footer.py   # Footer component
│   └── header.py   # Header component
├── services/       # Core services
│   └── models.py   # Model management
├── config/         # Configuration
│   └── config.py   # App settings
└── styles/         # Styling
    └── styles.py   # UI styles
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
