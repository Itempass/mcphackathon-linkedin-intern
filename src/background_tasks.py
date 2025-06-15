from src.models import api_models
from src import app_services, app_state

async def run_thread_processing(request: api_models.APISendMessageRequest):
    """
    Background task to process a thread, now using shared MCP clients.
    """
    await app_services.process_thread_and_create_draft(request, app_state.mcp_clients)

async def run_feedback_processing(request: api_models.APIProcessFeedbackRequest):
    """
    Background task to process feedback, now using shared MCP clients.
    """
    await app_services.create_revised_draft_from_feedback(request, app_state.mcp_clients) 