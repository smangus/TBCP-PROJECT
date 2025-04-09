# agents/market_agent/utils/response_formatter.py

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

def format_market_analysis(
    analysis_type: str,
    **kwargs
) -> str:
    """
    Format market analysis response based on analysis type.
    
    Args:
        analysis_type: Type of analysis ("competitive_landscape", "market_sizing", etc.)
        **kwargs: Type-specific data for formatting
        
    Returns:
        Formatted market analysis text
    """
    if analysis_type == "competitive_landscape":
        return _format_competitive_landscape(**kwargs)
    elif analysis_type == "market_sizing":
        return _format_market_sizing(**kwargs)
    elif analysis_type == "trend_analysis":
        return _format_trend_analysis(**kwargs)
    elif analysis_type == "strategic_recommendations":
        return _format_strategic_recommendations(**kwargs)
    else:
        return _format_general_overview(**kwargs)

def _format_competitive_landscape(
    therapeutic_area: Optional[str] = None,
    landscape_data: Optional[Dict[str, Any]] = None,
    news_data: Optional[List[Dict[str, Any]]] = None,
    market_share: Optional[Dict[str, Any]] = None,
    companies: Optional[List[str]] = None,
    technologies: Optional[List[str]] = None
) -> str:
    """Format competitive landscape analysis."""
    if not landscape_data:
        return "Insufficient data available for competitive landscape analysis."
    
    # Format the therapeutic area section
    if therapeutic_area:
        area_name = therapeutic_area.replace("_", " ").title()
        intro = f"# Competitive Landscape Analysis: {area_name}"
        if technologies and len(technologies) > 0:
            tech_list = ", ".join([t.title() for t in technologies])
            intro += f" - {tech_list} Technologies"
    else:
        if technologies and len(technologies) > 0:
            tech_list = ", ".join([t.title() for t in technologies])
            intro = f"# Competitive Landscape Analysis: {tech_list} Technologies"
        else:
            intro = "# Competitive Landscape Analysis"

    # Format key players section
    players_section = "## Key Market Players\n\n"
    if "key_players" in landscape_data and landscape_data["key_players"]:
        for company, details in landscape_data["key_players"].items():
            players_section += f"### {company}\n"
            
            if "description" in details:
                players_section += f"{details['description']}\n\n"
            
            if "market_position" in details:
                players_section += f"**Market Position**: {details['market_position']}\n\n"
            
            if "key_products" in details and details["key_products"]:
                players_section += "**Key Products/Technologies**:\n"
                for product in details["key_products"]:
                    players_section += f"- {product}\n"
                players_section += "\n"
            
            if "recent_developments" in details and details["recent_developments"]:
                players_section += "**Recent Developments**:\n"
                for dev in details["recent_developments"]:
                    players_section += f"- {dev}\n"
                players_section += "\n"
    else:
        players_section += "Data on key players is currently limited.\n\n"
    
    # Format market share section
    share_section = "## Market Share Analysis\n\n"
    if market_share and "share_data" in market_share:
        share_section += market_share.get("summary", "Market share data available for major players in this sector.") + "\n\n"
        
        if "chart_description" in market_share:
            share_section += market_share["chart_description"] + "\n\n"
    else:
        share_section += "Detailed market share data is not available for this segment.\n\n"
    
    # Format recent news section
    news_section = "## Recent Industry Developments\n\n"
    if news_data and len(news_data) > 0:
        for news_item in news_data[:5]:  # Limit to 5 news items
            date = news_item.get("date", "Recent")
            title = news_item.get("title", "Industry Development")
            summary = news_item.get("summary", "")
            
            news_section += f"### {date}: {title}\n"
            news_section += f"{summary}\n\n"
    else:
        news_section += "No recent news data is available for this segment.\n\n"
    
    # Format competitive dynamics section
    dynamics_section = "## Competitive Dynamics\n\n"
    if "competitive_dynamics" in landscape_data:
        dynamics = landscape_data["competitive_dynamics"]
        
        if "overview" in dynamics:
            dynamics_section += dynamics["overview"] + "\n\n"
        
        if "strengths_weaknesses" in dynamics:
            dynamics_section += "### Comparative Strengths & Weaknesses\n\n"
            for company, analysis in dynamics["strengths_weaknesses"].items():
                dynamics_section += f"**{company}**:\n"
                if "strengths" in analysis:
                    dynamics_section += "- Strengths: " + ", ".join(analysis["strengths"]) + "\n"
                if "weaknesses" in analysis:
                    dynamics_section += "- Weaknesses: " + ", ".join(analysis["weaknesses"]) + "\n"
                dynamics_section += "\n"
    
    # Combine all sections
    full_analysis = f"{intro}\n\n"
    
    # Add a market summary if available
    if "market_summary" in landscape_data:
        full_analysis += f"{landscape_data['market_summary']}\n\n"
    
    # Add the rest of the sections
    full_analysis += f"{players_section}\n{share_section}\n{dynamics_section}\n{news_section}"
    
    # Add a conclusion if available
    if "conclusion" in landscape_data:
        full_analysis += f"## Conclusion\n\n{landscape_data['conclusion']}\n"
    
    return full_analysis

