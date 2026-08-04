from pydantic import BaseModel
from typing import List

class RAGUploadResponse(BaseModel):
    message: str
    num_chunks: int

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3

class RAGQueryResponse(BaseModel):
    context: str
    documents: List[str]
