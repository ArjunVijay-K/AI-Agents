# AI Interview Prep Agent - Backend

This is the backend server for the AI Interview Prep Agent. It's built with FastAPI and is responsible for handling document uploads, processing text, interacting with the Llama language model via Langchain, and providing API endpoints for the frontend.

## Setup

### Prerequisites

*   Python (3.9+ recommended)
*   `pip` (Python package installer)
*   A virtual environment tool (e.g., `venv`)

### Installation

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you plan to use `llama-cpp-python` with GPU acceleration (e.g., Metal on Apple Silicon), you might need to install it with specific environment variables. For example:*
    ```bash
    # CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
    ```
    *Refer to the `llama-cpp-python` documentation for details.*

## Running the Server

There are two main ways to run the FastAPI server:

1.  **Using Uvicorn (recommended for development with auto-reload):**
    Ensure your current working directory is `backend/`.
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The server will be accessible at `http://localhost:8000`.

2.  **Running the Python script directly (for simple execution):**
    Ensure your current working directory is `backend/`.
    ```bash
    python app/main.py
    ```
    This will also start the server, typically on `http://localhost:8000`.

## API Endpoints

The API documentation (powered by Swagger UI) is automatically available at `http://localhost:8000/docs` when the server is running.
The ReDoc documentation is available at `http://localhost:8000/redoc`.

Key planned endpoints:

*   `GET /health`: Health check.
*   `POST /upload/`: Upload resume (file) and job description (form data).
    *   Parses uploaded resume (PDF, DOCX, DOC, TXT) using Langchain document loaders.
    *   Returns extracted text from resume and the provided job description.
*   `POST /generate-questions/`: Takes processed document texts (resume and job description).
    *   If an LLM is configured and loaded, it generates tailored interview questions using a predefined prompt and Langchain.
    *   If the LLM is not available, it returns a set of predefined placeholder questions.
*   `GET /get-feedback/` (Future): Endpoint to provide feedback on user's answers (not yet implemented).


## Llama Model and Langchain Integration

The backend uses Langchain for document processing and interaction with a Large Language Model (LLM) from the Llama family (via `LlamaCpp`).

### Prerequisites for AI Features:

1.  **Llama Model File:**
    *   You need to download a Llama model in GGUF format (e.g., from Hugging Face). Many variants exist (7B, 13B parameters, different quantization levels). Choose one that fits your hardware capabilities.
    *   Example: `llama-2-7b-chat.Q4_K_M.gguf`

2.  **Set `LLM_MODEL_PATH` Environment Variable:**
    *   The application expects the path to your GGUF model file to be set in an environment variable named `LLM_MODEL_PATH`.
    *   Example: `export LLM_MODEL_PATH="/path/to/your/models/llama-2-7b-chat.Q4_K_M.gguf"`
    *   If this variable is not set, or the path is invalid, the LLM will not load, and the system will fall back to using placeholder questions.

3.  **Python Dependencies for Langchain & LlamaCpp:**
    *   Ensure all dependencies from `requirements.txt` are installed, especially:
        *   `langchain`
        *   `llama-cpp-python` (May require specific compilation flags for GPU support, e.g., Metal on macOS: `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python`)
        *   `unstructured[docx,pdf]` for document parsing.

### How it Works:

*   **Document Parsing (`/upload/`):**
    *   Resumes are processed using Langchain's `PyPDFLoader` (for PDFs) and `UnstructuredWordDocumentLoader` (for DOC/DOCX) to extract raw text.
*   **Question Generation (`/generate-questions/`):**
    *   The extracted resume text and the job description are fed into a prompt template.
    *   A Langchain `LLMChain` with the configured `LlamaCpp` model generates questions based on this prompt.
    *   The prompt and response parsing are basic; improvements (e.g., using Langchain Output Parsers, more sophisticated prompts) can enhance question quality and reliability.
    *   If the LLM is not loaded, predefined sample questions are returned.

## Project Structure

*   `app/`: Contains the main FastAPI application.
    *   `main.py`: The FastAPI application logic, including endpoint definitions and AI integration points.
*   `uploads/`: Directory where uploaded files (e.g., resumes) are temporarily stored. This should be in your `.gitignore`.
*   `requirements.txt`: Python dependencies.
*   `README.md`: This file.
*   `venv/`: Virtual environment directory (should be in `.gitignore`).

## Next Steps

*   Implement actual document parsing (PDF, DOCX) using Langchain loaders.
*   Integrate a Llama model using `langchain.llms` (e.g., `LlamaCpp`).
*   Develop sophisticated prompts for question generation.
*   Build out the mock interview interaction (handling user answers, providing feedback).
*   Add more robust error handling and logging.
*   Write tests for the API endpoints and AI logic.
