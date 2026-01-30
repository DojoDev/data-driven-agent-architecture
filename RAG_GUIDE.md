# 📚 Guia RAG - Retrieval-Augmented Generation

## 🎯 O que é RAG?

RAG (Retrieval-Augmented Generation) permite que o agente consulte uma base de conhecimento para responder perguntas sobre documentação, manuais e procedimentos.

## 🏗️ Arquitetura

Seguindo os mesmos princípios SOLID do projeto:

```
app/
├── domain/
│   └── contracts.py              # Interface RAGProvider (abstração)
├── infrastructure/
│   ├── rag/
│   │   ├── chroma_provider.py    # Implementação com ChromaDB
│   │   └── __init__.py
│   └── tools/
│       └── rag_search_tool.py    # Tool de busca RAG
```

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
# Ative o ambiente virtual
source venv_estech/bin/activate  # Linux/WSL
# ou
venv_estech\Scripts\activate     # Windows

# Instale as novas dependências
pip install -r requirements.txt
```

### 2. Adicionar Documentos PDF

```bash
# Processar um PDF e adicionar à base
python ingest_pdf.py ./docs/manual.pdf

# Processar múltiplos PDFs
python ingest_pdf.py ./docs/manual1.pdf
python ingest_pdf.py ./docs/manual2.pdf
python ingest_pdf.py ./docs/procedimentos.pdf
```

### 3. Executar o Agente

```bash
python main.py
```

## 💬 Exemplos de Uso

### Consultas sobre Documentação
```
Você: Como funciona o sistema de refrigeração?
🤖 Lume: [Busca na base de conhecimento e responde com base nos PDFs]

Você: Qual o procedimento de manutenção preventiva?
🤖 Lume: [Consulta documentação e fornece o procedimento]

Você: Quais são as políticas de segurança?
🤖 Lume: [Retorna informações dos manuais]
```

### Consultas Híbridas (RAG + API)
```
Você: O sensor SENSOR_001 está consumindo muito. Qual o procedimento?
🤖 Lume: 
1. [Consulta consumo via API]
2. [Busca procedimento na base de conhecimento]
3. [Combina as informações na resposta]
```

## 🔧 Componentes

### RAGProvider (Interface)
```python
class RAGProvider(ABC):
    def search(query: str, top_k: int) -> List[Dict]
    def add_documents(documents: List[str], metadatas: List[Dict]) -> bool
```

### ChromaRAGProvider (Implementação)
- **Embeddings**: OpenAI embeddings
- **Vector Store**: ChromaDB (persistente em disco)
- **Chunking**: RecursiveCharacterTextSplitter (1000 chars, overlap 200)

### RAGSearchTool
- Integra o RAG ao agente como uma tool
- O LLM decide quando usar baseado na pergunta
- Retorna documentos com score de relevância

## 📊 Estrutura de Dados

### Chunks Armazenados
```json
{
  "content": "Texto do chunk...",
  "metadata": {
    "source": "manual.pdf",
    "page": 5,
    "total_pages": 50,
    "chunk_index": 0,
    "total_chunks": 3
  },
  "similarity_score": 0.85
}
```

## 🎨 Princípios SOLID Aplicados

1. **Single Responsibility**
   - `ChromaRAGProvider`: apenas gerencia busca vetorial
   - `RAGSearchTool`: apenas expõe RAG como tool
   - `ingest_pdf.py`: apenas processa PDFs

2. **Open/Closed**
   - Fácil trocar ChromaDB por Pinecone, Weaviate, etc.
   - Basta criar novo provider implementando `RAGProvider`

3. **Liskov Substitution**
   - Qualquer implementação de `RAGProvider` pode substituir outra

4. **Interface Segregation**
   - Interface mínima: apenas `search` e `add_documents`

5. **Dependency Inversion**
   - `RAGSearchTool` depende de `RAGProvider` (abstração)
   - Não depende de ChromaDB diretamente

## 🔄 Fluxo de Dados

```
1. PDF → ingest_pdf.py
2. Extração de texto (PyPDF2)
3. Chunking (RecursiveCharacterTextSplitter)
4. Embeddings (OpenAI)
5. Armazenamento (ChromaDB)
6. Persistência (./data/chroma_db)

Consulta:
1. Usuário faz pergunta
2. LLM decide usar RAGSearchTool
3. Query → Embedding → Busca vetorial
4. Top K documentos retornados
5. LLM sintetiza resposta com contexto
```

## 📁 Arquivos Criados

- `app/domain/contracts.py` - Interface `RAGProvider` adicionada
- `app/infrastructure/rag/chroma_provider.py` - Implementação ChromaDB
- `app/infrastructure/rag/__init__.py` - Módulo RAG
- `app/infrastructure/tools/rag_search_tool.py` - Tool de busca
- `ingest_pdf.py` - Script de ingestão
- `requirements.txt` - Dependências atualizadas
- `main.py` - Integração RAG ao agente

## 🎯 Próximos Passos

- [ ] Adicionar suporte para outros formatos (DOCX, TXT, MD)
- [ ] Implementar re-ranking dos resultados
- [ ] Adicionar cache de embeddings
- [ ] Interface web para upload de documentos
- [ ] Métricas de qualidade das respostas
- [ ] Suporte a múltiplas coleções (diferentes bases)

## 🐛 Troubleshooting

### Erro: "No documents found"
- Verifique se você executou `ingest_pdf.py`
- Confirme que `./data/chroma_db` existe e tem dados

### Erro: "OpenAI API key"
- Verifique `.env` tem `OPENAI_API_KEY` configurada
- A mesma key é usada para LLM e embeddings

### Resultados irrelevantes
- Ajuste `chunk_size` em `chroma_provider.py`
- Aumente `top_k` na busca
- Melhore a qualidade dos PDFs (evite scans de baixa qualidade)

---

**Desenvolvido seguindo arquitetura SOLID** 🚀
