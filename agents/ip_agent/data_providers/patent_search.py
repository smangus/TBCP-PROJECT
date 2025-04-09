# agents/ip_agent/data_providers/patent_search.py

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from agents.ip_agent.utils.cache_manager import CacheManager

class PatentSearchProvider:
    """
    Provider for patent search capabilities with cached results.
    Handles patent landscapes, trends, key players, and blocking patents.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize with cache manager."""
        self.cache_manager = cache_manager
        self.last_update = None
        
        # Set up data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load default data
        self._load_default_data()
    
    def update_if_needed(self) -> None:
        """Update data if it's older than the threshold."""
        # Only update once per day
        if self.last_update and (datetime.now() - self.last_update) < timedelta(days=1):
            return
            
        # In a real implementation, this would make API calls to update data
        # For now, we just refresh our timestamp
        self.last_update = datetime.now()
    
    def get_patent_landscape(self, tech_domain: Optional[str], 
                           companies: List[str],
                           time_range: str) -> Dict[str, Any]:
        """
        Get patent landscape analysis for a technology domain.
        
        Args:
            tech_domain: Technology domain (e.g., "crispr", "antibodies")
            companies: List of companies to focus on
            time_range: Timeframe (e.g., "5-year", "10-year")
            
        Returns:
            Patent landscape data
        """
        # Try to get from cache first
        cache_key = f"landscape:{tech_domain or 'general'}:{'-'.join(companies)}:{time_range}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get landscape data (from default data for now)
        landscape_key = tech_domain if tech_domain else "general"
        
        if landscape_key in self.landscapes:
            landscape = self.landscapes[landscape_key]
            
            # Add company-specific summary if requested
            if companies:
                company_insights = []
                for company in companies:
                    if company in self.company_data:
                        company_insights.append(f"{company} is {self.company_data[company].get('position', 'active')} in this space")
                
                if company_insights:
                    company_summary = " and ".join(company_insights)
                    landscape["summary"] = landscape["summary"] + f" {company_summary}."
            
            self.cache_manager.set(cache_key, landscape)
            return landscape
        
        # Fall back to general landscape if specific one not found
        general_landscape = self.landscapes.get("general", {})
        self.cache_manager.set(cache_key, general_landscape)
        
        return general_landscape
    
    def get_patent_trends(self, tech_domain: Optional[str], time_range: str) -> Dict[str, Any]:
        """
        Get patent filing trends for a technology domain.
        
        Args:
            tech_domain: Technology domain
            time_range: Timeframe
            
        Returns:
            Patent trend data
        """
        # Try to get from cache first
        cache_key = f"trends:{tech_domain or 'general'}:{time_range}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get trend data
        trend_key = f"{tech_domain}:{time_range}" if tech_domain else f"general:{time_range}"
        
        if trend_key in self.trends:
            trends = self.trends[trend_key]
            self.cache_manager.set(cache_key, trends)
            return trends
            
        # Try just tech domain as fallback
        if tech_domain in self.trends:
            trends = self.trends[tech_domain]
            self.cache_manager.set(cache_key, trends)
            return trends
            
        # Fall back to general trends
        general_trends = self.trends.get("general", {})
        self.cache_manager.set(cache_key, general_trends)
        
        return general_trends
    
    def get_key_players(self, tech_domain: Optional[str], time_range: str) -> List[Dict[str, Any]]:
        """
        Get key patent holders for a technology domain.
        
        Args:
            tech_domain: Technology domain
            time_range: Timeframe
            
        Returns:
            List of key player data
        """
        # Try to get from cache first
        cache_key = f"key_players:{tech_domain or 'general'}:{time_range}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get player data
        player_key = tech_domain if tech_domain else "general"
        
        if player_key in self.key_players:
            players = self.key_players[player_key]
            self.cache_manager.set(cache_key, players)
            return players
        
        # Fall back to general players
        general_players = self.key_players.get("general", [])
        self.cache_manager.set(cache_key, general_players)
        
        return general_players
    
    def get_blocking_patents(self, tech_domain: Optional[str],
                           target_markets: List[str],
                           molecule: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get potentially blocking patents for FTO analysis.
        
        Args:
            tech_domain: Technology domain
            target_markets: List of target markets
            molecule: Specific molecule (optional)
            
        Returns:
            List of blocking patent data
        """
        # Try to get from cache first
        cache_key = f"blocking:{tech_domain or 'general'}:{'-'.join(target_markets)}:{molecule or 'none'}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get blocking patent data
        blocking_key = tech_domain if tech_domain else "general"
        
        # Filter by markets
        blocking_patents = []
        if blocking_key in self.blocking_patents:
            all_patents = self.blocking_patents[blocking_key]
            for patent in all_patents:
                # Include if patent is in any of the target markets
                patent_markets = patent.get("markets", [])
                if any(market in target_markets for market in patent_markets):
                    blocking_patents.append(patent)
        
        # If no matching patents found, return empty list
        if not blocking_patents:
            self.cache_manager.set(cache_key, [])
            return []
        
        # If molecule specified, filter further
        if molecule and blocking_patents:
            molecule_patents = [
                patent for patent in blocking_patents
                if molecule.lower() in patent.get("description", "").lower()
            ]
            self.cache_manager.set(cache_key, molecule_patents)
            return molecule_patents
        
        # Return filtered patents
        self.cache_manager.set(cache_key, blocking_patents)
        return blocking_patents
    
    def get_patent_expirations(self, tech_domain: Optional[str],
                             target_markets: List[str]) -> Dict[str, Any]:
        """
        Get patent expiration analysis.
        
        Args:
            tech_domain: Technology domain
            target_markets: List of target markets
            
        Returns:
            Patent expiration analysis
        """
        # Try to get from cache first
        cache_key = f"expirations:{tech_domain or 'general'}:{'-'.join(target_markets)}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get expiration data
        expiration_key = tech_domain if tech_domain else "general"
        
        if expiration_key in self.expirations:
            expirations = self.expirations[expiration_key]
            
            # Filter by markets
            filtered_soon = []
            if "expiring_soon" in expirations:
                for patent in expirations["expiring_soon"]:
                    # Include if patent is in any of the target markets
                    patent_markets = patent.get("markets", [])
                    if any(market in target_markets for market in patent_markets):
                        filtered_soon.append(patent)
            
            filtered_expirations = expirations.copy()
            filtered_expirations["expiring_soon"] = filtered_soon
            
            self.cache_manager.set(cache_key, filtered_expirations)
            return filtered_expirations
        
        # Fall back to general expirations
        general_expirations = self.expirations.get("general", {})
        self.cache_manager.set(cache_key, general_expirations)
        
        return general_expirations
    
    def get_key_trends(self) -> List[Dict[str, Any]]:
        """
        Get key IP trends across biotech.
        
        Returns:
            List of key trend data
        """
        return self.key_trends
    
    def _load_default_data(self) -> None:
        """Load default data if real API is not available."""
        # Patent landscapes by tech domain
        self.landscapes = {
            "general": {
                "summary": "The biotech patent landscape shows steady growth with diversification across therapeutic areas and modalities. Large pharmaceutical companies and specialized biotechs actively protect innovations, with increasing activity from academic institutions and emerging market entities.",
                "strategic_implications": "The evolving biotech patent landscape suggests companies should maintain vigilance on competitive patent activity, particularly in rapidly growing areas like cell and gene therapy. Early filing in emerging markets may be warranted given increasing sophistication of global patent systems."
            },
            "crispr": {
                "summary": "The CRISPR patent landscape remains complex with foundational patents controlled by the Broad Institute and University of California. Research activity is shifting toward delivery methods, enhanced editing systems, and therapeutic applications.",
                "strategic_implications": "Organizations working in CRISPR should consider: (1) licensing foundational patents, (2) focusing innovation on delivery systems and specific applications rather than core editing mechanisms, and (3) monitoring the extensive interference proceedings that continue to shape this space."
            },
            "antibodies": {
                "summary": "The antibody patent landscape continues to evolve with increased focus on novel antibody formats, specific epitope targeting, and effector function engineering. The space is dominated by specialized antibody platform companies and large pharmaceutical firms.",
                "strategic_implications": "Antibody developers should prioritize: (1) precise epitope characterization to support claims, (2) functional data beyond sequence information, and (3) attention to emerging antibody formats where patent protection may be more readily available."
            }
        }
        
        # Patent trends by tech domain and time range
        self.trends = {
            "general": {
                "yearly_filings": {
                    "2020": 8500,
                    "2021": 9200,
                    "2022": 9800,
                    "2023": 10400
                }
            },
            "crispr": {
                "yearly_filings": {
                    "2020": 850,
                    "2021": 980,
                    "2022": 1250,
                    "2023": 1320
                }
            },
            "antibodies": {
                "yearly_filings": {
                    "2020": 1600,
                    "2021": 1680,
                    "2022": 1720,
                    "2023": 1840
                }
            },
            "small_molecules": {
                "yearly_filings": {
                    "2020": 3200,
                    "2021": 3150,
                    "2022": 3050,
                    "2023": 2920
                }
            }
        }
        
        # Key players by tech domain
        self.key_players = {
            "general": [
                {"name": "Roche", "patent_count": 4250, "technology_focus": "antibodies and diagnostics", "filing_growth": "stable"},
                {"name": "Novartis", "patent_count": 3950, "technology_focus": "small molecules and cell therapies", "filing_growth": "increasing"},
                {"name": "Pfizer", "patent_count": 3680, "technology_focus": "vaccines and small molecules", "filing_growth": "stable"},
                {"name": "Merck", "patent_count": 3550, "technology_focus": "small molecules and biologics", "filing_growth": "stable"},
                {"name": "Johnson & Johnson", "patent_count": 3300, "technology_focus": "biologics and medical devices", "filing_growth": "increasing"}
            ],
            "crispr": [
                {"name": "Broad Institute", "patent_count": 235, "technology_focus": "fundamental CRISPR mechanisms", "filing_growth": "stable"},
                {"name": "University of California", "patent_count": 180, "technology_focus": "CRISPR applications and variations", "filing_growth": "stable"},
                {"name": "CRISPR Therapeutics", "patent_count": 145, "technology_focus": "therapeutic applications", "filing_growth": "increasing"},
                {"name": "Editas Medicine", "patent_count": 130, "technology_focus": "ocular and genetic diseases", "filing_growth": "increasing"},
                {"name": "Intellia Therapeutics", "patent_count": 120, "technology_focus": "in vivo applications", "filing_growth": "increasing"}
            ],
            "antibodies": [
                {"name": "Regeneron", "patent_count": 580, "technology_focus": "human antibody platforms", "filing_growth": "stable"},
                {"name": "Genentech", "patent_count": 520, "technology_focus": "therapeutic antibodies", "filing_growth": "stable"},
                {"name": "AbbVie", "patent_count": 470, "technology_focus": "autoimmune disease antibodies", "filing_growth": "stable"},
                {"name": "Amgen", "patent_count": 430, "technology_focus": "bispecific platforms", "filing_growth": "increasing"},
                {"name": "Sanofi", "patent_count": 380, "technology_focus": "immunological disorders", "filing_growth": "increasing"}
            ]
        }
        
        # Company data for summaries
        self.company_data = {
            "Pfizer": {"position": "a major player"},
            "Merck": {"position": "a significant innovator"},
            "Novartis": {"position": "highly active"},
            "Roche": {"position": "a dominant force"},
            "AstraZeneca": {"position": "increasingly active"},
            "Regeneron": {"position": "a leading innovator"},
            "Vertex": {"position": "focused but influential"}
        }
        
        # Blocking patents by tech domain
        self.blocking_patents = {
            "general": [
                {
                    "id": "US10123456B2",
                    "owner": "Pharma Co.",
                    "title": "Biomarker detection methods",
                    "risk_level": 6,
                    "markets": ["US", "EU", "CN"],
                    "description": "Methods for detecting biomarkers in patient samples"
                },
                {
                    "id": "EP3234567B1",
                    "owner": "BioTech Inc.",
                    "title": "Modified cells for therapy",
                    "risk_level": 7,
                    "markets": ["EU", "JP"],
                    "description": "Modified immune cells with enhanced therapeutic properties"
                }
            ],
            "crispr": [
                {
                    "id": "US9876543B2",
                    "owner": "Broad Institute",
                    "title": "CRISPR-Cas systems for genome editing",
                    "risk_level": 9,
                    "markets": ["US", "EU", "CN", "JP"],
                    "description": "Fundamental CRISPR-Cas9 gene editing systems and methods"
                },
                {
                    "id": "US10765432B2",
                    "owner": "University of California",
                    "title": "CRISPR-Cas9 systems and methods",
                    "risk_level": 8,
                    "markets": ["US", "EU"],
                    "description": "CRISPR-Cas9 gene editing in eukaryotic cells"
                },
                {
                    "id": "EP3345678B1",
                    "owner": "CRISPR Therapeutics",
                    "title": "Delivery of CRISPR-Cas systems",
                    "risk_level": 6,
                    "markets": ["EU", "US", "CN", "JP"],
                    "description": "Methods for delivering CRISPR components to target cells"
                }
            ],
            "antibodies": [
                {
                    "id": "US10543210B2",
                    "owner": "Regeneron",
                    "title": "Human antibody production methods",
                    "risk_level": 8,
                    "markets": ["US", "EU", "CN", "JP"],
                    "description": "Methods for producing fully human antibodies"
                },
                {
                    "id": "US10876543B2",
                    "owner": "AbbVie",
                    "title": "Anti-TNF alpha antibodies",
                    "risk_level": 7,
                    "markets": ["US", "EU"],
                    "description": "Antibodies that bind TNF-alpha for treating autoimmune diseases"
                }
            ]
        }
        
        # Patent expirations by tech domain
        self.expirations = {
            "general": {
                "expiring_soon": [
                    {
                        "id": "US7654321B2",
                        "owner": "Pharma Inc.",
                        "expiry_date": "2026-05-15",
                        "markets": ["US", "EU", "CN"]
                    },
                    {
                        "id": "EP1234567B1",
                        "owner": "BioGenetics",
                        "expiry_date": "2025-11-30",
                        "markets": ["EU", "US"]
                    }
                ],
                "long_term_outlook": "Several foundational biotech patents are set to expire over the next 3-5 years, potentially opening opportunities for biosimilar and generic competition. Companies should evaluate their product lifecycle strategies accordingly."
            },
            "antibodies": {
                "expiring_soon": [
                    {
                        "id": "US7123456B2",
                        "owner": "Genentech",
                        "expiry_date": "2026-08-22",
                        "markets": ["US", "EU"]
                    },
                    {
                        "id": "EP1654321B1",
                        "owner": "AbbVie",
                        "expiry_date": "2025-04-10",
                        "markets": ["EU", "US", "JP"]
                    }
                ],
                "long_term_outlook": "Key antibody platform patents are approaching expiration, which may reduce barriers to entry for new competitors. However, method of treatment patents may provide extended protection for specific indications."
            }
        }
        
        # Key IP trends across biotech
        self.key_trends = [
            {
                "name": "AI-Driven IP Generation",
                "description": "Increasing use of AI and machine learning tools for identifying patentable innovations and optimizing claim language.",
                "impact": "Creating more sophisticated patent strategies and potentially increasing litigation complexity."
            },
            {
                "name": "Cross-Disciplinary Convergence",
                "description": "Growing intersection of digital technologies, biotech, and medical devices creating new IP challenges.",
                "impact": "Requiring broader IP expertise and multi-disciplinary protection strategies."
            },
            {
                "name": "Collaborative Innovation Models",
                "description": "Shift toward platform licensing, research collaborations, and open innovation in pre-competitive areas.",
                "impact": "Changing how IP is valued, shared, and commercialized in the industry."
            },
            {
                "name": "Global Patent Harmonization Efforts",
                "description": "Continued progress toward harmonizing patent laws and procedures across major jurisdictions.",
                "impact": "Potentially simplifying global protection strategies and reducing costs."
            },
            {
                "name": "Evolving Subject Matter Eligibility",
                "description": "Ongoing developments in patent eligibility for diagnostic methods, naturally-derived products, and AI innovations.",
                "impact": "Creating uncertainty but also opportunities for novel claiming strategies."
            }
        ]
