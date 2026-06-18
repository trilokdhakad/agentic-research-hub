from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from document_utils import process_file

from metadata_extractor import generate_metadata
from metadata_store import (
    save_metadata,
    get_all_metadata,
    get_metadata_by_filename
)

from database import (
    add_documents_to_db,
    get_all_documents,
    delete_document,
    document_exists
)

from rag_graph import rag_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)


class QueryRequest(BaseModel):
    question: str


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"data/{file.filename}"
    
    # Check if document already indexed
    if document_exists(file.filename):
        return {
            "message": f"{file.filename} already indexed."
        }

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    chunks = process_file(
        file_location,
        file.filename
    )

    add_documents_to_db(chunks)

    metadata = generate_metadata(
        chunks,
        file.filename
    )

    save_metadata(
        file.filename,
        metadata
    )

    return {
        "message":
        f"Successfully processed and embedded {file.filename}."
    }


@app.get("/documents/")
async def get_documents():
    documents = get_all_documents()

    return {
        "documents": documents
    }


@app.get("/metadata/")
async def get_all_document_metadata():
    return {
        "documents": get_all_metadata()
    }


@app.get("/metadata/{filename}")
async def get_document_metadata(
    filename: str
):
    metadata = get_metadata_by_filename(
        filename
    )

    if metadata is None:
        return {
            "error": "Metadata not found"
        }

    return metadata


@app.delete("/documents/{filename}")
async def remove_document(filename: str):
    deleted_chunks = delete_document(filename)

    return {
        "message": f"Deleted {filename}",
        "chunks_removed": deleted_chunks
    }


@app.post("/ask/")
async def ask_question(request: QueryRequest):
    inputs = {
        "question": request.question
    }

    result = rag_app.invoke(inputs)

    return {
        "answer": result["generation"],
        "sources": list(
            set(result.get("sources", []))
        ),
        "plan": result.get(
            "plan",
            "No plan generated."
        )
    }