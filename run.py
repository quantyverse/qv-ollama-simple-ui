"""
Simple run script to start the Quanty chat application.
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)
logger.info(f"Added {src_path} to Python path")

try:
    # Import the UI and app
    from nicegui import ui, app
    from quanty.config import TITLE
    
    # Import components
    from quanty.components.chat_container import chat_container
    from quanty.services.ollama_service import ollama_service
    from quanty.utils.state import chat_state
    
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
                ui.label(TITLE).classes('text-2xl font-bold')
                
                # Connection status indicator
                conn_status = ui.label('Connected').classes('text-green-500 text-sm')
                
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
            
            # Add the main chat container in a card
            with ui.card().classes('w-full p-4 max-w-[800px] mx-auto'):
                chat_container()
    
    def main():
        """Main application entry point."""
        try:
            logger.info("Starting Quanty Chat application")
            
            # Check Ollama connection
            try:
                history = ollama_service.get_history()
                logger.info(f"Ollama connected, history has {len(history)} messages")
            except Exception as e:
                logger.warning(f"Ollama connection issue: {str(e)}")
            
            # Initialize the UI
            init_ui()
            
            # Start the UI with explicit settings
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
            logger.critical(f"Error starting application: {str(e)}", exc_info=True)
            sys.exit(1)
    
    if __name__ == '__main__':
        main()
        
except Exception as e:
    logger.critical(f"Failed to import or initialize: {str(e)}", exc_info=True)
    print(f"ERROR: {str(e)}")
    sys.exit(1) 