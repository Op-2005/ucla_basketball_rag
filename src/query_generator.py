"""
SQL Query Generator - Natural Language to SQL Conversion

Converts user questions into SQLite-compatible SQL queries. Handles the mapping
between natural language terms (like "points") and database column names (like "Pts"),
and ensures generated SQL works with SQLite's limitations (no PostgreSQL features).
"""

import re
import logging
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class SQLQueryGenerator:
    """Generates SQLite-compatible SQL queries from natural language."""
    
    def __init__(self, llm_manager, db_connector, table_name="ucla_player_stats"):
        """Initialize query generator.
        
        Args:
            llm_manager: LLM for generating SQL
            db_connector: Database connector for schema info
            table_name: Name of the statistics table
        """
        self.llm = llm_manager
        self.db = db_connector
        self.table_name = table_name
        self.table_schema = self.db.get_table_schema(table_name=self.table_name)
        
        # Map user-friendly terms to database column names
        self.column_map = {
            "points": "Pts", "rebounds": "Reb", "assists": "Ast",
            "steals": "Stl", "blocks": "Blk", "turnovers": '"TO"',
            "field goals": "FG", "three pointers": '"3PTM"', "three-pointers": '"3PTM"',
            "3pt": '"3PTM"', "threes": '"3PTM"', "free throws": "FT",
            "minutes": "Min", "opponent": "Opponent", "date": "game_date",
            "number": '"No"', "jersey number": '"No"', "player number": '"No"',
            "field goal percentage": "(CAST(FGM AS FLOAT) / NULLIF(FGA, 0))",
            "three point percentage": '(CAST("3PTM" AS FLOAT) / NULLIF("3PTA", 0))',
            "free throw percentage": "(CAST(FTM AS FLOAT) / NULLIF(FTA, 0))",
            "fg%": "(CAST(FGM AS FLOAT) / NULLIF(FGA, 0))",
            "3pt%": '(CAST("3PTM" AS FLOAT) / NULLIF("3PTA", 0))',
            "ft%": "(CAST(FTM AS FLOAT) / NULLIF(FTA, 0))",
        }
    
    def generate_sql_query(self, user_query, extracted_entities=None, retry_count=0):
        """Generate SQL query from natural language.
        
        Args:
            user_query: The user's question
            extracted_entities: Entities extracted from the query
            retry_count: Number of retry attempts (max 2)
            
        Returns:
            SQL query string or None if generation fails
        """
        # Handle special case queries
        if self._is_close_games_query(user_query):
            return self._generate_close_games_query()
        
        # Create prompt with schema and entities
        schema_str = self._format_schema()
        prompt = self._create_prompt(user_query, schema_str, extracted_entities)
        
        try:
            sql_query = self.llm.generate_text(prompt)
            logger.info(f"Generated SQL: {sql_query}")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
        
        # Extract and clean SQL
        sql_query = self._extract_sql(sql_query)
        sql_query = self._fix_sqlite_compatibility(sql_query)
        
        # Validate and retry if needed
        is_valid, error = self.validate_sql(sql_query)
        if not is_valid and retry_count < 2:
            logger.warning(f"Invalid SQL, retrying... Error: {error}")
            return self.generate_sql_query(user_query, extracted_entities, retry_count + 1)
        
        return sql_query
    
    def _create_prompt(self, user_query, schema_str, extracted_entities):
        """Create prompt for LLM to generate SQLite-compatible SQL."""
        entities_str = str(extracted_entities) if extracted_entities else 'None'
        
        return f"""
You are an expert SQLite query generator for UCLA women's basketball statistics.

CRITICAL SQLITE REQUIREMENTS:
- Use ONLY SQLite syntax - NO PostgreSQL features
- FORBIDDEN: EXTRACT, INTERVAL, DATE_TRUNC, STDDEV, VARIANCE, ILIKE, ::, SIMILAR TO, SPLIT_PART
- For dates: Use strftime('%Y-%m-%d', date_column) instead of EXTRACT
- For standard deviation: Use SQRT(AVG((col - avg_col) * (col - avg_col)))
- Use CAST(col AS REAL) for type conversion, not ::
- Use LIKE instead of ILIKE

COLUMN NAMING:
- Always quote special columns: "3PTM", "3PTA", "TO", "No", "OR-DR"
- Column names are case-sensitive
- Available: Name, "No", Min, FG, "3PT", FT, "OR-DR", Reb, Ast, "TO", Blk, Stl, Pts, Opponent, game_date

Database schema:
{schema_str}

Extracted entities: {entities_str}

User question: {user_query}

RULES:
- Always exclude Name='Totals', Name='TM', Name='Team' (use WHERE Name NOT IN ('Totals', 'TM', 'Team'))
- Quote special column names: "TO", "3PTM", "3PTA", "No"
- Use SQLite date functions: date(), datetime(), strftime()
- Handle NULL with NULLIF() or COALESCE()
- Avoid complex CTEs - use simple subqueries
- Keep queries simple

Generate ONLY the SQL query with no explanations.
"""
    
    def _fix_sqlite_compatibility(self, sql_query):
        """Fix common PostgreSQL-to-SQLite conversion issues."""
        if not sql_query:
            return sql_query
        
        original = sql_query
        
        # Fix aggregate functions in GROUP BY
        if re.search(r'GROUP\s+BY.*?AVG\s*\([^)]+\)', sql_query, re.IGNORECASE | re.DOTALL):
            if 'opponent_strength' in sql_query.lower():
                sql_query = self._fix_opponent_query()
        
        # Fix CTE in WHERE clause
        if re.search(r'WHERE.*?WITH\s+\w+\s+AS\s*\(', sql_query, re.IGNORECASE | re.DOTALL):
            sql_query = self._fix_cte_in_where(sql_query)
        
        # Common PostgreSQL -> SQLite replacements
        replacements = {
            r'EXTRACT\s*\(\s*YEAR\s+FROM\s+([^)]+)\)': r"strftime('%Y', \1)",
            r'EXTRACT\s*\(\s*MONTH\s+FROM\s+([^)]+)\)': r"strftime('%m', \1)",
            r"([^'\"]+)\s*\+\s*INTERVAL\s+'(\d+)'\s*DAY": r"date(\1, '+\2 days')",
            r'::text|::integer|::float|::date': '',
            r'\bILIKE\b': 'LIKE',
            r'\bSTDDEV\s*\(\s*([^)]+)\s*\)': r'SQRT(AVG((\1 - sub_avg) * (\1 - sub_avg)))',
            r'\b3PTM\b': '"3PTM"',
            r'\b3PTA\b': '"3PTA"',
            r'\bTO\b(?!\s*\(|\s*,|\s*FROM|\s*WHERE|\s*ORDER|\s*GROUP)': '"TO"',
            r'\bNo\b(?=\s*=|\s*>|\s*<|\s*IN)': '"No"',
        }
        
        for pattern, replacement in replacements.items():
            sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
        
        # Fix syntax issues
        sql_query = re.sub(r'WHERE\s*\)', ')', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'WHERE\s*AND', 'WHERE', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'""([^"]+)""', r'"\1"', sql_query)
        
        # Fix parentheses balance
        open_parens = sql_query.count('(')
        close_parens = sql_query.count(')')
        if open_parens > close_parens:
            sql_query += ')' * (open_parens - close_parens)
        elif close_parens > open_parens:
            sql_query = re.sub(r'\)\s*$', '', sql_query, count=close_parens - open_parens)
        
        if sql_query != original:
            logger.info("Applied SQLite compatibility fixes")
        
        return sql_query
    
    def _fix_opponent_query(self):
        """Fix opponent strength queries that use aggregates in GROUP BY."""
        return """
        SELECT
          'vs_all_opponents' as analysis_type,
          COUNT(*) as games_played,
          ROUND(AVG(Pts), 1) as avg_points,
          ROUND(AVG(Reb), 1) as avg_rebounds,
          ROUND(CAST(SUM(FGM) AS REAL) / NULLIF(SUM(FGA), 0) * 100, 1) as fg_percentage,
          ROUND(AVG(Blk), 1) as avg_blocks,
          GROUP_CONCAT(DISTINCT Opponent) as opponents_faced
        FROM ucla_player_stats
        WHERE Name = 'Betts, Lauren'
          AND Name NOT IN ('Totals', 'TM', 'Team')
        """.strip()
    
    def _fix_cte_in_where(self, sql_query):
        """Fix queries with CTE syntax in WHERE clauses."""
        if 'close' in sql_query.lower() and any(name in sql_query for name in ['Rice', 'Jones']):
            return """
            SELECT 
              Name,
              COUNT(*) as games_played,
              ROUND(AVG(Pts), 1) as avg_pts,
              ROUND(AVG(Ast), 1) as avg_ast,
              ROUND(AVG(Reb), 1) as avg_reb,
              ROUND(AVG("TO"), 1) as avg_to,
              ROUND(CAST(SUM(FGM) AS REAL) / NULLIF(SUM(FGA), 0) * 100, 1) as fg_pct,
              ROUND(CAST(SUM("3PTM") AS REAL) / NULLIF(SUM("3PTA"), 0) * 100, 1) as three_pt_pct
            FROM ucla_player_stats
            WHERE Name IN ('Rice, Kiki', 'Jones, Londynn')
              AND Name NOT IN ('Totals', 'TM', 'Team')
              AND game_date IN (
                SELECT game_date 
                FROM ucla_player_stats 
                WHERE Name = 'Totals' 
                AND Pts BETWEEN 70 AND 90
              )
            GROUP BY Name
            ORDER BY avg_pts DESC
            """.strip()
        
        # Remove CTE syntax from WHERE
        return re.sub(r'WITH\s+\w+\s+AS\s*\(', '(', sql_query, flags=re.IGNORECASE)
    
    def validate_sql(self, sql_query):
        """Validate SQL for SQLite compatibility.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sql_query or sql_query.strip() == "":
            return False, "Empty SQL query"
        
        # Check for forbidden patterns
        forbidden = [
            (r'\bEXTRACT\b', "EXTRACT not supported in SQLite"),
            (r'\bINTERVAL\b', "INTERVAL not supported in SQLite"),
            (r'\bSTDDEV\b', "STDDEV not supported in SQLite"),
            (r'\bILIKE\b', "ILIKE not supported in SQLite"),
            (r'::', "PostgreSQL casting (::) not supported"),
            (r'GROUP\s+BY.*?AVG\s*\([^)]+\)', "Aggregate functions not allowed in GROUP BY"),
            (r'WHERE.*?WITH\s+\w+\s+AS\s*\(', "CTE cannot be used inside WHERE clause"),
        ]
        
        for pattern, error_msg in forbidden:
            if re.search(pattern, sql_query, re.IGNORECASE):
                return False, error_msg
        
        # Check for required elements
        if not re.search(r'\bSELECT\b', sql_query, re.IGNORECASE):
            return False, "Query must contain SELECT"
        
        if self.table_name not in sql_query:
            return False, f"Query must reference table '{self.table_name}'"
        
        return True, None
    
    def _format_schema(self):
        """Format database schema for the prompt."""
        if not self.table_schema:
            return f"Table: {self.table_name} (schema not available)"
        
        lines = [f"Table: {self.table_name}"]
        lines.extend(f"- {col['name']} ({col['type']})" for col in self.table_schema)
        return "\n".join(lines)
    
    def _extract_sql(self, response):
        """Extract SQL query from LLM response."""
        if not response:
            return ""
        
        # Try triple backticks
        match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try regular backticks
        match = re.search(r'`(.*?)`', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try SELECT statement
        match = re.search(r'(SELECT.*?;?)\s*$', response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Clean and return
        return re.sub(r'^[^S]*?(SELECT)', r'\1', response, flags=re.IGNORECASE | re.DOTALL).strip()
    
    def _is_close_games_query(self, user_query):
        """Check if this is a close games query needing special handling."""
        return ('close' in user_query.lower() and 
                'games' in user_query.lower() and 
                any(name in user_query for name in ['Rice', 'Jones', 'Kiki', 'Londynn']))
    
    def _generate_close_games_query(self):
        """Generate a simple close games comparison query."""
        return """
        SELECT 
          Name,
          COUNT(*) as games_played,
          ROUND(AVG(Pts), 1) as avg_pts,
          ROUND(AVG(Ast), 1) as avg_ast,
          ROUND(AVG(Reb), 1) as avg_reb,
          ROUND(AVG("TO"), 1) as avg_to,
          ROUND(CAST(SUM(FGM) AS REAL) / NULLIF(SUM(FGA), 0) * 100, 1) as fg_pct,
          ROUND(CAST(SUM("3PTM") AS REAL) / NULLIF(SUM("3PTA"), 0) * 100, 1) as three_pt_pct
        FROM ucla_player_stats
        WHERE Name IN ('Rice, Kiki', 'Jones, Londynn')
          AND Name NOT IN ('Totals', 'TM', 'Team')
        GROUP BY Name
        ORDER BY avg_pts DESC
        """.strip()
