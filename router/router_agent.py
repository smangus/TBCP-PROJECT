# router/router_agent.py

import json
from typing import Dict, List, Any

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langgraph.graph import StateGraph, END

# Import molecular agent (TxGemma-based) instead of separate chem and bio agents
from agents.molecular_agent.txgemma_agent import molecular_agent_executor

# Import synthesis agent
from synthesis.synthesis_agent import synthesis_agent

# Set up other domain agents as they become available
# Placeholder for market_agent
try:
    from agents.market_agent import market_agent_executor
except ImportError:
    market_agent_executor = None

# Placeholder for investor_agent
try:
    from agents.investor_agent import investor_agent_executor
except ImportError:
    investor_agent_executor = None

# Placeholder for ip_agent
try:
    from agents.ip_agent import ip_agent_executor
except ImportError:
    ip_agent_executor = None

# Placeholder for tech_stack_agent
try:
    from agents.tech_stack_agent import tech_stack_executor
except ImportError:
    tech_stack_executor = None

def route_query(state):
    """
    Examine the user query and determine which specialist agents should handle it.
    Returns a list of relevant agent names.
    """
    query = state["query"]
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create a prompt template for routing
    prompt = ChatPromptTemplate.from_template("""
        You are an intelligent routing system for the TechBio C-Suite CoPilot.
        Your job is to determine which domain specialists should handle the following query.
        
        The available specialists are:
        - molecular_agent: For chemistry, biology, and biochemistry questions involving molecular structures, 
          mechanisms, reactions, drug formulations, genomics, proteomics, and bioprocesses
        - investor_agent: For investment-related questions, funding, venture capital, financial projections
        - market_agent: For market analysis, competitive landscape, industry trends
        - ip_agent: For intellectual property questions, patents, licensing
        - tech_stack_agent: For questions about technology infrastructure, software platforms, data management
        
        Query: {query}
        
        Analyze the query and identify ALL relevant agents that could contribute to answering it.
        Return a JSON array of agent names. For example: ["molecular_agent", "market_agent"]
        
        The query may require expertise from multiple domains, so include all relevant agents.
    """)
    
    # Create a chain to get the agent names
    chain = prompt | llm | StrOutputParser()
    agent_names_json = chain.invoke({"query": query})
    
    # Parse the JSON response
    try:
        # Clean up the response if needed
        cleaned_json = agent_names_json.strip()
        if not cleaned_json.startswith('['):
            # Handle case where model might return something that's not JSON
            if '["' in cleaned_json and '"]' in cleaned_json:
                start = cleaned_json.find('[')
                end = cleaned_json.rfind(']') + 1
                cleaned_json = cleaned_json[start:end]
            else:
                # Fall back to a simple agent name
                cleaned_json = f'["{cleaned_json}"]'
                
        selected_agents = json.loads(cleaned_json)
        
        # Ensure we have a list of strings
        if isinstance(selected_agents, list):
            selected_agents = [agent.strip().lower() for agent in selected_agents]
        else:
            selected_agents = [str(selected_agents).strip().lower()]
            
    except Exception as e:
        # If JSON parsing fails, extract agent names using simple string matching
        potential_agents = ["molecular_agent", "investor_agent", 
                           "market_agent", "ip_agent", "tech_stack_agent"]
        selected_agents = []
        
        for agent in potential_agents:
            if agent.lower() in agent_names_json.lower():
                selected_agents.append(agent)
        
        # If still no agents found, default to a primary agent based on keywords
        if not selected_agents:
            selected_agents = ["molecular_agent"]  # Default fallback
    
    # Add the selected agents to the state
    state["selected_agents"] = selected_agents
    return state

# Function to delegate the query to appropriate agents
def delegate_to_agents(state):
    selected_agents = state["selected_agents"]
    query = state["query"]
    
    # Map agent names to the actual agent executors
    agent_map = {
        "molecular_agent": molecular_agent_executor,
    }
    
    # Add other agents to the map if they are available
    if market_agent_executor:
        agent_map["market_agent"] = market_agent_executor
    if investor_agent_executor:
        agent_map["investor_agent"] = investor_agent_executor
    if ip_agent_executor:
        agent_map["ip_agent"] = ip_agent_executor
    if tech_stack_executor:
        agent_map["tech_stack_agent"] = tech_stack_executor
    
    # Initialize responses dictionary to store results from each agent
    agent_responses = {}
    
    # Call each selected agent and store their responses
    for agent_name in selected_agents:
        if agent_name in agent_map and agent_map[agent_name] is not None:
            try:
                # Check if this is a molecular query that might need additional context
                if agent_name == "molecular_agent":
                    # Extract any relevant context from other agents' responses if they've already run
                    context = {
                        "previous_responses": {
                            a: agent_responses[a] for a in agent_responses
                            if a != "molecular_agent"
                        }
                    }
                    # Invoke the molecular agent with both query and context
                    result = agent_map[agent_name].invoke({
                        "input": query,
                        "context": context
                    })
                else:
                    # Regular invocation for other agents
                    result = agent_map[agent_name].invoke({"input": query})
                
                # Extract the response from the result
                if isinstance(result, dict) and "response" in result:
                    agent_responses[agent_name] = result["response"]
                else:
                    agent_responses[agent_name] = result
            except Exception as e:
                agent_responses[agent_name] = f"Error from {agent_name}: {str(e)}"
        else:
            # If we don't have the agent implemented yet, use a fallback
            agent_responses[agent_name] = f"I'm still learning about {agent_name} topics. This feature will be available soon."
    
    # Store all agent responses in the state
    state["agent_responses"] = agent_responses
    
    return state

# Function to synthesize responses from multiple agents
def synthesize_responses(state):
    # Use the dedicated synthesis agent
    return synthesis_agent(state)

# Create the workflow graph
def create_router_workflow():
    # Initialize the graph
    workflow = StateGraph(name="TechBio-CoPilot")
    
    # Add the nodes
    workflow.add_node("route", route_query)
    workflow.add_node("delegate", delegate_to_agents)
    workflow.add_node("synthesize", synthesize_responses)
    
    # Define the edges
    workflow.add_edge("route", "delegate")
    workflow.add_edge("delegate", "synthesize")
    workflow.add_edge("synthesize", END)
    
    # Set the entry point
    workflow.set_entry_point("route")
    
    # Compile the workflow
    return workflow.compile()

# Create a runnable application that processes user queries
def create_copilot_app():
    router_workflow = create_router_workflow()
    
    def process_query(query):
        # Initialize the state with the user query
        initial_state = {"query": query}
        
        # Execute the workflow
        result = router_workflow.invoke(initial_state)
        
        # Return the response
        return result
    
    return process_query

# Example usage
if __name__ == "__main__":
    copilot = create_copilot_app()
    
    # Test with a molecular query
    molecular_query = "What is the mechanism of action of paclitaxel and how does it bind to tubulin?"
    print("Molecular Query Response:", copilot(molecular_query))
    
    # Test with a market query
    market_query = "What is the current market size for CRISPR-based therapeutics?"
    print("Market Query Response:", copilot(market_query))