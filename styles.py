"""
CSS styles for the chat application.
"""

CHAT_STYLES = """
/* Import Roboto font */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
/* Import Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* Apply Roboto to text elements but not icons */
body, input, button, div, span, p, h1, h2, h3, h4, h5, h6, label, textarea {
    font-family: 'Roboto', sans-serif !important;
}

/* Preserve Material Icons font */
.material-icons, .q-icon, .material-symbols-outlined {
    font-family: 'Material Icons', 'Material Symbols Outlined' !important;
}

/* Remove bubble triangles */
.q-message-text:before {
    display: none !important;
}

/* Ensure proper message alignment */
.q-message-sent {
    margin-left: auto !important;
    margin-right: 8px !important;
}

.q-message-received {
    margin-right: auto !important;
    margin-left: 8px !important;
}

/* Custom assistant message bubble color */
.q-message-received .q-message-text {
    background-color: transparent !important;
    color: white !important;
}

/* Custom user message bubble color */
.q-message-sent .q-message-text {
    background-color: #f5f5f5 !important;
    color: #000000 !important;
    border-radius: 2px !important;
}

/* Make sure markdown content is visible */
.q-message-text .nicegui-markdown {
    width: 100%;
    color: inherit !important;
}

/* Style markdown code blocks */
.q-message-text pre {
    background-color: rgba(0, 0, 0, 0.1) !important;
    border-radius: 4px;
    padding: 8px !important;
    margin: 8px 0 !important;
    overflow-x: auto;
}

.q-message-text code {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 0.9em;
}

/* Custom header color */
.custom-header {
    background-color: #145068 !important;
}

/* Custom button color */
.custom-button {
    background-color: #145068 !important;
    color: white !important;
}

/* Add a bit more space between messages */
.q-message {
    margin-bottom: 8px !important;
}

/* Model list styling */
.model-list {
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 12px;
}

.model-item {
    padding: 8px 12px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.model-item:hover {
    background-color: rgba(20, 80, 104, 0.1);
}

.model-item.selected {
    background-color: rgba(20, 80, 104, 0.2);
    border-left: 4px solid #145068;
}

.model-item:last-child {
    border-bottom: none;
}

.model-name {
    font-weight: bold;
}

.model-meta {
    font-size: 0.8em;
    color: #666;
}

/* Header buttons */
.header-button {
    margin-left: 12px;
    background-color: #145068 !important;
    box-shadow: none !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: white !important;
}

/* Flat button with no elevation */
.q-btn--flat {
    box-shadow: none !important;
}

/* Badge for selected model */
.model-badge {
    padding: 2px 8px;
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.2);
    font-size: 0.8em;
    margin-left: 8px;
}
""" 