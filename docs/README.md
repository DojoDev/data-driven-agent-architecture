# 📚 Documentação da Arquitetura - Sistema de Agentes com RAG

## 🎯 Visão Geral

Este projeto implementa um **sistema de agentes inteligentes** baseado em **arquitetura SOLID** que combina:

1. **LLM (Large Language Model)** - OpenAI GPT-4o-mini
2. **Tools Customizadas** - Ferramentas especializadas para o agente
3. **RAG (Retrieval-Augmented Generation)** - Base de conhecimento vetorial
4. **API REST** - Dados em tempo real de sensores

---

## 🏗️ Arquitetura SOLID

### Estrutura de Camadas

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   main.py    │  │  server.py   │  │ ingest_pdf.py│  │
│  │ (CLI Agent)  │  │  (API REST)  │  │   (Script)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     USE CASES LAYER                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Agent (Orchestrator)                │   │
│  │  - Gerencia conversação                         │   │
│  │  - Decide quando usar tools                     │   │
│  │  - Coordena LLM + Tools                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ OpenAI       │  │ Energy Tool  │  │ RAG Tool     │  │
│  │ Provider     │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         ChromaDB RAG Provider                    │  │
│  │  - Embeddings OpenAI                            │  │
│  │  - Vector Search                                │  │
│  │  - Document Storage                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ LLMProvider  │  │     Tool     │  │ RAGProvider  │  │
│  │ (Interface)  │  │ (Interface)  │  │ (Interface)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principais

### 1. Domain Layer (Contratos)

**Localização:** `app/domain/contracts.py`

Define as **interfaces abstratas** que garantem baixo acoplamento:

#### LLMProvider
```python
class LLMProvider(ABC):
    """Interface para providers de LLM"""
    @abstractmethod
    def chat_completion(messages, tools) -> Dict
```

**Implementações:**
- `OpenAIProvider` - Integração com OpenAI GPT

**Princípio:** Dependency Inversion - Código depende da abstração, não da implementação

#### Tool
```python
class Tool(ABC):
    """Interface para ferramentas do agente"""
    @property
    @abstractmethod
    def name(self) -> str
    
    @abstractmethod
    def get_schema(self) -> Dict
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict
```

**Implementações:**
- `GetEnergyConsumptionTool` - Consulta consumo de sensores via API
- `RAGSearchTool` - Busca na base de conhecimento

**Princípio:** Interface Segregation - Interface mínima e específica

#### RAGProvider
```python
class RAGProvider(ABC):
    """Interface para providers de RAG"""
    @abstractmethod
    def search(query: str, top_k: int) -> List[Dict]
    
    @abstractmethod
    def add_documents(documents: List[str], metadatas: List[Dict]) -> bool
```

**Implementações:**
- `ChromaRAGProvider` - Busca vetorial com ChromaDB

**Princípio:** Open/Closed - Fácil adicionar novos providers (Pinecone, Weaviate, etc.)

---

### 2. Infrastructure Layer (Implementações)

**Localização:** `app/infrastructure/`

#### LLM Providers (`app/infrastructure/llm/`)

**OpenAIProvider**
- Implementa integração com OpenAI API
- Converte formato de mensagens
- Gerencia tool calls
- Trata erros e retries

**Responsabilidade:** Apenas comunicação com OpenAI (SRP)

#### Tools (`app/infrastructure/tools/`)

**GetEnergyConsumptionTool**
- Consulta API de sensores
- Valida parâmetros (sensor_id, period)
- Formata resposta para o LLM
- Trata erros de API

**RAGSearchTool**
- Busca documentos na base vetorial
- Formata resultados com scores de relevância
- Retorna fontes e páginas
- Trata casos sem resultados

**Responsabilidade:** Cada tool tem uma única função (SRP)

#### RAG Provider (`app/infrastructure/rag/`)

