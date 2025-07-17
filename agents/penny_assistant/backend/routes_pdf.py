from fastapi import APIRouter, UploadFile, File, HTTPException
from .pdf import extract_text_from_pdf, chunk_text
from .rag import embed_text_chunks, store_embeddings
import tempfile

router = APIRouter()

@router.post("/pdf/upload")
def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF, extract and chunk text, embed, and store in vector DB."""
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp.flush()
            text = extract_text_from_pdf(tmp.name)
        chunks = chunk_text(text)
        embeddings = embed_text_chunks(chunks)
        # TODO: Add user/session metadata
        store_embeddings(embeddings, metadata=[{"chunk": c} for c in chunks])
        return {"status": "success", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 