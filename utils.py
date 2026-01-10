
import os
import json
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor
import logging

from constants import *
from bible_lookup import get_bible_text
from pydantic import BaseModel, Field
from typing import List

# Initialize LLMs
def setup_llms():
    try:
        llm_insights = ChatOpenAI(
            model_name=OPEN_AI_LLM_MODEL_NAME,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            request_timeout=60,
            model_kwargs={"max_completion_tokens": MAX_TOKENS},
            temperature=1
        )
        llm_translate = ChatOpenAI(
            model_name=OPEN_AI_LLM_MODEL_NAME_TRANSLATION,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            request_timeout=60,
            model_kwargs={"max_completion_tokens": MAX_TOKENS},
            temperature=1
        )
        return llm_insights, llm_translate
    except Exception as e:
        logging.error(f"{LLM_ERROR}: {e}")
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
    
    def search_author(author):
        try:
            results = commentary_db.similarity_search_with_relevance_scores(
                search_query,
                k=1,
                filter={FATHER_NAME: author}
            )
            if results and results[0][1] > 0.83:
                return results
        except Exception as exc:
            logging.error(f"Author search generated an exception for {author}: {exc}")
        return []

    # Use ThreadPoolExecutor to search in parallel
    # Chroma/DuckDB are usually thread-safe for reading
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(search_author, CHURCH_FATHERS)
        
    for res in results:
        if res:
            search_results.extend(res)
            
    return search_results

import hashlib
try:
    import psycopg2
    from psycopg2.extras import DictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    DictCursor = None
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 not installed. Database caching disabled.")

def get_db_connection():
    if not PSYCOPG2_AVAILABLE:
        return None
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None


class TranslationBatch(BaseModel):
    translations: List[str] = Field(description="A list of translated texts in Polish. The output list MUST have exactly the same number of elements as the input list. Each input string must have a corresponding translated string at the same index.")

def translate_texts(texts, llm):
    """Translates a list of texts to Polish using the LLM, with DB caching and Structured Output."""
    if not llm or not texts:
        return texts
        
    # Filter out empty texts to avoid unnecessary processing
    valid_texts = [t for t in texts if t and t.strip()]
    if not valid_texts:
        return texts

    conn = get_db_connection()
    cached_translations = {}
    missing_texts = []
    missing_indices = []

    # 1. Check Cache
    if conn:
        try:
            with conn.cursor() as cur:
                for i, text in enumerate(texts):
                    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                    cur.execute("SELECT translated_text FROM bible_assistant.translations WHERE hash = %s AND language = 'pl'", (text_hash,))
                    result = cur.fetchone()
                    
                    if result:
                        cached_translations[i] = result[0]
                    else:
                        missing_texts.append(text)
                        missing_indices.append(i)
        except Exception as e:
             logging.error(f"Error checking cache: {e}")
             missing_texts = texts
             missing_indices = list(range(len(texts)))
        finally:
             conn.close()
    else:
        missing_texts = texts
        missing_indices = list(range(len(texts)))

    # 2. Translate Missing (Batch with Structured Output)
    if missing_texts:
        try:
            # Prepare batch prompt
            prompt = COMMENTARY_TRANSLATION_PROMPT.format(texts=json.dumps(missing_texts))
            
            # Use Structured Output (strict=True not supported by current env)
            structured_llm = llm.with_structured_output(TranslationBatch)
            batch_result = structured_llm.invoke(prompt)
            
            if isinstance(batch_result, dict):
                translated_batch = batch_result.get('translations', [])
            elif batch_result and hasattr(batch_result, 'translations'):
                translated_batch = batch_result.translations
            else:
                translated_batch = []
            
            # Verify length
            if len(translated_batch) != len(missing_texts):
                logging.warning(f"Translation length mismatch: got {len(translated_batch)}, expected {len(missing_texts)}. Falling back to individual translation.")
                
                # Fallback: Translate one by one
                translated_batch = []
                for text in missing_texts:
                    try:
                        # Simple individual prompt
                        single_prompt = f"Translate this theological text to Polish. Maintain tone and meaning. Text: {text}"
                        response = llm.invoke(single_prompt)
                        t_text = response.content if hasattr(response, 'content') else str(response)
                        translated_batch.append(t_text.strip())
                    except Exception as inner_e:
                        logging.error(f"Fallback translation failed for text: {inner_e}")
                        translated_batch.append(text) # Keep original on error

            # Save to DB
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        for idx, text in enumerate(missing_texts):
                            t_text = translated_batch[idx] if idx < len(translated_batch) else text
                            t_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                            cur.execute("""
                                INSERT INTO bible_assistant.translations (hash, original_text, translated_text, language) 
                                VALUES (%s, %s, %s, 'pl')
                                ON CONFLICT (hash) DO NOTHING
                            """, (t_hash, text, t_text))
                        conn.commit()
                except Exception as e:
                    logging.error(f"Error saving to cache: {e}")
                finally:
                    conn.close()

            # Merge back
            for i, idx in enumerate(missing_indices):
                cached_translations[idx] = translated_batch[i]
                
        except Exception as e:
            logging.error(f"Error translating commentaries: {e}")
            for i, idx in enumerate(missing_indices):
                     cached_translations[idx] = missing_texts[i]
    
    # 3. Reconstruct Result
    final_translations = []
    for i in range(len(texts)):
        final_translations.append(cached_translations.get(i, texts[i]))
        
    return final_translations

