"""
RAG Search Tool
Tool que permite ao agente buscar informações na base de conhecimento
Princípio: Single Responsibility - apenas busca na base RAG
"""

from typing import Dict, Any
from app.domain.contracts import Tool, RAGProvider


class RAGSearchTool(Tool):
    """Tool para buscar informações na base de conhecimento usando RAG"""
    
    def __init__(self, rag_provider: RAGProvider):
        """
        Inicializa a tool de busca RAG
        
        Args:
            rag_provider: Provider de RAG (abstração)
        """
        self._rag = rag_provider
    
    @property
    def name(self) -> str:
        return "search_knowledge_base"
    
    def get_schema(self) -> Dict[str, Any]:
        """Retorna o schema da tool para o LLM"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": """Busca informações na base de conhecimento da empresa.
Use esta ferramenta quando o usuário fizer perguntas sobre:
- Documentação técnica
- Procedimentos operacionais
- Políticas da empresa
- Manuais e guias
- Qualquer informação que não seja sobre consumo de energia em tempo real

Exemplos de uso:
- "Como funciona o sistema de refrigeração?"
- "Qual o procedimento de manutenção preventiva?"
- "Quais são as políticas de segurança?"
""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A pergunta ou consulta do usuário"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Número de documentos relevantes a retornar (padrão: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def execute(self, query: str, top_k: int = 3, **kwargs) -> Dict[str, Any]:
        """
        Executa a busca na base de conhecimento
        
        Args:
            query: Consulta do usuário
            top_k: Número de documentos a retornar
            
        Returns:
            Dicionário com os documentos encontrados
        """
        try:
            # Busca documentos relevantes
            documents = self._rag.search(query=query, top_k=top_k)
            
            if not documents:
                return {
                    "success": False,
                    "message": "Nenhum documento relevante encontrado na base de conhecimento.",
                    "documents": []
                }
            
            # Formata resposta
            formatted_docs = []
            for idx, doc in enumerate(documents, 1):
                formatted_docs.append({
                    "position": idx,
                    "content": doc["content"],
                    "source": doc["metadata"].get("source", "Desconhecido"),
                    "page": doc["metadata"].get("page", "N/A"),
                    "relevance_score": round(doc["similarity_score"], 4)
                })
            
            return {
                "success": True,
                "total_found": len(documents),
                "query": query,
                "documents": formatted_docs,
                "message": f"Encontrados {len(documents)} documentos relevantes."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro ao buscar na base de conhecimento: {e}"
            }
