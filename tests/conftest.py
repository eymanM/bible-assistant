import sys
import pytest
from unittest.mock import MagicMock

# -- MOCK DEPENDENCIES BEFORE APP IMPORT --
# We must mock these modules because app.py initializes global variables 
# (llm, bible_db, commentary_db) at import time using these libraries.
# By mocking them in sys.modules, we prevent real connections/loading.

mock_langchain_community = MagicMock()
sys.modules["langchain_community"] = mock_langchain_community
sys.modules["langchain_community.vectorstores"] = mock_langchain_community.vectorstores
sys.modules["langchain_community.embeddings"] = mock_langchain_community.embeddings

mock_langchain_openai = MagicMock()
sys.modules["langchain_openai"] = mock_langchain_openai

# Set specific classes on the mocks so "from ... import Chroma" works
# and "Chroma(...)" returns a mock instance we can control.
mock_chroma_class = MagicMock()
mock_chroma_class.side_effect = lambda *args, **kwargs: MagicMock()
sys.modules["langchain_community.vectorstores"].Chroma = mock_chroma_class

mock_embeddings_class = MagicMock()
sys.modules["langchain_community.embeddings"].HuggingFaceInstructEmbeddings = mock_embeddings_class

mock_chat_openai_class = MagicMock()
sys.modules["langchain_openai"].ChatOpenAI = mock_chat_openai_class


# Now we can safely import the app
# Import as a module to access global variables (bible_db, etc.)
import app as app_module
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_dependencies():
    """
    Returns the mock instances used by the app.
    We access them from the module level.
    """
    return {
        "bible_db": app_module.bible_db,         
        "commentary_db": app_module.commentary_db, 
        "llm": app_module.llm
    }
