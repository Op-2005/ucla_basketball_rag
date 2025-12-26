# UCLA Women's Basketball RAG Analytics

This project showcases a Retrieval-Augmented Generation (RAG) system that converts natural language questions about basketball statistics into SQL queries, executes them against a SQLite database, and returns conversational answers using Claude AI.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Project Demo

<!-- Project demo: [Add your demo video here] -->
https://drive.google.com/file/d/1NgWx8p0gqeaUSiCHQ2LOVcv0dUDO27te/view?usp=sharing

## Project Overview

Traditional sports analytics interfaces require users to understand database schemas and write SQL queries. This project solves the problem of making basketball statistics accessible through natural language, allowing users to ask questions like "Who scored the most points against USC?" without any technical knowledge.

The system takes natural language queries as input, processes them through a multi-stage RAG pipeline, and returns structured answers. The core challenge is bridging the gap between human language and structured database queries while ensuring correctness, safety, and SQLite compatibility.

**Input**: Natural language questions about UCLA Women's Basketball statistics  
**Output**: Conversational answers with specific statistics and insights  
**Core Components**: Entity extraction, SQL generation, query validation, database execution, response formatting

## System Architecture

The application follows a client-server architecture with a React frontend and Flask backend. The backend implements a RAG pipeline that orchestrates multiple components to process queries end-to-end.

**Frontend**: React application with TypeScript that provides a chat interface. The frontend is built as a static site and served by Flask, enabling single-process deployment.

**Backend**: Flask application that serves both the React frontend (from `frontend/dist/`) and provides REST API endpoints. The backend uses thread-local storage for database connections to ensure thread safety in a multi-threaded Flask environment.

**RAG Pipeline**: The core intelligence layer consists of four sequential components:
1. Entity Extractor: Identifies basketball-specific entities (players, stats, opponents)
2. Query Generator: Converts entities and natural language into SQL
3. Database Connector: Executes queries with validation and error handling
4. Response Generator: Formats results into natural language


## Core Components

### Entity Extractor (`src/entity_extractor.py`)

**Purpose**: Identifies and resolves basketball-specific entities from natural language queries.

**How it works**: Uses Claude AI to extract structured information (player names, statistics, opponents, dates) from queries. Then performs fuzzy matching against database values to resolve entities to exact database entries (e.g., "Kiki" → "Rice, Kiki").

**Key features**:
- LLM-based extraction for understanding context
- Fuzzy matching using `thefuzz` library to handle typos and variations
- Entity caching to avoid redundant database lookups
- Pre-loads valid players, opponents, and player numbers from the database

**Interactions**: Receives raw queries, queries the database for valid values, uses LLM manager for extraction, returns structured entity dictionary to Query Generator.

### Query Generator (`src/query_generator.py`)

**Purpose**: Converts natural language queries and extracted entities into SQLite-compatible SQL queries.

**How it works**: Uses Claude AI with a carefully crafted prompt that includes the database schema, extracted entities, and explicit SQLite syntax requirements. The prompt explicitly forbids PostgreSQL features and provides examples of correct SQLite syntax.

**Key features**:
- Column name mapping from user-friendly terms ("points") to database columns ("Pts")
- SQLite compatibility layer that fixes common PostgreSQL-to-SQLite conversion issues
- Query validation before execution to catch syntax errors early
- Retry logic (up to 2 attempts) if initial generation fails validation
- Special handling for complex query patterns (e.g., close games analysis)

**Interactions**: Receives entities from Entity Extractor, uses LLM manager for SQL generation, validates queries using Database Connector schema info, returns SQL strings to RAG Pipeline.

### Database Connector (`src/db_connector.py`)

**Purpose**: Provides thread-safe database operations with comprehensive error handling and query validation.

**How it works**: Manages SQLite connections with thread-local storage. Executes queries with timeout protection and validates syntax before execution. Tracks query statistics for monitoring.

**Key features**:
- Thread-safe connections using Python's `threading.local`
- SQL injection prevention through pattern matching and query validation
- Query statistics tracking (success rate, execution time)
- Schema introspection for dynamic query generation
- Optimized SQLite settings (foreign keys, cache size, temp store)

