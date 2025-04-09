# agents/market_agent/market_agent.py

from typing import Dict, Any, List, Optional
import os
import json
import datetime
import requests
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Import data providers (will create these next)
from agents.market_agent.data_providers.market_intelligence import MarketIntelligence
from agents.market_agent.data_providers.competitive_analysis import CompetitiveAnalysis
from agents.market_agent.data_providers.trend_analysis import TrendAnalysis
from agents.market_agent.data_providers.news_analyzer import NewsAnalyzer

# Import utilities
from agents.market_agent.utils.cache_manager import CacheManager
from agents.market_agent.utils.response_formatter import format_market_analysis

# Load environment variables
load_dotenv()

class MarketAgent:
    """
    Agent specialized in market intelligence for biotech executives.
    Provides competitive landscape analysis, market sizing, trend spotting,
    and strategic recommendations.
    """
    
    def __init__(self):
        """Initialize the market agent with its component services."""
        # Set up data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize cache manager
        self.cache_manager = CacheManager(os.path.join(self.data_dir, "cache"))
        
        # Initialize data providers
        self.market_intelligence = MarketIntelligence(self.cache_manager)
        self.competitive_analysis = CompetitiveAnalysis(self.cache_manager)
        self.trend_analysis = TrendAnalysis(self.cache_manager)
        self.news_analyzer = NewsAnalyzer(self.cache_manager)
        
        # Load therapeutic area database for domain-specific knowledge
        self.therapeutic_areas = self._load_therapeutic_areas()
        
        # Load competitor database
        self.competitor_database = self._load_competitor_database()
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a market analysis query using multiple data sources.
        
        Args:
            inputs: Dictionary containing input query and context
                - input (str): The query to process
                - context (Optional[Dict]): Additional context like
                  molecular insights from other agents
                
        Returns:
            Dict containing the market analysis response
        """
        query = inputs.get("input", "")
        context = inputs.get("context", {})
        
        # Ensure data is up to date
        self._refresh_market_data_if_needed()
        
        # Analyze the query to determine the market analysis focus
        market_focus = self._determine_market_focus(query, context)
        
        # Generate the appropriate market analysis
        if market_focus["type"] == "competitive_landscape":
            response = self._analyze_competitive_landscape(
                market_focus["therapeutic_area"],
                market_focus.get("companies", []),
                market_focus.get("technologies", [])
            )
        elif market_focus["type"] == "market_sizing":
            response = self._provide_market_sizing(
                market_focus["therapeutic_area"],
                market_focus.get("geography", "global"),
                market_focus.get("timeframe", "5-year")
            )
        elif market_focus["type"] == "trend_analysis":
            response = self._analyze_market_trends(
                market_focus.get("therapeutic_area"),
                market_focus.get("technology_focus")
            )
        elif market_focus["type"] == "strategic_recommendations":
            response = self._provide_strategic_recommendations(
                market_focus.get("therapeutic_area"),
                market_focus.get("company_focus"),
                market_focus.get("goal")
            )
        else:
            # Default to a general market overview
            response = self._provide_general_market_overview()
        
        return {
            "response": response,
            "market_focus": market_focus
        }
    
    def _determine_market_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the query to determine the market analysis focus.
        
        Args:
            query (str): The user query
            context (Dict[str, Any]): Additional context from other agents
            
        Returns:
            Dict with market focus information
        """
        query_lower = query.lower()
        
        # Check for competitive landscape requests
        competitive_keywords = ["competitors", "competitive", "landscape", "players", "companies in"]
        if any(keyword in query_lower for keyword in competitive_keywords):
            return self._extract_competitive_landscape_focus(query, context)
        
        # Check for market sizing requests
        sizing_keywords = ["market size", "market value", "market forecast", "how big is", "growth rate"]
        if any(keyword in query_lower for keyword in sizing_keywords):
            return self._extract_market_sizing_focus(query, context)
        
        # Check for trend analysis requests
        trend_keywords = ["trend", "emerging", "innovation", "future", "upcoming", "next generation"]
        if any(keyword in query_lower for keyword in trend_keywords):
            return self._extract_trend_analysis_focus(query, context)
        
        # Check for strategic recommendation requests
        strategy_keywords = ["strategy", "recommendation", "approach", "should we", "how to compete"]
        if any(keyword in query_lower for keyword in strategy_keywords):
            return self._extract_strategic_recommendation_focus(query, context)
        
        # Default to general market overview with detected therapeutic areas
        therapeutic_area = self._extract_therapeutic_area_from_query(query, context)
        return {
            "type": "general_overview",
            "therapeutic_area": therapeutic_area
        }
    
    def _extract_competitive_landscape_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitive landscape focus from query."""
        therapeutic_area = self._extract_therapeutic_area_from_query(query, context)
        
        # Extract mentioned companies
        companies = []
        for company_name in self.competitor_database.keys():
            if company_name.lower() in query.lower():
                companies.append(company_name)
        
        # Extract technologies of interest
        technologies = []
        tech_keywords = ["antibody", "gene therapy", "cell therapy", "small molecule", 
                         "CRISPR", "RNA", "protein degradation", "ADC", "vaccine"]
        for tech in tech_keywords:
            if tech.lower() in query.lower():
                technologies.append(tech)
        
        return {
            "type": "competitive_landscape",
            "therapeutic_area": therapeutic_area,
            "companies": companies,
            "technologies": technologies
        }
    
    def _extract_market_sizing_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market sizing focus from query."""
        therapeutic_area = self._extract_therapeutic_area_from_query(query, context)
        
        # Extract geography focus
        geography = "global"  # Default
        geography_keywords = {
            "us": ["united states", "us market", "us region", "north america"],
            "europe": ["european", "europe", "eu market"],
            "asia": ["asian", "asia", "asia pacific", "apac"],
            "global": ["worldwide", "global", "international"]
        }
        
        for geo, keywords in geography_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                geography = geo
                break
        
        # Extract timeframe
        timeframe = "5-year"  # Default
        if "10-year" in query.lower() or "ten year" in query.lower():
            timeframe = "10-year"
        elif "3-year" in query.lower() or "three year" in query.lower():
            timeframe = "3-year"
        
        return {
            "type": "market_sizing",
            "therapeutic_area": therapeutic_area,
            "geography": geography,
            "timeframe": timeframe
        }
    
    def _extract_trend_analysis_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract trend analysis focus from query."""
        therapeutic_area = self._extract_therapeutic_area_from_query(query, context)
        
        # Extract technology focus for trends
        technology_focus = None
        tech_areas = ["digital health", "ai drug discovery", "precision medicine", 
                     "gene editing", "cell therapy", "diagnostics", "drug delivery"]
        
        for tech in tech_areas:
            if tech.lower() in query.lower():
                technology_focus = tech
                break
        
        return {
            "type": "trend_analysis",
            "therapeutic_area": therapeutic_area,
            "technology_focus": technology_focus
        }
    
    def _extract_strategic_recommendation_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract strategic recommendation focus from query."""
        therapeutic_area = self._extract_therapeutic_area_from_query(query, context)
        
        # Extract company focus if mentioned
        company_focus = None
        for company_name in self.competitor_database.keys():
            if company_name.lower() in query.lower():
                company_focus = company_name
                break
        
        # Try to determine strategic goal
        goal = "market_entry"  # Default
        goal_keywords = {
            "market_entry": ["enter", "launch", "introduce", "new market"],
            "growth": ["grow", "expand", "increase market share", "scale"],
            "competitive_defense": ["defend", "against competitors", "protect position"],
            "innovation": ["innovate", "develop new", "next generation", "breakthrough"]
        }
        
        for g, keywords in goal_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                goal = g
                break
        
        return {
            "type": "strategic_recommendations",
            "therapeutic_area": therapeutic_area,
            "company_focus": company_focus,
            "goal": goal
        }
    
    def _extract_therapeutic_area_from_query(self, query: str, context: Dict[str, Any]) -> Optional[str]:
        """Extract therapeutic area from query and context."""
        # First check if a therapeutic area is directly mentioned in the query
        for area, data in self.therapeutic_areas.items():
            keywords = data.get("keywords", [])
            if any(keyword.lower() in query.lower() for keyword in keywords):
                return area
        
        # If not found in query, check context (e.g., from molecular agent)
        if context and "previous_responses" in context:
            for agent_response in context["previous_responses"].values():
                if isinstance(agent_response, str):
                    # For each therapeutic area, check if it or its keywords are mentioned
                    for area, data in self.therapeutic_areas.items():
                        if area.lower() in agent_response.lower():
                            return area
                        
                        # Check for keywords
                        keywords = data.get("keywords", [])
                        if any(keyword.lower() in agent_response.lower() for keyword in keywords):
                            return area
        
        # Default to None if no therapeutic area could be identified
        return None
    
    def _analyze_competitive_landscape(self, therapeutic_area: Optional[str], 
                                      companies: List[str], 
                                      technologies: List[str]) -> str:
        """Generate competitive landscape analysis."""
        # Get competitive landscape data
        landscape_data = self.competitive_analysis.get_landscape(
            therapeutic_area=therapeutic_area,
            companies=companies,
            technologies=technologies
        )
        
        # Get recent news about key competitors
        news_data = self.news_analyzer.get_competitor_news(
            therapeutic_area=therapeutic_area,
            companies=companies
        )
        
        # Get market share data if available
        market_share = self.market_intelligence.get_market_share(
            therapeutic_area=therapeutic_area,
            technologies=technologies
        )
        
        # Format the competitive landscape response
        return format_market_analysis(
            analysis_type="competitive_landscape",
            therapeutic_area=therapeutic_area,
            landscape_data=landscape_data,
            news_data=news_data,
            market_share=market_share,
            companies=companies,
            technologies=technologies
        )
    
    def _provide_market_sizing(self, therapeutic_area: Optional[str],
                              geography: str,
                              timeframe: str) -> str:
        """Generate market sizing and forecast analysis."""
        # Get market size data
        market_size = self.market_intelligence.get_market_size(
            therapeutic_area=therapeutic_area,
            geography=geography,
            timeframe=timeframe
        )
        
        # Get growth drivers and restraints
        growth_factors = self.market_intelligence.get_growth_factors(
            therapeutic_area=therapeutic_area,
            geography=geography
        )
        
        # Get regional breakdown if it's a global analysis
        regional_breakdown = None
        if geography == "global":
            regional_breakdown = self.market_intelligence.get_regional_breakdown(
                therapeutic_area=therapeutic_area
            )
        
        # Format the market sizing response
        return format_market_analysis(
            analysis_type="market_sizing",
            therapeutic_area=therapeutic_area,
            geography=geography,
            timeframe=timeframe,
            market_size=market_size,
            growth_factors=growth_factors,
            regional_breakdown=regional_breakdown
        )
    
    def _analyze_market_trends(self, therapeutic_area: Optional[str],
                              technology_focus: Optional[str]) -> str:
        """Generate analysis of market trends."""
        # Get trend data
        trends = self.trend_analysis.get_trends(
            therapeutic_area=therapeutic_area,
            technology_focus=technology_focus
        )
        
        # Get regulatory trends that might impact the market
        regulatory_trends = self.trend_analysis.get_regulatory_trends(
            therapeutic_area=therapeutic_area
        )
        
        # Get investment trends
        investment_trends = self.trend_analysis.get_investment_trends(
            therapeutic_area=therapeutic_area,
            technology_focus=technology_focus
        )
        
        # Format the trend analysis response
        return format_market_analysis(
            analysis_type="trend_analysis",
            therapeutic_area=therapeutic_area,
            technology_focus=technology_focus,
            trends=trends,
            regulatory_trends=regulatory_trends,
            investment_trends=investment_trends
        )
    
    def _provide_strategic_recommendations(self, therapeutic_area: Optional[str],
                                         company_focus: Optional[str],
                                         goal: str) -> str:
        """Generate strategic recommendations."""
        # Get market opportunity analysis
        opportunities = self.market_intelligence.get_opportunities(
            therapeutic_area=therapeutic_area,
            goal=goal
        )
        
        # Get competitive position if company is specified
        competitive_position = None
        if company_focus:
            competitive_position = self.competitive_analysis.get_company_position(
                company_name=company_focus,
                therapeutic_area=therapeutic_area
            )
        
        # Get strategic options based on goal
        strategic_options = self.market_intelligence.get_strategic_options(
            therapeutic_area=therapeutic_area,
            goal=goal,
            company_focus=company_focus
        )
        
        # Format the strategic recommendations response
        return format_market_analysis(
            analysis_type="strategic_recommendations",
            therapeutic_area=therapeutic_area,
            company_focus=company_focus,
            goal=goal,
            opportunities=opportunities,
            competitive_position=competitive_position,
            strategic_options=strategic_options
        )
    
    def _provide_general_market_overview(self) -> str:
        """Generate a general market overview."""
        # Get overall biotech market overview
        market_overview = self.market_intelligence.get_general_market_overview()
        
        # Get key trends
        key_trends = self.trend_analysis.get_key_trends()
        
        # Format the general overview response
        return format_market_analysis(
            analysis_type="general_overview",
            market_overview=market_overview,
            key_trends=key_trends
        )
    
    def _refresh_market_data_if_needed(self) -> None:
        """Refresh market data if it's outdated."""
        self.market_intelligence.update_if_needed()
        self.competitive_analysis.update_if_needed()
        self.trend_analysis.update_if_needed()
        self.news_analyzer.update_if_needed()
    
    def _load_therapeutic_areas(self) -> Dict[str, Any]:
        """Load therapeutic areas database."""
        db_path = os.path.join(self.data_dir, "therapeutic_areas.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading therapeutic areas database: {e}")
        
        # If file doesn't exist or error occurs, return default database
        return self._create_default_therapeutic_areas()
    
    def _create_default_therapeutic_areas(self) -> Dict[str, Any]:
        """Create a default therapeutic areas database."""
        areas = {
            "oncology": {
                "keywords": ["cancer", "tumor", "oncology", "immuno-oncology", "oncological"],
                "segments": ["solid tumors", "hematological cancers", "immunotherapy", "targeted therapy"],
                "key_technologies": ["checkpoint inhibitors", "CAR-T", "cancer vaccines", "ADCs"]
            },
            "neurology": {
                "keywords": ["brain", "neural", "neurological", "cns", "neurology", "alzheimer", "parkinson"],
                "segments": ["neurodegenerative", "psychiatric disorders", "pain management", "rare neurological"],
                "key_technologies": ["small molecules", "gene therapy", "neurostimulation", "biomarkers"]
            },
            "immunology": {
                "keywords": ["immune", "autoimmune", "inflammation", "immunological", "immunology"],
                "segments": ["autoimmune diseases", "inflammation", "transplantation", "allergy"],
                "key_technologies": ["monoclonal antibodies", "JAK inhibitors", "cytokine modulators"]
            },
            "infectious_diseases": {
                "keywords": ["infection", "bacterial", "viral", "pathogen", "antimicrobial"],
                "segments": ["antibiotics", "antivirals", "vaccines", "diagnostics"],
                "key_technologies": ["vaccines", "antibiotics", "antivirals", "rapid diagnostics"]
            },
            "rare_diseases": {
                "keywords": ["rare disease", "orphan", "ultra-rare", "genetic disorder"],
                "segments": ["metabolic disorders", "genetic diseases", "enzyme replacement"],
                "key_technologies": ["gene therapy", "enzyme replacement", "antisense oligonucleotides"]
            }
        }
        
        # Save the default database
        db_path = os.path.join(self.data_dir, "therapeutic_areas.json")
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with open(db_path, 'w') as f:
                json.dump(areas, f, indent=2)
        except Exception as e:
            print(f"Error saving default therapeutic areas database: {e}")
        
        return areas
    
    def _load_competitor_database(self) -> Dict[str, Any]:
        """Load competitor database."""
        db_path = os.path.join(self.data_dir, "competitors.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading competitor database: {e}")
        
        # If file doesn't exist or error occurs, return default database
        return self._create_default_competitor_database()
    
    def _create_default_competitor_database(self) -> Dict[str, Any]:
        """Create a default competitor database with major biotech companies."""
        competitors = {
            "Pfizer": {
                "ticker": "PFE",
                "market_cap": "240B",
                "therapeutic_areas": ["oncology", "rare_diseases", "vaccines", "immunology"],
                "key_products": ["Prevnar", "Ibrance", "Xeljanz", "Eliquis"],
                "pipeline_focus": ["oncology", "rare_diseases", "vaccines"]
            },
            "Roche": {
                "ticker": "RHHBY",
                "market_cap": "320B",
                "therapeutic_areas": ["oncology", "neurology", "immunology", "infectious_diseases"],
                "key_products": ["Tecentriq", "Avastin", "Herceptin", "Ocrevus"],
                "pipeline_focus": ["cancer immunotherapy", "neurology", "personalized healthcare"]
            },
            "Novartis": {
                "ticker": "NVS",
                "market_cap": "210B",
                "therapeutic_areas": ["oncology", "cardiology", "neurology", "immunology"],
                "key_products": ["Entresto", "Cosentyx", "Zolgensma", "Kisqali"],
                "pipeline_focus": ["cell therapy", "gene therapy", "radioligand therapy"]
            },
            "Amgen": {
                "ticker": "AMGN",
                "market_cap": "150B",
                "therapeutic_areas": ["oncology", "bone health", "cardiovascular", "neurology"],
                "key_products": ["Enbrel", "Prolia", "Neulasta", "Otezla"],
                "pipeline_focus": ["inflammation", "oncology", "cardiovascular"]
            },
            "Regeneron": {
                "ticker": "REGN",
                "market_cap": "90B",
                "therapeutic_areas": ["ophthalmology", "immunology", "oncology", "rare_diseases"],
                "key_products": ["Eylea", "Dupixent", "Praluent", "Libtayo"],
                "pipeline_focus": ["ophthalmology", "oncology", "genetic medicines"]
            },
            "Biogen": {
                "ticker": "BIIB",
                "market_cap": "35B",
                "therapeutic_areas": ["neurology", "rare_diseases", "immunology"],
                "key_products": ["Tecfidera", "Spinraza", "Aduhelm", "Tysabri"],
                "pipeline_focus": ["neurology", "neuropsychiatry", "gene therapy"]
            },
            "Gilead": {
                "ticker": "GILD",
                "market_cap": "85B",
                "therapeutic_areas": ["virology", "oncology", "inflammation"],
                "key_products": ["Biktarvy", "Veklury", "Yescarta", "Tecartus"],
                "pipeline_focus": ["virology", "oncology", "cell therapy"]
            },
            "Vertex": {
                "ticker": "VRTX",
                "market_cap": "80B",
                "therapeutic_areas": ["rare_diseases", "cystic fibrosis", "pain management"],
                "key_products": ["Trikafta", "Kalydeco", "Orkambi", "Symdeko"],
                "pipeline_focus": ["gene editing", "cell therapy", "pain"]
            }
        }
        
        # Save the default database
        db_path = os.path.join(self.data_dir, "competitors.json")
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with open(db_path, 'w') as f:
                json.dump(competitors, f, indent=2)
        except Exception as e:
            print(f"Error saving default competitor database: {e}")
        
        return competitors

# Create an instance of the MarketAgent
market_agent_executor = MarketAgent()

# Example usage
if __name__ == "__main__":
    test_query = "What is the competitive landscape for CRISPR-based therapeutics in oncology?"
    result = market_agent_executor.invoke({"input": test_query})
    print(result["response"])
