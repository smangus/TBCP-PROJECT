# agents/ip_agent/data_providers/legal_developments.py

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from agents.ip_agent.utils.cache_manager import CacheManager

class LegalDevelopmentsProvider:
    """
    Provider for IP legal developments and litigation analysis with cached results.
    Handles legal changes, court cases, and regulatory updates.
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
    
    def get_developments(self, tech_domain: Optional[str], region: str) -> List[Dict[str, Any]]:
        """
        Get legal developments for a technology domain and region.
        
        Args:
            tech_domain: Technology domain (e.g., "crispr", "antibodies")
            region: Region (e.g., "us", "eu", "global")
            
        Returns:
            List of legal developments
        """
        # Try to get from cache first
        cache_key = f"developments:{tech_domain or 'general'}:{region}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get development data
        developments = []
        
        # First check tech domain specific developments
        if tech_domain and tech_domain in self.developments:
            tech_developments = self.developments[tech_domain]
            for dev in tech_developments:
                if region == dev.get("region") or region == "global" or dev.get("region") == "global":
                    developments.append(dev)
        
        # Then add general developments for the region
        if "general" in self.developments:
            general_developments = self.developments["general"]
            for dev in general_developments:
                if region == dev.get("region") or region == "global" or dev.get("region") == "global":
                    # Check if similar development already added
                    if not any(d.get("title") == dev.get("title") for d in developments):
                        developments.append(dev)
        
        # Sort by date (most recent first)
        developments.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Cache results
        self.cache_manager.set(cache_key, developments)
        
        return developments
    
    def get_court_cases(self, tech_domain: Optional[str], region: str) -> List[Dict[str, Any]]:
        """
        Get recent court cases for a technology domain and region.
        
        Args:
            tech_domain: Technology domain
            region: Region
            
        Returns:
            List of court cases
        """
        # Try to get from cache first
        cache_key = f"court_cases:{tech_domain or 'general'}:{region}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get court case data
        cases = []
        
        # First check tech domain specific cases
        if tech_domain and tech_domain in self.court_cases:
            tech_cases = self.court_cases[tech_domain]
            for case in tech_cases:
                if region == case.get("region") or region == "global" or case.get("region") == "global":
                    cases.append(case)
        
        # Then add general cases for the region
        if "general" in self.court_cases:
            general_cases = self.court_cases["general"]
            for case in general_cases:
                if region == case.get("region") or region == "global" or case.get("region") == "global":
                    # Check if similar case already added
                    if not any(c.get("name") == case.get("name") for c in cases):
                        cases.append(case)
        
        # Sort by date (most recent first)
        cases.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Cache results
        self.cache_manager.set(cache_key, cases)
        
        return cases
    
    def get_regulatory_changes(self, tech_domain: Optional[str], region: str) -> List[Dict[str, Any]]:
        """
        Get regulatory changes for a technology domain and region.
        
        Args:
            tech_domain: Technology domain
            region: Region
            
        Returns:
            List of regulatory changes
        """
        # Try to get from cache first
        cache_key = f"regulatory:{tech_domain or 'general'}:{region}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get regulatory data
        regulations = []
        
        # First check tech domain specific regulations
        if tech_domain and tech_domain in self.regulatory_changes:
            tech_regulations = self.regulatory_changes[tech_domain]
            for reg in tech_regulations:
                if region == reg.get("region") or region == "global" or reg.get("region") == "global":
                    regulations.append(reg)
        
        # Then add general regulations for the region
        if "general" in self.regulatory_changes:
            general_regulations = self.regulatory_changes["general"]
            for reg in general_regulations:
                if region == reg.get("region") or region == "global" or reg.get("region") == "global":
                    # Check if similar regulation already added
                    if not any(r.get("title") == reg.get("title") for r in regulations):
                        regulations.append(reg)
        
        # Sort by date (most recent first)
        regulations.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Cache results
        self.cache_manager.set(cache_key, regulations)
        
        return regulations
    
    def get_litigation_risk(self, tech_domain: Optional[str], target_markets: List[str]) -> Dict[str, Any]:
        """
        Get litigation risk assessment for a technology domain and markets.
        
        Args:
            tech_domain: Technology domain
            target_markets: List of target markets
            
        Returns:
            Litigation risk assessment
        """
        # Try to get from cache first
        cache_key = f"litigation_risk:{tech_domain or 'general'}:{'-'.join(target_markets)}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, generate risk assessment
        if tech_domain and tech_domain in self.litigation_risks:
            risk = self.litigation_risks[tech_domain].copy()
        else:
            risk = self.litigation_risks.get("general", {}).copy()
        
        # Filter active cases by market
        if "active_cases" in risk:
            filtered_cases = [
                case for case in risk["active_cases"]
                if any(market in case.get("markets", []) for market in target_markets)
            ]
            risk["active_cases"] = filtered_cases
        
        # Cache results
        self.cache_manager.set(cache_key, risk)
        
        return risk
    
    def _load_default_data(self) -> None:
        """Load default data if real API is not available."""
        # Legal developments by tech domain
        self.developments = {
            "general": [
                {
                    "date": "2023-12-10",
                    "title": "USPTO releases new examination guidelines",
                    "impact": "Streamlined subject matter eligibility determination for biotech inventions",
                    "region": "us",
                    "impact_level": "medium"
                },
                {
                    "date": "2023-10-05",
                    "title": "EPO revises criteria for inventive step assessment",
                    "impact": "Higher bar for demonstrating non-obviousness for biotech inventions",
                    "region": "eu",
                    "impact_level": "high"
                },
                {
                    "date": "2023-09-22",
                    "title": "China introduces new Patent Law amendments",
                    "impact": "Strengthened patent enforcement mechanisms and increased damages",
                    "region": "cn",
                    "impact_level": "medium"
                }
            ],
            "crispr": [
                {
                    "date": "2023-11-15",
                    "title": "USPTO issues new guidance on CRISPR patent examination",
                    "impact": "Clarified criteria for enablement and written description requirements",
                    "region": "us",
                    "impact_level": "high"
                }
            ],
            "antibodies": [
                {
                    "date": "2023-08-20",
                    "title": "EPO releases new guidelines for antibody patenting",
                    "impact": "More stringent requirements for functional antibody claims",
                    "region": "eu",
                    "impact_level": "high"
                }
            ]
        }
        
        # Court cases by tech domain
        self.court_cases = {
            "general": [
                {
                    "name": "BioTech v. PharmaGenics",
                    "court": "US Federal Circuit",
                    "date": "2023-11-05",
                    "ruling": "Method claims for personalized medicine found patent-eligible under Section 101",
                    "impact": "Positive development for diagnostic method patents in the US",
                    "region": "us",
                    "precedent_setting": True
                },
                {
                    "name": "GeneRx v. MediPharm",
                    "court": "CJEU",
                    "date": "2023-09-14",
                    "ruling": "SPC term calculation clarified for combination products",
                    "impact": "May extend protection period for certain combination therapies",
                    "region": "eu",
                    "precedent_setting": False
                }
            ],
            "crispr": [
                {
                    "name": "CRISPRTx v. GenEdit",
                    "court": "US District Court",
                    "date": "2023-10-22",
                    "ruling": "Preliminary injunction granted for alleged CRISPR delivery system infringement",
                    "impact": "Indicates strong enforcement potential for delivery technologies",
                    "region": "us",
                    "precedent_setting": False
                },
                {
                    "name": "Broad Institute v. UC Berkeley",
                    "court": "USPTO PTAB",
                    "date": "2023-07-15",
                    "ruling": "Interference proceeding resolved in favor of Broad for specific CRISPR applications",
                    "impact": "Further clarifies ownership boundaries in CRISPR space",
                    "region": "us",
                    "precedent_setting": True
                }
            ],
            "antibodies": [
                {
                    "name": "AbCo v. ImmunoGen",
                    "court": "US Federal Circuit",
                    "date": "2023-08-30",
                    "ruling": "Functional antibody claims with minimal structural characterization found invalid",
                    "impact": "Sets higher enablement bar for broad antibody claims",
                    "region": "us",
                    "precedent_setting": True
                }
            ]
        }
        
        # Regulatory changes by tech domain
        self.regulatory_changes = {
            "general": [
                {
                    "title": "FDA Modernizes Regulatory Framework",
                    "authority": "FDA",
                    "date": "2023-11-10",
                    "status": "Implemented",
                    "impact": "Streamlined approval processes for certain biologic products",
                    "region": "us",
                    "impact_level": "medium"
                },
                {
                    "title": "EMA Revises Clinical Trial Requirements",
                    "authority": "EMA",
                    "date": "2023-09-05",
                    "status": "Public consultation phase",
                    "impact": "Expected to reduce clinical data requirements for certain follow-on biologics",
                    "region": "eu",
                    "impact_level": "medium"
                }
            ],
            "crispr": [
                {
                    "title": "FDA Issues Draft Guidance for CRISPR Therapeutics",
                    "authority": "FDA",
                    "date": "2023-10-15",
                    "status": "Draft released",
                    "impact": "Provides clearer pathway for CRISPR-based therapeutic approvals",
                    "region": "us",
                    "impact_level": "high"
                }
            ],
            "antibodies": [
                {
                    "title": "NMPA Expedited Review for Novel Antibody Formats",
                    "authority": "China NMPA",
                    "date": "2023-07-20",
                    "status": "Implemented",
                    "impact": "Faster approval pathway for bispecific and other novel antibody formats",
                    "region": "cn",
                    "impact_level": "medium"
                }
            ]
        }
        
        # Litigation risks by tech domain
        self.litigation_risks = {
            "general": {
                "overall_risk": "moderate",
                "active_cases": [
                    {
                        "plaintiff": "BioTech Inc.",
                        "defendant": "PharmaGenics",
                        "issue": "Diagnostic method patent infringement",
                        "markets": ["US", "EU"]
                    },
                    {
                        "plaintiff": "GeneRx",
                        "defendant": "MediPharm",
                        "issue": "Supplementary Protection Certificate dispute",
                        "markets": ["EU"]
                    }
                ],
                "trends": "Biotech IP litigation remains active but relatively stable, with increasing focus on biosimilars and diagnostic methods. Patent enforcement strategies vary significantly by jurisdiction."
            },
            "crispr": {
                "overall_risk": "high",
                "active_cases": [
                    {
                        "plaintiff": "CRISPRTx",
                        "defendant": "GenEdit",
                        "issue": "CRISPR delivery system patent infringement",
                        "markets": ["US"]
                    },
                    {
                        "plaintiff": "Broad Institute",
                        "defendant": "UC Berkeley",
                        "issue": "CRISPR-Cas9 patent rights",
                        "markets": ["US", "EU", "CN", "JP"]
                    },
                    {
                        "plaintiff": "CRISPR Therapeutics",
                        "defendant": "Editas Medicine",
                        "issue": "Guide RNA design patent dispute",
                        "markets": ["US", "EU"]
                    }
                ],
                "trends": "CRISPR litigation remains particularly active with multiple ongoing disputes over foundational patents. The focus is shifting toward delivery systems and specific therapeutic applications as the technology matures."
            },
            "antibodies": {
                "overall_risk": "elevated",
                "active_cases": [
                    {
                        "plaintiff": "AbCo",
                        "defendant": "ImmunoGen",
                        "issue": "Antibody epitope binding patent dispute",
                        "markets": ["US", "EU"]
                    },
                    {
                        "plaintiff": "BioMab",
                        "defendant": "AntibodyTx",
                        "issue": "Humanization technology patent infringement",
                        "markets": ["US", "JP"]
                    }
                ],
                "trends": "Antibody patent litigation centers on epitope coverage, humanization technologies, and novel formats. Recent decisions have raised the bar for functional claiming, potentially reducing litigation risk in some areas but increasing it in others."
            }
        }
