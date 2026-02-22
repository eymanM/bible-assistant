
def test_search_limit_exceeded(client):
    long_query = "x" * 151
    response = client.post('/search', json={'query': long_query})

    assert response.status_code == 400
    payload = response.get_json()
    assert 'Query too long' in payload['error']


def test_search_limit_boundary(client, mock_dependencies):
    mock_dependencies['bible_db'].similarity_search_with_relevance_scores.return_value = []

    boundary_query = "x" * 150
    response = client.post(
        '/search',
        json={
            'query': boundary_query,
            'settings': {
                'commentary': False,
                'insights': False,
            }
        },
    )

    assert response.status_code == 200
    assert response.mimetype == 'text/event-stream'
    assert 'event: results' in response.data.decode('utf-8')
