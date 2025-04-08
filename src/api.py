import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_litellm.chat_models import ChatLiteLLM
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from src.prompts import language_learner_prompt

app = FastAPI()
memory = MemorySaver()  # Use the same checkpointer so that state persists across turns

user_configs = {}

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit's default port
    "http://127.0.0.1",
    "http://127.0.0.1:8501",
    "*",  
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup

@app.post("/config")
async def config_set(learning_language: str, native_language: str, level: str, model_provider: str, model_name: str, api_key:str):
    # Generate a unique user identifier and store config for later use
    user_id = str(uuid.uuid4())
    user_configs[user_id] = {
        "learning_language": learning_language,
        "native_language": native_language,
        "level": level,
        "model_name":f'{model_provider}/{model_name}',
        "api_key": api_key
    }
    try:
        get_chat_app(user_id)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Language Learning API"}


@app.post('/chat/{user_id}')
async def chat_endpoint(user_id: str, body: Dict):
    message = body['message']
    # Check if user_id exists in user_configs
    if user_id not in user_configs:
        raise HTTPException(status_code=404, detail="User ID not found")

    # Get user config
    user_config = user_configs[user_id]
    app = user_config['app']    
    user_config['messages'].append(HumanMessage(content=message))

    try: 
        output = await app.ainvoke({'messages':user_config['messages']})
        user_config['messages'].append(AIMessage(content=output['messages'][-1].content))
        return {"response": output['messages'][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

def get_chat_app(user_id:str):
    
    try:
        
        conf = user_configs[user_id]
        # Define a new graph
        workflow = StateGraph(state_schema=MessagesState)
        model = ChatLiteLLM(model=conf['model_name'], api_key=conf['api_key'], max_retries=3)

        # Define the function that calls the model
        def call_model(state: MessagesState):
            response = model.invoke(state["messages"])
            return {"messages": response}

        print('add node')
        # Define the (single) node in the graph
        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)

        # Add memory
        # memory = MemorySaver()
        app = workflow.compile()
        user_configs[user_id]['app']=app
        user_configs[user_id]['messages']=[SystemMessage(content=language_learner_prompt.format(
            learning_language=conf['learning_language'],
            native_language=conf['native_language'],
            level=conf['level']
        ))]
        return app
    except Exception as e:
        raise e