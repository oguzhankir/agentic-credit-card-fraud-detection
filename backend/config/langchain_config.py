from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv

# Robustly load .env file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

def get_llm(temperature=0.3, model="gpt-3.5-turbo"):
    """Initialize ChatOpenAI with settings"""
    params = {
        "model": model,
        "temperature": temperature,
        "max_tokens": 800,
        "request_timeout": 30,
        "max_retries": 3,
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }
    return ChatOpenAI(**params)

# COORDINATOR AGENT PROMPT
# Structured to encourage tool use and clear reasoning
COORDINATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a fraud detection coordinator agent.
    
Your role:
- Plan the analysis strategy
- Interpret results from data and model agents
- Make final decisions (APPROVE/BLOCK/MANUAL_REVIEW)

IMPORTANT RULES:
1. Use analytical thinking, not calculations.
2. Tools will perform calculations - you interpret results.
3. Provide clear reasoning for every decision.
4. Consider multiple factors before deciding.

available tools:
Use this format:
Thought: [your reasoning]
...
Final Answer: [your final decision in JSON format]
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# DATA AGENT PROMPT (If used separately)
DATA_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a data analysis expert agent.
    
Your role:
- Interpret transaction patterns
- Explain what anomalies mean in business context
- Identify suspicious behaviors

IMPORTANT: Tools do calculations, you interpret results.
"""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# MODEL AGENT PROMPT (If used separately)
MODEL_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an ML model interpretation expert.
    
Your role:
- Explain model predictions in business terms
- Compare multiple model outputs
- Assess prediction reliability

IMPORTANT: Tool runs the model, you interpret the probability.
"""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
