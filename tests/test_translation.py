from unittest.mock import patch


def test_translation_not_called_for_en(client, mock_dependencies):
    mock_dependencies['bible_db'].similarity_search_with_relevance_scores.return_value = []

    with patch('search_service.translate_query') as mock_translate:
        response = client.post(
            '/search',
            json={
                'query': 'Love',
                'settings': {
                    'language': 'en',
                    'commentary': False,
                    'insights': False,
                },
            },
        )

    assert response.status_code == 200
    mock_translate.assert_not_called()


def test_translation_called_for_pl(client, mock_dependencies):
    mock_dependencies['bible_db'].similarity_search_with_relevance_scores.return_value = []

    with patch('search_service.translate_query', return_value='Love') as mock_translate:
        response = client.post(
            '/search',
            json={
                'query': 'Miłość',
                'settings': {
                    'language': 'pl',
                    'commentary': False,
                    'insights': False,
                },
            },
        )

    assert response.status_code == 200
    mock_translate.assert_called_once_with('Miłość', mock_dependencies['llm_translate'])
