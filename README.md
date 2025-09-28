uv venv
source .venv/bin/activate

docker build -t fintech-agent .
docker run --rm -p 8000:8000 -e GEMINI_API_KEY=AIzaSyDIu1RM_qeIBl9W4f7jvLbrLXzd4hQ3UIk fintech-agent