**ChromaRAGProvider**
- **Embeddings:** OpenAI text-embedding-ada-002
- **Vector Store:** ChromaDB (persistente em disco)
- **Chunking:** RecursiveCharacterTextSplitter
  - Tamanho: 1000 caracteres
  - Overlap: 200 caracteres
  - Separadores: `\n\n`, `\n`, ` `
- **Persistência:** `./data/chroma_db/`
- **Coleção:** `knowledge_base`

**Métodos:**
- `search(query, top_k)` - Busca por similaridade
- `add_documents(docs, metadata)` - Adiciona documentos
- `get_stats()` - Estatísticas da base

**Responsabilidade:** Apenas gerenciar busca vetorial (SRP)

---

### 3. Use Cases Layer (Lógica de Negócio)

**Localização:** `app/use_cases/agent.py`

#### Agent (Orquestrador)

**Responsabilidades:**
1. Gerenciar histórico de conversação
2. Decidir quando usar tools
3. Coordenar LLM + Tools
4. Processar respostas

**Fluxo de Execução:**

```
Usuário → Pergunta
    ↓
Agent.chat(message)
    ↓
Adiciona ao histórico
    ↓
Prepara mensagens + system prompt
    ↓
LLM.chat_completion(messages, tools)
    ↓
┌─────────────────┬─────────────────┐
│  Resposta       │   Tool Call     │
│  Direta         │                 │
└─────────────────┴─────────────────┘
        ↓                   ↓
   Retorna           Executa Tool
   Resposta               ↓
                    Adiciona resultado
                          ↓
                    LLM sintetiza
                          ↓
                    Retorna resposta
```

**System Prompt:**
```
Você é Lume, assistente de IA da Estech.

Fontes de informação:
1. Dados em Tempo Real → get_energy_consumption
2. Base de Conhecimento → search_knowledge_base

Quando usar cada tool:
- Consumo atual/histórico → get_energy_consumption
- Documentação/procedimentos → search_knowledge_base
- Perguntas híbridas → usar ambas em sequência
```

**Princípio:** Single Responsibility - Apenas orquestra, não implementa

---

### 4. Presentation Layer (Interfaces)

#### CLI Agent (`main.py`)

**Funcionalidades:**
- Interface de chat interativa
- Comandos: `sair`, `limpar`
- Feedback visual (emojis)
- Tratamento de erros

**Inicialização:**
```python
# 1. LLM Provider
llm_provider = OpenAIProvider(api_key, model="gpt-4o-mini")

# 2. RAG Provider
rag_provider = ChromaRAGProvider(api_key, persist_directory)

# 3. Tools
tools = [
    GetEnergyConsumptionTool(api_url, api_token),
    RAGSearchTool(rag_provider)
]

# 4. Agent
agent = Agent(llm_provider, tools)
```

**Princípio:** Dependency Injection - Componentes injetados, não criados internamente

#### API REST (`app/presentation/api/server.py`)

**Endpoints:**
- `GET /` - Informações da API
- `GET /api/sensors` - Lista sensores
- `GET /api/sensors/{id}/consumption` - Consumo por sensor
- `GET /api/sensors/{id}` - Detalhes do sensor
- `GET /health` - Health check

**Dados Simulados:**
- 5 sensores (refrigeração, HVAC, iluminação)
- Consumo variável por período
- Autenticação Bearer token

---

## 🔍 Sistema RAG (Retrieval-Augmented Generation)

### O que é RAG?

RAG combina:
1. **Retrieval** - Busca documentos relevantes
2. **Augmentation** - Enriquece o contexto do LLM
3. **Generation** - LLM gera resposta com contexto

### Arquitetura RAG

```
PDF → PyPDF2 → Extração de Texto
         ↓
   Text Splitter → Chunks (1000 chars)
         ↓
   OpenAI Embeddings → Vetores (1536 dim)
         ↓
   ChromaDB → Armazenamento Vetorial
         ↓
   Persistência → ./data/chroma_db/

Consulta:
Query → Embedding → Busca Vetorial → Top K Docs
                                         ↓
                              LLM + Contexto → Resposta
```

