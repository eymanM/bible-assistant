from unittest.mock import MagicMock

from search_service import SearchService
from utils import format_verse_numbers


def test_format_verse_numbers_ignores_invalid_values():
    assert format_verse_numbers('1, 2,foo,,4,4,5') == '1-2,4-5'


def test_generate_results_without_insights_model_skips_error_event():
    bible_db = MagicMock()
    bible_db.similarity_search_with_relevance_scores.return_value = []

    service = SearchService(
        bible_db=bible_db,
        commentary_db=MagicMock(),
        llm_insights=None,
        llm_translate=None,
    )

    events = list(service.generate_results(
        'hope',
        {
            'language': 'en',
            'oldTestament': True,
            'newTestament': True,
            'commentary': False,
            'insights': True,
        },
    ))

    assert any('event: results' in event for event in events)
    assert any('event: end' in event for event in events)
    assert not any('event: error' in event for event in events)
