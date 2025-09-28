from pydantic import BaseModel
from typing import Optional, List

class TableMetadata(BaseModel):
    company_name: str
    company_id: int
    table_name: str
    keywords: list[str]
    source_url: str
    currency: Optional[str] = None
    

class Document(BaseModel):
    """
    Represents a single, enriched data chunk ready for embedding and retrieval.
    This remains our internal standard for a processed document.
    """
    doc_id: int
    content: str      # The natural language text to be embedded
    metadata: TableMetadata

# --- API Schemas ---
class ChatRequest(BaseModel):
    """
    Defines the structure of an incoming chat request.
    """
    query: str
    conversation_id: Optional[str] = None
    evaluate: Optional[bool] = False

class ChatResponse(BaseModel):
    """
    Defines the structure of the response sent back to the user.
    """
    response: str
    conversation_id: str
    retrieved_context: Optional[List[str]] = None