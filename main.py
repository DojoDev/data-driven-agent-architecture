"""
POC - Agente de Consulta de Consumo Energético com RAG
Arquitetura baseada em princípios SOLID
"""
import os
from dotenv import load_dotenv
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.tools.get_energy_consumption_tool import GetEnergyConsumptionTool
from app.infrastructure.tools.rag_search_tool import RAGSearchTool
from app.infrastructure.rag.chroma_provider import ChromaRAGProvider
from app.use_cases.agent import Agent


def main():
    """Função principal da POC"""
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    api_url = os.getenv("DATA_DRIVEN_API_URL", "http://localhost:8000/api")
    api_token = os.getenv("DATA_DRIVEN_API_TOKEN", "mock_token")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY não configurada!")
        print("Configure no arquivo .env (use .env.example como base)")
        return
    
    # Inicializa componentes (seguindo Dependency Inversion)
    print("🤖 Inicializando Lume - Assistente de Eficiência Energética com RAG\n")
    
    # 1. Provider de LLM (pode ser trocado facilmente)
    llm_provider = OpenAIProvider(api_key=openai_key, model="gpt-4o-mini")
    
    # 2. Provider de RAG (pode ser trocado facilmente)
    rag_provider = ChromaRAGProvider(
        openai_api_key=openai_key,
        persist_directory="./data/chroma_db",
        collection_name="knowledge_base"
    )
    
    # Verifica se há documentos na base
    stats = rag_provider.get_stats()
    if stats.get("total_documents", 0) > 0:
        print(f"📚 Base de conhecimento carregada: {stats['total_documents']} chunks disponíveis")
    else:
        print("⚠️  Base de conhecimento vazia. Use 'python ingest_pdf.py <arquivo.pdf>' para adicionar documentos.")
    
    # 3. Tools disponíveis (pode adicionar mais tools facilmente)
    tools = [
        GetEnergyConsumptionTool(api_url=api_url, api_token=api_token),
        RAGSearchTool(rag_provider=rag_provider)
    ]
    
    # 4. Agente orquestrador
    agent = Agent(llm_provider=llm_provider, tools=tools)
    
    # Interface de chat
    print("=" * 60)
    print("Lume está pronta! Digite 'sair' para encerrar.")
    print("Experimente perguntar sobre:")
    print("  • Consumo de sensores (dados em tempo real)")
    print("  • Documentação e procedimentos (base de conhecimento)")
    print("=" * 60)
    print()
    
    while True:
        try:
            user_input = input("Você: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Até logo!")
                break
            
            if user_input.lower() == 'limpar':
                agent.reset_conversation()
                print("🔄 Conversa reiniciada!\n")
                continue
            
            # Processa mensagem
            print("\n🤖 Lume: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}\n")


if __name__ == "__main__":
    main()
