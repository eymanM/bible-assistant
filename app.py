import os
import logging
import traceback
from flask import Flask, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from flask_cors import CORS
from flasgger import Swagger

from constants import *
from utils import setup_llms, setup_db
from search_service import SearchService

# Load environment variables
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

ALLOWED_LANGUAGES = {"en", "pl"}


@app.before_request
def require_api_key():
    # Allow OPTIONS requests for CORS preflight
    if request.method == 'OPTIONS':
        return

    # Allow health check without authentication
    if request.endpoint == 'health_check':
        return

    # Allow Swagger UI and static docs assets without authentication
    if request.path.startswith('/apidocs') or request.path.startswith('/flasgger_static'):
        return

    # Check for API Key
    api_key = os.getenv('API_KEY')
    if api_key:
        request_key = request.headers.get('X-API-KEY')
        if not request_key or request_key != api_key:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing X-API-KEY'}), 401


def _parse_search_settings(raw_settings):
    settings = raw_settings if isinstance(raw_settings, dict) else {}

    language = settings.get('language', 'en')
    if not isinstance(language, str):
        raise ValueError("Invalid language. Allowed values: en, pl.")

    language = language.strip().lower()
    if language not in ALLOWED_LANGUAGES:
        raise ValueError("Invalid language. Allowed values: en, pl.")

    def _read_bool(key, default):
        value = settings.get(key, default)
        return value if isinstance(value, bool) else default

    return {
        'oldTestament': _read_bool('oldTestament', True),
        'newTestament': _read_bool('newTestament', True),
        'commentary': _read_bool('commentary', True),
        'insights': _read_bool('insights', True),
        'language': language,
    }


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
search_service = SearchService(bible_db, commentary_db, llm_insights, llm_translate)


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

        if not isinstance(search_query, str) or not search_query.strip():
            return jsonify({'error': 'No query provided'}), 400

        search_query = search_query.strip()
        if len(search_query) > 150:
            return jsonify({'error': 'Query too long. Maximum 150 characters allowed.'}), 400

        try:
            settings = _parse_search_settings(data.get('settings', {}))
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400

        return Response(
            stream_with_context(search_service.generate_results(search_query, settings)),
            mimetype='text/event-stream',
        )

    except Exception as e:
        logging.error(f"Error in search endpoint: {e}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
