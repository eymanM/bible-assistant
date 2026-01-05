from unittest.mock import MagicMock
import json

def test_search_no_query(client):
    """Test that missing query returns 400"""
    response = client.post('/search', json={})
    assert response.status_code == 400
    assert b'No query provided' in response.data

def test_search_success(client, mock_dependencies):
    """Test a full successful search flow with mocked results"""
    # Setup mocks
    bible_db = mock_dependencies['bible_db']
    commentary_db = mock_dependencies['commentary_db']
    
    # Configure Bible DB results
    # Each result is a tuple: (Document, score)
    # Document has page_content and metadata
    doc1 = MagicMock()
    doc1.page_content = "In the beginning..."
    doc1.metadata = {"book": "GEN", "chapter": "1", "verse_nums": "1"}
    
    doc2 = MagicMock()
    doc2.page_content = "For God so loved..."
    doc2.metadata = {"book": "JHN", "chapter": "3", "verse_nums": "16"}
    
    # Default return value for any search
    # Note: app.py calls bible_db.similarity_search_with_relevance_scores(query, 10)
    # If using the same mock instance for both DBs, sidebar: app.py calls setup_db twice.
    # verify if bible_db and commentary_db are same object.
    # In conftest, we mocked the class Chroma. 
    # If app.py did: db1 = Chroma(); db2 = Chroma(). 
    # Unless side_effect is set, db1 and db2 are likely the same MagicMock object if created from same MagicMock class return_value.
    # Let's assume they might be shared, but we can set side_effect on the method if needed.
    
    # However, to be robust, let's just make the method return a mix or check arguments.
    # But wait, app.py calls them differently.
    # Bible: similarity_search_with_relevance_scores(query, 10)
    # Commentary: similarity_search_with_relevance_scores(query, k=1, filter=...)
    
    # Let's just return a list containing our bible docs. 
    # The commentary loop in app.py iterates CHURCH_FATHERS and calls explicitly.
    # We can perform a simpler check: just ensure response contains expected data.
    
    bible_db.similarity_search_with_relevance_scores.return_value = [(doc1, 0.9), (doc2, 0.9)]
    commentary_db.similarity_search_with_relevance_scores.return_value = [] # Return empty for commentary to keep it simple

    # Make request
    response = client.post('/search', json={'query': 'creation'})
    assert response.status_code == 200
    assert response.mimetype == 'text/event-stream'
    
    # Read the stream
    data = response.data.decode('utf-8')
    
    # Check for "event: results"
    assert "event: results" in data
    
    # Extract the JSON data from the results event
    # typical SSE format: "event: results\ndata: {...}\n\n"
    lines = data.split('\n')
    json_data = None
    for i, line in enumerate(lines):
        if line.startswith("event: results"):
            # The next line should be data: ...
            if i + 1 < len(lines) and lines[i+1].startswith("data: "):
                json_str = lines[i+1][6:] # strip "data: "
                json_data = json.loads(json_str)
                break
    
    assert json_data is not None
    assert "bible_results" in json_data
    assert len(json_data["bible_results"]) == 2
    assert "Genesis" in json_data["bible_results"][0]

def test_search_filtering_ot_only(client, mock_dependencies):
    """Test that Old Testament filter works"""
    bible_db = mock_dependencies['bible_db']
    
    doc_ot = MagicMock()
    doc_ot.metadata = {"book": "GEN", "verse_nums": "1"}
    
    doc_nt = MagicMock()
    doc_nt.metadata = {"book": "MAT", "verse_nums": "1"}
    
    # Mock return both
    bible_db.similarity_search_with_relevance_scores.return_value = [(doc_ot, 0.9), (doc_nt, 0.9)]
    
    # Request with newTestament=False
    response = client.post('/search', json={
        'query': 'test',
        'settings': {'oldTestament': True, 'newTestament': False, 'commentary': False, 'insights': False}
    })
    
    data = response.data.decode('utf-8')
    # Parse results similar to above
    # Or just simple string check
    assert "Genesis" in data
    assert "Matthew" not in data

def test_search_error_handling(client, mock_dependencies):
    """Test that DB errors are handled gracefully"""
    bible_db = mock_dependencies['bible_db']
    # Force an exception
    bible_db.similarity_search_with_relevance_scores.side_effect = Exception("DB Down")
    
    response = client.post('/search', json={'query': 'crash'})
    
    # Application catches error and prints it, but should proceed (likely returning empty list)
    assert response.status_code == 200
    assert "event: results" in response.data.decode('utf-8')
    # Should contain empty result lists
