import os
import json
import requests
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/chat"
EVAL_DATASET_PATH = os.path.join(os.path.dirname(__file__), "eval_dataset.json")

def get_agent_response(query: str, conversation_id: str = None) -> dict:
    """Calls the local chat API and returns the JSON response."""
    payload = {"query": query, "evaluate": "True"}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    response = requests.post(API_URL, json=payload)
    response.raise_for_status() # Will raise an error for 4xx/5xx responses
    return response.json()

def run_evaluation():
    """
    Loads the evaluation dataset, runs it against the agent, and scores the results with Ragas.
    """
    print("--- Starting Evaluation ---")
    
    with open(EVAL_DATASET_PATH, 'r') as f:
        eval_tests = json.load(f)

    results_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    # --- Run all test cases and collect results ---
    for test in eval_tests[:]:
        print(f"\nRunning test: {test['test_id']}...")
        conversation_id = None
        for turn in test["turns"]:
            question = turn["question"]
            ground_truth = turn["ground_truth_answer"]
            
            try:
                api_response = get_agent_response(question, conversation_id)
                answer = api_response["response"]
                retrieved_context = api_response["retrieved_context"]
                conversation_id = api_response["conversation_id"] # Maintain conversation state
                
                # Append data for Ragas
                results_data["question"].append(question)
                results_data["answer"].append(answer)
                results_data["contexts"].append(retrieved_context)
                results_data["ground_truth"].append(ground_truth)
                print(f"  - Question: '{question}' -> PASS")

            except requests.RequestException as e:
                print(f"  - Question: '{question}' -> FAIL (API Error: {e})")

    # --- Evaluate the collected results with Ragas ---
    if not results_data["question"]:
        print("\nNo results collected. Skipping Ragas evaluation.")
        return

    # Convert our results into a Hugging Face Dataset object
    dataset = Dataset.from_dict(results_data)

    print("\n--- Ragas Evaluation ---")
    # Define the metrics we want to calculate
    metrics = [
        faithfulness,       # How factually consistent is the answer with the context? (Measures hallucination)
        context_precision,  # Is the retrieved context relevant?
        context_recall,     # Did we retrieve all the necessary context?
    ]
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=GEMINI_API_KEY)
    google_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)

    # Run the evaluation
    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=gemini_llm,
        embeddings=google_embeddings
    )

    # Print the results
    print("\nEvaluation Results:")
    print(result)

if __name__ == "__main__":
    run_evaluation()