### Componentes RAG

#### 1. Ingestão de Documentos

**Script:** `ingest_pdf.py`

**Processo:**
1. Lê PDF com PyPDF2
2. Extrai texto página por página
3. Divide em chunks (RecursiveCharacterTextSplitter)
4. Gera embeddings (OpenAI)
5. Armazena no ChromaDB
6. Persiste em disco

**Metadados armazenados:**
```json
{
  "source": "manual.pdf",
  "page": 5,
  "total_pages": 50,
  "chunk_index": 0,
  "total_chunks": 3
}
```

**Uso:**
```bash
python ingest_pdf.py docs/seu_arquivo.pdf
```

#### 2. Busca Vetorial

**Provider:** `ChromaRAGProvider`

**Método:** `search(query, top_k=3)`

**Processo:**
1. Query → Embedding OpenAI
2. Busca por similaridade (cosine)
3. Retorna top K documentos
4. Inclui score de relevância

**Retorno:**
```python
[
  {
    "content": "Texto do chunk...",
    "metadata": {"source": "manual.pdf", "page": 5},
    "similarity_score": 0.85
  }
]
```

#### 3. Tool de Busca

**Tool:** `RAGSearchTool`

**Integração com Agent:**
- LLM decide quando usar baseado na pergunta
- Tool executa busca vetorial
- Formata resultados para o LLM
- LLM sintetiza resposta com contexto

**Schema para LLM:**
```json
{
  "name": "search_knowledge_base",
  "description": "Busca informações na base de conhecimento...",
  "parameters": {
    "query": "Pergunta do usuário",
    "top_k": 3
  }
}
```

---

## 🎨 Princípios SOLID Aplicados

### ✅ Single Responsibility Principle (SRP)

| Componente | Responsabilidade Única |
|------------|------------------------|
| `Agent` | Orquestrar LLM + Tools |
| `OpenAIProvider` | Comunicar com OpenAI |
| `ChromaRAGProvider` | Gerenciar busca vetorial |
| `GetEnergyConsumptionTool` | Consultar API de sensores |
| `RAGSearchTool` | Buscar na base de conhecimento |
| `ingest_pdf.py` | Processar PDFs |

### ✅ Open/Closed Principle (OCP)

**Extensível sem modificar código existente:**

```python
# Adicionar novo LLM Provider
class GeminiProvider(LLMProvider):
    def chat_completion(self, messages, tools):
        # Implementação Gemini
        pass

# Adicionar nova Tool
class CreateTicketTool(Tool):
    def execute(self, **kwargs):
        # Criar chamado técnico
        pass

# Adicionar novo RAG Provider
class PineconeRAGProvider(RAGProvider):
    def search(self, query, top_k):
        # Busca no Pinecone
        pass
```

**Uso:**
```python
# Basta trocar a implementação
llm = GeminiProvider(api_key)
rag = PineconeRAGProvider(api_key)
tools = [CreateTicketTool(), RAGSearchTool(rag)]
agent = Agent(llm, tools)
```

### ✅ Liskov Substitution Principle (LSP)

**Qualquer implementação pode substituir outra:**

```python
# Todas implementam LLMProvider
llm1 = OpenAIProvider(key)
llm2 = GeminiProvider(key)
llm3 = DeepSeekProvider(key)

# Todas podem ser usadas pelo Agent
agent = Agent(llm1, tools)  # ✅
agent = Agent(llm2, tools)  # ✅
agent = Agent(llm3, tools)  # ✅
```

### ✅ Interface Segregation Principle (ISP)

**Interfaces mínimas e específicas:**

```python
# LLMProvider - apenas chat
class LLMProvider(ABC):
    def chat_completion(messages, tools) -> Dict

# Tool - apenas 3 métodos essenciais
class Tool(ABC):
    def name(self) -> str
    def get_schema(self) -> Dict
    def execute(self, **kwargs) -> Dict

# RAGProvider - apenas 2 métodos
class RAGProvider(ABC):
    def search(query, top_k) -> List
    def add_documents(docs, metadata) -> bool
```