def _format_market_sizing(
    therapeutic_area: Optional[str] = None,
    geography: str = "global",
    timeframe: str = "5-year",
    market_size: Optional[Dict[str, Any]] = None,
    growth_factors: Optional[Dict[str, Any]] = None,
    regional_breakdown: Optional[Dict[str, Any]] = None
) -> str:
    """Format market sizing analysis."""
    if not market_size:
        return "Insufficient data available for market sizing analysis."
    
    # Format the title based on available parameters
    if therapeutic_area:
        area_name = therapeutic_area.replace("_", " ").title()
        title = f"# Market Size Analysis: {area_name}"
    else:
        title = "# Biotech Market Size Analysis"
    
    # Add geography and timeframe to title
    geo_display = geography.title()
    if geography != "global":
        title += f" - {geo_display} Market"
    
    time_display = timeframe.replace("-", " ").title()
    title += f" ({time_display} Outlook)"
    
    # Format market size section
    size_section = "## Market Size & Growth Projections\n\n"
    
    if "current_size" in market_size:
        size_section += f"**Current Market Size**: {market_size['current_size']}\n\n"
    
    if "forecast" in market_size:
        size_section += f"**Forecast Size ({timeframe})**: {market_size['forecast']}\n\n"
    
    if "cagr" in market_size:
        size_section += f"**CAGR**: {market_size['cagr']}\n\n"
    
    if "historical_trend" in market_size and market_size["historical_trend"]:
        size_section += "**Historical Trend**:\n"
        for year, value in market_size["historical_trend"].items():
            size_section += f"- {year}: {value}\n"
        size_section += "\n"
        
    if "forecast_trend" in market_size and market_size["forecast_trend"]:
        size_section += "**Forecast Trend**:\n"
        for year, value in market_size["forecast_trend"].items():
            size_section += f"- {year}: {value}\n"
        size_section += "\n"
    
    if "summary" in market_size:
        size_section += f"{market_size['summary']}\n\n"
    
    # Format growth factors section
    factors_section = "## Market Growth Factors\n\n"
    
    if growth_factors:
        if "drivers" in growth_factors and growth_factors["drivers"]:
            factors_section += "### Growth Drivers\n\n"
            for driver in growth_factors["drivers"]:
                factors_section += f"- {driver}\n"
            factors_section += "\n"
        
        if "restraints" in growth_factors and growth_factors["restraints"]:
            factors_section += "### Market Restraints\n\n"
            for restraint in growth_factors["restraints"]:
                factors_section += f"- {restraint}\n"
            factors_section += "\n"
        
        if "opportunities" in growth_factors and growth_factors["opportunities"]:
            factors_section += "### Market Opportunities\n\n"
            for opportunity in growth_factors["opportunities"]:
                factors_section += f"- {opportunity}\n"
            factors_section += "\n"
    else:
        factors_section += "Detailed growth factor data is currently unavailable.\n\n"
    
    # Format regional breakdown section (if global analysis)
    regions_section = ""
    if geography == "global" and regional_breakdown:
        regions_section = "## Regional Market Breakdown\n\n"
        
        if "summary" in regional_breakdown:
            regions_section += f"{regional_breakdown['summary']}\n\n"
        
        if "regions" in regional_breakdown and regional_breakdown["regions"]:
            for region, data in regional_breakdown["regions"].items():
                regions_section += f"### {region.title()}\n"
                
                if "market_share" in data:
                    regions_section += f"**Market Share**: {data['market_share']}\n\n"
                
                if "market_size" in data:
                    regions_section += f"**Market Size**: {data['market_size']}\n\n"
                
                if "growth_rate" in data:
                    regions_section += f"**Growth Rate**: {data['growth_rate']}\n\n"
                
                if "key_countries" in data and data["key_countries"]:
                    regions_section += "**Key Countries**: " + ", ".join(data["key_countries"]) + "\n\n"
                
                if "highlights" in data:
                    regions_section += f"{data['highlights']}\n\n"
    
    # Combine all sections
    full_analysis = f"{title}\n\n"
    
    # Add an executive summary if available
    if "executive_summary" in market_size:
        full_analysis += f"{market_size['executive_summary']}\n\n"
    
    # Add the rest of the sections
    full_analysis += f"{size_section}\n{factors_section}"
    
    # Add regional breakdown if available
    if regions_section:
        full_analysis += f"\n{regions_section}"
    
    # Add a conclusion if available
    if "conclusion" in market_size:
        full_analysis += f"\n## Conclusion\n\n{market_size['conclusion']}\n"
    
    return full_analysis

