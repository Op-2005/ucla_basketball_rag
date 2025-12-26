"""
RAG Pipeline - Main Query Processing Orchestrator

Orchestrates the entire RAG process: extracts entities from user questions,
generates SQL queries, executes them, and converts results into natural language
responses. Includes fallback strategies for when queries fail.
"""

import logging
import re

logger = logging.getLogger(__name__)


class RAGPipeline:
    #Main RAG pipeline for processing basketball statistics queries.
    
    def __init__(self, llm_manager, db_connector, table_name="ucla_player_stats"):
        """Initialize the RAG pipeline.
        
        Args:
            llm_manager: LLM manager for text generation
            db_connector: Database connector for queries
            table_name: Name of the statistics table
        """
        self.llm = llm_manager
        self.db = db_connector
        self.table_name = table_name
        
        from src.entity_extractor import EntityExtractor
        from src.query_generator import SQLQueryGenerator
        
        self.entity_extractor = EntityExtractor(self.db, self.llm, table_name=self.table_name)
        self.query_generator = SQLQueryGenerator(self.llm, self.db, table_name=self.table_name)
    
    def process_query(self, user_query):
        """Process a user query through the full RAG pipeline.
        
        Args:
            user_query: Natural language question from the user
            
        Returns:
            Dict with response, success status, and metadata
        """
        logger.info(f"Processing query: {user_query}")
        
        try:
            # Extract entities (players, stats, opponents, etc.)
            entities = self.entity_extractor.extract_entities(user_query)
            logger.info(f"Extracted entities: {entities}")
            
            # Generate SQL query
            sql_query = self.query_generator.generate_sql_query(user_query, entities)
            logger.info(f"Generated SQL: {sql_query}")
            
            if not sql_query:
                return self._error_response(user_query, "Failed to generate SQL query")
            
            # Validate SQL
            is_valid, error = self.query_generator.validate_sql(sql_query)
            if not is_valid:
                logger.error(f"SQL validation failed: {error}")
                fallback = self._try_fallback(user_query, entities, error)
                if fallback:
                    return fallback
                return self._error_response(user_query, f"SQL validation failed: {error}")
            
            # Execute query
            if self.db.conn is None:
                self.db.connect()
            
            results, sql_error = self.db.execute_query(sql_query, return_error=True)
            
            if sql_error:
                logger.error(f"SQL execution error: {sql_error}")
                fallback = self._try_fallback(user_query, entities, sql_error)
                if fallback:
                    return fallback
                return self._error_response(user_query, f"SQL execution failed: {sql_error}")
            
            # Handle empty results
            if not results or len(results) == 0:
                logger.warning("Query returned no results")
                fallback = self._handle_empty(user_query, entities, sql_query)
                if fallback:
                    return fallback
                return {
                    "user_query": user_query,
                    "sql_query": sql_query,
                    "query_results": [],
                    "response": "I couldn't find any data matching your criteria. Please try rephrasing your question.",
                    "success": False
                }
            
            # Generate natural language response
            response = self._generate_response(user_query, sql_query, results)
            
            logger.info(f"Successfully processed query with {len(results)} results")
            
            return {
                "user_query": user_query,
                "extracted_entities": entities,
                "sql_query": sql_query,
                "query_results": results,
                "response": response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return self._error_response(
                user_query,
                str(e),
                "I encountered an unexpected error. Please try again or rephrase your question."
            )
    
    def _try_fallback(self, user_query, entities, original_error):
        """Try simpler fallback queries when main query fails."""
        logger.info("Trying fallback strategies")
        
        fallbacks = [
            self._simple_aggregation_query,
            self._basic_player_query,
            self._top_performers_query
        ]
        
        for fallback_func in fallbacks:
            try:
                fallback_sql = fallback_func(user_query, entities)
                if not fallback_sql:
                    continue
                
                is_valid, _ = self.query_generator.validate_sql(fallback_sql)
                if not is_valid:
                    continue
                
                results, error = self.db.execute_query(fallback_sql, return_error=True)
                if error or not results:
                    continue
                
                logger.info(f"Fallback succeeded with {len(results)} results")
                response = self._generate_response(user_query, fallback_sql, results)
                
                return {
                    "user_query": user_query,
                    "sql_query": fallback_sql,
                    "query_results": results,
                    "response": response + "\n\n(Note: Used a simplified query due to complexity.)",
                    "success": True,
                    "fallback_used": True
                }
            except Exception as e:
                logger.warning(f"Fallback failed: {str(e)}")
                continue
        
        return None
    
    def _simple_aggregation_query(self, user_query, entities):
        """Fallback: Simple aggregation query."""
        player_filter = ""
        if entities and entities.get("player_names"):
            names = entities["player_names"]
            name_list = "', '".join(names) if isinstance(names, list) else names
            player_filter = f"AND Name IN ('{name_list}')"
        
        query_lower = user_query.lower()
        
        if "average" in query_lower or "avg" in query_lower:
            if "points" in query_lower:
                return f"""
                SELECT Name, ROUND(AVG(Pts), 2) as avg_points
                FROM {self.table_name}
                WHERE Name NOT IN ('Totals', 'TM', 'Team') {player_filter}
                GROUP BY Name
                ORDER BY avg_points DESC
                LIMIT 10
                """
            elif "rebounds" in query_lower:
                return f"""
                SELECT Name, ROUND(AVG(Reb), 2) as avg_rebounds
                FROM {self.table_name}
                WHERE Name NOT IN ('Totals', 'TM', 'Team') {player_filter}
                GROUP BY Name
                ORDER BY avg_rebounds DESC
                LIMIT 10
                """
        
        return None
    
    def _basic_player_query(self, user_query, entities):
        """Fallback: Basic player stats query."""
        if entities and entities.get("player_names"):
            names = entities["player_names"]
            name_list = "', '".join(names) if isinstance(names, list) else names
            where_clause = f"Name IN ('{name_list}')"
            
            return f"""
            SELECT Name, Pts, Reb, Ast, "TO", Stl, Blk, Opponent, game_date
            FROM {self.table_name}
            WHERE {where_clause} AND Name NOT IN ('Totals', 'TM', 'Team')
            ORDER BY game_date DESC
            LIMIT 20
            """
        
        return None
    
    def _top_performers_query(self, user_query, entities):
        """Fallback: Top performers query."""
        query_lower = user_query.lower()
        if "best" in query_lower or "top" in query_lower:
            return f"""
            SELECT Name, AVG(Pts) as avg_points, AVG(Reb) as avg_rebounds, AVG(Ast) as avg_assists
            FROM {self.table_name}
            WHERE Name NOT IN ('Totals', 'TM', 'Team')
            GROUP BY Name
            ORDER BY avg_points DESC
            LIMIT 10
            """
        
        return None
    
    def _handle_empty(self, user_query, entities, sql_query):
        """Try alternative approach when query returns no results."""
        if entities and entities.get("player_names"):
            # Try without player filter
            modified = re.sub(
                r"WHERE.*?Name.*?=.*?'[^']*'.*?AND",
                "WHERE",
                sql_query,
                flags=re.IGNORECASE
            )
            
            if modified != sql_query:
                results, error = self.db.execute_query(modified, return_error=True)
                if not error and results:
                    response = f"I couldn't find specific data for that player. Here's what I found instead:\n"
                    response += self._generate_response(user_query, modified, results[:5])
                    
                    return {
                        "user_query": user_query,
                        "sql_query": modified,
                        "query_results": results[:5],
                        "response": response,
                        "success": True,
                        "fallback_used": True
                    }
        
        return None
    
    def _generate_response(self, user_query, sql_query, query_results):
        """Generate natural language response from query results."""
        if not query_results:
            return "I couldn't find any data matching your request."
        
        prompt = f"""
        Based on the following UCLA women's basketball statistics, provide a clear answer to the user's question.
        
        User question: {user_query}
        SQL query used: {sql_query}
        Query results (up to 10 rows): {query_results[:10]}
        
        Instructions:
        - Provide a direct answer to the user's question
        - Include specific numbers and statistics from the data
        - Format clearly and concisely
        - If comparing players, present the comparison clearly
        - Don't mention SQL or technical details
        """
        
        try:
            return self.llm.generate_text(prompt)
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}")
            # Basic fallback
            if len(query_results) == 1:
                return f"I found one result: {query_results[0]}"
            else:
                return f"I found {len(query_results)} results. Here are the first few: {query_results[:3]}"
    
    def _error_response(self, user_query, error, user_message=None):
        """Create standardized error response."""
        return {
            "user_query": user_query,
            "error": error,
            "sql_query": None,
            "query_results": None,
            "response": user_message or "There was an error processing your question. Please try again.",
            "success": False
        }
