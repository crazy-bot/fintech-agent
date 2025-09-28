FROM python:3.13-slim

# Set environment variables for best practices.
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container.
WORKDIR /app

# Install uv for faster dependency installation
RUN pip install uv

COPY requirements.txt .

# Install the Python dependencies using uv
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container.
COPY ./src ./src
COPY ./data ./data

# Expose the port the API will run on.
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]