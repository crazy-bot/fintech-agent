 # 9fin Conversational Financial Agent

This project is a conversational AI agent designed to answer questions about company financial data. It uses a Retrieval-Augmented Generation (RAG) pipeline to provide accurate, cited answers from a knowledge base of financial tables.

The agent is built with FastAPI, uses a FAISS vector store for efficient retrieval, and is fully containerized with Docker for easy deployment.

## Features

-   **Conversational Memory:** Maintains a history to understand and answer follow-up questions.
-   **RAG Pipeline:** Ensures answers are grounded in provided data by retrieving relevant context before generation.
-   **Source Citations:** All factual statements in responses are cited with their source URL.
-   **Proactive Suggestions:** The agent suggests relevant next steps to guide the user's analysis.
-   **Dockerized:** The entire application is containerized for consistent and reproducible deployments.
-   **FastAPI** 

## Project Structure

A brief overview of the key directories in this project:

```
├── checkpoints/      # Stores the pre-computed FAISS index and metadata for fast startup.
├── data/             # Contains the raw input financial data (e.g., financial_data.json).
├── evaluation/       # Contains evaluation scripts and eval dataset.
├── src/              # All Python source code for the application.
│   ├── agents        # Core agent logic, including prompt engineering.
│   ├── retriever     # Handles data processing, embeddings creation, and vector storage.
|.  └── common        # Common utility files and functions.
│   ├── main.py       # The FastAPI application and API endpoints.
│   └── ...
├── .env              # Local file for storing secret keys (ignored by Git).
├── pyproject.toml    # Project metadata and dependencies.
└── Dockerfile        # Instructions for building the application container image.
```

## Prerequisites

Before you begin, ensure you have the following installed:
-   Python (>=3.13, as specified in `pyproject.toml`)
-   [uv](https://github.com/astral-sh/uv) (a fast Python package installer)
-   [Docker](https://www.docker.com/products/docker-desktop/)

## Local Setup and Execution

Follow these steps to run the application on your local machine.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd fintech-chatbot
```

### 2. Set Up the Environment

Create and activate a virtual environment.
```bash
python -m venv .venv
source .venv/bin/activate
```

Install the required dependencies using `uv`.
```bash
uv pip sync
```

### 3. Configure Environment Variables

The application requires a Google API key for the Gemini model.

Next, create a `.env` file and add your secret key:
```ini
# .env
GOOGLE_API_KEY="your_actual_google_api_key_here"
```

### 5. Run the API Server

Start the local API server using Uvicorn. The `--reload` flag will automatically restart the server when you make code changes.

```bash
uvicorn src.main:app --reload
```

The API will now be running at `http://127.0.0.1:8000`. ypu can access the swagger api documentation at `http://127.0.0.1:8000/docs`.


## Running with Docker

Using Docker is the recommended way to run the application as it encapsulates all dependencies and ensures a consistent environment.

### 1. Build the Docker Image

From the root directory of the project, run the build command. This will create a Docker image named `fintech-agent`.

```bash
docker build -t fintech-agent .
```

### 2. Run the Docker Container

Once the image is built, run it as a container.

**Important:** You must pass your API key into the container as an environment variable using the `-e` flag.

```bash
docker run --rm -p 8000:8000 -e GOOGLE_API_KEY="your_actual_google_api_key" fintech-agent
```

-   `--rm`: Automatically removes the container when it stops.
-   `-p 8000:8000`: Maps port 8000 on your local machine to port 8000 inside the container.
-   `-e GOOGLE_API_KEY="..."`: Securely injects your secret API key.

The containerized application is now running and accessible at `http://127.0.0.1:8000`.

## How to Interact with the Agent

With the server running (either locally or in Docker), you can interact with the agent using the auto-generated API documentation:

1.  Open your web browser and navigate to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.
2.  Expand the `/chat` endpoint.
3.  Click **"Try it out"**.
4.  In the request body, enter your query. For the first message, you can leave the `conversation_id` field empty or pass a new id.
    ```json
    {
      "query": "What were the sales for Tronox in 2024?"
    }
    ```
5.  Click **"Execute"**. The response will contain the agent's answer and a `conversation_id`.
6.  To ask a follow-up question, copy the `conversation_id` from the response and paste it into the request body along with your new query.