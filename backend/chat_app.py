from dotenv import load_dotenv
import os
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from typing import Optional, List
from database import DatabaseConn
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.mistral import MistralModel
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

@dataclass
class NoteIntent:
    action: str
    title: Optional[str] = None
    description: Optional[str] = None

@dataclass
class NoteDependencies:
    db: DatabaseConn

class Titles(BaseModel):
    title: Optional[str] = None
    id: int

class NoteResponse(BaseModel):
    message: str
    note: Optional[dict] = None
    titles: Optional[List[Titles]] = None

# 1. Agent for parsing the user's intent

# intent_model = GeminiModel('gemini-1.5-pro', api_key=os.getenv('GEMINI_KEY'))
# intent_model = AnthropicModel('claude-3-5-sonnet-latest', api_key=os.getenv('CLAUDE_KEY'))
intent_model = GroqModel('llama-3.3-70b-versatile', api_key=os.getenv('GROQ_KEY'))

intent_agent = Agent(
    intent_model,
    result_type=NoteIntent,
    system_prompt=(
        "You are an intent extraction assistant. Your task is to understand the user's intent (e.g., create, retrieve, list) and extract relevant details from their input. Your output must be in the following JSON-like format: "
        "{'action': '<the user's intent>', 'title': '<a concise summary or headline>', 'description': '<main topic of the user's intent>'} "
        "- Action: Extract the primary action or intent from the user's input (e.g., create, retrieve, list). "
        "- Title: Extract a concise and specific summary or headline "
        "- Description: Extract any details that identifies the main topic of the user's input. "
        "Examples: "
        "Input: 'Create a note about my Monday meeting with Guillermo about launching Kubernetes.' "
        "Output: {'action': 'create', 'title': 'Monday meeting with Guillermo', 'description': 'about launching Kubernetes'} "
        "Input: 'List my notes about project deadlines.' "
        "Output: {'action': 'list', 'title': '', 'description': 'project deadlines'} "
        "Input: 'Retrieve details about the quarterly earnings report for Q3 2023.' "
        "Output: {'action': 'retrieve', 'title': 'quarterly earnings report for Q3 2023', 'description': 'quarterly earnings report for Q3 2023.'} "
        "Ensure that: "
        "- You always extract the `action`, `title` and `description`. "
        "- If no specific `title` or `description` is provided in the input, leave them as an empty string ('')."
    )
)

# 2. Agent for executing the identified action

# action_model = GroqModel('llama-3.3-70b-versatile', api_key=os.getenv('GROQ_KEY'))

action_model = MistralModel('mistral-small-latest', api_key=os.getenv('MISTRAL_KEY'))

action_agent = Agent(
    action_model,
    deps_type=NoteDependencies, 
    result_type=NoteResponse,
    system_prompt=(
        "Based on the identified user intent, carry out the requested action on the note storage."
        "Actions can include: 'create' (add note), 'retrieve' (get note), or 'list' (list all notes)."
    )
)

# Tools for action_agent

@action_agent.tool
async def create_note_tool(ctx: RunContext[NoteDependencies], title: str, description: str) -> NoteResponse:
    db = ctx.deps.db
    success = await db.add_note(title, description)
    return NoteResponse(message="CREATED:SUCCESS" if success else "CREATED:FAILED")

@action_agent.tool
async def retrieve_note_tool(ctx: RunContext[NoteDependencies], title: str) -> NoteResponse:
    db = ctx.deps.db
    note = await db.get_note_by_title(title)
    return NoteResponse(message="GET:SUCCESS", note=note) if note else NoteResponse(message="GET:FAILED")

@action_agent.tool
async def list_notes_tool(ctx: RunContext[NoteDependencies]) -> NoteResponse:
    db = ctx.deps.db
    all_titles = await db.list_all_titles()
    return NoteResponse(message="LIST:SUCCESS", titles=all_titles)

async def handle_user_query(user_input: str, deps: NoteDependencies) -> NoteResponse:
    # Determine user intent
    intent = await intent_agent.run(user_input)
    print(intent.data)
    if intent.data.action == "create":
        query = f"Create a note named '{intent.data.title}' with the description '{intent.data.description}'."
        response = await action_agent.run(query, deps=deps)
        return response.data
    elif intent.data.action == "retrieve":
        query = f"Retrieve the note titled '{intent.data.title}'."
        response = await action_agent.run(query, deps=deps)
        return response.data
    elif intent.data.action == "list":
        query = f"'{intent.data.action}' the titles of all notes."
        response = await action_agent.run(query, deps=deps)
        return response.data
    else:
        return NoteResponse(message="Action not recognized.")
    
async def ask(query: str):
    db_conn = DatabaseConn()
    note_deps = NoteDependencies(db=db_conn)
    return await handle_user_query(query, note_deps)

# server endpoint to host the agent

app = FastAPI()

class UserInput(BaseModel):
    user_input: str

origins = [
    "https://agentbots.vercel.app"
]

# origins = [
#     "http://localhost:3000"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/')
async def use_agent(user_query: UserInput):
    response = await ask(user_query.user_input)
    if response:
        return {"response": response}
    else:
        raise Exception("Check intent and action agent.")

@app.get('/')
async def get_data():
    db_conn = DatabaseConn()
    response = await db_conn.list_all_titles()
    if response:
        return {"response": response}
    else:
        raise Exception("Check intent and action agent.")

# To run, execute python chat_app.py or comment the below lines of code and run uvicorn chat_app:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