**Sem métodos desnecessários!**

### ✅ Dependency Inversion Principle (DIP)

**Depende de abstrações, não de implementações:**

```python
# ❌ ERRADO - Depende de implementação
class Agent:
    def __init__(self):
        self.llm = OpenAIProvider()  # Acoplado!
        self.rag = ChromaRAGProvider()  # Acoplado!

# ✅ CORRETO - Depende de abstração
class Agent:
    def __init__(self, llm: LLMProvider, tools: List[Tool]):
        self._llm = llm  # Abstração!
        self._tools = tools  # Abstração!
```

**Benefícios:**
- Fácil testar (mock das abstrações)
- Fácil trocar implementações
- Baixo acoplamento

---

## 🚀 Fluxo Completo de Uso

### 1. Setup Inicial

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
OPENAI_API_KEY=sk-...
DATA_DRIVEN_API_URL=http://localhost:8000/api
DATA_DRIVEN_API_TOKEN=test_token_123
```

### 2. Adicionar Conhecimento (RAG)

```bash
# Colocar PDFs em docs/
cp manual.pdf docs/

# Processar PDF
python ingest_pdf.py docs/manual.pdf
```

**Saída:**
```
🚀 Iniciando Ingestão de PDF para Base RAG
📄 Processando PDF: manual.pdf
📊 Total de páginas: 50
✅ 50 páginas extraídas com sucesso!
💾 Adicionando documentos à base vetorial...
✅ 245 chunks adicionados à base de conhecimento
```

### 3. Executar Agente

```bash
python main.py
```

**Saída:**
```
🤖 Inicializando Lume - Assistente com RAG
📚 Base de conhecimento: 245 chunks disponíveis
============================================================
Lume está pronta! Digite 'sair' para encerrar.
Experimente perguntar sobre:
  • Consumo de sensores (dados em tempo real)
  • Documentação e procedimentos (base de conhecimento)
============================================================
```

### 4. Interagir

**Exemplo 1: Consulta RAG**
```
Você: Como funciona o sistema de refrigeração?

🤖 Lume: [Busca na base de conhecimento]
Segundo o manual (página 12), o sistema de refrigeração
funciona através de...

Fonte: manual.pdf, página 12
```

**Exemplo 2: Consulta API**
```
Você: Qual o consumo do SENSOR_001 hoje?

🤖 Lume: [Consulta API em tempo real]
O sensor SENSOR_001 (Refrigeração - Câmara Fria A)
registrou 285.4 kWh no dia de hoje.
```

**Exemplo 3: Híbrido (RAG + API)**
```
Você: O SENSOR_001 está com consumo alto. O que fazer?

🤖 Lume: 
[1. Consulta consumo via API]
O SENSOR_001 está com 285.4 kWh hoje, acima da média.

[2. Busca procedimento no RAG]
Segundo o manual de manutenção (página 34), quando
o consumo está elevado, siga este procedimento:
1. Verificar temperatura ambiente
2. Inspecionar vedação das portas
3. Checar filtros de ar
...
```

---

## 📊 Estatísticas e Monitoramento

### Verificar Base RAG

```python
from app.infrastructure.rag.chroma_provider import ChromaRAGProvider
import os
from dotenv import load_dotenv

load_dotenv()
rag = ChromaRAGProvider(os.getenv("OPENAI_API_KEY"))
print(rag.get_stats())
```

**Saída:**
```json
{
  "total_documents": 245,
  "collection_name": "knowledge_base",
  "persist_directory": "./data/chroma_db"
}
```

### Testar Busca Direta

```python
results = rag.search("sistema de refrigeração", top_k=3)
for doc in results:
    print(f"Score: {doc['similarity_score']:.4f}")
    print(f"Fonte: {doc['metadata']['source']}, Página: {doc['metadata']['page']}")
    print(f"Conteúdo: {doc['content'][:200]}...")
    print("-" * 80)
