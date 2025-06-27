import sys
import os
from contextlib import asynccontextmanager

# Add parent directory to Python path so we can use absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Response, status, BackgroundTasks, Request
from api import models, app_services
from api import background_tasks as tasks
import httpx
from fastmcp import Client
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the MCP clients on startup
    print("🚀 Starting up and creating MCP Clients...")
    db_mcp_url = os.getenv("MCP_DB_SERVER_URL", "http://localhost:8001/mcp")
    
    app.state.mcp_clients = [
        Client(db_mcp_url)
    ]
    print(f"✅ MCP Clients created for URL: {db_mcp_url}")
    yield
    # No specific cleanup needed for Client objects themselves
    print("ℹ️ Shutting down.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# == GENERAL BACKEND SERVER ==

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/send-messages/", status_code=status.HTTP_202_ACCEPTED)
def send_messages(request_body: models.api_models.APISendMessageRequest, request: Request, background_tasks: BackgroundTasks):
    mcp_clients = request.app.state.mcp_clients
    background_tasks.add_task(tasks.run_thread_processing, request_body, mcp_clients)
    return {"message": "Message processing started in the background"}

@app.post("/process-feedback/", status_code=status.HTTP_202_ACCEPTED)
def process_feedback(request_body: models.api_models.APIProcessFeedbackRequest, request: Request, background_tasks: BackgroundTasks):
    mcp_clients = request.app.state.mcp_clients
    background_tasks.add_task(tasks.run_feedback_processing, request_body, mcp_clients)
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

# Run the server directly when script is executed
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True) 