**Interactions**: Provides schema information to Query Generator, executes queries from RAG Pipeline, returns results or error messages.

### RAG Pipeline (`src/rag_pipeline.py`)

**Purpose**: Orchestrates the end-to-end query processing flow with fallback strategies.

**How it works**: Coordinates Entity Extractor, Query Generator, and Database Connector in sequence. Implements multiple fallback strategies when queries fail or return empty results.

**Key features**:
- Sequential pipeline execution with error handling at each stage
- Three-tier fallback system: simplified aggregation → basic select → player lookup
- Empty result handling with alternative query suggestions
- Comprehensive error messages for debugging

**Interactions**: Receives user queries from Flask app, coordinates all components, returns structured responses with success status and metadata.

### LLM Manager (`src/llm_utils.py`)

**Purpose**: Manages Anthropic Claude API interactions with proper error handling and configuration.

**How it works**: Wraps LangChain's `ChatAnthropic` with timeout and retry logic. Configurable model name via environment variable (defaults to `claude-sonnet-4-5-20250929`).

**Key features**:
- Network robustness with 60-second timeout and 2 retry attempts
- Configurable model selection via `ANTHROPIC_MODEL_NAME` environment variable
- Clear error messages for connection issues
- Embedding model support (HuggingFace) for potential future vector search

**Interactions**: Used by Entity Extractor and Query Generator for LLM calls.

## Data Flow

### Query Processing Flow

1. **User Input**: User submits natural language question via React frontend
2. **HTTP Request**: Frontend sends POST request to `/api/query` with JSON payload
3. **Entity Extraction**: RAG Pipeline calls Entity Extractor
   - Entity Extractor uses Claude AI to parse query into structured entities
   - Performs fuzzy matching against database values
   - Returns entity dictionary (player names, stats, opponents, etc.)
4. **SQL Generation**: RAG Pipeline calls Query Generator
   - Query Generator creates prompt with schema, entities, and user query
   - Claude AI generates SQL query
   - Query Generator applies SQLite compatibility fixes
   - Validates SQL syntax using Database Connector
   - Retries up to 2 times if validation fails
5. **Query Execution**: RAG Pipeline calls Database Connector
   - Database Connector validates query for SQL injection patterns
   - Executes query against SQLite database
   - Returns results or error message
6. **Fallback Handling**: If query fails or returns empty results
   - RAG Pipeline tries simplified fallback queries
   - Attempts: simplified aggregation → basic select → player lookup
7. **Response Generation**: RAG Pipeline formats results
   - Creates prompt with user query, SQL query, and results
   - Claude AI generates natural language response
   - Returns structured response with answer, metadata, and success status
8. **HTTP Response**: Flask returns JSON to frontend
9. **UI Update**: React frontend displays response in chat interface

### Data Storage

- **Database**: SQLite file (`data/ucla_wbb.db`) containing ~400 records
- **Schema**: Single table `ucla_player_stats` with columns: Name, No, Min, FG, 3PT, FT, OR-DR, Reb, Ast, TO, Blk, Stl, Pts, Opponent, game_date
- **Session Data**: Flask sessions store chat history and token counts (in-memory, not persisted)

## Model / Logic

### Entity Extraction Logic

**Input**: Raw natural language query string  
**Output**: Structured entity dictionary with fields: `player_names`, `player_number`, `opponent`, `statistic`, `comparison`, `value`, `exclude_totals`, `is_comparison_query`

**Process**:
1. LLM receives query and prompt template requesting JSON output
2. LLM returns JSON with extracted entities
3. System parses JSON and validates structure
4. Fuzzy matching resolves entities to database values (75% similarity threshold)
5. Returns resolved entity dictionary

**Fallback**: If LLM fails or returns invalid JSON, uses regex-based pattern matching for basic entity extraction.

### SQL Generation Logic

**Input**: User query, extracted entities, database schema  
**Output**: Validated SQLite-compatible SQL query string

**Process**:
1. Applies column name mapping to user query (e.g., "points" → "Pts")
2. Constructs prompt with:
   - Database schema (column names and types)
   - Extracted entities
   - Explicit SQLite syntax requirements
   - Examples of correct SQLite queries
