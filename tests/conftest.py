import os
import sys
from unittest.mock import MagicMock

import pytest

# Disable API key auth in tests unless a test explicitly sets it.
os.environ.pop("API_KEY", None)

# -- MOCK DEPENDENCIES BEFORE APP IMPORT --
# app.py initializes global resources on import. These mocks keep tests isolated
# from network/model/vectorstore side effects.

mock_langchain_community = MagicMock()
sys.modules["langchain_community"] = mock_langchain_community
sys.modules["langchain_community.vectorstores"] = mock_langchain_community.vectorstores
sys.modules["langchain_community.embeddings"] = mock_langchain_community.embeddings

mock_langchain_chroma = MagicMock()
sys.modules["langchain_chroma"] = mock_langchain_chroma

mock_langchain_openai = MagicMock()
sys.modules["langchain_openai"] = mock_langchain_openai

mock_langchain_google_genai = MagicMock()
sys.modules["langchain_google_genai"] = mock_langchain_google_genai


mock_flask_cors = MagicMock()
sys.modules["flask_cors"] = mock_flask_cors
sys.modules["flask_cors"].CORS = lambda *args, **kwargs: None

mock_flasgger = MagicMock()
sys.modules["flasgger"] = mock_flasgger
sys.modules["flasgger"].Swagger = lambda *args, **kwargs: None

# Set concrete classes used by utils.py imports.
mock_chroma_class = MagicMock()
mock_chroma_class.side_effect = lambda *args, **kwargs: MagicMock()
sys.modules["langchain_chroma"].Chroma = mock_chroma_class
sys.modules["langchain_community.vectorstores"].Chroma = mock_chroma_class

mock_embeddings_class = MagicMock()
sys.modules["langchain_community.embeddings"].HuggingFaceInstructEmbeddings = mock_embeddings_class

mock_chat_openai_class = MagicMock()
sys.modules["langchain_openai"].ChatOpenAI = mock_chat_openai_class

mock_chat_google_class = MagicMock()
sys.modules["langchain_google_genai"].ChatGoogleGenerativeAI = mock_chat_google_class

# Now we can safely import the app module.
import app as app_module
from app import app


@pytest.fixture
def client():
    # app.py loads .env on import; clear API_KEY for tests unless explicitly needed.
    os.environ.pop("API_KEY", None)
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_dependencies():
    return {
        "bible_db": app_module.bible_db,
        "commentary_db": app_module.commentary_db,
        "llm_insights": app_module.llm_insights,
        "llm_translate": app_module.llm_translate,
    }
