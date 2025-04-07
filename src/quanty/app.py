"""
Main application entry point for the chat interface.
"""
from nicegui import ui, app
import sys
import os
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now import from the modules
from src.quanty.config import TITLE
from src.quanty.components.chat_container import chat_container
from src.quanty.services.ollama_service import ollama_service

def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    try:
        # Try to get the history as a simple test
        logger.debug("Testing Ollama connection...")
        ollama_service.get_history()
        logger.info("Successfully connected to Ollama")
        return True, "Connected to Ollama successfully"
    except Exception as e:
        error_msg = f"Error connecting to Ollama: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg

def test_ollama():
    """Test Ollama connection and show result in notification."""
    try:
        logger.debug("Manual Ollama connection test triggered")
        success, message = check_ollama_connection()
        if success:
            ui.notify(message, type='positive')
        else:
            ui.notify(message, type='negative', timeout=10000)
            
        # Also test sending a simple message
        logger.debug("Testing sending a message to Ollama...")
        response = ollama_service.send_message("Hello, is Ollama working?")
        ui.notify(f"Test message response received: {len(response)} characters", type='positive')
    except Exception as e:
        error_msg = f"Error testing Ollama: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        ui.notify(error_msg, type='negative', timeout=10000)

def print_startup_message(host, port):
    """Print a clear message about where the app is running."""
    url = f"http://{host}:{port}"
    border = "=" * (len(url) + 14)
    message = f"""
{border}
   App URL: {url}   
{border}
"""
    print(message)
    logger.info(f"NiceGUI server started at {url}")

def init_ui():
    """Initialize the user interface."""
    # Set the page title
    ui.page_title(TITLE)
    
    # Add connection handling
    @ui.page('/')
    def page_index():
        # Create a header with status
        with ui.header().classes('items-center justify-between'):
            with ui.row().classes('items-center'):
                ui.label(TITLE).classes('text-2xl font-bold')
                
                # Test button
                ui.button('Test Ollama', on_click=test_ollama).classes('ml-4')
                
                # Connection status indicator
                ui.label('Connected').classes('text-green-500 text-sm ml-4')
                
            # Add reconnection handling
            @ui.run_javascript
            def handle_disconnect():
                return '''
                document.addEventListener('disconnect', () => {
                    console.log('Connection lost, will auto-reconnect');
                });
                document.addEventListener('reconnect', () => {
                    console.log('Reconnected successfully');
                    location.reload();  // Force page reload on reconnect
                });
                '''
        
        # Check Ollama connection
        ollama_ok, message = check_ollama_connection()
        
        # Show connection status
        with ui.column().classes('w-full p-4'):
            with ui.card().classes('w-full mb-4'):
                with ui.row().classes('items-center'):
                    status_color = 'green' if ollama_ok else 'red'
                    ui.icon('circle', color=status_color)
                    ui.label(f'Ollama Status: {"Connected" if ollama_ok else "Disconnected"}')
                    ui.label(message).classes('ml-2 text-sm')
                
                if not ollama_ok:
                    ui.separator()
                    ui.markdown("""
                    ## Troubleshooting:
                    1. Make sure Ollama is installed and running
                    2. Check that the model specified in config.py is available
                    3. Try running `ollama serve` in a separate terminal
                    4. Click the "Test Ollama" button to try again
                    """)
        
        # Add the main content with padding
        with ui.column().classes('w-full p-4'):
            chat_container()

def main():
    """Main application entry point."""
    try:
        logger.info("Starting Quanty Chat application")
        # Initialize the UI
        init_ui()
        
        # Start the UI
        logger.info("Starting NiceGUI server")
        host = '127.0.0.1'
        port = 8080
        print_startup_message(host, port)
        
        # Enable reconnect with a longer timeout
        app.on_shutdown(lambda: logger.info("Shutting down NiceGUI app"))
        app.on_connect(lambda client: logger.info(f"Client connected: {client.id}"))
        app.on_disconnect(lambda client: logger.info(f"Client disconnected: {client.id}"))
        
        ui.run(
            title=TITLE,
            reload=False,
            host=host,
            port=port,
            show=False,
            reconnect_timeout=10,  # Increase reconnect timeout
            tailwind=True  # Ensure Tailwind is enabled
        )
    except Exception as e:
        logger.critical(f"Error starting application: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
