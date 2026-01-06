
import os
import json
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor

from constants import *
from bible_lookup import get_bible_text

# Initialize LLMs
def setup_llms():
    try:
        # User requested specific models:
        # - gpt-4.1-mini for AI insights
        # - gpt-4.1-nano for translations
        llm_insights = ChatOpenAI(
            max_tokens=MAX_TOKENS, 
            model_name="gpt-4.1-mini",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        llm_translate = ChatOpenAI(
            max_tokens=MAX_TOKENS, 
            model_name="gpt-4.1-nano",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )
        return llm_insights, llm_translate
    except Exception as e:
        print(f"{LLM_ERROR}: {e}")
        return None, None

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

def perform_commentary_search(commentary_db, search_query):
    search_results = []
    # Optimization: Search Church Fathers in parallel if simple iteration is too slow.
    # For now, keeping it simple as Chroma is usually fast enough for 9 authors.
    for author in CHURCH_FATHERS:
        try:
            results = commentary_db.similarity_search_with_relevance_scores(
                search_query,
                k=1,
                filter={FATHER_NAME: author}
            )
            if results and results[0][1] > 0.83:
                search_results.extend(results)
        except Exception as exc:
            print(f"Author search generated an exception for {author}: {exc}")
    return search_results

def translate_texts(texts, llm):
    """Translates a list of texts to Polish using the LLM."""
    if not llm:
        return texts
    
    try:
        # Batch translation to save calls
        prompt = COMMENTARY_TRANSLATION_PROMPT.format(texts=json.dumps(texts))
        response = llm.invoke(prompt)
        content = response.content
        
        # Strip markdown json block if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
             content = content.split("```")[1].split("```")[0].strip()
             
        translated_texts = json.loads(content)
        
        if isinstance(translated_texts, list) and len(translated_texts) == len(texts):
            return translated_texts
        else:
            print("Translation returned mismatching list length or invalid format.")## odaj tekst do logow
            print(translated_texts)
            return texts
            
    except Exception as e:
        print(f"Error translating commentaries: {e}")
        return texts

def search_and_format_commentaries(commentary_db, search_query, language, llm_translate):
    """
    Performs search and translation/formatting.
    Designed to run in a thread to unblock other tasks.
    """
    if not commentary_db:
        return []
    
    commentary_results = perform_commentary_search(commentary_db, search_query)
    commentary_results.sort(key=lambda x: x[1], reverse=True)
    commentary_results = commentary_results[:3]
    
    if not commentary_results:
        return []

    # Extract texts for potential translation
    texts_to_translate = []
    if language == 'pl':
        for r in commentary_results:
             texts_to_translate.append(r[0].page_content)
        
        # Translate
        translated_texts = translate_texts(texts_to_translate, llm_translate)
    
    formatted_results = []
    seen = set()
    for i, r in enumerate(commentary_results):
        display_content = r[0].page_content
        father_name = r[0].metadata.get(FATHER_NAME)
        
        if language == 'pl':
            if i < len(translated_texts):
                 display_content = translated_texts[i]
            father_name = CHURCH_FATHERS_PL.get(father_name, father_name)
             
        result_string = f"Source: {father_name}\nContent: {display_content}"
        
        if result_string not in seen:
            formatted_results.append(result_string)
            seen.add(result_string)
            
    return formatted_results

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

def format_bible_results(bible_search_results, language='en'):
    formatted_results = []
    seen = set()
    for r in bible_search_results:
        metadata = r[0].metadata
        book_code = metadata.get('book', '')
        book_name = BOOK_NAMES.get(book_code, book_code)
        
        # Use English name for lookup
        lookup_book_name = book_name
        
        # Determine display name
        display_book_name = book_name
        if language == 'pl':
            display_book_name = BOOK_NAMES_PL.get(book_code, display_book_name)
            
        verse_nums_str = metadata.get("verse_nums", "")
        formatted_verse_nums = format_verse_numbers(verse_nums_str)
        chapter = metadata.get("chapter")
        
        content = r[0].page_content
        
        full_text = get_bible_text(language, lookup_book_name, chapter, verse_nums_str)
        if full_text:
            content = full_text

        result_string = f'Source: {display_book_name} {chapter}: {formatted_verse_nums}\nContent: {content}'
        
        if result_string not in seen:
            formatted_results.append(result_string)
            seen.add(result_string)

    return formatted_results