def translate_query(query, llm):
    """Translates a search query to English using the LLM, with DB caching (en target)."""
    if not llm or not query:
        return query
    
    query = query.strip()
    if not query:
        return query

    conn = get_db_connection()
    cached_translation = None
    query_hash = hashlib.md5(query.encode('utf-8')).hexdigest()

    # 1. Check Cache (target language 'en' for queries)
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT translated_text FROM bible_assistant.translations WHERE hash = %s AND language = 'en'", (query_hash,))
                result = cur.fetchone()
                if result:
                    cached_translation = result[0]
        except Exception as e:
             logging.error(f"Error checking cache for query: {e}")
        finally:
             conn.close()
    
    if cached_translation:
        return cached_translation

    # 2. Translate
    try:
        translation_query = QUERY_TRANSLATION_PROMPT.format(query=query)
        response = llm.invoke(translation_query)
        # Handle different response types from langchain
        translated_text = response.content if hasattr(response, 'content') else str(response)
        translated_text = translated_text.strip()
        
        # 3. Save to DB
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Use ON CONFLICT DO NOTHING
                    cur.execute("""
                        INSERT INTO bible_assistant.translations (hash, original_text, translated_text, language) 
                        VALUES (%s, %s, %s, 'en')
                        ON CONFLICT (hash) DO NOTHING
                    """, (query_hash, query, translated_text))
                conn.commit()
            except Exception as e:
                logging.error(f"Error saving query to cache: {e}")
            finally:
                conn.close()
        
        return translated_text
            
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return query

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
        
        # Check for empty content
        if not display_content or not display_content.strip():
            continue
            
        # Clean short parenthetical prefixes (e.g. citations)
        display_content = display_content.strip()
        if display_content.startswith('('):
            end_paren_idx = display_content.find(')')
            if end_paren_idx != -1 and end_paren_idx < 30:
                 display_content = display_content[end_paren_idx+1:].strip()
                 
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
            
        chapter = metadata.get("chapter")
        verse_nums_str = metadata.get("verse_nums", "")
        # FIX: The metadata verse_nums might be wrong if the chunk didn't respect line boundaries perfectly,
        # or if the vector DB metadata is just a range. 
        # We now identify the REAL verses in the chunk content.
        from bible_lookup import get_real_verse_nums
        real_verse_nums = get_real_verse_nums(book_code, chapter, r[0].page_content)
        
        if real_verse_nums:
            verse_nums_str = ",".join(str(n) for n in real_verse_nums)
            
        formatted_verse_nums = format_verse_numbers(verse_nums_str)
        
        content = r[0].page_content
        
        full_text = get_bible_text(language, lookup_book_name, chapter, verse_nums_str)
        if full_text:
            content = full_text

        result_string = f'Source: {display_book_name} {chapter}: {formatted_verse_nums}\nContent: {content}'
        
        if result_string not in seen:
            formatted_results.append(result_string)
            seen.add(result_string)

    return formatted_results
