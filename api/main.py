# api/main.py

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from app.role_router import route_query

app = FastAPI(title="LLM Assistant API", 
              description="API for routing requests to appropriate LLM backends")

class ChatRequest(BaseModel):
    message: str
    role: str = "user"  # Default to regular user

class ChatResponse(BaseModel):
    response: str
    role: str
    status: str

@app.post("/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest):
    """
    Process a chat request and route it to the appropriate LLM backend
    based on the user's role.
    """
    try:
        # Validate role
        if request.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'user' or 'admin'")
        
        # Route the query according to role
        response = route_query(request.role, request.message)
        
        return {
            "response": response,
            "role": request.role,
            "status": "success"
        }
    except Exception as e:
        return {
            "response": f"Error processing request: {str(e)}",
            "role": request.role,
            "status": "error"
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}