3. LLM generates SQL query
4. Extracts SQL from LLM response (handles markdown code blocks, backticks)
5. Applies SQLite compatibility fixes:
   - Replaces PostgreSQL functions (EXTRACT → strftime, STDDEV → custom calculation)
   - Fixes type casting (:: → CAST)
   - Ensures proper quoting of special columns ("3PTM", "TO", "No")
   - Fixes parentheses mismatches
6. Validates SQL syntax using SQLite's EXPLAIN command
7. Retries up to 2 times if validation fails

**Special Cases**: Hardcoded queries for known problematic patterns (e.g., close games analysis with multiple players).

### Query Validation

**Syntax Validation**: Uses SQLite's `EXPLAIN` command to validate query syntax without execution.

**Safety Validation**: Pattern matching to detect:
- SQL injection attempts (DROP, DELETE, UPDATE, INSERT, CREATE, ALTER)
- Dangerous UNION SELECT patterns
- SQL comment injection (/* */)

**Schema Validation**: Ensures query references correct table name and contains SELECT statement.

### Response Generation Logic

**Input**: User query, executed SQL query, query results  
**Output**: Natural language response string

**Process**:
1. Constructs prompt with user question, SQL query used, and query results (limited to 10 rows)
2. LLM generates conversational response
3. Returns formatted answer

**Fallback**: If LLM generation fails, creates basic response from raw query results.


## How to Run the Project

### Prerequisites

- Python 3.9 or higher
- Node.js 16+ (for frontend build only)
- Anthropic API key

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ucla-basketball-rag.git
   cd ucla-basketball-rag
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   FLASK_SECRET_KEY=your-secret-key-here  # Optional
   ANTHROPIC_MODEL_NAME=claude-sonnet-4-5-20250929  # Optional, defaults to this
   ```

4. **Build the React frontend**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   npm run build
   cd ..
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Verify it's working**
   
   - Open browser to `http://localhost:5001`
   - Check health endpoint: `curl http://localhost:5001/api/health`
   - Try a test query: "Who is UCLA's leading scorer?"

### Development Mode

For frontend development with hot reload:

```bash
# Terminal 1: Flask backend
python app.py

# Terminal 2: React frontend (optional)
cd frontend
npm run dev
```

## Project Structure

```
ucla-basketball-rag/
├── app.py                      # Flask application (serves frontend + API)
├── src/                        # Core RAG pipeline components
│   ├── __init__.py
│   ├── rag_pipeline.py         # Main orchestration
│   ├── entity_extractor.py    # NLP entity extraction
│   ├── query_generator.py     # SQL generation
│   ├── db_connector.py         # Database operations
│   └── llm_utils.py            # LLM integration
├── frontend/                   # React frontend
│   ├── src/                   # React source code
│   │   ├── components/        # UI components
│   │   ├── context/           # State management
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript types
│   ├── public/                # Static assets
│   └── dist/                  # Production build (served by Flask)
├── data/                      # Database files
│   ├── ucla_wbb.db            # SQLite database
│   └── uclawbb_season.csv     # Raw CSV data from WBB database
├── logs/                      # Application logs (auto-created)
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # This file
```

**Key Files**:
- `app.py`: Flask application entry point, handles routing and RAG pipeline integration
- `src/rag_pipeline.py`: Core orchestration logic
- `src/query_generator.py`: SQL generation with SQLite compatibility layer
- `frontend/src/services/api.ts`: API client for backend communication


### Future Improvements to Consider

 There are several meaningful ways this system could be expanded and strengthened over time. One natural next step would be migrating the data layer to PostgreSQL to support stronger transactional guarantees, better concurrency, and more flexible analytical queries. Introducing a Redis-based caching layer would help reduce latency by storing frequently accessed query results, resolved entities, and repeated LLM responses. The system could also be extended with semantic vector search to support more nuanced querying over game summaries or play-by-play data. Further improvements could focus on query performance and reliability, including smarter query planning, adaptive rewriting when failures occur, and more graceful fallback mechanisms.

