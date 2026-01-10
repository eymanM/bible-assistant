import os
import json
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, Response, stream_with_context
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

# Load environment variables
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)
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

    # Translate Polish query to English
    if language == 'pl' and llm_translate:
        search_query = translate_query(search_query, llm_translate)

    # Parallel Execution
    
    future_bible = executor.submit(
        bible_db.similarity_search_with_relevance_scores, 
        search_query, 
        3
    )
    
    future_commentary = None
    if include_commentary:
        future_commentary = executor.submit(
            search_and_format_commentaries, 
            commentary_db, 
            search_query,
            language,
            llm_translate
        )
    
    # Logic moved to generator to prevent blocking

    def generate(future_bible=future_bible, future_commentary=future_commentary,
                 search_query=search_query, language=language, 
                 include_ot=include_ot, include_nt=include_nt,
                 include_insights=include_insights, llm_insights=llm_insights):
        try:
            # 1. Resolve Futures (Blocking happens here, inside the stream)
            # Use local variables
            bible_hits = []
            formatted_commentary = []
            
            try:
                bible_hits = future_bible.result()
            except Exception as e:
                logging.error(f"Error in bible search from future: {e}")
                bible_hits = []

            if future_commentary:
                try:
                    formatted_commentary = future_commentary.result()
                except Exception as e:
                    logging.error(f"Error in commentary search/translation from future: {e}")
                    formatted_commentary = []

            # Filter Bible Results
            filtered_bible = []
            for hit in bible_hits:
                book = hit[0].metadata.get('book')
                if not book: 
                    continue
                if include_ot and book in OT_BOOKS:
                    filtered_bible.append(hit)
                elif include_nt and book in NT_BOOKS:
                    filtered_bible.append(hit)

            # 2. Send Search Results
            # Bible formatting is fast (local lookup)
            formatted_bible = format_bible_results(filtered_bible, language=language)
            
            results_data = json.dumps({
                'bible_results': formatted_bible,
                'commentary_results': formatted_commentary
            })
            logging.info(f"Sending results: {results_data[:200]}...") # Log first 200 chars
            yield f"event: results\ndata: {results_data}\n\n"

            # 2. Prepare Prompt and Stream LLM if insights enabled
            if include_insights:
                passages = "\n".join([f"Source: {r[0].metadata['book']}\nContent: {r[0].page_content}" for r in filtered_bible])
                
                if formatted_commentary:
                    commentary_text = "\n".join(formatted_commentary)
                    passages += f"\n\nCommentaries:\n{commentary_text}"

                if not passages:
                    passages = "No relevant passages found."

                summary_prompt = BIBLE_SUMMARY_PROMPT_PL if language == 'pl' else BIBLE_SUMMARY_PROMPT
                llm_query = summary_prompt.format(topic=search_query, passages=passages)

                # 3. Stream LLM works synchronously now
                # Use llm_insights specifically
                for chunk in llm_insights.stream(llm_query):
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    if content:
                        data = json.dumps({'token': content})
                        # logging.info(f"Sending token: {content}") # Too verbose?
                        yield f"event: token\ndata: {data}\n\n"
            
            yield "event: end\ndata: {}\n\n"
        except Exception as e:
            logging.error(f"Error in generator: {e}")
            logging.error(traceback.format_exc())
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
