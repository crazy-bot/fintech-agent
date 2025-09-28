from fastapi import FastAPI, HTTPException
from loguru import logger

from .common.schema import ChatRequest, ChatResponse
from .common.session_manager import SessionManager
from .retriever.retriever import Retriever
from .agents.llm_client import LLMClient
from .agents.agent import Agent

logger.info("Starting application setup...")
try:
    retriever = Retriever()
    llm_client = LLMClient()
    agent = Agent(retriever=retriever, llm_client=llm_client)
    session_manager = SessionManager()
    
    app = FastAPI(
        title="9fin Conversational AI Agent",
        description="An AI agent for answering questions about 9fin financial data.",
        version="1.0.0"
    )
    logger.success("Application setup complete.")

except Exception as e:
    logger.critical(f"Failed to initialize application components: {e}")
    raise

# --- API Endpoints ---

@app.post("/chat", response_model=ChatResponse, status_code=200)
def handle_chat(request: ChatRequest):
    """
    Main endpoint for handling a user's chat message.
    """
    try:
        conversation_id = request.conversation_id

        # If no conversation_id is provided, start a new session.
        if not conversation_id:
            conversation_id = session_manager.start_session()
            logger.info(f"Started new conversation with ID: {conversation_id}")
        
        # Get the conversation history for the current session.
        history = session_manager.get_history(conversation_id)

        logger.info(f"[{conversation_id}] Processing query: '{request.query}'")

        # Rewrite the user's query to be self-contained
        standalone_query = agent.generate_standalone_question(request.query, history)

        # Get the agent's response.
        agent_response = agent.get_response(request.query, standalone_query, conversation_history=history)

        # Add the new user message to the history.
        session_manager.add_message(conversation_id, role="user", content=standalone_query)

        # Add the agent's response to the history.
        session_manager.add_message(conversation_id, role="assistant", content=agent_response)

        logger.info(f"[{conversation_id}] Generated response: '{agent_response[:100]}...'")

        return ChatResponse(response=agent_response, conversation_id=conversation_id)

    except Exception as e:
        logger.error(f"An error occurred in the chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.get("/health", status_code=200)
def health_check():
    """
    A simple health check endpoint to confirm the service is running.
    """
    return {"status": "ok"}