def _format_trend_analysis(
    therapeutic_area: Optional[str] = None,
    technology_focus: Optional[str] = None,
    trends: Optional[Dict[str, Any]] = None,
    regulatory_trends: Optional[Dict[str, Any]] = None,
    investment_trends: Optional[Dict[str, Any]] = None
) -> str:
    """Format trend analysis."""
    if not trends:
        return "Insufficient data available for trend analysis."
    
    # Format the title based on available parameters
    if therapeutic_area and technology_focus:
        area_name = therapeutic_area.replace("_", " ").title()
        tech_name = technology_focus.replace("_", " ").title()
        title = f"# Market Trend Analysis: {tech_name} in {area_name}"
    elif therapeutic_area:
        area_name = therapeutic_area.replace("_", " ").title()
        title = f"# Market Trend Analysis: {area_name}"
    elif technology_focus:
        tech_name = technology_focus.replace("_", " ").title()
        title = f"# Market Trend Analysis: {tech_name} Technologies"
    else:
        title = "# Biotech Market Trend Analysis"
    
    # Format key trends section
    trends_section = "## Key Market Trends\n\n"
    
    if "key_trends" in trends and trends["key_trends"]:
        for trend in trends["key_trends"]:
            if "name" in trend:
                trends_section += f"### {trend['name']}\n\n"
            else:
                trends_section += "### Emerging Trend\n\n"
            
            if "description" in trend:
                trends_section += f"{trend['description']}\n\n"
            
            if "impact" in trend:
                trends_section += f"**Impact**: {trend['impact']}\n\n"
            
            if "timeline" in trend:
                trends_section += f"**Timeline**: {trend['timeline']}\n\n"
            
            if "key_companies" in trend and trend["key_companies"]:
                trends_section += "**Key Companies Involved**: " + ", ".join(trend["key_companies"]) + "\n\n"
    else:
        trends_section += "Detailed trend data is currently unavailable.\n\n"
    
    # Format regulatory trends section
    regulatory_section = "## Regulatory Trends\n\n"
    
    if regulatory_trends:
        if "summary" in regulatory_trends:
            regulatory_section += f"{regulatory_trends['summary']}\n\n"
        
        if "key_developments" in regulatory_trends and regulatory_trends["key_developments"]:
            regulatory_section += "### Key Regulatory Developments\n\n"
            for development in regulatory_trends["key_developments"]:
                if "name" in development:
                    regulatory_section += f"**{development['name']}**\n\n"
                
                if "description" in development:
                    regulatory_section += f"{development['description']}\n\n"
                
                if "impact" in development:
                    regulatory_section += f"**Impact**: {development['impact']}\n\n"
                
                if "regions" in development and development["regions"]:
                    regulatory_section += "**Affected Regions**: " + ", ".join(development["regions"]) + "\n\n"
    else:
        regulatory_section += "Detailed regulatory trend data is currently unavailable.\n\n"
    
    # Format investment trends section
    investment_section = "## Investment Trends\n\n"
    
    if investment_trends:
        if "summary" in investment_trends:
            investment_section += f"{investment_trends['summary']}\n\n"
        
        if "total_investment" in investment_trends:
            investment_section += f"**Total Investment (Last 12 Months)**: {investment_trends['total_investment']}\n\n"
        
        if "key_deals" in investment_trends and investment_trends["key_deals"]:
            investment_section += "### Notable Investment Deals\n\n"
            for deal in investment_trends["key_deals"]:
                if "company" in deal and "amount" in deal:
                    investment_section += f"**{deal['company']}**: {deal['amount']}"
                    
                    if "date" in deal:
                        investment_section += f" ({deal['date']})"
                    
                    investment_section += "\n\n"
                    
                    if "description" in deal:
                        investment_section += f"{deal['description']}\n\n"
        
        if "investment_focus" in investment_trends and investment_trends["investment_focus"]:
            investment_section += "### Investment Focus Areas\n\n"
            for area, percentage in investment_trends["investment_focus"].items():
                investment_section += f"- {area}: {percentage}\n"
            investment_section += "\n"
    else:
        investment_section += "Detailed investment trend data is currently unavailable.\n\n"
    
    # Combine all sections
    full_analysis = f"{title}\n\n"
    
    # Add an executive summary if available
    if "executive_summary" in trends:
        full_analysis += f"{trends['executive_summary']}\n\n"
    
    # Add the rest of the sections
    full_analysis += f"{trends_section}\n{investment_section}\n{regulatory_section}"
    
    # Add implications section if available
    if "implications" in trends:
        full_analysis += f"\n## Strategic Implications\n\n{trends['implications']}\n"
    
    # Add a conclusion if available
    if "conclusion" in trends:
        full_analysis += f"\n## Conclusion\n\n{trends['conclusion']}\n"
    
    return full_analysis

