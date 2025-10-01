from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os

app = FastAPI()

# Add CORS middleware for Janitor AI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment variable
NIM_API_KEY = os.getenv("NIM_API_KEY")

@app.get("/")
async def root():
    return {"message": "NIM Proxy is running!"}

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "meta/llama-3.1-8b-instruct",
                "object": "model",
                "owned_by": "nvidia"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        
        # Prepare request for NVIDIA NIM
        nim_payload = {
            "model": "meta/llama-3.1-8b-instruct",
            "messages": body.get("messages", []),
            "temperature": body.get("temperature", 0.7),
            "max_tokens": body.get("max_tokens", 1024),
            "stream": False  # Disable streaming for simplicity
        }
        
        headers = {
            "Authorization": f"Bearer {NIM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Forward to NVIDIA NIM
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                json=nim_payload,
                headers=headers,
                timeout=60.0
            )
            return JSONResponse(content=response.json())
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
