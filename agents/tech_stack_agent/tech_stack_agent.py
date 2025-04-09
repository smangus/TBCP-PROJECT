# agents/tech_stack_agent/tech_stack_agent.py

import os
import json
from typing import Dict, Any, List, Optional

# Import data providers
from agents.tech_stack_agent.data_providers.cloud_services import CloudServicesProvider
from agents.tech_stack_agent.data_providers.lab_informatics import LabInformaticsProvider
from agents.tech_stack_agent.data_providers.research_tools import ResearchToolsProvider
from agents.tech_stack_agent.data_providers.data_management import DataManagementProvider

# Import utilities
from agents.tech_stack_agent.utils.cache_manager import CacheManager
from agents.tech_stack_agent.utils.response_formatter import format_tech_analysis

class TechStackAgent:
    """
    Agent for providing technology infrastructure recommendations for biotech executives.
    Specializes in cloud services, laboratory informatics, bioinformatics, and R&D tools.
    """
    
    def __init__(self):
        """Initialize the tech stack agent with its component services."""
        # Set up data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize cache manager
        self.cache_manager = CacheManager(os.path.join(self.data_dir, "cache"))
        
        # Initialize data providers
        self.cloud_services = CloudServicesProvider(self.cache_manager)
        self.lab_informatics = LabInformaticsProvider(self.cache_manager)
        self.research_tools = ResearchToolsProvider(self.cache_manager)
        self.data_management = DataManagementProvider(self.cache_manager)
        
        # Load tech categories database
        self.tech_categories = self._load_tech_categories()
        
        # Load use cases database
        self.use_cases = self._load_use_cases()
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a tech stack query using domain knowledge.
        
        Args:
            inputs: Dictionary containing input query and context
                - input (str): The query to process
                - context (Optional[Dict]): Additional context like
                  insights from other agents
                
        Returns:
            Dict containing the tech stack response
        """
        query = inputs.get("input", "")
        context = inputs.get("context", {})
        
        # Ensure data is up to date
        self._refresh_data_if_needed()
        
        # Analyze the query to determine the tech analysis focus
        tech_focus = self._determine_tech_focus(query, context)
        
        # Generate the appropriate tech analysis
        if tech_focus["type"] == "cloud_infrastructure":
            response = self._analyze_cloud_infrastructure(
                tech_focus["research_stage"],
                tech_focus.get("data_volume", "medium"),
                tech_focus.get("compliance_needs", [])
            )
        elif tech_focus["type"] == "laboratory_informatics":
            response = self._analyze_laboratory_informatics(
                tech_focus["research_areas"],
                tech_focus.get("lab_size", "medium"),
                tech_focus.get("integration_needs", [])
            )
        elif tech_focus["type"] == "research_tools":
            response = self._recommend_research_tools(
                tech_focus["research_areas"],
                tech_focus.get("specific_techniques", []),
                tech_focus.get("budget_level", "medium")
            )
        elif tech_focus["type"] == "data_management":
            response = self._analyze_data_management(
                tech_focus["data_types"],
                tech_focus.get("collaboration_needs", "internal"),
                tech_focus.get("compliance_needs", [])
            )
        else:
            # Default to a general tech overview
            response = self._provide_general_tech_overview()
        
        return {
            "response": response,
            "tech_focus": tech_focus
        }
    
    def _determine_tech_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the query to determine the tech analysis focus.
        
        Args:
            query (str): The user query
            context (Dict[str, Any]): Additional context from other agents
            
        Returns:
            Dict with tech focus information
        """
        query_lower = query.lower()
        
        # Check for cloud infrastructure requests
        cloud_keywords = ["cloud", "aws", "azure", "gcp", "infrastructure", "compute", "storage", "servers"]
        if any(keyword in query_lower for keyword in clou