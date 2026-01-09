import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

def get_gemini_model():
    """Get Google Gemini model"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

def get_perplexity_model():
    """Get Perplexity Sonar model"""
    return ChatOpenAI(
        model="sonar",
        base_url="https://api.perplexity.ai",
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        temperature=0
    )

def get_openai_model():
    """Get OpenAI model for validation"""
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )

# Keep existing for backward compatibility
def get_llm_model():
    return get_openai_model()

def get_embed_model():
    """Get embedding model"""
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(model="text-embedding-3-small")