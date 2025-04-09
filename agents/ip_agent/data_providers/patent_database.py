# agents/ip_agent/data_providers/patent_database.py

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from agents.ip_agent.utils.cache_manager import CacheManager

class PatentDatabaseProvider:
    """
    Provider for patent database access with cached results.
    Provides filing strategies, competitive positioning, and strategic options.
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
    
    def get_filing_strategy(self, tech_domain: Optional[str], company_stage: str) -> Dict[str, Any]:
        """
        Get filing strategy recommendations based on technology domain and company stage.
        
        Args:
            tech_domain: Technology domain (e.g., "crispr", "antibodies")
            company_stage: Company stage (e.g., "early", "growth", "mature")
            
        Returns:
            Filing strategy recommendations
        """
        # Try to get from cache first
        cache_key = f"filing_strategy:{tech_domain or 'general'}:{company_stage}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, generate strategy (from default data for now)
        if tech_domain and tech_domain in self.filing_strategies:
            strategy = self.filing_strategies[tech_domain].get(company_stage)
            if strategy:
                self.cache_manager.set(cache_key, strategy)
                return strategy
        
        # Fall back to general strategy if specific one not found
        general_strategy = self.filing_strategies.get("general", {}).get(company_stage, {})
        self.cache_manager.set(cache_key, general_strategy)
        
        return general_strategy
    
    def get_company_ip_position(self, company_name: str, tech_domain: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Get competitive positioning information for a company.
        
        Args:
            company_name: Name of the company
            tech_domain: Technology domain (optional)
            
        Returns:
            Competitive positioning information or None if not found
        """
        # Try to get from cache first
        cache_key = f"company_position:{company_name}:{tech_domain or 'general'}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, get from default data
        position_key = f"{company_name}:{tech_domain}" if tech_domain else company_name
        
        if position_key in self.competitive_positions:
            position = self.competitive_positions[position_key]
            self.cache_manager.set(cache_key, position)
            return position
            
        # Try just company name as fallback
        if company_name in self.competitive_positions:
            position = self.competitive_positions[company_name]
            self.cache_manager.set(cache_key, position)
            return position
            
        return None
    
    def get_strategic_options(self, tech_domain: Optional[str], stage: str, company: Optional[str]) -> Dict[str, Any]:
        """
        Get strategic IP options based on technology domain and company stage.
        
        Args:
            tech_domain: Technology domain
            stage: Company stage
            company: Company name (optional)
            
        Returns:
            Strategic options
        """
        # Try to get from cache first
        cache_key = f"strategic_options:{tech_domain or 'general'}:{stage}:{company or 'none'}"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, generate options
        # Use tech-specific options if available
        if tech_domain and tech_domain in self.strategic_options:
            domain_options = self.strategic_options[tech_domain]
            if stage in domain_options:
                options = domain_options[stage]
                self.cache_manager.set(cache_key, options)
                return options
        
        # Fall back to general options
        general_options = self.strategic_options.get("general", {}).get(stage, {})
        self.cache_manager.set(cache_key, general_options)
        
        return general_options
    
    def get_general_ip_overview(self) -> Dict[str, Any]:
        """
        Get general IP overview information.
        
        Returns:
            General IP overview data
        """
        # Try to get from cache first
        cache_key = "general_ip_overview"
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, return default data
        self.cache_manager.set(cache_key, self.general_overview)
        
        return self.general_overview
    
    def _load_default_data(self) -> None:
        """Load default data if real API is not available."""
        # Filing strategies by tech domain and company stage
        self.filing_strategies = {
            "general": {
                "early": {
                    "key_areas": [
                        {"name": "Core technology platform", "rationale": "Foundational protection for key innovations"},
                        {"name": "Initial applications", "rationale": "Practical use-cases demonstrating utility"}
                    ],
                    "approach": "For early-stage companies, prioritize a focused patent strategy that protects core technology while conserving resources. Start with provisional applications for initial protection, followed by targeted PCT filings for key innovations.",
                    "jurisdictions": [
                        {"name": "United States", "reason": "Largest market with established legal framework"},
                        {"name": "Europe (EPO)", "reason": "Unified application covering multiple markets"}
                    ]
                },
                "growth": {
                    "key_areas": [
                        {"name": "Platform extensions", "rationale": "Expanding scope of core IP"},
                        {"name": "Application-specific innovations", "rationale": "Tailored solutions for market needs"},
                        {"name": "Manufacturing methods", "rationale": "Process protection for commercial scale-up"}
                    ],
                    "approach": "For growth-stage companies, expand patent coverage to support market expansion and investment activities. Develop a portfolio of both broad platform patents and specific application patents to create a multi-layered protection strategy.",
                    "jurisdictions": [
                        {"name": "United States", "reason": "Primary market with robust enforcement"},
                        {"name": "Europe (EPO)", "reason": "Unified application for European markets"},
                        {"name": "China", "reason": "Critical manufacturing and growing market"},
                        {"name": "Japan", "reason": "Significant biotech market and innovation hub"},
                        {"name": "Canada", "reason": "Strategic North American market"}
                    ]
                },
                "mature": {
                    "key_areas": [
                        {"name": "Next-generation platforms", "rationale": "Future revenue streams"},
                        {"name": "Lifecycle management", "rationale": "Extending protection for commercial products"},
                        {"name": "Combinatorial applications", "rationale": "New uses for existing IP"}
                    ],
                    "approach": "For mature companies, implement sophisticated IP lifecycle management strategies. Balance protection of commercial products with investment in next-generation technologies. Consider strategic portfolios of patents, trade secrets, and regulatory exclusivities.",
                    "jurisdictions": [
                        {"name": "United States", "reason": "Primary market with complex litigation landscape"},
                        {"name": "Europe (EPO)", "reason": "Unified application with SPC opportunities"},
                        {"name": "China", "reason": "Critical manufacturing and growing market"},
                        {"name": "Japan", "reason": "Significant biotech market with strong IP respect"},
                        {"name": "Brazil", "reason": "Emerging market with growing importance"},
                        {"name": "India", "reason": "Key manufacturing hub with evolving IP landscape"},
                        {"name": "Australia", "reason": "Strategic market with favorable IP system"}
                    ]
                }
            },
            "crispr": {
                "early": {
                    "key_areas": [
                        {"name": "Delivery systems", "rationale": "Differentiated approaches to CRISPR delivery"},
                        {"name": "Guide RNA designs", "rationale": "Optimized targeting with reduced off-target effects"},
                        {"name": "Specific applications", "rationale": "Disease-specific implementations"}
                    ],
                    "approach": "For early-stage CRISPR companies, focus on novel delivery methods and specific applications rather than the core CRISPR-Cas system which faces significant existing IP barriers. Consider strategic licensing of foundational CRISPR patents.",
                    "jurisdictions": [
                        {"name": "United States", "reason": "Primary market with complex CRISPR patent landscape"},
                        {"name": "Europe (EPO)", "reason": "Different CRISPR patent holdings than US"}
                    ]
                }
            },
            "antibodies": {
                "early": {
                    "key_areas": [
                        {"name": "Novel targets", "rationale": "Unique disease targets with clinical potential"},
                        {"name": "Antibody engineering", "rationale": "Structural modifications for improved function"},
                        {"name": "Screening methodology", "rationale": "Proprietary approaches to antibody discovery"}
                    ],
                    "approach": "For early-stage antibody companies, prioritize patents on novel targets and unique antibody engineering approaches. Consider complementary protection through biological deposits and sequence listings.",
                    "jurisdictions": [
                        {"name": "United States", "reason": "Primary market with evolving antibody case law"},
                        {"name": "Europe (EPO)", "reason": "Different antibody patentability standards than US"}
                    ]
                }
            }
        }
        
        # Competitive positions by company and tech domain
        self.competitive_positions = {
            "Regeneron": {
                "strength": "very strong",
                "strengths": [
                    "Industry-leading antibody platform patents",
                    "Strong position in ophthalmology applications",
                    "Growing gene therapy patent portfolio"
                ],
                "gaps": [
                    "Limited coverage in some emerging therapeutic areas",
                    "Some key patents approaching expiration"
                ]
            },
            "Regeneron:antibodies": {
                "strength": "dominant",
                "strengths": [
                    "Comprehensive VelocImmune® platform protection",
                    "Broad epitope coverage for key targets",
                    "Strong position in bispecific antibody formats"
                ],
                "gaps": [
                    "Some competition in next-generation antibody formats"
                ]
            },
            "CRISPR Therapeutics": {
                "strength": "strong",
                "strengths": [
                    "Key licensed foundational CRISPR-Cas9 patents",
                    "Growing portfolio of delivery technologies",
                    "Strong position in ex vivo cell therapy applications"
                ],
                "gaps": [
                    "Competitive landscape in core CRISPR patent space",
                    "Limited coverage for newer CRISPR systems",
                    "Potential freedom-to-operate constraints in some applications"
                ]
            }
        }
        
        # Strategic options by tech domain and company stage
        self.strategic_options = {
            "general": {
                "early": {
                    "organic": [
                        {"name": "Platform fundamentals", "impact": "High"},
                        {"name": "Initial application specific patents", "impact": "Medium"}
                    ],
                    "partnerships": [
                        {"name": "Academic institutions", "complementarity": "Access to foundational research"},
                        {"name": "Platform technology companies", "complementarity": "Complementary technologies"}
                    ]
                },
                "growth": {
                    "organic": [
                        {"name": "Platform extensions", "impact": "High"},
                        {"name": "Application diversification", "impact": "Medium"},
                        {"name": "Manufacturing process protection", "impact": "Medium"}
                    ],
                    "partnerships": [
                        {"name": "Pharma companies", "complementarity": "Clinical development expertise"},
                        {"name": "Diagnostic companies", "complementarity": "Companion diagnostic opportunities"}
                    ],
                    "acquisitions": [
                        {"name": "Small specialty biotechs", "rationale": "Complementary technology acquisition"},
                        {"name": "IP portfolios from discontinued programs", "rationale": "Strategic blocking positions"}
                    ]
                },
                "mature": {
                    "organic": [
                        {"name": "Next-generation platform development", "impact": "High"},
                        {"name": "Lifecycle management innovations", "impact": "High"},
                        {"name": "Manufacturing optimization", "impact": "Medium"}
                    ],
                    "partnerships": [
                        {"name": "Digital health companies", "complementarity": "Data-driven innovation"},
                        {"name": "AI drug discovery platforms", "complementarity": "Accelerated innovation"}
                    ],
                    "acquisitions": [
                        {"name": "Mid-size biotechs", "rationale": "Pipeline and technology expansion"},
                        {"name": "Platform technology companies", "rationale": "Next-generation capabilities"}
                    ]
                }
            },
            "crispr": {
                "early": {
                    "organic": [
                        {"name": "Novel delivery technologies", "impact": "Very High"},
                        {"name": "Guide RNA optimization", "impact": "High"},
                        {"name": "Specific disease applications", "impact": "Medium"}
                    ],
                    "partnerships": [
                        {"name": "Foundational CRISPR patent holders", "complementarity": "Freedom to operate"},
                        {"name": "Delivery technology companies", "complementarity": "Enhanced delivery capabilities"}
                    ]
                }
            }
        }
        
        # General IP overview
        self.general_overview = {
            "executive_summary": "The biotech intellectual property landscape continues to evolve through technological advancement, regulatory developments, and shifting business models. Key value is increasingly created through strategic patent portfolios complemented by regulatory exclusivities, trade secrets, and collaborative innovation models. Companies must balance aggressive protection with freedom to operate considerations.",
            "filing_overview": "Biotech patent filings continue to grow globally, with particular concentration in therapeutic applications. The USPTO, EPO, and CNIPA remain the dominant patent offices for biotech innovation, with an increasing number of filings also seen in emerging markets like Brazil and India. Digital biotech innovations are seeing the fastest growth in patent activity.",
            "enforcement_landscape": "The biotech IP enforcement landscape remains complex, with significant regional variations. US litigation continues to focus on biologics and biosimilars, while European enforcement often centers on supplementary protection certificates (SPCs) and regulatory data protection. China has strengthened IP enforcement mechanisms, creating new strategic opportunities.",
            "key_challenges": "Biotech innovators face several persistent IP challenges:\n\n- Increasing scrutiny of patent subject matter eligibility\n- Growing complexity in global patent strategy coordination\n- Balancing open innovation with proprietary protection\n- Managing rising costs of global patent portfolios\n- Addressing disclosure requirements for bioinformatics and AI innovations",
            "strategic_considerations": "For biotech organizations navigating the current IP landscape, consider these key strategies:\n\n1. Implement adaptive IP strategies responsive to evolving legal doctrines\n2. Utilize complementary protection mechanisms beyond patents\n3. Develop territory-specific approaches for global IP portfolios\n4. Consider defensive publication for non-core innovations\n5. Explore collaborative IP models in pre-competitive research areas"
        }
