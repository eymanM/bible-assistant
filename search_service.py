import json
import logging
import asyncio

from constants import *
from utils import translate_query, format_bible_results, search_and_format_commentaries

class SearchService:
    def __init__(self, bible_db, commentary_db, llm_insights, llm_translate):
        self.bible_db = bible_db
        self.commentary_db = commentary_db
        self.llm_insights = llm_insights
        self.llm_translate = llm_translate

    async def bible_search_task(self, query, language, include_ot, include_nt):
        if not (include_ot or include_nt):
            return []

        try:
            # Async Bible Search
            results = await self.bible_db.asimilarity_search_with_relevance_scores(query, k=3)

            # Filter
            filtered_results = []
            for hit in results:
                book = hit[0].metadata.get('book')
                if not book:
                    continue

                # Relevance check
                if hit[1] < 0.84:
                    continue

                if include_ot and book in OT_BOOKS:
                    filtered_results.append(hit)
                elif include_nt and book in NT_BOOKS:
                    filtered_results.append(hit)

            return format_bible_results(filtered_results, language=language)
        except Exception as e:
            logging.error(f"Error in bible_search_task: {e}")
            return []

    async def commentary_search_task(self, query, language):
        # This includes inner translation if needed
        return await search_and_format_commentaries(
            self.commentary_db,
            query,
            language,
            self.llm_translate,
        )

    async def generate_results(self, search_query, settings):
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

        effective_query = search_query
        if language == 'pl' and self.llm_translate:
            try:
                effective_query = await translate_query(search_query, self.llm_translate)
            except Exception as e:
                logging.error(f"Translation failed: {e}")

        # Gather parallel tasks
        tasks = [self.bible_search_task(effective_query, language, include_ot, include_nt)]
        if include_commentary:
            tasks.append(self.commentary_search_task(effective_query, language))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Parse results
        bible_res = results[0] if not isinstance(results[0], Exception) else []
        if isinstance(results[0], Exception):
            logging.error(f"Bible search failed: {results[0]}")
            
        commentary_res = []
        if include_commentary and len(results) > 1:
            commentary_res = results[1] if not isinstance(results[1], Exception) else []
            if isinstance(results[1], Exception):
                logging.error(f"Commentary search failed: {results[1]}")

        # First Yield: Bible only (we can still do this iteratively if we handled tasks dynamically,
        # but gather awaits all. To preserve streaming UI, we yield the complete object)
        yield f"event: results\ndata: {json.dumps({'bible_results': bible_res, 'commentary_results': []})}\n\n"

        # Second Yield: All Results
        if include_commentary:
            yield f"event: results\ndata: {json.dumps({'bible_results': bible_res, 'commentary_results': commentary_res})}\n\n"

        # Insights
        if include_insights and self.llm_insights:
            async for chunk in self.stream_insights(search_query, language, bible_res, commentary_res):
                yield chunk
        elif include_insights and not self.llm_insights:
            logging.info("Insights requested, but llm_insights is unavailable. Skipping insight generation.")

        yield "event: end\ndata: {}\n\n"

    async def stream_insights(self, topic, language, bible_res, commentary_res):
        try:
            passages = "\n".join(bible_res)
            if commentary_res:
                passages += "\n\nCommentaries:\n" + "\n".join(commentary_res)

            if not passages.strip():
                passages = "No relevant passages found."

            summary_prompt = BIBLE_SUMMARY_PROMPT_PL if language == 'pl' else BIBLE_SUMMARY_PROMPT_EN
            llm_query = summary_prompt.format(topic=topic, passages=passages)

            async for chunk in self.llm_insights.astream(llm_query):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)

                # Handle structured content (list of dicts) from new Google models
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and 'text' in part:
                            text_parts.append(part['text'])
                        elif isinstance(part, str):
                            text_parts.append(part)
                    content = "".join(text_parts)

                if content:
                    data = json.dumps({'token': content})
                    yield f"event: token\ndata: {data}\n\n"
        except Exception as e:
            logging.error(f"Insights generation failed: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
