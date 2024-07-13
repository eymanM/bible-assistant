import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_anthropic import ChatAnthropic
from constants import *
import xml.etree.ElementTree as ET
from flask_wtf.csrf import CSRFProtect

load_dotenv()
# Set the secret key from environment variable
app = Flask(__name__)
#app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')
#csrf = CSRFProtect(app)


# Set up the language model
def setup_llm():
    try:
        llm = ChatAnthropic(max_tokens=MAX_TOKENS, model_name=LLM_MODEL_NAME)
    except Exception as e:
        print(LLM_ERROR)
        llm = None
    return llm


# Set up the database for Bible search
def setup_db(persist_directory, query_instruction):
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        query_instruction=query_instruction,
    )
    db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    return db


# Load Bible XML data
def load_bible_xml(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    return root


# Load lexicon XML data
def load_lexicon_xml(input_file):
    lexicon = {}
    tree = ET.parse(input_file)
    root = tree.getroot()
    ns = {'tei': 'http://www.crosswire.org/2008/TEIOSIS/namespace'}

    for entry in root.findall('tei:entry', ns):
        entry_id = entry.get('n')
        orth_element = entry.find('tei:orth', ns)
        orth_text = orth_element.text if orth_element is not None else None
        defs = {}
        for def_element in entry.findall('tei:def', ns):
            role = def_element.get('role')
            defs[role] = def_element.text
        lexicon[entry_id] = {
            'orth': orth_text,
            'definitions': defs
        }

    return lexicon


# Perform commentary search
def perform_commentary_search(commentary_db, search_query):
    search_results = []

    for author in CHURCH_FATHERS:
        try:
            results = commentary_db.similarity_search_with_relevance_scores(
                search_query,
                k=1,
                filter={FATHER_NAME: author},
            )
            if results:
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
def format_bible_results(bible_search_results):
    formatted_results = [
        (f'Source: {r[0].metadata["book"]} '
         f'{r[0].metadata["chapter"]}:'
         f'{r[0].metadata["verse_nums"].split(",")[0]}-{r[0].metadata["verse_nums"].split(",")[-1]}'
         f"\nContent: {r[0].page_content}")
        for r in bible_search_results
    ]
    return formatted_results


# Initialize the LLM, Bible database, and commentary database
llm = setup_llm()
bible_db = setup_db(DB_DIR, DB_QUERY)
commentary_db = setup_db(COMMENTARY_DB_DIR, COMMENTARY_DB_QUERY)
bible_xml = load_bible_xml(BIBLE_XML_FILE)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['query']
    bible_search_results = bible_db.similarity_search_with_relevance_scores(search_query, k=2)
    results = []
    for r in bible_search_results:
        content = r[0].page_content
        metadata = r[0].metadata["book"]
        results.append(f"Source: {metadata}\nContent: {content}")
    all_results = "\n".join(results)
    llm_query = BIBLE_SUMMARY_PROMPT.format(topic=search_query, passages=all_results)
    llm_response = llm.invoke(llm_query)

    # Perform commentary search
    commentary_search_results = perform_commentary_search(commentary_db, search_query)

    # Extract relevant information from llm_response
    llm_response_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

    return jsonify({
        'bible_results': format_bible_results(bible_search_results),
        'commentary_results': format_commentary_results(commentary_search_results),
        'llm_response': llm_response_content
    })


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
