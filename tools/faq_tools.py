import os
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase.client import create_client

def retrieve_faq_context(question: str, top_k: int = 3) -> dict:

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    
    if not SUPABASE_URL or not SUPABASE_KEY or not OPENAI_API_KEY:
        print("[FAQ] Missing environment variables")
        return {"found": False, "content": ""}
    
    try:
        # Initialize
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        vector_store = SupabaseVectorStore(
            embedding=embeddings,
            client=supabase,
            table_name="documents",
            query_name="match_documents",
        )
        
       
        results = vector_store.similarity_search_with_relevance_scores(
            question, k=top_k
        )
        
        
        if not results:
            print(f"[FAQ] No results for: {question}")
            return {"found": False, "content": ""}
        
        
        docs = [doc for doc, _ in results]
        content = "\n\n".join(doc.page_content for doc in docs)
        
        print(f"[FAQ] Found {len(docs)} documents for: {question}")
        return {"found": True, "content": content}
        
    except Exception as e:
        print(f"[FAQ] Error: {e}")
        return {"found": False, "content": ""}