```

---

## 🔧 Manutenção e Operação

### Adicionar Novos Documentos

```bash
# Processar novo PDF
python ingest_pdf.py docs/novo_manual.pdf

# Processar múltiplos PDFs
for pdf in docs/*.pdf; do
    python ingest_pdf.py "$pdf"
done
```

### Limpar Base RAG

```bash
# Remover base vetorial
rm -rf data/chroma_db

# Reprocessar todos os PDFs
for pdf in docs/*.pdf; do
    python ingest_pdf.py "$pdf"
done
```

### Atualizar Documentos

1. Remover base antiga: `rm -rf data/chroma_db`
2. Atualizar PDFs em `docs/`
3. Reprocessar: `python ingest_pdf.py docs/*.pdf`

---

## 🎯 Casos de Uso

### 1. Suporte Técnico
- **Pergunta:** "Como fazer manutenção preventiva?"
- **Ação:** RAG busca no manual
- **Resultado:** Procedimento detalhado com fonte

### 2. Monitoramento
- **Pergunta:** "Qual sensor está consumindo mais?"
- **Ação:** API consulta todos os sensores
- **Resultado:** Ranking de consumo

### 3. Diagnóstico
- **Pergunta:** "SENSOR_002 com 400 kWh. Está normal?"
- **Ação:** API + RAG (dados + referência)
- **Resultado:** Comparação com valores normais do manual

### 4. Treinamento
- **Pergunta:** "Explique o ciclo de refrigeração"
- **Ação:** RAG busca documentação técnica
- **Resultado:** Explicação detalhada com diagramas (se no PDF)

---

## 📚 Estrutura de Arquivos

```
data-driven-agent-architecture/
│
├── app/                                    # Código da Aplicação (SOLID)
│   ├── __init__.py
│   ├── domain/                            # Camada de Domínio
│   │   ├── __init__.py
│   │   └── contracts.py                   # Interfaces (LLMProvider, Tool, RAGProvider)
│   │
│   ├── infrastructure/                    # Camada de Infraestrutura
│   │   ├── __init__.py
│   │   ├── llm/                          # Providers de LLM
│   │   │   ├── __init__.py
│   │   │   └── openai_provider.py        # Implementação OpenAI
│   │   │
│   │   ├── rag/                          # Providers de RAG
│   │   │   ├── __init__.py
│   │   │   └── chroma_provider.py        # Implementação ChromaDB
│   │   │
│   │   └── tools/                        # Tools do Agente
│   │       ├── __init__.py
│   │       ├── get_energy_consumption_tool.py  # Tool de API
│   │       └── rag_search_tool.py        # Tool de RAG
│   │
│   ├── use_cases/                        # Camada de Casos de Uso
│   │   ├── __init__.py
│   │   └── agent.py                      # Orquestrador do Agente
│   │
│   └── presentation/                     # Camada de Apresentação
│       ├── __init__.py
│       └── api/                          # API REST
│           ├── __init__.py
│           └── server.py                 # FastAPI Server
│
├── docs/                                  # Documentos para RAG
│   ├── README.md                         # Esta documentação
│   └── *.pdf                             # PDFs processados
│
├── data/                                  # Dados Gerados
│   ├── README.md
│   └── chroma_db/                        # Base Vetorial ChromaDB
│
├── tests/                                 # Testes
│   ├── __init__.py
│   └── ...
│
├── .agent/                                # Workflows
│   └── workflows/
│       └── init.md
│
├── main.py                                # Entry Point - CLI Agent
├── ingest_pdf.py                          # Script - Ingestão de PDFs
├── requirements.txt                       # Dependências
├── .env                                   # Variáveis de Ambiente
├── .gitignore                            # Git Ignore
├── README.md                             # Documentação Principal
├── RAG_GUIDE.md                          # Guia RAG
├── QUICK_START_RAG.md                    # Quick Start
└── IMPLEMENTATION_SUMMARY.md             # Resumo da Implementação
```

---

## 🎓 Conceitos Avançados

### Embeddings

**O que são?**
- Representação vetorial de texto
- Dimensão: 1536 (OpenAI ada-002)
- Captura semântica, não apenas palavras

**Exemplo:**
```
"sistema de refrigeração" → [0.12, -0.34, 0.56, ...]
"refrigerador industrial" → [0.15, -0.32, 0.58, ...]
                              ↑ Vetores similares!
```

### Busca por Similaridade

**Métrica:** Cosine Similarity

```
similarity = (A · B) / (||A|| × ||B||)

Onde:
A = embedding da query
B = embedding do documento
```

**Score:**
- 1.0 = Idêntico
- 0.8-0.9 = Muito similar
- 0.6-0.7 = Relacionado
- < 0.5 = Pouco relacionado

### Chunking

**Por que dividir documentos?**
1. Contexto limitado do LLM (tokens)
2. Precisão na busca (chunks menores = mais específicos)
3. Performance (busca mais rápida)

**Estratégia:**
- Tamanho: 1000 caracteres
- Overlap: 200 caracteres (mantém contexto entre chunks)
- Separadores: `\n\n` → `\n` → ` ` (prioriza quebras naturais)

---

## 🚀 Próximos Passos

### Melhorias Sugeridas

1. **Múltiplos Formatos**
   - Suporte a DOCX, TXT, MD
   - Parser de tabelas
   - OCR para PDFs escaneados

2. **Interface Web**
   - Upload de documentos
   - Dashboard de estatísticas
   - Histórico de conversas

3. **Otimizações**
   - Cache de embeddings
   - Re-ranking de resultados
   - Compressão de contexto

4. **Múltiplas Coleções**
   - Base por departamento
   - Base por tipo de documento
   - Controle de acesso

5. **Métricas**
   - Qualidade das respostas
   - Tempo de resposta
   - Taxa de uso de cada tool

6. **Integração**
   - Webhook para ingestão automática
   - API endpoint para RAG
   - Integração com Chatwoot/WhatsApp

---

## 📖 Referências

### Tecnologias

- **LangChain:** https://python.langchain.com/
- **ChromaDB:** https://www.trychroma.com/
- **OpenAI:** https://platform.openai.com/docs
- **FastAPI:** https://fastapi.tiangolo.com/
- **PyPDF2:** https://pypdf2.readthedocs.io/

### Conceitos

- **SOLID Principles:** https://en.wikipedia.org/wiki/SOLID
- **Clean Architecture:** https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **RAG:** https://arxiv.org/abs/2005.11401
- **Vector Databases:** https://www.pinecone.io/learn/vector-database/

---

## 🤝 Contribuindo

### Adicionar Nova Tool

1. Criar classe em `app/infrastructure/tools/`
2. Implementar interface `Tool`
3. Adicionar ao `main.py`

```python
class MyNewTool(Tool):
    @property
    def name(self) -> str:
        return "my_new_tool"
    
    def get_schema(self) -> Dict[str, Any]:
        return {...}
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return {...}
```

### Adicionar Novo LLM Provider

1. Criar classe em `app/infrastructure/llm/`
2. Implementar interface `LLMProvider`
3. Usar no `main.py`

```python
class GeminiProvider(LLMProvider):
    def chat_completion(self, messages, tools):
        # Implementação
        pass
```

---

## 📝 Licença

Este projeto demonstra arquitetura SOLID para sistemas de agentes com RAG.

---

**Desenvolvido com foco em Clean Code e Princípios SOLID** 🚀

**Arquitetura:** Domain-Driven Design + Clean Architecture  
**Padrões:** Dependency Injection, Strategy, Factory  
**Princípios:** SOLID, DRY, KISS, YAGNI
