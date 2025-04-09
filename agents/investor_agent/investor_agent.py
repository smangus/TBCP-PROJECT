# agents/investor_agent/investor_agent.py

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import data providers
from agents.investor_agent.data_providers.market_data import MarketDataProvider
from agents.investor_agent.data_providers.clinical_trials import ClinicalTrialsProvider
from agents.investor_agent.data_providers.sec_data import SECDataProvider
from agents.investor_agent.data_providers.news_data import NewsDataProvider

# Import models
from agents.investor_agent.models.drug_model import DrugFinancialModel
from agents.investor_agent.models.therapeutic_area import TherapeuticAreaAnalyzer
from agents.investor_agent.models.sentiment_analysis import SentimentAnalyzer

# Import utilities
from agents.investor_agent.utils.cache import CacheManager
from agents.investor_agent.utils.formatters import format_investment_analysis

class InvestorAgent:
    """
    Agent for providing investment insights for biotech executives.
    Utilizes public data sources to deliver competitive analysis without
    expensive data subscriptions.
    """
    
    def __init__(self):
        """Initialize the investor agent with its component services."""
        # Set up data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize cache manager
        self.cache_manager = CacheManager(os.path.join(os.path.dirname(__file__), "data"))
        
        # Initialize data providers
        self.market_data = MarketDataProvider(self.cache_manager)
        self.clinical_trials = ClinicalTrialsProvider(self.cache_manager)
        self.sec_data = SECDataProvider(self.cache_manager)
        self.news_data = NewsDataProvider(self.cache_manager)
        
        # Initialize analysis models
        self.drug_model = DrugFinancialModel()
        self.therapeutic_area = TherapeuticAreaAnalyzer()
        self.sentiment = SentimentAnalyzer()
        
        # Load drug database
        self.drug_database = self._load_drug_database()
        self.therapeutic_areas = self._load_therapeutic_areas()
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an investment query using public financial data.
        
        Args:
            inputs: Dictionary containing the input query and context
                - input (str): The query to process
                - context (Optional[Dict]): Additional context
                
        Returns:
            Dict containing the investment analysis response
        """
        query = inputs.get("input", "")
        context = inputs.get("context", {})
        
        # Ensure data is up to date
        self._update_data_if_needed()
        
        # Analyze the query to determine the investment focus
        investment_focus = self._determine_investment_focus(query)
        
        # Generate the appropriate investment analysis
        if investment_focus["type"] == "drug_specific":
            response = self._analyze_drug_investment(
                investment_focus["drug_name"],
                investment_focus.get("therapeutic_area", "unknown")
            )
        elif investment_focus["type"] == "therapeutic_area":
            response = self._analyze_therapeutic_area(
                investment_focus["therapeutic_area"]
            )
        elif investment_focus["type"] == "company_specific":
            response = self._analyze_company_investment(
                investment_focus["company_ticker"]
            )
        elif investment_focus["type"] == "market_trend":
            response = self._analyze_market_trends()
        else:
            response = self._generate_general_investment_advice()
        
        return {
            "response": response,
            "investment_focus": investment_focus
        }
    
    def _determine_investment_focus(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query to determine the investment focus.
        
        Args:
            query (str): The user query
            
        Returns:
            Dict with investment focus information
        """
        query_lower = query.lower()
        
        # Check for specific drug mentions
        for drug_name, drug_info in self.drug_database.items():
            if drug_name.lower() in query_lower:
                return {
                    "type": "drug_specific",
                    "drug_name": drug_name,
                    "therapeutic_area": drug_info.get("therapeutic_area", "unknown")
                }
        
        # Check for therapeutic area mentions
        for area, data in self.therapeutic_areas.items():
            for keyword in data.get("keywords", []):
                if keyword.lower() in query_lower:
                    return {
                        "type": "therapeutic_area",
                        "therapeutic_area": area
                    }
        
        # Check for company mentions (using stock tickers and company names)
        for ticker, company_name in self.market_data.get_tracked_companies().items():
            if ticker.lower() in query_lower or company_name.lower() in query_lower:
                return {
                    "type": "company_specific",
                    "company_ticker": ticker,
                    "company_name": company_name
                }
        
        # Check for market trend queries
        market_keywords = ["market", "trend", "investment", "stock", "financial", 
                          "sector", "industry", "biotech market"]
        if any(keyword in query_lower for keyword in market_keywords):
            return {
                "type": "market_trend"
            }
        
        # Default to general investment advice
        return {
            "type": "general"
        }
    
    def _analyze_drug_investment(self, drug_name: str, therapeutic_area: str) -> str:
        """Generate investment analysis for a specific drug."""
        # Fetch data for analysis
        drug_info = self.drug_database.get(drug_name, {})
        trial_data = self.clinical_trials.get_trials_for_drug(drug_name)
        market_data = self.therapeutic_area.get_market_data(therapeutic_area)
        news = self.news_data.get_news_for_drug(drug_name)
        company_data = {}
        
        # Get associated companies
        associated_companies = drug_info.get("associated_companies", [])
        if associated_companies:
            company_data = self.market_data.get_data_for_companies(associated_companies)
        
        # Generate financial model
        financial_model = self.drug_model.generate_model(
            drug_name, 
            trial_data, 
            drug_info.get("market_size", 0),
            drug_info.get("peak_share", 0)
        )
        
        # Analyze sentiment
        sentiment = self.sentiment.analyze(drug_name, news)
        
        # Format the response
        return format_investment_analysis(
            analysis_type="drug",
            drug_name=drug_name,
            therapeutic_area=therapeutic_area,
            trial_data=trial_data,
            market_data=market_data,
            news=news,
            company_data=company_data,
            financial_model=financial_model,
            sentiment=sentiment
        )
    
    def _analyze_therapeutic_area(self, therapeutic_area: str) -> str:
        """Generate investment analysis for a therapeutic area."""
        # Get therapeutic area data
        area_data = self.therapeutic_areas.get(therapeutic_area, {})
        
        # Get market data for companies in this therapeutic area
        companies = area_data.get("companies", [])
        company_data = self.market_data.get_data_for_companies(companies)
        
        # Get recent trials in this area
        trials = self.clinical_trials.get_trials_for_therapeutic_area(therapeutic_area)
        
        # Get news for this therapeutic area
        news = self.news_data.get_news_for_therapeutic_area(therapeutic_area)
        
        # Analyze area trends
        area_analysis = self.therapeutic_area.analyze(
            therapeutic_area, 
            company_data, 
            trials, 
            news
        )
        
        # Format the response
        return format_investment_analysis(
            analysis_type="therapeutic_area",
            therapeutic_area=therapeutic_area,
            area_analysis=area_analysis,
            company_data=company_data,
            trials=trials,
            news=news
        )
    
    def _analyze_company_investment(self, company_ticker: str) -> str:
        """Generate investment analysis for a specific company."""
        # Get company data
        company_data = self.market_data.get_data_for_companies([company_ticker])
        company_info = company_data.get(company_ticker, {})
        
        # Get SEC filings
        sec_filings = self.sec_data.get_filings_for_company(company_ticker)
        
        # Get company news
        news = self.news_data.get_news_for_company(company_ticker)
        
        # Get company's drug pipeline
        pipeline = self.clinical_trials.get_pipeline_for_company(company_ticker)
        
        # Format the response
        return format_investment_analysis(
            analysis_type="company",
            company_ticker=company_ticker,
            company_name=company_info.get("name", ""),
            company_data=company_info,
            sec_filings=sec_filings,
            news=news,
            pipeline=pipeline
        )
    
    def _analyze_market_trends(self) -> str:
        """Generate analysis of overall biotech market trends."""
        # Get ETF data
        etfs = self.market_data.get_etf_data()
        
        # Get industry metrics
        industry_metrics = self.market_data.get_industry_metrics()
        
        # Get latest market news
        news = self.news_data.get_market_news()
        
        # Format the response
        return format_investment_analysis(
            analysis_type="market_trend",
            etfs=etfs,
            industry_metrics=industry_metrics,
            news=news
        )
    
    def _generate_general_investment_advice(self) -> str:
        """Generate general biotech investment advice."""
        # Get current market conditions
        market_conditions = self.market_data.get_market_conditions()
        
        # Format the response
        return format_investment_analysis(
            analysis_type="general",
            market_conditions=market_conditions
        )
    
    def _update_data_if_needed(self):
        """Update all data sources if needed."""
        self.market_data.update_if_needed()
        self.clinical_trials.update_if_needed()
        self.sec_data.update_if_needed()
        self.news_data.update_if_needed()
    
    def _load_drug_database(self) -> Dict[str, Any]:
        """Load drug database from file."""
        db_path = os.path.join(self.data_dir, "drug_database.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading drug database: {e}")
        
        # If file doesn't exist or error occurs, return default database
        return self._create_default_drug_database()
    
    def _create_default_drug_database(self) -> Dict[str, Any]:
        """Create a default drug database with some common drugs."""
        db = {
            "paclitaxel": {
                "therapeutic_area": "oncology",
                "associated_companies": ["BMY", "TEVA", "MYOK"],
                "market_size": 1200000000,  # $1.2B in USD
                "peak_share": 0.35  # 35% market share at peak
            },
            "pembrolizumab": {
                "therapeutic_area": "oncology",
                "associated_companies": ["MRK"],
                "market_size": 17000000000,  # $17B in USD
                "peak_share": 0.45  # 45% market share at peak
            },
            "adalimumab": {
                "therapeutic_area": "immunology",
                "associated_companies": ["ABBV", "AMGN", "PFE"],
                "market_size": 20000000000,  # $20B in USD
                "peak_share": 0.55  # 55% market share at peak
            },
            "trastuzumab": {
                "therapeutic_area": "oncology",
                "associated_companies": ["RHHBY", "PFE", "AMGN"],
                "market_size": 7000000000,  # $7B in USD
                "peak_share": 0.40  # 40% market share at peak
            },
            "lenvatinib": {
                "therapeutic_area": "oncology",
                "associated_companies": ["MRK", "ESALY"],
                "market_size": 4500000000,  # $4.5B in USD
                "peak_share": 0.30  # 30% market share at peak
            }
        }
        
        # Save the default database
        db_path = os.path.join(self.data_dir, "drug_database.json")
        try:
            with open(db_path, 'w') as f:
                json.dump(db, f, indent=2)
        except Exception as e:
            print(f"Error saving default drug database: {e}")
        
        return db
    
    def _load_therapeutic_areas(self) -> Dict[str, Any]:
        """Load therapeutic areas mapping from file."""
        areas_path = os.path.join(self.data_dir, "therapeutic_areas.json")
        if os.path.exists(areas_path):
            try:
                with open(areas_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading therapeutic areas: {e}")
        
        # If file doesn't exist or error occurs, return default mapping
        return self._create_default_therapeutic_areas()
    
    def _create_default_therapeutic_areas(self) -> Dict[str, Any]:
        """Create a default therapeutic areas mapping."""
        areas = {
            "oncology": {
                "keywords": ["cancer", "tumor", "oncology", "immuno-oncology", "carcinoma", "leukemia", "lymphoma"],
                "companies": ["MRK", "BMY", "PFE", "RHHBY", "ABBV", "AZN", "NVS", "GILD", "REGN"],
                "etfs": ["XBI", "IBB", "ARKG"]
            },
            "immunology": {
                "keywords": ["autoimmune", "immunology", "inflammation", "arthritis", "psoriasis", "ibd"],
                "companies": ["ABBV", "JNJ", "AMGN", "NVS", "LLY"],
                "etfs": ["XBI", "IBB"]
            },
            "neurology": {
                "keywords": ["alzheimer", "parkinson", "neurology", "cns", "brain", "neurodegenerative"],
                "companies": ["BIIB", "LLY", "PFE", "NVS", "ABBV", "SAGE"],
                "etfs": ["XBI", "IBB"]
            },
            "cardiology": {
                "keywords": ["heart", "cardiovascular", "cardiology", "atherosclerosis", "thrombosis"],
                "companies": ["PFE", "NVS", "JNJ", "AMGN", "BMY"],
                "etfs": ["XBI", "IBB"]
            },
            "rare_diseases": {
                "keywords": ["rare disease", "orphan drug", "genetic disorder", "ultra-rare"],
                "companies": ["VRTX", "SRPT", "ALXN", "REGN", "BMRN"],
                "etfs": ["XBI", "IBB", "ARKG"]
            }
        }
        
        # Save the default mapping
        areas_path = os.path.join(self.data_dir, "therapeutic_areas.json")
        try:
            with open(areas_path, 'w') as f:
                json.dump(areas, f, indent=2)
        except Exception as e:
            print(f"Error saving default therapeutic areas: {e}")
        
        return areas

# Create an instance of the investor agent
investor_agent_executor = InvestorAgent()

# Example usage
if __name__ == "__main__":
    test_query = "What's the investment outlook for paclitaxel based therapies?"
    result = investor_agent_executor.invoke({"input": test_query})
    print(result["response"])