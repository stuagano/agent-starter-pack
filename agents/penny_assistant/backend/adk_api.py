from fastapi import FastAPI, Request
from pydantic import BaseModel
from adk.agent import Agent
from adk.memorybank import MemoryBank

app = FastAPI()

# TODO: Configure your agent and memorybank
memorybank = MemoryBank()
agent = Agent(memorybank=memorybank)

class ChatRequest(BaseModel):
    message: str

@app.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    """Send a message to Penny and get a response."""
    # TODO: Implement agent logic
    response = agent.run(req.message)  # Stub
    return {"response": response}

@app.get("/memory")
def get_memory():
    """Retrieve current memorybank contents."""
    # TODO: Implement memorybank retrieval
    return {"memory": memorybank.get_all()} 