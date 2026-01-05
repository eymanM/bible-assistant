import unittest
from unittest.mock import MagicMock, patch
from flask import json
import app

class TestTranslation(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        self.app.testing = True

    @patch('app.llm')
    def test_translation_en(self, mock_llm):
        # Verify NO translation for 'en'
        payload = {'query': 'Love', 'settings': {'language': 'en'}}
        
        # We Mock execute_search or just check calls. 
        # Since logic is inside 'search', we can verify mock_llm.invoke is NOT called with translation prompt.
        # But wait, 'llm' is global in app.py. patching app.llm should work if we import app.
        
        # We need to ensure we don't actually hit the DB if possible, or just ignore errors.
        # The logic is: 
        # 1. Translate
        # 2. Search DB (Thread pool)
        
        # If we just want to verify translation logic:
        # We can patch 'app.bible_db.similarity_search_with_relevance_scores' to avoid DB errors.
        
        with patch('app.bible_db') as mock_db:
             mock_db.similarity_search_with_relevance_scores.return_value = []
             with patch('app.perform_commentary_search') as mock_comm:
                 mock_comm.return_value = []
                 
                 self.app.post('/search', data=json.dumps(payload), content_type='application/json')
                 
                 # Verify LLM NOT invoked for translation
                 # LLM is used for summary though if 'insights' is True.
                 # Let's clean up: invoke is used for translation. stream is used for summary.
                 # So we check if invoke was called.
                 mock_llm.invoke.assert_not_called()

    @patch('app.llm')
    def test_translation_pl(self, mock_llm):
        # Verify translation for 'pl'
        payload = {'query': 'Miłość', 'settings': {'language': 'pl'}}
        
        # Mock translation response
        mock_response = MagicMock()
        mock_response.content = "Love"
        mock_llm.invoke.return_value = mock_response
        
        with patch('app.bible_db') as mock_db:
             mock_db.similarity_search_with_relevance_scores.return_value = []
             with patch('app.perform_commentary_search') as mock_comm:
                 mock_comm.return_value = []
                 
                 self.app.post('/search', data=json.dumps(payload), content_type='application/json')
                 
                 # Verify LLM invoke CALLED with proper prompt
                 self.assertTrue(mock_llm.invoke.called)
                 args, _ = mock_llm.invoke.call_args
                 self.assertIn("Translate the following Polish search query", args[0])
                 self.assertIn("Miłość", args[0])

if __name__ == '__main__':
    unittest.main()
