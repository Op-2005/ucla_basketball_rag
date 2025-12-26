#!/usr/bin/env python3
"""
UCLA Women's Basketball RAG Analytics Web Application

Flask web application that serves the React frontend and provides API endpoints
for the RAG-powered basketball statistics chatbot. Handles natural language
queries and returns intelligent responses using Claude AI.
"""

import os
import sys
import sqlite3
import logging
import traceback
import subprocess
from datetime import datetime
from threading import local
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.db_connector import DatabaseConnector
    from src.rag_pipeline import RAGPipeline
    from src.llm_utils import LLMManager
except ImportError as e:
    print(f"Error importing RAG components: {e}")
    sys.exit(1)

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ucla_webapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app - serve React build + API
react_build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
app = Flask(__name__, 
           static_folder=react_build_dir,
           static_url_path='',
           template_folder=react_build_dir)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ucla-womens-basketball-rag-secret-key-2024')

# Enable CORS for API endpoints
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Thread-local storage for database connections
thread_local = local()


def get_thread_safe_connection():
    # Get thread-safe database connection
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect(
            'data/ucla_wbb.db', 
            check_same_thread=False
        )
        thread_local.connection.row_factory = sqlite3.Row
    return thread_local.connection


def init_session():
    # Initialize session variables
    if 'token_count' not in session:
        session['token_count'] = 0
    if 'chat_history' not in session:
        session['chat_history'] = []


@app.before_request
def before_request():
    # Initialize session before each request
    init_session()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # Serve React app for all non-API routes
    if path.startswith('api/') or path in ['query', 'health', 'stats', 'history', 'clear-chat']:
        return jsonify({'error': 'Not found'}), 404
    
    build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
    index_path = os.path.join(build_dir, 'index.html')
    
    if os.path.exists(index_path):
        return send_from_directory(build_dir, 'index.html')
    else:
        return f"React app not found. Build directory: {build_dir}", 500


@app.route('/api/query', methods=['POST'])
@app.route('/query', methods=['POST'])
def query():
    # Handle user queries using RAG pipeline
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({'error': 'Please enter a question'}), 400
        
        logger.info(f"Processing query: {user_query}")
        
        # Process with RAG pipeline
        response_data = process_with_rag_pipeline(user_query)
        
        # Update session
        token_count = len(response_data.get('response', '').split())
        session['token_count'] += token_count
        session['chat_history'].append({
            'timestamp': datetime.now().isoformat(),
            'query': user_query,
            'response': response_data.get('response', ''),
            'tokens': token_count
        })
        
        return jsonify({
            'response': response_data.get('response', 'Sorry, no response generated.'),
            'tokens': token_count,
            'total_tokens': session['token_count']
        })
        
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'response': 'Sorry, there was an error processing your question. Please try again.'
        }), 200


def process_with_rag_pipeline(user_query):
    # Process query through RAG pipeline
    try:
        db_connector = DatabaseConnector(db_path='data/ucla_wbb.db')
        db_connector.connect()
        llm_manager = LLMManager()
        rag_pipeline = RAGPipeline(llm_manager, db_connector, table_name="ucla_player_stats")
        
        result = rag_pipeline.process_query(user_query)
        db_connector.close()
        
        return {
            'response': result.get('response', 'I could not process that query.'),
            'success': result.get('success', False)
        }
        
    except Exception as e:
        logger.error(f"RAG pipeline error: {str(e)}")
        traceback.print_exc()
        return {
            'response': f'I encountered an error: {str(e)[:100]}',
            'success': False
        }


@app.route('/api/health', methods=['GET'])
@app.route('/health')
def health():
    # Health check endpoint
    try:
        conn = get_thread_safe_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ucla_player_stats")
        count = cursor.fetchone()[0]
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'records': count,
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
@app.route('/stats')
def stats():
    # Get application and database statistics
    try:
        conn = get_thread_safe_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT game_date) FROM ucla_player_stats")
        games_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT Name) FROM ucla_player_stats WHERE Name NOT IN ('Totals', 'TM')")
        players_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT AVG(CAST(Pts AS REAL)) 
            FROM ucla_player_stats 
            WHERE Name = 'Totals' AND Pts IS NOT NULL AND Pts != ''
        """)
        avg_points = round(cursor.fetchone()[0] or 0, 1)
        
        return jsonify({
            'total_tokens': session.get('token_count', 0),
            'chat_sessions': len(session.get('chat_history', [])),
            'games_in_db': games_count,
            'players_tracked': players_count,
            'avg_points': avg_points,
            'rag_status': 'active'
        })
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({
            'total_tokens': session.get('token_count', 0),
            'chat_sessions': len(session.get('chat_history', [])),
            'games_in_db': 0,
            'players_tracked': 0,
            'avg_points': 0.0,
            'rag_status': 'error'
        })


@app.route('/api/history', methods=['GET'])
@app.route('/history')
def history():
    # Get chat history for current session
    return jsonify(session.get('chat_history', []))


@app.route('/api/clear-chat', methods=['POST'])
@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    # Clear chat history and reset counters
    session['chat_history'] = []
    session['token_count'] = 0
    return jsonify({'success': True})


if __name__ == '__main__':
    try:
        # Test database connection
        conn = sqlite3.connect('data/ucla_wbb.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ucla_player_stats")
        record_count = cursor.fetchone()[0]
        conn.close()
        
        # Check React build
        react_ready = os.path.exists(react_build_dir) and os.path.exists(os.path.join(react_build_dir, 'index.html'))
        
        if not react_ready:
            print("React frontend not built. Building now...")
            try:
                frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
                build_result = subprocess.run(
                    ['npm', 'run', 'build'],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                react_ready = build_result.returncode == 0
            except Exception as e:
                print(f"Could not build automatically: {str(e)}")
                print("Please run: cd frontend && npm run build")
        
        # Startup messages
        print("=" * 60)
        print("UCLA Women's Basketball RAG Analytics Web App")
        print("=" * 60)
        print(f"Database connected: {record_count} records found")
        print(f"React frontend: {'Ready' if react_ready else 'Not built'}")
        print(f"Server: http://localhost:5001")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5001, threaded=True, use_reloader=False)
        
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        traceback.print_exc()
        logger.error(f"Application startup failed: {str(e)}")
