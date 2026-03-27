
# AI Learning Journey

This repository documents my journey of learning AI, including notes, demos, and small projects.

## Learning Roadmap
- LLM
- RAG
- Agent
- AI Applications

## Projects
1. **AI Chatbot API** - FastAPI-based chat API with multi-turn conversation support
2. RAG Knowledge Base
3. AI Code Assistant
4. Research Agent

## Tech Stack
- Python
- FastAPI
- OpenAI API (compatible with LM Studio)
- Redis (for session storage)
- tiktoken (for token counting)

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- (Optional) Redis server for production

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` file based on `.env.example`

### Running the Chat API
```bash
cd /Users/lijiao/Documents/AI/ai-journey && python -m uvicorn main:app --reload --app-dir demos/chatAPI
```

### API Endpoints
- `GET /` - Root endpoint with API information
- `GET /models` - Get all available models
- `GET /models/grouped` - Get models grouped by type
- `GET /models/{model_id}` - Get model details
- `POST /chat` - Chat interface with multi-turn support
- `POST /chat/clear` - Clear conversation history
- `POST /chat/history` - Get conversation history

## Project Structure
- `demos/` - Demo applications
  - `chatAPI/` - Chat API service
    - `main.py` - FastAPI application
    - `token_utils.py` - Token counting utilities
- `docs/` - Documentation
- `notes/` - Learning notes
- `plans/` - Learning plans

## License
MIT