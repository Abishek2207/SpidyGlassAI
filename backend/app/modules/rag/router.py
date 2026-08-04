from fastapi import APIRouter, Depends, UploadFile, File
from app.core.security import get_current_user_id
from app.modules.rag.schema import RAGQueryRequest, RAGQueryResponse, RAGUploadResponse
from app.modules.rag.service import RAGService

router = APIRouter(prefix='/rag', tags=['RAG Module'])
_service = RAGService()

@router.post('/upload', response_model=RAGUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    _: int = Depends(get_current_user_id)
):
    content = await file.read()
    text = content.decode('utf-8')
    # Simple chunking for now
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    metadatas = [{'source': file.filename} for _ in chunks]
    num = _service.upload_documents(chunks, metadatas)
    return RAGUploadResponse(message='Success', num_chunks=num)

@router.post('/query', response_model=RAGQueryResponse)
async def query_knowledge(
    req: RAGQueryRequest,
    _: int = Depends(get_current_user_id)
):
    return _service.query(req)
