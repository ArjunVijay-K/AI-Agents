from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pydantic import BaseModel
from typing import Optional

# Langchain and Llama integration
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS # Example vector store
# from langchain_community.embeddings import HuggingFaceEmbeddings # Example embeddings
# from langchain.chains import RetrievalQA
from langchain_community.llms import LlamaCpp # Example Llama integration
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# --- Configuration ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Pydantic Models ---
class ProcessedDocuments(BaseModel):
    resume_text: str
    job_description_text: str
    message: str

class InterviewQuestion(BaseModel):
    question: str
    category: str # e.g., behavioral, technical

class InterviewResponse(BaseModel):
    answer: str

class Feedback(BaseModel):
    feedback_text: str
    suggestions: Optional[list[str]] = None


# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Interview Prep Agent API",
    description="API for managing interview preparation, including document processing and mock interviews.",
    version="0.1.0"
)

# --- CORS Middleware ---
# This is important for allowing the Vue.js frontend (running on a different port)
# to communicate with the backend.
# Adjust origins as necessary for your development/production environments.
origins = [
    "http://localhost:5173", # Default Vite dev server port
    "http://localhost:8080", # Common alternative dev port
    "http://localhost:3000", # Another common dev port
    # Add your production frontend URL here if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)


# --- AI Model Loading & Configuration ---
LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "path/to/your/llama-model.gguf") # Placeholder
LLM = None
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def initialize_llm():
    global LLM
    if not os.path.exists(LLM_MODEL_PATH):
        print(f"WARNING: LLM model not found at {LLM_MODEL_PATH}. Question generation will use dummy data.")
        LLM = None
        return

    try:
        LLM = LlamaCpp(
            model_path=LLM_MODEL_PATH,
            n_gpu_layers=-1, # -1 to use all available GPU layers, 0 for CPU only
            n_batch=512,
            n_ctx=4096,    # Context window size
            f16_kv=True,   # Must be True for some models
            verbose=True,
            # temperature=0.7,
            # top_p=0.9,
            # stop=["USER:", "\n"], # Example stop tokens
        )
        print(f"LLM loaded successfully from {LLM_MODEL_PATH}")
    except Exception as e:
        print(f"Error loading LLM: {e}")
        LLM = None

@app.on_event("startup")
async def startup_event():
    initialize_llm()
    if LLM is None:
        print("Startup: LLM could not be initialized. Using placeholder logic for question generation.")


# --- Helper Functions ---
def parse_document(file_path: str, filename: str) -> str:
    """Loads and splits document into text."""
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        loader = UnstructuredWordDocumentLoader(file_path)
    elif filename.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, DOC or TXT.")

    try:
        documents = loader.load()
        # docs_split = TEXT_SPLITTER.split_documents(documents) # If splitting is needed before concatenation
        # For now, just join all page content. Consider splitting if context is too large.
        full_text = " ".join([doc.page_content for doc in documents])
        return full_text
    except Exception as e:
        print(f"Error parsing document {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {filename}. Error: {str(e)}")


# --- API Endpoints ---
@app.get("/health", summary="Health Check", tags=["General"])
async def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return {"status": "healthy", "message": "API is up and running!"}


@app.post("/upload/", summary="Upload Resume and Job Description", tags=["Documents"], response_model=ProcessedDocuments)
async def upload_documents(
    resume: UploadFile = File(..., description="User's resume/CV file (PDF, DOCX, DOC, TXT)"),
    job_description: str = Form(..., description="Text of the job description")
):
    """
    Uploads the user's resume and job description.
    Processes the resume using Langchain document loaders and returns extracted text.
    """
    resume_filename = resume.filename
    resume_path = os.path.join(UPLOAD_DIR, resume_filename)

    if not resume_filename:
        raise HTTPException(status_code=400, detail="Resume filename cannot be empty.")

    # Save the uploaded resume temporarily
    try:
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save resume file: {e}")
    finally:
        resume.file.close()

    # Parse the document using the helper function
    try:
        resume_text_content = parse_document(resume_path, resume_filename)
    except HTTPException as e: # Propagate HTTPException from parse_document
        os.remove(resume_path) # Clean up
        raise e
    except Exception as e: # Catch any other parsing errors
        os.remove(resume_path) # Clean up
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    finally:
        if os.path.exists(resume_path): # Ensure cleanup after parsing
            os.remove(resume_path)

    if not resume_text_content.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from resume or resume is empty.")
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    return ProcessedDocuments(
        resume_text=resume_text_content,
        job_description_text=job_description,
        message="Documents processed successfully."
    )

