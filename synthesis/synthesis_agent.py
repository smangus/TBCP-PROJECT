from typing import Dict, List, Any, Optional
import os
import json
import time
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SynthesisAgent:
    """
    The Synthesis Agent combines responses from multiple domain agents
    into a cohesive, unified response for the user.
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        """Initialize the synthesis agent with an LLM."""
        try:
            # Try to use OpenAI directly
            self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        except Exception as e:
            # Fallback to a smaller model if needed
            print(f"Warning: Could not load {model_name}: {str(e)}. Falling back to gpt-3.5-turbo.")
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)
        
        # Create a prompt template for synthesis
        self.prompt = ChatPromptTemplate.from_template("""
            You are the Synthesis Agent for the TechBio C-Suite CoPilot, responsible for creating cohesive, 
            comprehensive responses that combine insights from multiple domain specialists.
            
            The original query was:
            ---
            {query}
            ---
            
            The following domain specialists have provided responses:
            {agent_responses}
            
            Your task is to synthesize these responses into a single, coherent answer that:
            1. Integrates all relevant information from each agent
            2. Resolves any contradictions between agent responses
            3. Presents a unified perspective that addresses all aspects of the original query
            4. Organizes information in a logical flow
            5. Highlights key insights and actionable recommendations for a biotech executive
            
            IMPORTANT NOTES:
            - You should pay special attention to molecular insights from the molecular_agent, which uses Google's TxGemma, an expert in molecular reasoning
            - When discussing molecular structures, mechanisms, or biochemical processes, prioritize the TxGemma insights
            - For market data or investment insights, ensure you preserve specific numbers, percentages, and facts
            - When relevant, include actionable next steps or recommendations
            - Your audience is C-suite biotech executives, so maintain a professional, executive-level tone
            
            Write a comprehensive response that sounds like a single expert voice rather than
            a collection of different opinions. Present the most relevant content first, and
            ensure that each domain's contribution is properly represented.
        """)
        
        # Special prompt for single-agent responses
        self.single_agent_prompt = ChatPromptTemplate.from_template("""
            You are the Synthesis Agent for the TechBio C-Suite CoPilot.
            
            The original query was:
            ---
            {query}
            ---
            
            Only one domain specialist has provided a response:
            {agent_responses}
            
            Your task is to refine this response to ensure it:
            1. Fully addresses the original query
            2. Is presented in a clear, well-structured format
            3. Provides actionable insights for a biotech executive
            4. Maintains a professional, executive-level tone
            
            If the response is from the molecular_agent (using Google's TxGemma), ensure you preserve the molecular insights while making them accessible to C-suite executives.
            
            Refine the response while preserving all factual information and technical accuracy.
        """)
    
    def synthesize(self, query: str, agent_responses: Dict[str, str]) -> str:
        """
        Synthesize responses from multiple agents into a unified response.
        
        Args:
            query: The original user query
            agent_responses: Dictionary mapping agent names to their responses
            
        Returns:
            A cohesive synthesized response
        """
        # Check if we only have one agent response
        if len(agent_responses) == 1:
            return self._synthesize_single_agent(query, agent_responses)
        
        # Format agent responses for the prompt
        agent_responses_text = self._format_agent_responses(agent_responses)
        
        # Create and run the synthesis chain
        chain = self.prompt | self.llm | StrOutputParser()
        
        try:
            synthesized_response = chain.invoke({
                "query": query,
                "agent_responses": agent_responses_text
            })
            
            return synthesized_response
        
        except Exception as e:
            error_msg = f"Error during synthesis: {str(e)}"
            print(error_msg)
            # Return a fallback response
            return self._create_fallback_response(query, agent_responses, error_msg)
    
    def _synthesize_single_agent(self, query: str, agent_responses: Dict[str, str]) -> str:
        """Handle the case where we only have one agent response."""
        agent_name = next(iter(agent_responses))
        response = agent_responses[agent_name]
        
        # Format the single agent response
        agent_responses_text = f"--- {agent_name} Response ---\n{response}\n"
        
        # Create and run the single agent synthesis chain
        chain = self.single_agent_prompt | self.llm | StrOutputParser()
        
        try:
            refined_response = chain.invoke({
                "query": query,
                "agent_responses": agent_responses_text
            })
            
            return refined_response
        
        except Exception as e:
            # If refinement fails, return the original response
            print(f"Error refining single agent response: {str(e)}")
            return response
    
    def _format_agent_responses(self, agent_responses: Dict[str, str]) -> str:
        """Format agent responses for inclusion in the prompt."""
        formatted_text = ""
        
        # Determine display order - put molecular_agent first if present
        ordered_agents = list(agent_responses.keys())
        if "molecular_agent" in ordered_agents:
            ordered_agents.remove("molecular_agent")
            ordered_agents.insert(0, "molecular_agent")
        
        # Format each agent's response
        for agent_name in ordered_agents:
            response = agent_responses[agent_name]
            
            # Ensure response is a string
            if not isinstance(response, str):
                if isinstance(response, dict) and "text" in response:
                    response = response["text"]
                else:
                    response = str(response)
            
            # Add to formatted text
            formatted_text += f"\n--- {agent_name} Response ---\n{response}\n"
        
        return formatted_text
    
    def _create_fallback_response(self, query: str, agent_responses: Dict[str, str], error_msg: str) -> str:
        """Create a fallback response when synthesis fails."""
        fallback = f"I've analyzed responses from {len(agent_responses)} experts regarding your query: '{query}'. "
        fallback += "Here are their key insights:\n\n"
        
        for agent_name, response in agent_responses.items():
            # Get a short snippet from the response
            snippet = response[:300] + "..." if len(response) > 300 else response
            fallback += f"• From {agent_name.replace('_agent', ' expert')}: {snippet}\n\n"
        
        fallback += "I apologize that I couldn't provide a more integrated analysis at this time."
        return fallback
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make the agent callable for use with LangGraph.
        
        Args:
            state: The state object containing query and agent_responses
            
        Returns:
            Updated state with synthesized response
        """
        query = state["query"]
        agent_responses = state["agent_responses"]
        
        synthesized_response = self.synthesize(query, agent_responses)
        
        # Store the synthesized response in the state
        state["response"] = synthesized_response
        
        return state


# Create an instance of the synthesis agent
synthesis_agent = SynthesisAgent()

# For standalone testing
if __name__ == "__main__":
    # Test with sample responses
    test_query = "How does paclitaxel's mechanism of action affect its market potential?"
    
    test_responses = {
        "molecular_agent": "Paclitaxel acts by stabilizing microtubules, preventing their disassembly during cell division. It specifically binds to the β-tubulin subunit, enhancing polymerization and making the microtubules resistant to depolymerization. This mechanism leads to mitotic arrest and ultimately apoptosis in rapidly dividing cells, making it effective against various cancer types. Its binding site includes interactions with amino acid residues 217–233 in β-tubulin.",
        
        "market_agent": "The global paclitaxel market was valued at approximately $4.3 billion in 2022 and is projected to grow at a CAGR of 7.6% through 2030. Growth drivers include increasing cancer incidence and expansion of indications. Key competitors include Bristol-Myers Squibb, Celgene, and Hospira. Patent expirations have led to generics entry, though novel formulations and delivery systems provide opportunities for premium pricing."
    }
    
    # Test the synthesis
    result = synthesis_agent.synthesize(test_query, test_responses)
    print("Synthesized Response:")
    print(result)