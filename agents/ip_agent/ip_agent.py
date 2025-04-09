# agents/ip_agent/ip_agent.py

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Import data providers
from agents.ip_agent.data_providers.patent_database import PatentDatabaseProvider
from agents.ip_agent.data_providers.patent_search import PatentSearchProvider
from agents.ip_agent.data_providers.legal_developments import LegalDevelopmentsProvider

# Import utilities
from agents.ip_agent.utils.cache_manager import CacheManager
from agents.ip_agent.utils.response_formatter import format_ip_analysis

class IPAgent:
    """
    Agent for intellectual property analysis in biotech and pharmaceutical domains.
    Provides insights on patent landscapes, freedom to operate, and IP strategies.
    """
    
    def __init__(self):
        """Initialize the IP agent with its component services."""
        # Set up data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize cache manager
        self.cache_manager = CacheManager(os.path.join(self.data_dir, "cache"))
        
        # Initialize data providers
        self.patent_db = PatentDatabaseProvider(self.cache_manager)
        self.patent_search = PatentSearchProvider(self.cache_manager)
        self.legal_developments = LegalDevelopmentsProvider(self.cache_manager)
        
        # Load technology domain database
        self.tech_domains = self._load_tech_domains()
        
        # Load company database
        self.company_database = self._load_company_database()
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an IP-related query and provide analysis.
        
        Args:
            inputs: Dictionary containing input query and context
                - input (str): The query to process
                - context (Optional[Dict]): Additional context like
                  molecular insights from other agents
                
        Returns:
            Dict containing the IP analysis response
        """
        query = inputs.get("input", "")
        context = inputs.get("context", {})
        
        # Ensure data is up to date
        self._refresh_ip_data_if_needed()
        
        # Analyze the query to determine the IP analysis focus
        ip_focus = self._determine_ip_focus(query, context)
        
        # Generate the appropriate IP analysis
        if ip_focus["type"] == "patent_landscape":
            response = self._analyze_patent_landscape(
                ip_focus["tech_domain"],
                ip_focus.get("companies", []),
                ip_focus.get("time_range", "10-year")
            )
        elif ip_focus["type"] == "freedom_to_operate":
            response = self._analyze_freedom_to_operate(
                ip_focus["tech_domain"],
                ip_focus.get("target_markets", ["US", "EU", "CN"]),
                ip_focus.get("molecule", None)
            )
        elif ip_focus["type"] == "ip_strategy":
            response = self._provide_ip_strategy(
                ip_focus["tech_domain"],
                ip_focus.get("company", None),
                ip_focus.get("stage", "early")
            )
        elif ip_focus["type"] == "legal_developments":
            response = self._analyze_legal_developments(
                ip_focus["tech_domain"],
                ip_focus.get("region", "global")
            )
        else:
            # Default to a general IP overview
            response = self._provide_general_ip_overview()
        
        return {
            "response": response,
            "ip_focus": ip_focus
        }
    
    def _determine_ip_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the query to determine the IP analysis focus.
        
        Args:
            query (str): The user query
            context (Dict[str, Any]): Additional context from other agents
            
        Returns:
            Dict with IP focus information
        """
        query_lower = query.lower()
        
        # Check for patent landscape requests
        landscape_keywords = ["patent landscape", "patent analysis", "ip landscape", 
                             "patent portfolio", "patent map", "patent activity"]
        if any(keyword in query_lower for keyword in landscape_keywords):
            return self._extract_landscape_focus(query, context)
        
        # Check for freedom to operate (FTO) requests
        fto_keywords = ["freedom to operate", "fto", "patent risk", "infringement risk", 
                       "clear ip", "patent barrier", "blocking patent"]
        if any(keyword in query_lower for keyword in fto_keywords):
            return self._extract_fto_focus(query, context)
        
        # Check for IP strategy requests
        strategy_keywords = ["ip strategy", "patent strategy", "intellectual property strategy",
                            "patenting strategy", "protect innovation", "protect invention"]
        if any(keyword in query_lower for keyword in strategy_keywords):
            return self._extract_strategy_focus(query, context)
        
        # Check for legal developments requests
        legal_keywords = ["legal development", "patent law", "ip law change", 
                         "court decision", "patent case", "patent ruling"]
        if any(keyword in query_lower for keyword in legal_keywords):
            return self._extract_legal_focus(query, context)
        
        # Default to general IP overview with detected tech domain
        tech_domain = self._extract_tech_domain_from_query(query, context)
        return {
            "type": "general_overview",
            "tech_domain": tech_domain
        }
    
    def _extract_landscape_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patent landscape focus from query."""
        tech_domain = self._extract_tech_domain_from_query(query, context)
        
        # Extract mentioned companies
        companies = []
        for company_name in self.company_database.keys():
            if company_name.lower() in query.lower():
                companies.append(company_name)
        
        # Extract time range
        time_range = "10-year"  # Default
        if "5-year" in query.lower() or "five year" in query.lower():
            time_range = "5-year"
        elif "20-year" in query.lower() or "twenty year" in query.lower():
            time_range = "20-year"
        
        return {
            "type": "patent_landscape",
            "tech_domain": tech_domain,
            "companies": companies,
            "time_range": time_range
        }
    
    def _extract_fto_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract freedom to operate focus from query."""
        tech_domain = self._extract_tech_domain_from_query(query, context)
        
        # Extract target markets
        target_markets = ["US", "EU", "CN"]  # Default
        market_keywords = {
            "US": ["united states", "us market", "usa", "america"],
            "EU": ["europe", "european", "eu"],
            "CN": ["china", "chinese"],
            "JP": ["japan", "japanese"],
            "KR": ["korea", "korean"],
            "IN": ["india", "indian"]
        }
        
        explicit_markets = []
        for market, keywords in market_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                explicit_markets.append(market)
        
        if explicit_markets:
            target_markets = explicit_markets
        
        # Extract molecule if mentioned (check from molecular agent context)
        molecule = None
        if context and "previous_responses" in context:
            molecular_response = context["previous_responses"].get("molecular_agent", "")
            if molecular_response and isinstance(molecular_response, str):
                # Simple extraction - in a real system, this would be more sophisticated
                if "molecule:" in molecular_response.lower():
                    parts = molecular_response.lower().split("molecule:")
                    if len(parts) > 1:
                        molecule_part = parts[1].strip().split()[0]
                        molecule = molecule_part
        
        return {
            "type": "freedom_to_operate",
            "tech_domain": tech_domain,
            "target_markets": target_markets,
            "molecule": molecule
        }
    
    def _extract_strategy_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract IP strategy focus from query."""
        tech_domain = self._extract_tech_domain_from_query(query, context)
        
        # Extract company if mentioned
        company = None
        for company_name in self.company_database.keys():
            if company_name.lower() in query.lower():
                company = company_name
                break
        
        # Try to determine company stage
        stage = "early"  # Default
        stage_keywords = {
            "early": ["early stage", "startup", "beginning", "novel", "new company"],
            "growth": ["growth stage", "expanding", "series b", "series c"],
            "mature": ["mature", "established", "public company", "large company"]
        }
        
        for s, keywords in stage_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                stage = s
                break
        
        return {
            "type": "ip_strategy",
            "tech_domain": tech_domain,
            "company": company,
            "stage": stage
        }
    
    def _extract_legal_focus(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract legal developments focus from query."""
        tech_domain = self._extract_tech_domain_from_query(query, context)
        
        # Extract region focus
        region = "global"  # Default
        region_keywords = {
            "us": ["united states", "us law", "uspto", "american"],
            "eu": ["european", "europe", "epo", "eu law"],
            "cn": ["china", "chinese", "sipo"],
            "global": ["worldwide", "global", "international", "wipo"]
        }
        
        for reg, keywords in region_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                region = reg
                break
        
        return {
            "type": "legal_developments",
            "tech_domain": tech_domain,
            "region": region
        }
    
    def _extract_tech_domain_from_query(self, query: str, context: Dict[str, Any]) -> Optional[str]:
        """Extract technology domain from query and context."""
        # First check if a tech domain is directly mentioned in the query
        for domain, data in self.tech_domains.items():
            keywords = data.get("keywords", [])
            if any(keyword.lower() in query.lower() for keyword in keywords):
                return domain
        
        # If not found in query, check context (e.g., from molecular agent)
        if context and "previous_responses" in context:
            for agent_response in context["previous_responses"].values():
                if isinstance(agent_response, str):
                    # For each tech domain, check if it or its keywords are mentioned
                    for domain, data in self.tech_domains.items():
                        if domain.lower() in agent_response.lower():
                            return domain
                        
                        # Check for keywords
                        keywords = data.get("keywords", [])
                        if any(keyword.lower() in agent_response.lower() for keyword in keywords):
                            return domain
        
        # Default to None if no tech domain could be identified
        return None
    
    def _analyze_patent_landscape(self, tech_domain: Optional[str], 
                                companies: List[str], 
                                time_range: str) -> str:
        """Generate patent landscape analysis."""
        # Get patent landscape data
        landscape_data = self.patent_search.get_patent_landscape(
            tech_domain=tech_domain,
            companies=companies,
            time_range=time_range
        )
        
        # Get patent trend data
        trend_data = self.patent_search.get_patent_trends(
            tech_domain=tech_domain,
            time_range=time_range
        )
        
        # Get key player analysis
        key_players = self.patent_search.get_key_players(
            tech_domain=tech_domain,
            time_range=time_range
        )
        
        # Format the patent landscape response
        return format_ip_analysis(
            analysis_type="patent_landscape",
            tech_domain=tech_domain,
            landscape_data=landscape_data,
            trend_data=trend_data,
            key_players=key_players,
            companies=companies,
            time_range=time_range
        )
    
    def _analyze_freedom_to_operate(self, tech_domain: Optional[str],
                                  target_markets: List[str],
                                  molecule: Optional[str]) -> str:
        """Generate freedom to operate analysis."""
        # Get potential blocking patents
        blocking_patents = self.patent_search.get_blocking_patents(
            tech_domain=tech_domain,
            target_markets=target_markets,
            molecule=molecule
        )
        
        # Get patent expiration analysis
        expiration_analysis = self.patent_search.get_patent_expirations(
            tech_domain=tech_domain,
            target_markets=target_markets
        )
        
        # Get litigation risk assessment
        litigation_risk = self.legal_developments.get_litigation_risk(
            tech_domain=tech_domain,
            target_markets=target_markets
        )
        
        # Format the FTO response
        return format_ip_analysis(
            analysis_type="freedom_to_operate",
            tech_domain=tech_domain,
            target_markets=target_markets,
            molecule=molecule,
            blocking_patents=blocking_patents,
            expiration_analysis=expiration_analysis,
            litigation_risk=litigation_risk
        )
    
    def _provide_ip_strategy(self, tech_domain: Optional[str],
                           company: Optional[str],
                           stage: str) -> str:
        """Generate IP strategy recommendations."""
        # Get filing strategy recommendations
        filing_strategy = self.patent_db.get_filing_strategy(
            tech_domain=tech_domain,
            company_stage=stage
        )
        
        # Get competitive positioning if company is specified
        competitive_position = None
        if company:
            competitive_position = self.patent_db.get_company_ip_position(
                company_name=company,
                tech_domain=tech_domain
            )
        
        # Get strategic options based on stage
        strategic_options = self.patent_db.get_strategic_options(
            tech_domain=tech_domain,
            stage=stage,
            company=company
        )
        
        # Format the IP strategy response
        return format_ip_analysis(
            analysis_type="ip_strategy",
            tech_domain=tech_domain,
            company=company,
            stage=stage,
            filing_strategy=filing_strategy,
            competitive_position=competitive_position,
            strategic_options=strategic_options
        )
    
    def _analyze_legal_developments(self, tech_domain: Optional[str],
                                  region: str) -> str:
        """Generate analysis of legal developments."""
        # Get recent legal developments
        developments = self.legal_developments.get_developments(
            tech_domain=tech_domain,
            region=region
        )
        
        # Get court cases and their implications
        court_cases = self.legal_developments.get_court_cases(
            tech_domain=tech_domain,
            region=region
        )
        
        # Get regulatory changes
        regulatory_changes = self.legal_developments.get_regulatory_changes(
            tech_domain=tech_domain,
            region=region
        )
        
        # Format the legal developments response
        return format_ip_analysis(
            analysis_type="legal_developments",
            tech_domain=tech_domain,
            region=region,
            developments=developments,
            court_cases=court_cases,
            regulatory_changes=regulatory_changes
        )
    
    def _provide_general_ip_overview(self) -> str:
        """Generate a general IP overview."""
        # Get general biotech IP overview
        ip_overview = self.patent_db.get_general_ip_overview()
        
        # Get key trends
        key_trends = self.patent_search.get_key_trends()
        
        # Format the general overview response
        return format_ip_analysis(
            analysis_type="general_overview",
            ip_overview=ip_overview,
            key_trends=key_trends
        )
    
    def _refresh_ip_data_if_needed(self) -> None:
        """Refresh IP data if it's outdated."""
        self.patent_db.update_if_needed()
        self.patent_search.update_if_needed()
        self.legal_developments.update_if_needed()
    
    def _load_tech_domains(self) -> Dict[str, Any]:
        """Load technology domains database."""
        db_path = os.path.join(self.data_dir, "tech_domains.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading tech domains database: {e}")
        
        # If file doesn't exist or error occurs, return default database
        return self._create_default_tech_domains()
    
    def _create_default_tech_domains(self) -> Dict[str, Any]:
        """Create a default technology domains database."""
        domains = {
            "crispr": {
                "keywords": ["crispr", "cas9", "gene editing", "genetic engineering", "genome editing"],
                "key_players": ["Broad Institute", "UC Berkeley", "Editas", "CRISPR Therapeutics", "Intellia"],
                "key_technologies": ["crispr-cas9", "base editing", "prime editing", "cas12", "cas13"]
            },
            "antibodies": {
                "keywords": ["antibody", "monoclonal", "bispecific", "immunoglobulin", "mab"],
                "key_players": ["Regeneron", "Amgen", "Genentech", "AbbVie", "Sanofi"],
                "key_technologies": ["monoclonal antibodies", "bispecific antibodies", "antibody-drug conjugates"]
            },
            "car_t": {
                "keywords": ["car-t", "chimeric antigen receptor", "cell therapy", "adoptive cell"],
                "key_players": ["Novartis", "Gilead", "Bristol-Myers Squibb", "Johnson & Johnson", "Autolus"],
                "key_technologies": ["car-t", "tcr", "til", "nk cell therapy"]
            },
            "small_molecules": {
                "keywords": ["small molecule", "chemical compound", "low molecular weight", "oral drug"],
                "key_players": ["Pfizer", "Merck", "Novartis", "AstraZeneca", "Bristol-Myers Squibb"],
                "key_technologies": ["kinase inhibitors", "gpcr modulators", "protacs", "molecular glues"]
            },
            "rna_therapeutics": {
                "keywords": ["rna", "rnai", "sirna", "mrna", "antisense"],
                "key_players": ["Moderna", "BioNTech", "Alnylam", "Ionis", "Arrowhead"],
                "key_technologies": ["mrna vaccines", "sirna", "antisense oligonucleotides", "splicing modulators"]
            }
        }
        
        # Save the default database
        db_path = os.path.join(self.data_dir, "tech_domains.json")
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with open(db_path, 'w') as f:
                json.dump(domains, f, indent=2)
        except Exception as e:
            print(f"Error saving default tech domains database: {e}")
        
        return domains
    
    def _load_company_database(self) -> Dict[str, Any]:
        """Load company database."""
        db_path = os.path.join(self.data_dir, "companies.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading company database: {e}")
        
        # If file doesn't exist or error occurs, return default database
        return self._create_default_company_database()
    
    def _create_default_company_database(self) -> Dict[str, Any]:
        """Create a default company database with major biotech companies."""
        companies = {
            "Pfizer": {
                "ticker": "PFE",
                "ip_strength": "very strong",
                "key_ip_areas": ["small molecules", "vaccines", "antibodies"],
                "notable_patents": ["COVID-19 vaccine technology", "Ibrance", "Xeljanz"]
            },
            "Regeneron": {
                "ticker": "REGN",
                "ip_strength": "strong",
                "key_ip_areas": ["antibodies", "gene therapy", "inflammation"],
                "notable_patents": ["VelocImmune platform", "Dupixent", "Eylea"]
            },
            "Moderna": {
                "ticker": "MRNA",
                "ip_strength": "strong",
                "key_ip_areas": ["mRNA therapeutics", "vaccines", "delivery systems"],
                "notable_patents": ["mRNA delivery technology", "Spikevax", "LNP formulations"]
            },
            "CRISPR Therapeutics": {
                "ticker": "CRSP",
                "ip_strength": "moderate",
                "key_ip_areas": ["gene editing", "CAR-T", "ex vivo cell therapy"],
                "notable_patents": ["CRISPR-Cas9 applications", "CTX001", "Allogeneic CAR-T"]
            },
            "Alnylam": {
                "ticker": "ALNY",
                "ip_strength": "strong",
                "key_ip_areas": ["RNAi therapeutics", "siRNA", "delivery systems"],
                "notable_patents": ["GalNAc conjugate technology", "Onpattro", "RNAi platform"]
            },
            "Vertex": {
                "ticker": "VRTX",
                "ip_strength": "very strong",
                "key_ip_areas": ["cystic fibrosis", "small molecules", "gene editing"],
                "notable_patents": ["CFTR modulators", "CTX001 (with CRISPR Tx)", "Pain therapies"]
            },
            "Illumina": {
                "ticker": "ILMN",
                "ip_strength": "very strong",
                "key_ip_areas": ["DNA sequencing", "diagnostics", "genetic analysis"],
                "notable_patents": ["Sequencing-by-synthesis", "Flow cells", "NextSeq technology"]
            },
            "Biogen": {
                "ticker": "BIIB",
                "ip_strength": "strong",
                "key_ip_areas": ["multiple sclerosis", "neurology", "biosimilars"],
                "notable_patents": ["Tecfidera", "Spinraza", "Anti-CD20 antibodies"]
            }
        }
        
        # Save the default database
        db_path = os.path.join(self.data_dir, "companies.json")
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with open(db_path, 'w') as f:
                json.dump(companies, f, indent=2)
        except Exception as e:
            print(f"Error saving default company database: {e}")
        
        return companies

# Create an instance of the IPAgent
ip_agent_executor = IPAgent()

# Example usage
if __name__ == "__main__":
    test_query = "What's the patent landscape for CRISPR-based therapies in oncology?"
    result = ip_agent_executor.invoke({"input": test_query})
    print(result["response"])
