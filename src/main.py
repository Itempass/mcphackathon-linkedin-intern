from fastapi import FastAPI, Response, status, BackgroundTasks
from . import models, services
from . import background_tasks as tasks

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/send-messages/", status_code=status.HTTP_202_ACCEPTED)
def send_messages(request: models.api_models.APISendMessageRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(tasks.run_thread_processing, request)
    return {"message": "Message processing started in the background"}

@app.post("/process-feedback/", status_code=status.HTTP_202_ACCEPTED)
def process_feedback(request: models.api_models.APIProcessFeedbackRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(tasks.run_feedback_processing, request)
    return {"message": "Feedback processing started in the background"}

@app.post("/reject-draft/", status_code=status.HTTP_200_OK)
def reject_draft(request: models.api_models.APIRejectDraftRequest):
    services.delete_draft(request)
    return {"message": "Draft rejected"}

@app.get("/draft-messages/", response_model=models.api_models.APIDraftMessageResponse)
def get_draft_messages(user_id: str):
    internal_drafts = services.get_all_drafts_for_user(user_id)
    # Map the internal message models to API models for the response
    api_drafts = [draft.to_api_draft_message() for draft in internal_drafts]
    return models.api_models.APIDraftMessageResponse(draft_messages=api_drafts)