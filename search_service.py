import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from constants import *
from utils import setup_llms, translate_query, format_bible_results, search_and_format_commentaries

# Initialize Executor for SearchService
executor = ThreadPoolExecutor(max_workers=8)

class SearchService:
    def __init__(self, bible_db, commentary_db, llm_insights, llm_translate):
        self.bible_db = bible_db
        self.commentary_db = commentary_db
        self.llm_insights = llm_insights
        self.llm_translate = llm_translate

    def bible_search_task(self, query, language, include_ot, include_nt):
        if not (include_ot or include_nt):
            return []
            
        try:
            # Bible Search is fast
            results = self.bible_db.similarity_search_with_relevance_scores(query, k=3)
            
            # Filter
            filtered_results = []
            for hit in results:
                book = hit[0].metadata.get('book')
                if not book: continue
                if include_ot and book in OT_BOOKS:
                    filtered_results.append(hit)
                elif include_nt and book in NT_BOOKS:
                    filtered_results.append(hit)
            
            return format_bible_results(filtered_results, language=language)
        except Exception as e:
            logging.error(f"Error in bible_search_task: {e}")
            return []

    def commentary_search_task(self, query, language):
        # This includes inner translation if needed
        return search_and_format_commentaries(
            self.commentary_db, 
            query, 
            language, 
            self.llm_translate
        )

    def generate_results(self, search_query, settings):
        """
        Main Generator Function.
        Yields events: 'results', 'token', 'end', 'error'
        """
        # Settings
        language = settings.get('language', 'en')
        include_ot = settings.get('oldTestament', True)
        include_nt = settings.get('newTestament', True)
        include_commentary = settings.get('commentary', True)
        include_insights = settings.get('insights', True)
        
        # 1. Start Initial Parallel Tasks: Translate Query
        # We start translation immediately if needed
        future_translate = None
        if language == 'pl' and self.llm_translate:
             future_translate = executor.submit(translate_query, search_query, self.llm_translate)
        
        # Resolve Translation
        effective_query = search_query
        if future_translate:
            try:
                effective_query = future_translate.result()
            except Exception as e:
                logging.error(f"Translation failed: {e}")
        
        # 2. Start Deep Parallel Search (Bible & Commentary)
        future_bible = executor.submit(
            self.bible_search_task, 
            effective_query, 
            language, 
            include_ot, 
            include_nt
        )
        
        future_commentary = None
        if include_commentary:
            future_commentary = executor.submit(
                self.commentary_search_task,
                effective_query,
                language
            )

        # 3. Yield Incremental Results
        
        # A. Yield Bible (Fastest)
        bible_res = []
        try:
            bible_res = future_bible.result()
        except Exception as e:
            logging.error(f"Bible search failed: {e}")
            
        # First Yield: Bible only
        yield f"event: results\ndata: {json.dumps({'bible_results': bible_res, 'commentary_results': []})}\n\n"
        
        # B. Yield Commentary (Slower)
        commentary_res = []
        if future_commentary:
            try:
                commentary_res = future_commentary.result()
            except Exception as e:
                logging.error(f"Commentary search failed: {e}")
        
        # Second Yield: All Results
        if future_commentary or commentary_res:
             yield f"event: results\ndata: {json.dumps({'bible_results': bible_res, 'commentary_results': commentary_res})}\n\n"

        # 4. Insights
        if include_insights:
            yield from self.stream_insights(search_query, language, bible_res, commentary_res)
            
        yield "event: end\ndata: {}\n\n"

    def stream_insights(self, topic, language, bible_res, commentary_res):
        try:
            passages = "\n".join(bible_res)
            if commentary_res:
                passages += f"\n\nCommentaries:\n" + "\n".join(commentary_res)
            
            if not passages.strip():
                passages = "No relevant passages found."

            summary_prompt = BIBLE_SUMMARY_PROMPT_PL if language == 'pl' else BIBLE_SUMMARY_PROMPT
            llm_query = summary_prompt.format(topic=topic, passages=passages)

            for chunk in self.llm_insights.stream(llm_query):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    data = json.dumps({'token': content})
                    yield f"event: token\ndata: {data}\n\n"
        except Exception as e:
            logging.error(f"Insights generation failed: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
