"""
Contratos do domínio (interfaces/abstrações)

Aqui ficam APENAS contratos.
- Dependency Inversion: use_cases dependem disso, não de OpenAI/HTTP/etc
- Interface Segregation: interfaces pequenas e claras
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class Tool(ABC):
    """Interface abstrata para ferramentas que o agente pode usar"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único da tool"""
        raise NotImplementedError

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Retorna o schema da tool no formato esperado pelo LLM
        (nome, descrição e parâmetros)
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Executa a tool com os parâmetros fornecidos"""
        raise NotImplementedError


class LLMProvider(ABC):
    """Interface abstrata para providers de LLM"""

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Executa uma requisição de chat completion
        Retorna um dict com a resposta do LLM e possível tool call.
        """
        raise NotImplementedError


class RAGProvider(ABC):
    """Interface abstrata para providers de RAG (Retrieval-Augmented Generation)"""

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes na base de conhecimento
        
        Args:
            query: Consulta do usuário
            top_k: Número de documentos mais relevantes a retornar
            
        Returns:
            Lista de documentos com conteúdo e metadados
        """
        raise NotImplementedError

    @abstractmethod
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Adiciona documentos à base de conhecimento
        
        Args:
            documents: Lista de textos a serem indexados
            metadatas: Metadados opcionais para cada documento
            
        Returns:
            True se bem-sucedido
        """
        raise NotImplementedError

