"""
LLM Manager - Claude AI Integration

Handles initialization and interaction with Anthropic's Claude models.
Manages both the main language model (for text generation) and embeddings
model (for semantic search, though currently using HuggingFace for embeddings).
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()


class LLMManager:
    #Manages Claude AI model for generating text responses.
    
    def __init__(self, model_name=None, embedding_model="sentence-transformers/all-mpnet-base-v2"):
        """Initialize the Claude model and embeddings.
        
        Args:
            model_name: Claude model to use (defaults to latest Sonnet from env or claude-sonnet-4-5-20250929)
            embedding_model: HuggingFace model for embeddings (Anthropic doesn't provide embeddings)
        """
        if model_name is None:
            model_name = os.getenv("ANTHROPIC_MODEL_NAME", "claude-sonnet-4-5-20250929")
        
        self.model_name = model_name
        self.embedding_model_name = embedding_model
        self.llm = None
        self.embeddings = None
        
        self._initialize_llm()
        self._initialize_embeddings()
    
    def _initialize_llm(self):
        """Set up the Claude model with proper configuration."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.llm = ChatAnthropic(
            api_key=api_key,
            model=self.model_name,
            temperature=0.7,
            max_tokens=1000,
            timeout=60.0,
            max_retries=2
        )
    
    def _initialize_embeddings(self):
        """Set up embeddings model (using HuggingFace since Anthropic doesn't provide one)."""
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
    
    def generate_text(self, prompt, max_tokens=1000):
        """Generate text response from Claude.
        
        Args:
            prompt: The text prompt to send to Claude
            max_tokens: Maximum tokens in response (default: 1000)
            
        Returns:
            Generated text response
            
        Raises:
            ConnectionError: If there's a network issue connecting to Anthropic
            ValueError: If LLM isn't initialized
        """
        if not self.llm:
            raise ValueError("LLM not initialized")
        
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "nodename" in error_msg:
                raise ConnectionError(f"Network error connecting to Anthropic API: {error_msg}")
            raise
    
    def get_embeddings(self, texts):
        """Get embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.embeddings:
            raise ValueError("Embeddings model not initialized")
        
        return self.embeddings.embed_documents(texts)
