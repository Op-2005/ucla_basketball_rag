"""
UCLA Women's Basketball RAG Analytics - Core Package

This package provides the core components for the RAG (Retrieval-Augmented Generation)
pipeline that powers the basketball statistics chatbot.

The pipeline works by:
1. Extracting entities (players, stats, opponents) from natural language queries
2. Generating SQLite-compatible SQL queries
3. Executing queries against the basketball statistics database
4. Converting results into natural language responses

Main components:
- rag_pipeline: Orchestrates the entire RAG process
- entity_extractor: Identifies key information from user questions
- query_generator: Converts questions into SQL queries
- db_connector: Handles database operations safely
- llm_utils: Manages the Claude AI model integration
"""

__version__ = "1.0.0"
__author__ = "Om"
