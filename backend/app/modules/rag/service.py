import os
import logging
from typing import List
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException
from app.modules.rag.schema import RAGQueryRequest, RAGQueryResponse

logger = logging.getLogger('spiderglass.rag')

class RAGService:
    def __init__(self):
        self.db_dir = os.path.join(os.getcwd(), 'rag', 'vectorstore')
        os.makedirs(self.db_dir, exist_ok=True)
        self.client = PersistentClient(path=self.db_dir)
        
        # Use Ollama embeddings
        self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
            url=f'{settings.ollama_base_url}/api/embeddings',
            model_name='nomic-embed-text'
        )
        
        self.collection = self.client.get_or_create_collection(
            name='spiderglass_knowledge',
            embedding_function=self.embedding_function
        )

    def upload_documents(self, texts: List[str], metadatas: List[dict]):
        try:
            ids = [f'doc_{i}_{os.urandom(4).hex()}' for i in range(len(texts))]
            self.collection.add(documents=texts, metadatas=metadatas, ids=ids)
            return len(texts)
        except Exception as e:
            logger.error(f'RAG upload error: {e}')
            raise ServiceUnavailableException('ChromaDB Offline or Ollama Embedding Failed')

    def query(self, req: RAGQueryRequest) -> RAGQueryResponse:
        try:
            results = self.collection.query(
                query_texts=[req.query],
                n_results=req.top_k
            )
            
            docs = results.get('documents', [[]])[0]
            context = ' '.join(docs) if docs else ''
            return RAGQueryResponse(context=context, documents=docs)
        except Exception as e:
            logger.error(f'RAG query error: {e}')
            # Do not crash if offline, just return empty
            return RAGQueryResponse(context='', documents=[])
