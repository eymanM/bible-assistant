import os
import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_openai import ChatOpenAI
from constants import *
import xml.etree.ElementTree as ET
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

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

# Load XML data
def load_xml_data(input_file):
    tree = ET.parse(input_file)
    return tree.getroot()

# Load lexicon XML data
def load_lexicon_xml(input_file):
    lexicon = {}
    root = load_xml_data(input_file)
    ns = {'tei': 'http://www.crosswire.org/2008/TEIOSIS/namespace'}

    for entry in root.findall('tei:entry', ns):
        entry_id = entry.get('n')
        orth_element = entry.find('tei:orth', ns)
        orth_text = orth_element.text if orth_element is not None else None
        defs = {def_element.get('role'): def_element.text for def_element in entry.findall('tei:def', ns)}
        lexicon[entry_id] = {'orth': orth_text, 'definitions': defs}

    return lexicon

# Perform commentary search asynchronously
async def perform_commentary_search_async(commentary_db, search_query):
    search_results = []
    loop = asyncio.get_running_loop()
    for author in CHURCH_FATHERS:
        try:
            results = await loop.run_in_executor(
                None,
                commentary_db.similarity_search_with_relevance_scores,
                search_query,
                1,
                {FATHER_NAME: author},
            )
            if results and results[0][1] > 0.83:
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
llm = setup_llm()
bible_db = setup_db(DB_DIR, DB_QUERY)
commentary_db = setup_db(COMMENTARY_DB_DIR, COMMENTARY_DB_QUERY)
bible_xml = load_xml_data(BIBLE_XML_FILE)

@app.route('/search', methods=['POST'])
async def search():
    search_query = request.json['query']
    loop = asyncio.get_running_loop()
    
    bible_search_task = loop.run_in_executor(
        None,
        bible_db.similarity_search_with_relevance_scores,
        search_query,
        2
    )
    commentary_search_task = perform_commentary_search_async(commentary_db, search_query)
    
    bible_search_results, commentary_search_results = await asyncio.gather(
        bible_search_task,
        commentary_search_task
    )
    
    llm_query = BIBLE_SUMMARY_PROMPT.format(
        topic=search_query, 
        passages="\n".join([f"Source: {r[0].metadata['book']}\nContent: {r[0].page_content}" for r in bible_search_results])
    )
    llm_response = llm.invoke(llm_query)
    llm_response_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

    return jsonify({
        'bible_results': format_bible_results(bible_search_results),
        'commentary_results': format_commentary_results(commentary_search_results),
        'llm_response': llm_response_content
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
