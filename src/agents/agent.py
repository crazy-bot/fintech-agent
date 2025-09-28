from ..retriever.retriever import Retriever
from .llm_client import LLMClient
from typing import List, Dict, Optional
from loguru import logger

class Agent:
    """
    The main conversational agent that orchestrates retrieval and generation.
    """
    
    REWRITE_PROMPT_TEMPLATE = """
Based on the chat history provided, rewrite the user's 'Follow-up Question' into a single, self-contained, standalone question. The new question should be complete enough to be understood without the chat history.

**Chat History:**
{history_str}

**Follow-up Question:**
{query}

**Standalone Question:**
"""

    ANSWER_PROMPT_TEMPLATE = """
You are a highly specialized financial analyst AI assistant for 9fin. Your purpose is to answer questions strictly based on the financial data provided in the 'CONTEXT' section.

**Available Data Tables:**
You have access to the following financial tables for each company:
- `key_financials`: Contains core profitability metrics like Sales, Adjusted EBITDA, and profit margins.
- `cash_flow_and_leverage`: Contains data on debt, cash, and leverage multiples like Net Debt and Net Leverage.
- `cap_table`: Provides a detailed breakdown of a company's debt instruments, including security, maturity, and rates.

**Rules and Constraints:**
1.  **Strictly Grounded:** Answer ONLY using the information from the 'CONTEXT'. Do not use any prior knowledge or information from outside the provided context.
2.  **Acknowledge Limitations:** If the answer is not available in the context, you MUST say that you do not have information to answer this question. Do not try to guess or infer.
3.  **Cite Sources:** Every piece of information you provide MUST be followed by a citation. The citation should be the `source_url` from the context document, formatted as `[cite: source_url]`.
4.  **Be Concise and proactive:** Provide direct and precise answers. Do not add conversational fluff unless the user asks for it.
5.  **Be Proactive:** After answering the user's question, you may suggest a relevant next step as a brief question based on the **'Available Data Tables'** knowledge, you have. Examples: "Compare to 2023?", "Calculate the YoY change?"
6.  **Handle Ambiguity:** If the user's question is ambiguous (e.g., "what is the revenue?" without a year), use the most relevant data available in the context to construct your answer and ask clarifying question that invites the user to explore the topic further.
7.  **Use Conversation History:** Refer to the 'CONVERSATION HISTORY' to understand the context of the 'USER QUESTION', especially for follow-up questions. For example, if the user asks "what about 2023?", use the history to determine which company and metric they are still talking about.
8.  **Consolidate Citations:** If multiple pieces of information come from the same source, consolidate the citations at the end of the relevant pieces of information.

**Output Format:**
- For numerical data, present it clearly with appropriate units.
- For comparisons or summaries, use bullet points.
- Always attach citations after the relevant information. For example: "The sales for Tronox in 2024 were 3,074 USD millions [cite: www.9fin.com/company_id/1/key_financials]."

--------------------

**CONTEXT:**
{context_str}

--------------------

**CONVERSATION HISTORY:**
{history_str}

--------------------

**USER QUESTION:**
{query}

**YOUR ANSWER:**
"""

    def __init__(self, retriever: Retriever, llm_client: LLMClient):
        self.retriever = retriever
        self.llm_client = llm_client
        # A simple way to know the company names available for filtering
        self.known_companies = list(self.retriever.company_index.keys())
        logger.info(f"Agent initialized. Known companies: {self.known_companies}")

    def _build_prompt(self, query: str, context_docs: List, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Constructs the final prompt string from the template."""
        
        # Format the context documents into a readable string
        context_str = "\n\n---\n\n".join([f"Source URL: {doc.metadata.source_url}\n\n{doc.content}" for doc in context_docs])
        if not context_docs:
            context_str = "No relevant data found in the knowledge base."

        # Format the conversation history
        if history:
            history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        else:
            history_str = "This is the beginning of the conversation."

        return self.ANSWER_PROMPT_TEMPLATE.format(
            context_str=context_str,
            history_str=history_str,
            query=query
        )

    def _extract_company_filter(self, query: str) -> Optional[str]:
        """A simple entity extraction to find a company name for filtering."""
        for company in self.known_companies:
            if company.lower() in query.lower():
                logger.debug(f"Extracted company filter: '{company}' from query.")
                return company
        return None

    def generate_standalone_question(self, query: str, history: List[Dict[str, str]]) -> str:
        """Uses the LLM to rewrite a follow-up query into a standalone question."""
        # If there's no history, the query is already standalone
        if not history:
            return query

        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        logger.debug(f"Generating standalone question from history:\n{history_str}\nand query: '{query}'")
        
        prompt = self.REWRITE_PROMPT_TEMPLATE.format(history_str=history_str, query=query)
        
        standalone_question = self.llm_client.generate_response(prompt)
        logger.info(f"Rewrote query to: '{standalone_question.strip()}'")
        return standalone_question.strip()

    def get_response(self, query: str, standalone_query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        The main method to get a response from the agent.
        """

        # Pre-process query to get filters
        company_filter = self._extract_company_filter(standalone_query)

        # Call the Retriever to get context
        logger.info(f"Searching for context with query: '{query}' and filter: '{company_filter}'")
        context_documents = self.retriever.search(standalone_query, k=10, company_filter=company_filter)

        # Build the prompt
        prompt = self._build_prompt(query, context_documents, conversation_history)
        logger.debug(f"Constructed prompt for LLM:\n{prompt[:1000]}...")  # Log a snippet of the prompt

        # Call the LLM to get the final answer
        response = self.llm_client.generate_response(prompt)
        
        return response