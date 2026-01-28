"""
Agente orquestrador que gerencia a conversa e execução de tools.
Princípio: Single Responsibility + Dependency Inversion (SOLID)
"""
from typing import List, Dict, Any
import json
from app.domain.contracts import LLMProvider, Tool


class Agent:
    """Agente responsável por orquestrar LLM e tools"""
    
    def __init__(self, llm_provider: LLMProvider, tools: List[Tool]):
        """
        Inicializa o agente
        
        Args:
            llm_provider: Provider de LLM (abstração)
            tools: Lista de tools disponíveis
        """
        self._llm = llm_provider
        self._tools = {tool.name: tool for tool in tools}
        self._conversation_history: List[Dict[str, str]] = []
        
        # System prompt
        self._system_prompt = """Você é Lume, assistente de IA da Estech, especializada em eficiência energética e sistemas de refrigeração.

Seu papel é ajudar os usuários a consultar dados de consumo de energia dos sensores instalados.

Seja objetivo, técnico quando necessário, mas sempre amigável. Use a tool disponível para consultar dados reais quando solicitado."""
    
    def chat(self, user_message: str) -> str:
        """
        Processa uma mensagem do usuário
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            Resposta do agente
        """
        # Adiciona mensagem do usuário ao histórico
        self._conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepara mensagens com system prompt
        messages = [
            {"role": "system", "content": self._system_prompt}
        ] + self._conversation_history
        
        # Obtém schemas das tools
        tool_schemas = [tool.get_schema() for tool in self._tools.values()]
        
        # Chama o LLM
        response = self._llm.chat_completion(messages, tools=tool_schemas)
        
        # Processa resposta
        if "tool_calls" in response:
            # LLM quer usar uma tool
            return self._handle_tool_calls(response)
        else:
            # Resposta direta
            assistant_message = response.get("content", "")
            self._conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            return assistant_message
    
    def _handle_tool_calls(self, llm_response: Dict[str, Any]) -> str:
        """
        Processa tool calls do LLM
        
        Args:
            llm_response: Resposta do LLM contendo tool calls
            
        Returns:
            Resposta final após executar as tools
        """
        # Adiciona resposta do assistente ao histórico
        self._conversation_history.append({
            "role": "assistant",
            "content": llm_response.get("content"),
            "tool_calls": llm_response["tool_calls"]
        })
        
        # Executa cada tool call
        for tool_call in llm_response["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            # Executa a tool
            if tool_name in self._tools:
                result = self._tools[tool_name].execute(**tool_args)
            else:
                result = {"error": f"Tool {tool_name} não encontrada"}
            
            # Adiciona resultado ao histórico
            self._conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result, ensure_ascii=False)
            })
        
        # Chama LLM novamente para gerar resposta final
        messages = [
            {"role": "system", "content": self._system_prompt}
        ] + self._conversation_history
        
        final_response = self._llm.chat_completion(messages)
        
        assistant_message = final_response.get("content", "")
        self._conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def reset_conversation(self):
        """Limpa o histórico da conversa"""
        self._conversation_history = []
