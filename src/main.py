import sys
import os

# Add parent directory to Python path so we can use absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Response, status, BackgroundTasks, Request
from contextlib import asynccontextmanager
from fastmcp import Client
from src import models, app_services, app_state
from src import background_tasks as tasks
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("🚀 Application startup: Initializing MCP clients...")
    
    # These URLs should point to the reverse proxy endpoints on this server.
    # The base URL should be the address of this main backend service.
    backend_url = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000')
    db_mcp_url = f"{backend_url}/db-mcp"
    gsheet_mcp_url = f"{backend_url}/gsheet-mcp"
    
    db_client = Client(db_mcp_url)
    gsheet_client = Client(gsheet_mcp_url)
    
    try:
        # Asynchronously connect the clients
        await db_client.__aenter__()
        await gsheet_client.__aenter__()
        
        # Store clients in the shared state
        app_state.mcp_clients["db"] = db_client
        app_state.mcp_clients["gsheet"] = gsheet_client
        
        print(f"✅ MCP clients connected and ready: {list(app_state.mcp_clients.keys())}")
        
        yield # The application is now running
        
    finally:
        # Shutdown logic
        print("🔌 Application shutdown: Closing MCP clients...")
        for client in app_state.mcp_clients.values():
            # Ensure the client has an active session before trying to close it
            if client.session:
                await client.__aexit__(None, None, None)
        print("MCP clients closed.")

app = FastAPI(lifespan=lifespan)

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

# MCP Reverse Proxy for Database MCP Server
@app.api_route("/db-mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def db_mcp_proxy(request: Request, path: str):
    """Proxy requests to the Database MCP server running on port specified by MCP_DB_SERVERPORT env var"""
    # Configure timeout for MCP server requests (30 seconds total, 10 seconds connect)
    timeout = httpx.Timeout(30.0, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
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

# MCP Reverse Proxy for Google Sheets MCP Server
@app.api_route("/gsheet-mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def gsheet_mcp_proxy(request: Request, path: str):
    """Proxy requests to the Google Sheets MCP server running on port specified by MCP_GSHEETS_SERVERPORT env var"""
    # Configure timeout for MCP server requests (30 seconds total, 10 seconds connect)
    timeout = httpx.Timeout(30.0, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Get MCP server port from environment variable
        mcp_port = os.getenv("MCP_GSHEETS_SERVERPORT")
        
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

# Run the server directly when script is executed
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)