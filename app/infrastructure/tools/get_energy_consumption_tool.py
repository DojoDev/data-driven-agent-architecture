"""
Tool para consultar consumo de energia de sensores.
Princípio: Single Responsibility (SOLID)
"""
from typing import Dict, Any
import requests
from app.domain.contracts import Tool



class GetEnergyConsumptionTool(Tool):
    """Tool para consultar consumo de energia de um sensor específico"""
    
    def __init__(self, api_url: str, api_token: str):
        self._api_url = api_url
        self._api_token = api_token
    
    @property
    def name(self) -> str:
        return "get_energy_consumption"
    
    def get_schema(self) -> Dict[str, Any]:
        """Schema da tool para o LLM"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Consulta o consumo de energia de um sensor específico. Retorna dados de consumo em kWh, período analisado e status do sensor.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sensor_id": {
                            "type": "string",
                            "description": "ID único do sensor a ser consultado (ex: SENSOR_001)"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["hora", "dia", "semana", "mes"],
                            "description": "Período de tempo para análise do consumo"
                        }
                    },
                    "required": ["sensor_id", "period"]
                }
            }
        }
    
    def execute(self, sensor_id: str, period: str) -> Dict[str, Any]:
        """
        Executa a consulta de consumo de energia
        
        Args:
            sensor_id: ID do sensor
            period: Período de análise
            
        Returns:
            Dados de consumo do sensor
        """
        try:
            # Faz chamada real à API
            response = requests.get(
                f"{self._api_url}/sensors/{sensor_id}/consumption",
                headers={"Authorization": f"Bearer {self._api_token}"},
                params={"period": period},
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro ao consultar sensor {sensor_id}. Verifique se a API está rodando em {self._api_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro inesperado ao consultar sensor {sensor_id}"
            }

