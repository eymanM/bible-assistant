# Bible Assistant API

The **Bible Assistant API** is a powerful semantic search engine and AI-powered insights generator for biblical texts and patristic commentaries. Built with **Flask**, **LangChain**, and **ChromaDB**, it enables users to explore scripture through natural language queries, delivering context-aware search results and theological insights.

## 🚀 Key Features

*   **Semantic Search**: Find relevant Bible verses and Church Father commentaries using natural language (e.g., "What does the Bible say about anxiety?" vs. keyword search).
*   **AI Insights**: Generates theological summaries, connections, and practical applications based on retrieved passages using LLMs (OpenAI/Anthropic).
*   **Real-time Streaming**: Utilizes Server-Sent Events (SSE) to stream search results and AI tokens for a responsive user experience.
*   **Vector Database**: Uses **ChromaDB** with `hkunlp/instructor-large` embeddings for high-accuracy text retrieval.
*   **Comprehensive Filtering**: Filter results by Old Testament, New Testament, or Church Father commentaries.

## 🛠️ Architecture

*   **Backend**: Flask (Python)
*   **AI/Orchestration**: LangChain, OpenAI API / Anthropic API
*   **Database**: ChromaDB (Vector Store)
*   **Embeddings**: HuggingFace Instructor Embeddings
*   **Documentation**: Swagger UI (`flasgger`)

## 📦 Getting Started

### Prerequisites

*   Python 3.12
*   OpenAI API Key
*   Git

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/eymanM/bible-assistant.git
    cd bible-assistant
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory (see `.env.example` for a template) and add your keys:
    ```env
    OPENAI_API_KEY=your_openai_key
    XAI_API_KEY=your_xai_key
    DATABASE_URL=postgresql://user:password@localhost:5432/bible_assistant
    API_KEY=your_secret_api_key
    ENV=dev
    PORT=5000
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```
    The API will start at `http://127.0.0.1:5000`.

### 🐳 Docker Usage

Build and run the application using Docker:

```bash
# Build the image
docker build -t bible-assistant .

# Run the container
docker run -p 5000:5000 --env-file .env bible-assistant
```

## 📖 API Documentation

Interactive API documentation is available via Swagger UI.

1.  Start the application.
2.  Navigate to `http://127.0.0.1:5000/apidocs`.

### Key Endpoints

*   **`POST /search`**: Main search endpoint. Accepts a JSON body with `query` and `settings`. Returns an event stream.
*   **`GET /health`**: Health check endpoint. Returns `200 OK` if the service is running.

## 🧪 Testing

This project uses `pytest` for unit testing. The tests mock external dependencies (OpenAI, ChromaDB) to ensure speed and reliability.

```bash
# Run tests
python -m pytest tests/
```

## 🌐 Frontend Integration

This API is designed to work with a modern frontend application. 
The official frontend implementation is built with **Next.js** and can be found here:

**[Bible Assistant Frontend](https://github.com/eymanM/bible-assistant-ui)**

Ensure the frontend is configured to point to `http://127.0.0.1:5000` (or your deployed URL).

## 📄 License

[MIT](LICENSE)

## ✨ About the Author

[![](https://img.shields.io/badge/GitHub-eymanM-181717?style=for-the-badge&logo=github)](https://github.com/eymanM)
