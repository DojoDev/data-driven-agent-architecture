"""
ChromaDB RAG Provider
Implementação de RAG usando ChromaDB e LangChain
Princípio: Single Responsibility - apenas gerencia busca vetorial
"""

from typing import List, Dict, Any, Optional
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.domain.contracts import RAGProvider


class ChromaRAGProvider(RAGProvider):
    """Provider de RAG usando ChromaDB para armazenamento vetorial"""
    
    def __init__(
        self,
        openai_api_key: str,
        persist_directory: str = "./data/chroma_db",
        collection_name: str = "knowledge_base"
    ):
        """
        Inicializa o provider de RAG
        
        Args:
            openai_api_key: Chave da API OpenAI para embeddings
            persist_directory: Diretório para persistir o banco vetorial
            collection_name: Nome da coleção no ChromaDB
        """
        self._embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self._persist_directory = persist_directory
        self._collection_name = collection_name
        
        # Cria diretório se não existir
        os.makedirs(persist_directory, exist_ok=True)
        
        # Inicializa ou carrega o vector store
        self._vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings,
            persist_directory=persist_directory
        )
        
        # Text splitter para dividir documentos em chunks
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes na base de conhecimento
        
        Args:
            query: Consulta do usuário
            top_k: Número de documentos mais relevantes a retornar
            
        Returns:
            Lista de documentos com conteúdo e metadados
        """
        try:
            # Busca por similaridade
            results = self._vectorstore.similarity_search_with_score(query, k=top_k)
            
            # Formata resultados
            documents = []
            for doc, score in results:
                documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return documents
            
        except Exception as e:
            print(f"❌ Erro ao buscar documentos: {e}")
            return []
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Adiciona documentos à base de conhecimento
        
        Args:
            documents: Lista de textos a serem indexados
            metadatas: Metadados opcionais para cada documento
            
        Returns:
            True se bem-sucedido
        """
        try:
            # Divide documentos em chunks
            all_chunks = []
            all_metadatas = []
            
            for idx, doc in enumerate(documents):
                chunks = self._text_splitter.split_text(doc)
                all_chunks.extend(chunks)
                
                # Adiciona metadados para cada chunk
                doc_metadata = metadatas[idx] if metadatas and idx < len(metadatas) else {}
                for chunk_idx, _ in enumerate(chunks):
                    chunk_metadata = {
                        **doc_metadata,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks)
                    }
                    all_metadatas.append(chunk_metadata)
            
            # Adiciona ao vector store
            self._vectorstore.add_texts(
                texts=all_chunks,
                metadatas=all_metadatas
            )
            
            # Persiste no disco
            self._vectorstore.persist()
            
            print(f"✅ {len(all_chunks)} chunks adicionados à base de conhecimento")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar documentos: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de conhecimento"""
        try:
            collection = self._vectorstore._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "collection_name": self._collection_name,
                "persist_directory": self._persist_directory
            }
        except Exception as e:
            return {
                "error": str(e)
            }
