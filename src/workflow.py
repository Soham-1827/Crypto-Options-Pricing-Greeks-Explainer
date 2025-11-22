from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from .agents import volatility_agent, pricer_agent, teacher_agent

# Define State
class AgentState(TypedDict):
    coin_id: str
    target_date_days: int
    strike_price: float
    option_type: str
    
    # Intermediate state
    parameters: dict
    current_price: float
    results: dict
    explanation: str

# Define Workflow
def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("volatility_agent", volatility_agent)
    workflow.add_node("pricer_agent", pricer_agent)
    workflow.add_node("teacher_agent", teacher_agent)
    
    # Set entry point
    workflow.set_entry_point("volatility_agent")
    
    # Add edges
    workflow.add_edge("volatility_agent", "pricer_agent")
    workflow.add_edge("pricer_agent", "teacher_agent")
    workflow.add_edge("teacher_agent", END)
    
    # Compile
    app = workflow.compile()
    return app
