import os
import json
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, Response, stream_with_context, abort
from dotenv import load_dotenv
from flask_cors import CORS
from flasgger import Swagger
import logging
import traceback

from constants import *
from utils import (
    setup_llms, setup_db, 
    format_bible_results, search_and_format_commentaries,
    translate_query
)
from search_service import SearchService

# Load environment variables
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

@app.before_request
def require_api_key():
    # Allow OPTIONS requests for CORS preflight
    if request.method == 'OPTIONS':
        return
        
    # Allow health check without authentication
    if request.endpoint == 'health_check':
        return

    # Check for API Key
    api_key = os.getenv('API_KEY')
    if api_key:
        request_key = request.headers.get('X-API-KEY')
        if not request_key or request_key != api_key:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing X-API-KEY'}), 401
template = {
    "info": {
        "title": "Bible Assistant API",
        "description": "Semantic search and AI insights for the Bible.",
        "contact": {
            "name": "eymanM",
            "url": "https://github.com/eymanM",
        },
        "version": "1.0.0"
    }
}
swagger = Swagger(app, template=template)

# Initialize Resources
llm_insights, llm_translate = setup_llms()
bible_db = setup_db(DB_DIR, DB_QUERY)
commentary_db = setup_db(COMMENTARY_DB_DIR, COMMENTARY_DB_QUERY)


# Initialize Executor (Global)
executor = ThreadPoolExecutor(max_workers=4)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    responses:
        200:
            description: Service is healthy
            schema:
                type: object
                properties:
                    status:
                        type: string
                        example: healthy
    """
    return jsonify({'status': 'healthy'}), 200

@app.route('/search', methods=['POST'])
def search():
    """
    Semantic Search Endpoint
    ---
    parameters:
        - name: body
          in: body
          required: true
          schema:
              type: object
              properties:
                  query:
                      type: string
                      example: "What is love?"
                  settings:
                      type: object
                      properties:
                          oldTestament:
                              type: boolean
                              default: true
                          newTestament:
                              type: boolean
                              default: true
                          commentary:
                              type: boolean
                              default: true
                          insights:
                              type: boolean
                              default: true
                          language:
                              type: string
                              default: "en"
                              enum: ["en", "pl"]
    responses:
        200:
            description: Stream of search results and AI insights
            content:
                text/event-stream:
                    schema:
                        type: string
                        example: "event: results..."
        400:
            description: Missing query parameter
    """
    try:
        data = request.get_json(silent=True) or {}
        search_query = data.get('query')
        settings = data.get('settings', {})

        # Settings parsing
        include_ot = settings.get('oldTestament', True)
        include_nt = settings.get('newTestament', True)
        include_commentary = settings.get('commentary', True)
        include_insights = settings.get('insights', True)
        language = settings.get('language', 'en')

        if not search_query:
            return jsonify({'error': 'No query provided'}), 400

        if len(search_query) > 150:
            return jsonify({'error': 'Query too long. Maximum 150 characters allowed.'}), 400

        # Delegate to SearchService
        search_service = SearchService(bible_db, commentary_db, llm_insights, llm_translate)
        
        return Response(stream_with_context(search_service.generate_results(search_query, settings)), mimetype='text/event-stream')

    except Exception as e:
        logging.error(f"Error in search endpoint: {e}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
