# chat_handler.py

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langsmith import traceable
import os
import requests

# Load environment variables
load_dotenv()

# Setup FastAPI
app = FastAPI()

# CORS config for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safely grab API keys from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "chatbot-openrouter")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# Set LangSmith-specific env vars
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")

# Request model from the frontend
class ChatRequest(BaseModel):
    message: str
    model: str = "mistralai/mistral-small-3.1-24b-instruct:free"  # default model

# Main chatbot endpoint using OpenRouter + LangSmith tracing
@app.post("/api/chat")
@traceable(name="Chatbot Interaction")
async def chat_endpoint(req: ChatRequest):
    if not OPENROUTER_API_KEY:
        return {"reply": "Missing OpenRouter API key. Check your .env setup."}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": req.message},
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code != 200:
        return {"reply": f"OpenRouter error: {response.status_code} - {response.text}"}

    reply = response.json()["choices"][0]["message"]["content"]
    return {"reply": reply}
