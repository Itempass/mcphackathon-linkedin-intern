from fastapi import FastAPI, Response, status, BackgroundTasks, Request
from . import models, app_services
from . import background_tasks as tasks
import httpx
import os

app = FastAPI()

# MCP Reverse Proxy
@app.api_route("/mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def mcp_proxy(request: Request, path: str):
    """Proxy requests to the MCP server running on port specified by MCP_DB_SERVERPORT env var"""
    async with httpx.AsyncClient() as client:
        # Get MCP server port from environment variable
        mcp_port = os.getenv("MCP_DB_SERVERPORT")
        
        # Forward the request to the internal MCP server
        url = f"http://localhost:{mcp_port}/mcp/{path}"
        
        # Get request body if present
        body = await request.body()
        
        # Forward the request
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=body,
            params=dict(request.query_params)
        )
        
        # Return the response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    

# == GENERAL BACKEND SERVER ==

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
async def reject_draft(request: models.api_models.APIRejectDraftRequest):
    await app_services.delete_draft(request)
    return {"message": "Draft rejected"}

@app.get("/draft-messages/", response_model=models.api_models.APIDraftMessageResponse)
async def get_draft_messages(user_id: str):
    internal_drafts = await app_services.get_all_drafts_for_user(user_id)
    # Map the internal message models to API models for the response
    api_drafts = [draft.to_api_draft_message() for draft in internal_drafts]
    return models.api_models.APIDraftMessageResponse(draft_messages=api_drafts)