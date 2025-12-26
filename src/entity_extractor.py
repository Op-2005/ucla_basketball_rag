"""
Entity Extractor - Natural Language Processing

Extracts key information from user queries like player names, statistics, opponents, etc.
Uses Claude AI to understand the query and then matches entities to database values using
fuzzy matching to handle typos and variations.
"""

import re
import json
from thefuzz import process


class EntityExtractor:
    #Extracts and resolves entities from user queries
    
    def __init__(self, db_connector, llm_manager, table_name="ucla_player_stats"):
        """Initialize entity extractor.
        
        Args:
            db_connector: Database connector for looking up valid values
            llm_manager: LLM for understanding queries
            table_name: Name of the statistics table
        """
        self.db = db_connector
        self.llm = llm_manager
        self.table_name = table_name
        self.entity_cache = {}
        
        # Load valid values from database for fuzzy matching
        self._load_entities()
    
    def _load_entities(self):
        """Load valid players, opponents, etc. from the database."""
        if self.db.conn is None:
            self.db.connect()
        
        self.players = self.db.get_distinct_values("Name", table=self.table_name)
        self.player_numbers = self.db.get_distinct_values("No", table=self.table_name)
        self.opponents = self.db.get_distinct_values("Opponent", table=self.table_name)
    
    def extract_entities(self, query):
        """Extract entities from a user query.
        
        Args:
            query: The user's natural language question
            
        Returns:
            Dict with extracted entities: player_names, opponent, statistic, etc.
        """
        prompt = f"""
        Extract entities from this UCLA women's basketball statistics query.
        Return a JSON object with these fields:
        - player_names: Array of player names mentioned
        - player_number: Jersey number if mentioned
        - opponent: Opponent team if mentioned
        - statistic: Statistic mentioned (points, rebounds, assists, etc.)
        - comparison: Comparison operators (>, <, =, etc.)
        - value: Numeric value for comparison
        - exclude_totals: true if query wants individual players only
        - is_comparison_query: true if comparing multiple players
        
        Query: {query}
        
        JSON output:
        """
        
        try:
            result = self.llm.generate_text(prompt)
            json_match = re.search(r'({.*})', result, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group(1))
            else:
                entities = self._pattern_extract(query)
        except Exception as e:
            print(f"Error parsing JSON from LLM: {str(e)}")
            entities = self._pattern_extract(query)
        
        return self._resolve_entities(entities)
    
    def _pattern_extract(self, query):
        """Fallback: Extract entities using regex patterns."""
        entities = {
            "player_name": None,
            "player_number": None,
            "opponent": None,
            "statistic": None,
            "comparison": None,
            "value": None
        }
        
        # Extract jersey numbers
        number_match = re.search(r'#(\d+)|No\. (\d+)|number (\d+)', query, re.IGNORECASE)
        if number_match:
            entities["player_number"] = next(g for g in number_match.groups() if g)
        
        # Extract statistics
        stat_keywords = ["points", "rebounds", "assists", "steals", "blocks", "turnovers",
                        "pts", "reb", "ast", "stl", "blk", "to"]
        stat_mapping = {"pts": "points", "reb": "rebounds", "ast": "assists",
                       "stl": "steals", "blk": "blocks", "to": "turnovers"}
        
        for stat in stat_keywords:
            if stat in query.lower():
                entities["statistic"] = stat_mapping.get(stat, stat)
                break
        
        # Extract comparisons
        comp_match = re.search(r'(more than|less than|at least|at most|>|<|>=|<=|=)', query)
        if comp_match:
            entities["comparison"] = comp_match.group(1)
        
        # Extract numeric values
        value_match = re.search(r'\b(\d+)\b', query)
        if value_match:
            entities["value"] = value_match.group(1)
        
        return entities
    
    def _resolve_entities(self, entities):
        """Match extracted entities to actual database values using fuzzy matching."""
        resolved = {}
        
        # Resolve player names
        if entities.get("player_names"):
            names = entities["player_names"]
            if isinstance(names, str):
                names = [names]
            
            resolved_names = []
            for name in names:
                match = self._fuzzy_match(name, self.players)
                if match:
                    resolved_names.append(match)
            
            if resolved_names:
                resolved["player_names"] = resolved_names
        
        # Resolve player number
        if entities.get("player_number"):
            match = self._fuzzy_match(str(entities["player_number"]), self.player_numbers)
            if match:
                resolved["player_number"] = match
        
        # Resolve opponent
        if entities.get("opponent"):
            match = self._fuzzy_match(entities["opponent"], self.opponents)
            if match:
                resolved["opponent"] = match
        
        # Copy other fields directly
        for field in ["statistic", "comparison", "value", "exclude_totals", "is_comparison_query"]:
            if field in entities and entities[field] is not None:
                resolved[field] = entities[field]
        
        return resolved
    
    def _fuzzy_match(self, query, options, threshold=75):
        """Find best match using fuzzy string matching.
        
        Args:
            query: The string to match
            options: List of valid options
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Best matching string or None if no good match
        """
        if not query or not options or not isinstance(query, str):
            return None
        
        # Check cache
        cache_key = f"{query}:{','.join(str(opt) for opt in options[:5])}"
        if cache_key in self.entity_cache:
            return self.entity_cache[cache_key]
        
        try:
            match, score = process.extractOne(query, options)
            if score >= threshold:
                self.entity_cache[cache_key] = match
                return match
        except Exception as e:
            print(f"Error in fuzzy matching: {str(e)}")
        
        return None
