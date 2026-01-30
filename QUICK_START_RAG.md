# 📚 Exemplo de Uso do RAG

## Passo a Passo Completo

### 1. Instalar Dependências

```bash
# Ative o ambiente virtual (WSL/Linux)
wsl bash -c "cd /home/igniteboost/apps/data-driven-agent-architecture && source venv_estech/bin/activate && pip install -r requirements.txt"
```

### 2. Preparar um PDF de Teste

Crie um arquivo `docs/manual_exemplo.pdf` com conteúdo sobre sistemas de refrigeração, ou use qualquer PDF técnico que você tenha.

### 3. Ingerir o PDF

```bash
# Processar o PDF e adicionar à base vetorial
wsl bash -c "cd /home/igniteboost/apps/data-driven-agent-architecture && source venv_estech/bin/activate && python ingest_pdf.py docs/manual_exemplo.pdf"
```

Você verá:
```
============================================================
🚀 Iniciando Ingestão de PDF para Base RAG
============================================================

📄 Processando PDF: manual_exemplo.pdf
📊 Total de páginas: 10
  ✓ Página 1/10 processada
  ✓ Página 2/10 processada
  ...
✅ 10 páginas extraídas com sucesso!

🔧 Inicializando RAG Provider...
💾 Adicionando documentos à base vetorial...
✅ 45 chunks adicionados à base de conhecimento

============================================================
✅ INGESTÃO CONCLUÍDA COM SUCESSO!
============================================================

📊 Estatísticas da Base:
  • Total de chunks: 45
  • Coleção: knowledge_base
  • Diretório: ./data/chroma_db

💡 Agora você pode usar o agente para fazer perguntas sobre o documento!
   Execute: python main.py
```

### 4. Executar o Agente

```bash
wsl bash -c "cd /home/igniteboost/apps/data-driven-agent-architecture && source venv_estech/bin/activate && python main.py"
```

### 5. Testar Consultas

```
🤖 Inicializando Lume - Assistente de Eficiência Energética com RAG

📚 Base de conhecimento carregada: 45 chunks disponíveis
============================================================
Lume está pronta! Digite 'sair' para encerrar.
Experimente perguntar sobre:
  • Consumo de sensores (dados em tempo real)
  • Documentação e procedimentos (base de conhecimento)
============================================================

Você: Como funciona o sistema de refrigeração?
🤖 Lume: [Busca na base de conhecimento e responde com base no PDF]

Você: Qual o consumo do sensor SENSOR_001 na última hora?
🤖 Lume: [Consulta a API e retorna dados em tempo real]

Você: O sensor está consumindo muito. O que devo fazer?
🤖 Lume: [Combina dados da API + procedimentos do PDF]
```

## 🎯 Casos de Uso

### Caso 1: Apenas RAG
**Pergunta:** "Quais são os procedimentos de manutenção preventiva?"
**Ação:** Agente usa `search_knowledge_base`
**Resultado:** Retorna informações do PDF

### Caso 2: Apenas API
**Pergunta:** "Qual o consumo do SENSOR_002 hoje?"
**Ação:** Agente usa `get_energy_consumption`
**Resultado:** Retorna dados em tempo real

### Caso 3: Híbrido (RAG + API)
**Pergunta:** "O SENSOR_001 está com consumo alto. Como resolver?"
**Ação:** 
1. Consulta consumo via API
2. Busca procedimentos no PDF
3. Combina as informações

**Resultado:** Resposta completa com dados + procedimentos

## 📝 Comandos Úteis

```bash
# Ver estatísticas da base
wsl bash -c "cd /home/igniteboost/apps/data-driven-agent-architecture && source venv_estech/bin/activate && python -c 'from app.infrastructure.rag.chroma_provider import ChromaRAGProvider; import os; from dotenv import load_dotenv; load_dotenv(); rag = ChromaRAGProvider(os.getenv(\"OPENAI_API_KEY\")); print(rag.get_stats())'"

# Limpar base vetorial (recomeçar)
rm -rf data/chroma_db

# Adicionar múltiplos PDFs
for pdf in docs/*.pdf; do
  wsl bash -c "cd /home/igniteboost/apps/data-driven-agent-architecture && source venv_estech/bin/activate && python ingest_pdf.py $pdf"
done
```

## 🔍 Estrutura de Arquivos Criados

```
data-driven-agent-architecture/
├── app/
│   ├── domain/
│   │   └── contracts.py              # ✅ RAGProvider adicionado
│   ├── infrastructure/
│   │   ├── rag/                      # ✅ NOVO
│   │   │   ├── __init__.py
│   │   │   └── chroma_provider.py
│   │   └── tools/
│   │       └── rag_search_tool.py    # ✅ NOVO
│   └── use_cases/
│       └── agent.py                  # ✅ Atualizado
├── data/
│   ├── chroma_db/                    # ✅ Criado automaticamente
│   └── README.md
├── docs/                             # ✅ Seus PDFs aqui
│   └── manual_exemplo.pdf
├── ingest_pdf.py                     # ✅ NOVO
├── main.py                           # ✅ Atualizado
├── requirements.txt                  # ✅ Atualizado
├── RAG_GUIDE.md                      # ✅ NOVO
└── README.md                         # ✅ Atualizado
```

## ✅ Checklist de Implementação

- [x] Interface `RAGProvider` criada (domain)
- [x] Implementação `ChromaRAGProvider` (infrastructure)
- [x] Tool `RAGSearchTool` criada
- [x] Script `ingest_pdf.py` criado
- [x] Agente integrado com RAG
- [x] System prompt atualizado
- [x] Dependencies atualizadas
- [x] Documentação completa
- [x] .gitignore atualizado
- [ ] **Você precisa:** Instalar dependências
- [ ] **Você precisa:** Adicionar PDFs
- [ ] **Você precisa:** Testar!

---

**Arquitetura SOLID mantida! 🚀**
