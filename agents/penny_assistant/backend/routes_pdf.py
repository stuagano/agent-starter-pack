from fastapi import APIRouter, UploadFile, File, HTTPException
from enhanced_rag import embed_text_chunks, store_embeddings, query_rag, rag_system
from pdf import extract_text_from_pdf, chunk_text
import tempfile
from typing import Dict, Any

router = APIRouter()

@router.post("/pdf/upload")
def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF, extract and chunk text, embed, and store in vector DB."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
            content = file.file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file")
            
            tmp.write(content)
            tmp.flush()
            
            # Extract text from PDF
            text = extract_text_from_pdf(tmp.name)
            if not text.strip():
                raise HTTPException(status_code=400, detail="No text found in PDF")
            
            # Chunk the text
            chunks = chunk_text(text)
            if not chunks:
                raise HTTPException(status_code=400, detail="No text chunks created")
            
            # Create embeddings
            embeddings = embed_text_chunks(chunks)
            
            # Store embeddings
            metadata = [{"chunk": c, "source": file.filename} for c in chunks]
            store_result = store_embeddings(embeddings, metadata)
            
            return {
                "status": "success", 
                "chunks": len(chunks),
                "stored_count": store_result.get("stored_count", 0),
                "storage_method": store_result.get("storage_method", rag_system.get_storage_method()),
                "embedding_method": rag_system.get_embedding_method(),
                "filename": file.filename,
                "chunk_preview": chunks[:3]  # First 3 chunks for preview
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/pdf/query")
def query_pdf(query: str, user_id: str = "demo-user"):
    """Query the PDF knowledge base using RAG."""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = query_rag(query, user_id)
        return {
            "status": "success",
            "answer": result.get("answer", "No answer available"),
            "context": result.get("context", []),
            "sources": result.get("sources", []),
            "method": result.get("method", "unknown"),
            "storage_method": result.get("storage_method", rag_system.get_storage_method())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/pdf/health")
def pdf_health():
    """Health check for PDF processing functionality."""
    return {
        "status": "ok", 
        "service": "pdf-processing",
        "storage_method": rag_system.get_storage_method(),
        "embedding_method": rag_system.get_embedding_method()
    } 