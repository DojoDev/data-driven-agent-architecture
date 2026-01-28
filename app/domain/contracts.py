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
