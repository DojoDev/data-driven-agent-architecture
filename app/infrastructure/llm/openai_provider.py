"""
Implementação concreta do provider OpenAI.
Princípio: Dependency Inversion (SOLID)
"""
from typing import List, Dict, Any
from openai import OpenAI
from app.domain.contracts import LLMProvider


class OpenAIProvider(LLMProvider):
    """Provider concreto para OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executa chat completion via OpenAI"""
        
        params = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**params)
        
        # Normaliza a resposta
        message = response.choices[0].message
        
        result = {
            "content": message.content,
            "role": message.role,
        }
        
        # Adiciona tool calls se existirem
        if hasattr(message, 'tool_calls') and message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        
        return result
