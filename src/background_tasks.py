from . import app_services
from .models import api_models

async def run_thread_processing(request: api_models.APISendMessageRequest):
    """
    This function is executed in the background.
    It calls the thread processing service to create a draft.
    """
    print("BACKGROUND_TASK: Starting thread processing.")
    await app_services.process_thread_and_create_draft(request)
    print("BACKGROUND_TASK: Thread processing finished.")


async def run_feedback_processing(request: api_models.APIProcessFeedbackRequest):
    """
    This function is executed in the background.
    It calls the feedback processing service.
    """
    print("BACKGROUND_TASK: Starting feedback processing.")
    await app_services.create_revised_draft_from_feedback(request)
    print("BACKGROUND_TASK: Feedback processing finished.") 