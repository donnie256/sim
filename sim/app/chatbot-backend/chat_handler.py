# chat_handler.py

from gmail_handler import router as gmail_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langsmith import traceable
from email_agent import run_email_agent  # 👈 Import the LangGraph agent
import os

# Load environment variables
load_dotenv()

# Setup FastAPI
app = FastAPI()

# Include Gmail MCP routes
app.include_router(gmail_router)

# CORS config for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangSmith env config
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "chatbot-openrouter")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")

# Request model
class ChatRequest(BaseModel):
    message: str
    model: str = "mistralai/mistral-small-3.1-24b-instruct:free"  # now using model from LangGraph

# Updated /api/chat route using LangGraph + tools
@app.post("/api/chat")
@traceable(name="Chatbot Interaction")
async def chat_endpoint(req: ChatRequest):
    try:
        reply = run_email_agent(req.message)
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Something went wrong: {str(e)}"}