def _format_strategic_recommendations(
    therapeutic_area: Optional[str] = None,
    company_focus: Optional[str] = None,
    goal: Optional[str] = None,
    opportunities: Optional[Dict[str, Any]] = None,
    competitive_position: Optional[Dict[str, Any]] = None,
    strategic_options: Optional[Dict[str, Any]] = None
) -> str:
    """Format strategic recommendations."""
    if not opportunities or not strategic_options:
        return "Insufficient data available for strategic recommendations."
    
    # Format the title based on available parameters
    title = "# Strategic Recommendations"
    
    if company_focus:
        title += f" for {company_focus}"
    
    if therapeutic_area:
        area_name = therapeutic_area.replace("_", " ").title()
        title += f": {area_name} Market"
    
    if goal:
        goal_display = goal.replace("_", " ").title()
        title += f" - {goal_display} Strategy"
    
    # Format market opportunity section
    opportunity_section = "## Market Opportunity Analysis\n\n"
    
    if opportunities:
        if "summary" in opportunities:
            opportunity_section += f"{opportunities['summary']}\n\n"
        
        if "key_opportunities" in opportunities and opportunities["key_opportunities"]:
            opportunity_section += "### Key Opportunities\n\n"
            for opportunity in opportunities["key_opportunities"]:
                if "name" in opportunity:
                    opportunity_section += f"**{opportunity['name']}**\n\n"
                
                if "description" in opportunity:
                    opportunity_section += f"{opportunity['description']}\n\n"
                
                if "potential_impact" in opportunity:
                    opportunity_section += f"**Potential Impact**: {opportunity['potential_impact']}\n\n"
                
                if "timeline" in opportunity:
                    opportunity_section += f"**Timeline**: {opportunity['timeline']}\n\n"
    else:
        opportunity_section += "Detailed market opportunity data is currently unavailable.\n\n"
    
    # Format competitive position section if company_focus is specified
    position_section = ""
    if company_focus and competitive_position:
        position_section = f"## Competitive Position: {company_focus}\n\n"
        
        if "overview" in competitive_position:
            position_section += f"{competitive_position['overview']}\n\n"
        
        if "strengths" in competitive_position and competitive_position["strengths"]:
            position_section += "### Strengths\n\n"
            for strength in competitive_position["strengths"]:
                position_section += f"- {strength}\n"
            position_section += "\n"
        
        if "weaknesses" in competitive_position and competitive_position["weaknesses"]:
            position_section += "### Weaknesses\n\n"
            for weakness in competitive_position["weaknesses"]:
                position_section += f"- {weakness}\n"
            position_section += "\n"
        
        if "competitive_advantage" in competitive_position:
            position_section += f"### Competitive Advantage\n\n{competitive_position['competitive_advantage']}\n\n"
    
    # Format strategic options section
    strategy_section = "## Strategic Options\n\n"
    
    if strategic_options:
        if "summary" in strategic_options:
            strategy_section += f"{strategic_options['summary']}\n\n"
        
        if "options" in strategic_options and strategic_options["options"]:
            for option in strategic_options["options"]:
                if "name" in option:
                    strategy_section += f"### {option['name']}\n\n"
                else:
                    strategy_section += "### Strategic Option\n\n"
                
                if "description" in option:
                    strategy_section += f"{option['description']}\n\n"
                
                if "pros" in option and option["pros"]:
                    strategy_section += "**Pros**:\n"
                    for pro in option["pros"]:
                        strategy_section += f"- {pro}\n"
                    strategy_section += "\n"
                
                if "cons" in option and option["cons"]:
                    strategy_section += "**Cons**:\n"
                    for con in option["cons"]:
                        strategy_section += f"- {con}\n"
                    strategy_section += "\n"
                
                if "resource_requirements" in option:
                    strategy_section += f"**Resource Requirements**: {option['resource_requirements']}\n\n"
                
                if "timeline" in option:
                    strategy_section += f"**Implementation Timeline**: {option['timeline']}\n\n"
                
                if "key_metrics" in option and option["key_metrics"]:
                    strategy_section += "**Key Success Metrics**:\n"
                    for metric in option["key_metrics"]:
                        strategy_section += f"- {metric}\n"
                    strategy_section += "\n"
    else:
        strategy_section += "Detailed strategic options data is currently unavailable.\n\n"
    
    # Format recommended approach section
    recommendation_section = "## Recommended Approach\n\n"
    
    if strategic_options and "recommended_approach" in strategic_options:
        recommendation_section += f"{strategic_options['recommended_approach']}\n\n"
        
        if "implementation_steps" in strategic_options and strategic_options["implementation_steps"]:
            recommendation_section += "### Implementation Steps\n\n"
            for i, step in enumerate(strategic_options["implementation_steps"], 1):
                recommendation_section += f"**{i}. {step['name']}**\n\n"
                
                if "description" in step:
                    recommendation_section += f"{step['description']}\n\n"
                
                if "timeline" in step:
                    recommendation_section += f"**Timeline**: {step['timeline']}\n\n"
                
                if "key_stakeholders" in step and step["key_stakeholders"]:
                    recommendation_section += "**Key Stakeholders**: " + ", ".join(step["key_stakeholders"]) + "\n\n"
    else:
        recommendation_section += "A specific recommended approach is not available based on current data.\n\n"
        recommendation_section += "For a tailored strategy, a more detailed analysis considering company-specific factors would be required.\n\n"
    
    # Combine all sections
    full_analysis = f"{title}\n\n"
    
    # Add an executive summary if available
    if strategic_options and "executive_summary" in strategic_options:
        full_analysis += f"{strategic_options['executive_summary']}\n\n"
    
    # Add the rest of the sections
    full_analysis += f"{opportunity_section}\n"
    
    # Add position section if available
    if position_section:
        full_analysis += f"{position_section}\n"
    
    # Add strategy and recommendation sections
    full_analysis += f"{strategy_section}\n{recommendation_section}"
    
    # Add a conclusion if available
    if strategic_options and "conclusion" in strategic_options:
        full_analysis += f"\n## Conclusion\n\n{strategic_options['conclusion']}\n"
    
    return full_analysis

