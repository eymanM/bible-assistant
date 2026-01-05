import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_openai import ChatOpenAI
from constants import *
from flask_cors import CORS
from flasgger import Swagger

# Load environment variables
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Book lists for filtering
OT_BOOKS = {
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 
    'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO', 'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 
    'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL'
}
NT_BOOKS = {
    'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP', 'COL', '1TH', '2TH', 
    '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV'
}

# Set up the language model
def setup_llm():
    try:
        return ChatOpenAI(max_tokens=MAX_TOKENS, model_name=OPEN_AI_LLM_MODEL_NAME)
    except Exception as e:
        print(LLM_ERROR)
        return None

# Set up the database
def setup_db(persist_directory, query_instruction):
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        query_instruction=query_instruction,
    )
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )

# Perform commentary search synchronously
def perform_commentary_search(commentary_db, search_query):
    search_results = []
    
    # We can use a thread pool for the individual author searches if we want even more parallelism,
    # but simplest is to just run them sequentially or in the main pool. 
    # Let's keep it simple: iterate sequentially here since this function is already running in a thread.
    for author in CHURCH_FATHERS:
        try:
            results = commentary_db.similarity_search_with_relevance_scores(
                search_query,
                k=1,
                filter={FATHER_NAME: author}
            )
            if results and results[0][1] > 0.82:
                search_results.extend(results)
        except Exception as exc:
            print(f"Author search generated an exception for {author}: {exc}")
    return search_results

# Format commentary results
def format_commentary_results(commentary_results):
    return [
        f"Source: {r[0].metadata[FATHER_NAME]}{r[0].metadata['book']} {r[0].metadata[SOURCE_TITLE]}\nContent: {r[0].page_content}"
        for r in commentary_results
    ]

# Format Bible search results
def format_verse_numbers(verse_nums_str):
    if not verse_nums_str:
        return ""
    nums = sorted([int(n) for n in verse_nums_str.split(',')])
    if not nums:
        return ""
    
    ranges = []
    range_start = nums[0]
    prev_num = nums[0]
    
    for num in nums[1:] + [None]:
        if num is None or num != prev_num + 1:
            if prev_num == range_start:
                ranges.append(str(range_start))
            else:
                ranges.append(f"{range_start}-{prev_num}")
            range_start = num
        prev_num = num if num is not None else prev_num
    
    return ','.join(ranges)

def format_bible_results(bible_search_results):
    formatted_results = []
    for r in bible_search_results:
        metadata = r[0].metadata
        book_code = metadata.get('book', '')
        book_name = BOOK_NAMES.get(book_code, book_code)
        verse_nums = format_verse_numbers(metadata.get("verse_nums", ""))
        formatted_results.append(
            f'Source: {book_name} {metadata.get("chapter")}: {verse_nums}\nContent: {r[0].page_content}'
        )
    return formatted_results

# Initialize the LLM, Bible database, and commentary database
# Using global variables for simplicity in this script
llm = setup_llm()
bible_db = setup_db(DB_DIR, DB_QUERY)
commentary_db = setup_db(COMMENTARY_DB_DIR, COMMENTARY_DB_QUERY)


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

    if not search_query:
        return jsonify({'error': 'No query provided'}), 400

    # Sync search execution using ThreadPoolExecutor for parallelism
    bible_hits = []
    commentary_hits = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_bible = executor.submit(
            bible_db.similarity_search_with_relevance_scores, 
            search_query, 
            10
        )
        
        future_commentary = None
        if include_commentary:
            future_commentary = executor.submit(
                perform_commentary_search, 
                commentary_db, 
                search_query
            )
        
        # Wait for results
        try:
            bible_hits = future_bible.result()
        except Exception as e:
            print(f"Error in bible search: {e}")
            
        if future_commentary:
            try:
                commentary_hits = future_commentary.result()
            except Exception as e:
                print(f"Error in commentary search: {e}")

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
    
    # Limit to top 2 results
    filtered_bible = filtered_bible[:2]

    def generate():
        # 1. Send Search Results
        formatted_bible = format_bible_results(filtered_bible)
        formatted_commentary = format_commentary_results(commentary_hits)
        
        results_data = json.dumps({
            'bible_results': formatted_bible,
            'commentary_results': formatted_commentary
        })
        yield f"event: results\ndata: {results_data}\n\n"

        # 2. Prepare Prompt and Stream LLM if insights enabled
        if include_insights:
            passages = "\n".join([f"Source: {r[0].metadata['book']}\nContent: {r[0].page_content}" for r in filtered_bible])
            if not passages and not formatted_commentary:
                passages = "No relevant passages found."

            llm_query = BIBLE_SUMMARY_PROMPT.format(topic=search_query, passages=passages)

            # 3. Stream LLM works synchronously now
            for chunk in llm.stream(llm_query):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    data = json.dumps({'token': content})
                    yield f"event: token\ndata: {data}\n\n"
        
        yield "event: end\ndata: {}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
