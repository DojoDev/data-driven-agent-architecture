# POC - Agente de Consulta de Consumo Energético

Proof of Concept de um agente conversacional para consulta de dados de consumo energético, seguindo princípios SOLID e boas práticas de arquitetura. **Inclui API simulada com FastAPI.**

## 🎯 Objetivo

Demonstrar uma arquitetura limpa e extensível para orquestração de agentes com LLM e tools customizadas, inspirada nas práticas da Estech.

## 🆕 Novidade: API Simulada Incluída!

Esta POC agora inclui uma **API REST completa** que simula a API do Data Driven, permitindo testar o agente com chamadas reais a endpoints HTTP!

### Recursos da API:
- ✅ 5 sensores simulados (refrigeração, HVAC, iluminação)
- ✅ Consulta de consumo por período (hora, dia, semana, mês)
- ✅ Autenticação via Bearer token
- ✅ Documentação interativa (Swagger UI)
- ✅ Dados variáveis e realistas

## 🏗️ Arquitetura SOLID

### Single Responsibility Principle (SRP)
- **Agent**: Apenas orquestra LLM e tools
- **Tool**: Apenas define interface de ferramentas
- **GetEnergyConsumptionTool**: Apenas consulta consumo de energia
- **LLMProvider**: Apenas define interface de providers LLM
- **OpenAIProvider**: Apenas implementa integração com OpenAI

### Open/Closed Principle (OCP)
- Fácil adicionar novos providers LLM (Gemini, DeepSeek, etc.) sem modificar código existente
- Fácil adicionar novas tools sem modificar o agente

### Liskov Substitution Principle (LSP)
- Qualquer implementação de `LLMProvider` pode substituir outra
- Qualquer implementação de `Tool` pode ser usada pelo agente

### Interface Segregation Principle (ISP)
- Interfaces mínimas e específicas para LLM e Tools
- Nenhuma classe é forçada a implementar métodos que não usa

### Dependency Inversion Principle (DIP)
- Agent depende de abstrações (LLMProvider, Tool), não de implementações concretas
- Facilita testes e manutenção

## 📁 Estrutura do Projeto

```
.
├── llm_provider.py                 # Interface abstrata para LLM providers
├── openai_provider.py              # Implementação OpenAI
├── tool.py                         # Interface abstrata para tools
├── get_energy_consumption_tool.py  # Tool de consulta de consumo (chama API real)
├── agent.py                        # Orquestrador do agente
├── main.py                         # Ponto de entrada do agente
├── api_server.py                   # 🆕 API REST simulada (FastAPI)
├── test_integration.py             # 🆕 Testes de integração
├── test_agent.py                   # Testes unitários
├── requirements.txt                # Dependências
├── .env.example                    # Exemplo de configuração
├── COMO_USAR.md                    # 🆕 Guia rápido de uso
└── README.md                       # Este arquivo
```

## 🚀 Como Usar

### Setup Inicial

```bash
# 1. Criar ambiente virtual
python3 -m venv venv

# 2. Ativar
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY
```

### Executar o Sistema Completo

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
python api_server.py
```

**Terminal 2 - Agente:**
```bash
source venv/bin/activate
python main.py
```

### Testar a Integração

```bash
# Com a API rodando
python test_integration.py
```

### Documentação da API

Com a API rodando, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💬 Exemplos de Uso

```
Você: Olá!
🤖 Lume: Olá! Sou a Lume, assistente da Estech. Posso ajudar você a consultar dados de consumo de energia dos sensores. Como posso ajudar?

Você: Qual o consumo do sensor SENSOR_001 na última hora?
🤖 Lume: O sensor SENSOR_001 (Sensor Refrigeração - SENSOR_001) registrou um consumo de 12.5 kWh na última hora...

Você: E no mês?
🤖 Lume: No período de um mês, o mesmo sensor registrou um consumo de 8642.4 kWh...
```

## 🔧 Extensibilidade

### Adicionar um novo LLM Provider

```python
from llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        # Inicializa cliente Gemini
        pass
    
    def chat_completion(self, messages, tools=None):
        # Implementa lógica do Gemini
        pass

# No main.py, basta trocar:
llm_provider = GeminiProvider(api_key=gemini_key)
```

### Adicionar uma nova Tool

```python
from tool import Tool

class CreateTicketTool(Tool):
    @property
    def name(self) -> str:
        return "create_ticket"
    
    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Cria um chamado técnico",
                # ... parâmetros
            }
        }
    
    def execute(self, **kwargs):
        # Lógica de criação de chamado
        pass

# No main.py:
tools = [
    GetEnergyConsumptionTool(...),
    CreateTicketTool(...)
]
```

## 🎨 Princípios Aplicados

1. **Abstração**: Interfaces claras entre componentes
2. **Encapsulamento**: Cada classe tem responsabilidade bem definida
3. **Polimorfismo**: Providers e tools intercambiáveis
4. **Composição**: Agent compõe LLM + Tools ao invés de herdar

## 🔄 Próximos Passos

- [ ] Adicionar logging estruturado
- [ ] Implementar cache Redis para respostas
- [ ] Adicionar validação de input com Pydantic
- [ ] Implementar fallback entre múltiplos LLM providers
- [ ] Adicionar persistência de conversação (PostgreSQL)
- [ ] Integração com Chatwoot
- [ ] Adicionar mais tools (criar chamado, consultar histórico, etc.)
- [ ] Implementar RAG para knowledge base

## 📝 Notas

- A API está **totalmente funcional** e simula cenários reais
- Os dados de consumo são gerados dinamicamente com variações
- Em produção, apenas substituir a URL da API pelo endpoint real
- Sistema testado e funcionando com chamadas HTTP reais

## 🤝 Alinhamento com Estech

Esta POC reflete as práticas mencionadas:
- ✅ Orquestração de agentes com tools customizadas
- ✅ Integração com LLMs (OpenAI, extensível para Gemini, DeepSeek, Grok)
- ✅ Arquitetura extensível e manutenível
- ✅ Fácil adicionar validação e fallbacks
- ✅ Base sólida para adicionar memória, logs, RAG

---

**Desenvolvido com foco em clean code e princípios SOLID** 🚀