def _format_general_overview(
    market_overview: Optional[Dict[str, Any]] = None,
    key_trends: Optional[Dict[str, Any]] = None
) -> str:
    """Format general market overview."""
    if not market_overview:
        return "Insufficient data available for market overview."
    
    # Format title
    title = "# Biotech Market Overview\n\n"
    
    # Format market overview section
    overview_section = "## Current Market Landscape\n\n"
    
    if "summary" in market_overview:
        overview_section += f"{market_overview['summary']}\n\n"
    
    if "market_size" in market_overview:
        overview_section += f"**Current Market Size**: {market_overview['market_size']}\n\n"
    
    if "growth_rate" in market_overview:
        overview_section += f"**Growth Rate**: {market_overview['growth_rate']}\n\n"
    
    if "key_segments" in market_overview and market_overview["key_segments"]:
        overview_section += "### Key Market Segments\n\n"
        for segment, details in market_overview["key_segments"].items():
            overview_section += f"**{segment}**"
            
            if "market_share" in details:
                overview_section += f" ({details['market_share']} of total market)"
            
            overview_section += ":\n"
            
            if "description" in details:
                overview_section += f"{details['description']}\n\n"
            
            if "key_players" in details and details["key_players"]:
                overview_section += "Key Players: " + ", ".join(details["key_players"]) + "\n\n"
    
    # Format key trends section
    trends_section = "## Key Industry Trends\n\n"
    
    if key_trends:
        if "summary" in key_trends:
            trends_section += f"{key_trends['summary']}\n\n"
        
        if "trends" in key_trends and key_trends["trends"]:
            for trend in key_trends["trends"]:
                if "name" in trend:
                    trends_section += f"### {trend['name']}\n\n"
                else:
                    trends_section += "### Industry Trend\n\n"
                
                if "description" in trend:
                    trends_section += f"{trend['description']}\n\n"
                
                if "impact" in trend:
                    trends_section += f"**Impact**: {trend['impact']}\n\n"
    else:
        trends_section += "Detailed trend data is currently unavailable.\n\n"
    
    # Format market drivers and challenges section
    drivers_section = "## Market Drivers & Challenges\n\n"
    
    if "drivers" in market_overview and market_overview["drivers"]:
        drivers_section += "### Key Market Drivers\n\n"
        for driver in market_overview["drivers"]:
            drivers_section += f"- {driver}\n"
        drivers_section += "\n"
    
    if "challenges" in market_overview and market_overview["challenges"]:
        drivers_section += "### Key Market Challenges\n\n"
        for challenge in market_overview["challenges"]:
            drivers_section += f"- {challenge}\n"
        drivers_section += "\n"
    
    # Format regional highlights section
    regional_section = "## Regional Highlights\n\n"
    
    if "regional_highlights" in market_overview and market_overview["regional_highlights"]:
        for region, details in market_overview["regional_highlights"].items():
            regional_section += f"### {region}\n\n"
            
            if "description" in details:
                regional_section += f"{details['description']}\n\n"
            
            if "market_size" in details:
                regional_section += f"**Market Size**: {details['market_size']}\n\n"
            
            if "growth_rate" in details:
                regional_section += f"**Growth Rate**: {details['growth_rate']}\n\n"
    else:
        regional_section += "Detailed regional data is currently unavailable.\n\n"
    
    # Combine all sections
    full_analysis = title
    
    # Add an executive summary if available
    if "executive_summary" in market_overview:
        full_analysis += f"{market_overview['executive_summary']}\n\n"
    
    # Add the rest of the sections
    full_analysis += f"{overview_section}\n{trends_section}\n{drivers_section}\n{regional_section}"
    
    # Add a conclusion if available
    if "conclusion" in market_overview:
        full_analysis += f"\n## Conclusion\n\n{market_overview['conclusion']}\n"
    
    # Add date stamp
    current_date = datetime.now().strftime("%B %d, %Y")
    full_analysis += f"\n\n*Analysis generated on {current_date}. Data subject to change.*"
    
    return full_analysis
