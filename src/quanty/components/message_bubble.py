"""
Component for displaying individual chat messages using very basic elements.
"""
from nicegui import ui
import logging

# Configure logging
logger = logging.getLogger(__name__)

def message_bubble(content, is_user=False, is_streaming=False, name=None):
    """
    Create a chat message bubble for the conversation.
    
    Args:
        content: The message text content
        is_user: Whether this is a user message (True) or assistant message (False)
        is_streaming: Whether this message is currently being streamed
        name: Optional name to display
        
    Returns:
        The message container UI element
    """
    logger.debug(f"Creating message bubble: user={is_user}, streaming={is_streaming}, content_length={len(content)}")
    
    # Determine styling based on sender
    align = 'flex-end' if is_user else 'flex-start'
    bg_color = '#e6f3ff' if is_user else '#f0f0f0'  # Basic colors instead of Tailwind classes
    sender_name = name or ('You' if is_user else 'Assistant')
    
    # Create a simple container
    container = ui.row().style(f'width: 100%; display: flex; justify-content: {align}; margin: 8px 0;')
    
    with container:
        # Create the message box
        box = ui.column().style(f'max-width: 80%; background-color: {bg_color}; padding: 10px; border-radius: 8px;')
        
        with box:
            # Sender name as plain text
            ui.label(sender_name).style('font-weight: bold; font-size: 0.9rem;')
            
            # Message content as plain text (no markdown to avoid issues)
            ui.label(content).style('margin-top: 5px; white-space: pre-wrap; word-break: break-word;')
            
            # Simple spinner text instead of an actual spinner
            if is_streaming:
                ui.label('...').style('margin-top: 5px; font-style: italic;')
    
    logger.debug(f"Created message bubble for {sender_name}")
    return container

def update_message_content(message, new_content):
    """
    Update the content of an existing message (for streaming).
    
    Args:
        message: The message UI element to update
        new_content: The new text content
    """
    logger.debug(f"Updating message content, new length: {len(new_content)}")
    
    # Make sure message exists and is a valid element
    if message is None:
        logger.warning("Cannot update message: message is None")
        return
        
    try:
        # Recreation approach - clear and rebuild
        message.clear()
        
        with message:
            # Create the message box (simplified for reliability)
            box = ui.column().style(f'max-width: 80%; background-color: #f0f0f0; padding: 10px; border-radius: 8px;')
            
            with box:
                # Sender name
                ui.label('Assistant').style('font-weight: bold; font-size: 0.9rem;')
                
                # Message content as plain text
                ui.label(new_content).style('margin-top: 5px; white-space: pre-wrap; word-break: break-word;')
                
                # Simple spinner text
                ui.label('...').style('margin-top: 5px; font-style: italic;')
    except Exception as e:
        logger.error(f"Error updating message: {str(e)}", exc_info=True) 