"""
Database Connector - SQLite Operations

Handles all database connections and query execution for the basketball statistics database.
Provides thread-safe operations and basic query validation to prevent SQL injection.
"""

import sqlite3
import logging
import time
import re

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Manages SQLite database connections and query execution."""
    
    def __init__(self, db_path='data/ucla_wbb.db'):
        """Initialize database connector.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Optimize SQLite settings
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute("PRAGMA cache_size = 10000")
            self.cursor.execute("PRAGMA temp_store = MEMORY")
            
            logger.info(f"Connected to database at {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Database connection closed")
    
    def execute_query(self, query, return_error=False):
        """Execute a SQL query and return results.
        
        Args:
            query: SQL query string to execute
            return_error: If True, returns (results, error) tuple; otherwise returns results or None
            
        Returns:
            Query results as list of tuples, or (results, error) if return_error=True
        """
        if not self.conn:
            self.connect()
        
        start_time = time.time()
        
        try:
            # Basic SQL injection check
            if self._is_dangerous_query(query):
                error_msg = "Query contains potentially dangerous SQL patterns"
                logger.error(error_msg)
                if return_error:
                    return None, error_msg
                return None
            
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            execution_time = time.time() - start_time
            logger.info(f"Query executed in {execution_time:.3f}s, returned {len(result)} rows")
            
            if return_error:
                return result, None
            return result
            
        except sqlite3.Error as e:
            error_msg = f"SQLite error: {str(e)}"
            logger.error(f"Query failed: {error_msg}")
            if return_error:
                return None, error_msg
            return None
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Query failed: {error_msg}")
            if return_error:
                return None, error_msg
            return None
    
    def _is_dangerous_query(self, query):
        """Check for potentially dangerous SQL patterns."""
        dangerous = [
            r';\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER)\s+',
            r'UNION\s+SELECT.*--',
        ]
        return any(re.search(pattern, query, re.IGNORECASE) for pattern in dangerous)
    
    def get_table_schema(self, table_name="ucla_player_stats"):
        """Get the schema for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of dicts with column info: {name, type, notnull, pk}
        """
        if not self.conn:
            self.connect()
        
        try:
            result = self.execute_query(f"PRAGMA table_info({table_name})")
            if result:
                schema = [{
                    "name": col[1],
                    "type": col[2],
                    "notnull": col[3],
                    "pk": col[5]
                } for col in result]
                logger.info(f"Retrieved schema for '{table_name}' with {len(schema)} columns")
                return schema
        except Exception as e:
            logger.error(f"Error retrieving schema: {str(e)}")
        
        return None
    
    def get_distinct_values(self, column, table="ucla_player_stats", limit=1000):
        """Get distinct values for a column.
        
        Args:
            column: Column name
            table: Table name
            limit: Maximum number of values to return
            
        Returns:
            List of distinct values
        """
        if not self.conn:
            self.connect()
        
        try:
            query = f'SELECT DISTINCT "{column}" FROM {table} WHERE "{column}" IS NOT NULL LIMIT {limit}'
            result = self.execute_query(query)
            if result:
                return [item[0] for item in result]
        except Exception as e:
            logger.error(f"Error getting distinct values for '{column}': {str(e)}")
        
        return []
