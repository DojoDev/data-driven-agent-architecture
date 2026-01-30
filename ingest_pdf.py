"""
Script de Ingestão de PDFs para a Base de Conhecimento RAG

Este script processa PDFs e adiciona seu conteúdo à base vetorial.
Uso: python ingest_pdf.py <caminho_do_pdf>
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from app.infrastructure.rag.chroma_provider import ChromaRAGProvider


def extract_text_from_pdf(pdf_path: str) -> tuple[list[str], list[dict]]:
    """
    Extrai texto de um PDF página por página
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        
    Returns:
        Tupla com (lista de textos, lista de metadados)
    """
    try:
        reader = PdfReader(pdf_path)
        documents = []
        metadatas = []
        
        pdf_name = Path(pdf_path).name
        
        print(f"📄 Processando PDF: {pdf_name}")
        print(f"📊 Total de páginas: {len(reader.pages)}")
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            
            if text.strip():  # Apenas adiciona se houver texto
                documents.append(text)
                metadatas.append({
                    "source": pdf_name,
                    "page": page_num,
                    "total_pages": len(reader.pages)
                })
                
                print(f"  ✓ Página {page_num}/{len(reader.pages)} processada")
        
        print(f"✅ {len(documents)} páginas extraídas com sucesso!\n")
        return documents, metadatas
        
    except Exception as e:
        print(f"❌ Erro ao processar PDF: {e}")
        return [], []


def main():
    """Função principal do script de ingestão"""
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY não configurada!")
        print("Configure no arquivo .env")
        return
    
    # Verifica argumentos
    if len(sys.argv) < 2:
        print("❌ Uso: python ingest_pdf.py <caminho_do_pdf>")
        print("\nExemplo:")
        print("  python ingest_pdf.py ./docs/manual.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    # Verifica se o arquivo existe
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        return
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"❌ O arquivo deve ser um PDF: {pdf_path}")
        return
    
    print("=" * 60)
    print("🚀 Iniciando Ingestão de PDF para Base RAG")
    print("=" * 60)
    print()
    
    # Extrai texto do PDF
    documents, metadatas = extract_text_from_pdf(pdf_path)
    
    if not documents:
        print("❌ Nenhum texto extraído do PDF")
        return
    
    # Inicializa RAG provider
    print("🔧 Inicializando RAG Provider...")
    rag_provider = ChromaRAGProvider(
        openai_api_key=openai_key,
        persist_directory="./data/chroma_db",
        collection_name="knowledge_base"
    )
    
    # Adiciona documentos à base
    print("💾 Adicionando documentos à base vetorial...")
    success = rag_provider.add_documents(documents, metadatas)
    
    if success:
        print()
        print("=" * 60)
        print("✅ INGESTÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        # Mostra estatísticas
        stats = rag_provider.get_stats()
        print(f"\n📊 Estatísticas da Base:")
        print(f"  • Total de chunks: {stats.get('total_documents', 'N/A')}")
        print(f"  • Coleção: {stats.get('collection_name', 'N/A')}")
        print(f"  • Diretório: {stats.get('persist_directory', 'N/A')}")
        print()
        print("💡 Agora você pode usar o agente para fazer perguntas sobre o documento!")
        print("   Execute: python main.py")
    else:
        print("❌ Falha ao adicionar documentos à base")


if __name__ == "__main__":
    main()
