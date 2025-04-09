# Language Helper - System Architecture Documentation

## Overview
Language Helper is an AI-powered language learning application that provides interactive conversations tailored to the user's proficiency level. The system uses a modern microservices architecture with a FastAPI backend and Streamlit frontend.



## Components Description

### 1. Frontend Layer (Streamlit)
- **Purpose**: Provides user interface and interaction
- **Key Features**:
  - Configuration input for language settings
  - Chat interface
  - Session management
- **Location**: `src/app.py`

### 2. Backend Layer (FastAPI)
- **Purpose**: Handles business logic and LLM integration
- **Components**:
  - **API Server**: Manages HTTP endpoints and request handling
  - **State Management**: Maintains conversation history and user sessions
  - **LangGraph Integration**: Orchestrates the conversation flow
- **Location**: `src/api.py`

### 3. Core Components
- **Language Learning Prompt**: Template system for AI responses (`src/prompts.py`)
- **Configuration Management**: Environment and user settings (`src/utils.py`)
- **State Management**: Uses LangGraph for maintaining conversation state

## Data Flow

1. **Configuration Flow**:
   ```
   User Input → Frontend → Backend → User Config Store
   ```

2. **Conversation Flow**:
   ```
   User Message → Frontend → Backend → LLM API → State Store → Response
   ```

## Technical Specifications

### Technologies Used
- Frontend: Streamlit (Python)
- Backend: FastAPI (Python)
- State Management: LangGraph
- LLM Integration: LangChain & LiteLLM
- Container: Docker

### API Endpoints
- `POST /config`: Sets up user configuration and returns user ID
- `POST /chat/{user_id}`: Handles chat messages and responses
- `GET /`: Health check endpoint

### Environment Configuration
Required environment variables:
- `MODEL_API_KEY`: API key for the language model
- `MODEL_NAME`: Model identifier in format `provider/model-name`

## Deployment

The application can be deployed using either Docker or a traditional virtual environment:

### Docker Deployment
```bash
docker build -t myapp .
docker run -p 8000:8000 -p 8501:8501 myapp
```

### Manual Deployment
```bash
python -m venv .venv
source .venv/bin/activate
pip install .
# Run backend and frontend in separate terminals
uvicorn src.api:app --port 8000 --host 0.0.0.0
streamlit run src/app.py
```

## Security Considerations
- API keys are handled securely through environment variables
- CORS is configured for specific origins
- User sessions are managed with UUID-based identification

## Future Improvements
1. Add database persistence for user conversations
2. Implement user authentication
3. Add support for multiple language models
4. Enhance error handling and recovery
5. Add monitoring and logging systems