@app.post("/generate-questions/", summary="Generate Interview Questions", tags=["Interview"], response_model=list[InterviewQuestion])
async def generate_questions(processed_docs: ProcessedDocuments):
    """
    Generates interview questions based on the processed resume and job description
    using the configured Llama model via Langchain.
    """
    if LLM is None:
        print("LLM not available. Returning dummy questions.")
        # Fallback to dummy questions if LLM is not loaded
        return [
            InterviewQuestion(question="Tell me about yourself. (LLM not loaded)", category="Behavioral"),
            InterviewQuestion(question="Why are you interested in this role? (LLM not loaded)", category="Behavioral"),
            InterviewQuestion(question=f"What are your key skills for this job? (LLM not loaded)", category="Technical"),
        ]

    # Simple prompt template
    # This needs significant refinement for good quality questions
    template = """
    Based on the following resume and job description, generate 5 distinct interview questions.
    Categorize each question as 'Behavioral', 'Technical', or 'Situational'.
    Format each question as: Category: Question Text

    Resume:
    {resume}

    Job Description:
    {job_description}

    Generated Questions:
    """
    prompt = PromptTemplate(template=template, input_variables=["resume", "job_description"])

    # Using a simple LLMChain
    llm_chain = LLMChain(prompt=prompt, llm=LLM)

    try:
        # Truncate inputs if they are too long to prevent exceeding context window
        # This is a naive truncation, better methods might be needed (e.g. summarization or text splitting)
        max_resume_len = 1500  # Characters
        max_jd_len = 1000     # Characters

        truncated_resume = processed_docs.resume_text[:max_resume_len]
        truncated_jd = processed_docs.job_description_text[:max_jd_len]

        raw_response = await llm_chain.arun(resume=truncated_resume, job_description=truncated_jd)

        # Parse the raw_response
        # Expecting lines like "Category: Question Text"
        generated_questions = []
        for line in raw_response.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                category_part, question_part = line.split(":", 1)
                category = category_part.strip()
                question_text = question_part.strip()
                if category and question_text: # Ensure both parts are non-empty
                     # Basic validation of category
                    valid_categories = ["Behavioral", "Technical", "Situational"]
                    if category not in valid_categories:
                        category = "General" # Default if category is not recognized
                    generated_questions.append(InterviewQuestion(question=question_text, category=category))
            except ValueError:
                # If line doesn't match "Category: Question" format, treat as a general question
                print(f"Warning: Could not parse line for question: {line}")
                generated_questions.append(InterviewQuestion(question=line, category="General"))

        if not generated_questions: # If parsing failed or LLM returned empty/malformed response
             return [InterviewQuestion(question="Could not generate specific questions. Tell me about a time you faced a challenge.", category="Behavioral")]

        return generated_questions

    except Exception as e:
        print(f"Error during question generation with LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions using LLM: {str(e)}")


# TODO: Add endpoint for feedback on answers
# @app.post("/get-feedback/", summary="Get Feedback on Answer", tags=["Interview"])
# async def get_feedback(answer_data: InterviewResponse, question_text: str = Form(...)):
# ... implement feedback logic using LLM ...

# Further endpoints for mock interview interaction (e.g., submit answer, get feedback)
# would be added here.

# --- Main entry point for Uvicorn (if running directly) ---
if __name__ == "__main__":
    import uvicorn
    # This is for development only. For production, use a process manager like Gunicorn.
    # The UPLOAD_DIR will be created relative to where this script is run.
    # Ensure backend/app/ is your current working directory or adjust path for UPLOAD_DIR.
    print(f"Attempting to run Uvicorn. CWD: {os.getcwd()}")
    print(f"Upload directory configured: {os.path.abspath(UPLOAD_DIR)}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# To run this (from the 'backend' directory, after creating 'app' subdirectory and this file):
# 1. Create and activate a virtual environment:
#    python -m venv venv
#    source venv/bin/activate  (or .\venv\Scripts\activate on Windows)
# 2. Install dependencies (see requirements.txt below)
#    pip install -r requirements.txt
# 3. Run the server:
#    python app/main.py
#    OR (better for development with auto-reload):
#    uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
