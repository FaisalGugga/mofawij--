# app/role_router.py
from app.ollama_client import query_ollama
from app.groq_client import query_groq
from app.data_loader import load_local_data

def route_query(role, prompt):
    """Route query to appropriate model based on user role"""
    try:
        if role.lower() == "admin":
            # For admin, include local data context and use Ollama
            local_data = load_local_data()
            context = "\n\n".join([f"{item['title']}: {item['content']}" for item in local_data])
            
            # Create prompt with context
            enriched_prompt = f"""
Use the following internal information as context for answering:

{context}

User query: {prompt}
"""
            return query_ollama(enriched_prompt)
        else:
            # For regular users, use Groq
            return query_groq(prompt)
            
    except Exception as e:
        return f"Error processing your request: {str(e)}"