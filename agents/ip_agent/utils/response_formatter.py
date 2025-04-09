# agents/ip_agent/utils/response_formatter.py

from typing import Dict, Any, List, Optional

def format_ip_analysis(analysis_type: str, **kwargs) -> str:
    \"\"\"
    Format the IP analysis results into a readable response.
    
    Args:
        analysis_type: Type of analysis (patent_landscape, freedom_to_operate, ip_strategy, legal_developments, general_overview)
        **kwargs: Analysis-specific data
        
    Returns:
        Formatted response string
    \"\"\"
    if analysis_type == \"patent_landscape\":
        return _format_patent_landscape(**kwargs)
    elif analysis_type == \"freedom_to_operate\":
        return _format_freedom_to_operate(**kwargs)
    elif analysis_type == \"ip_strategy\":
        return _format_ip_strategy(**kwargs)
    elif analysis_type == \"legal_developments\":
        return _format_legal_developments(**kwargs)
    else:
        return _format_general_overview(**kwargs)

def _format_patent_landscape(tech_domain: Optional[str], 
                           landscape_data: Dict[str, Any],
                           trend_data: Dict[str, Any],
                           key_players: List[Dict[str, Any]],
                           companies: List[str],
                           time_range: str,
                           **kwargs) -> str:
    \"\"\"Format patent landscape analysis.\"\"\"
    # Create domain-specific title
    if tech_domain:
        title = f\"Patent Landscape Analysis: {tech_domain.upper()} Technology\"
    else:
        title = \"Biotech Patent Landscape Analysis\"
    
    # Add time range
    time_frame = f\"{time_range} Patent Activity Analysis\"
    
    # Format filing trends
    filing_trends = \"\
## Patent Filing Trends\
\"
    if trend_data and \"yearly_filings\" in trend_data:
        filing_trends += \"Recent patent filing activity shows \"
        yearly = trend_data[\"yearly_filings\"]
        
        # Analyze trend direction
        years = sorted(yearly.keys())
        if len(years) >= 2:
            first_year = yearly[years[0]]
            last_year = yearly[years[-1]]
            
            if last_year > first_year * 1.2:  # 20% increase
                filing_trends += f\"significant growth with a {int((last_year/first_year - 1) * 100)}% increase \"
            elif last_year > first_year:
                filing_trends += \"moderate growth \"
            elif last_year < first_year * 0.8:  # 20% decrease
                filing_trends += f\"a notable decline of {int((1 - last_year/first_year) * 100)}% \"
            else:
                filing_trends += \"relatively stable activity \"
                
            filing_trends += f\"over the {time_range} period. \"
        
        # Add annual data point
        filing_trends += f\"In the most recent year, there were {yearly[years[-1]]} new patent filings \"
        if tech_domain:
            filing_trends += f\"in the {tech_domain} space.\"
        else:
            filing_trends += \"in this technology area.\"
    else:
        filing_trends += \"No specific trend data available for this technology area.\"
    
    # Format key players
    key_players_section = \"\
## Key Patent Holders\
\"
    if key_players and len(key_players) > 0:
        key_players_section += \"The dominant intellectual property holders in this space include:\
\
\"
        
        # Sort by patent count if available
        sorted_players = sorted(key_players, 
                               key=lambda x: x.get(\"patent_count\", 0), 
                               reverse=True)
        
        # List top players
        for i, player in enumerate(sorted_players[:5]):
            name = player.get(\"name\", \"Unknown\")
            count = player.get(\"patent_count\", \"N/A\")
            focus = player.get(\"technology_focus\", \"various technologies\")
            
            key_players_section += f\"- **{name}**: {count} patents focusing on {focus}\
\"
        
        # Add overall insight
        key_players_section += \"\
This patent distribution indicates \"
        if len(sorted_players) > 0 and sorted_players[0].get(\"patent_count\", 0) > sorted_players[-1].get(\"patent_count\", 0) * 2:
            key_players_section += \"a concentrated market with dominant players controlling significant IP.\"
        else:
            key_players_section += \"a relatively fragmented intellectual property landscape.\"
    else:
        key_players_section += \"No specific key player data available for this technology area.\"
    
    # Format company-specific insights
    company_insights = \"\"
    if companies and len(companies) > 0:
        company_insights = \"\
## Requested Company Analysis\
\"
        for company in companies:
            company_data = next((player for player in key_players if player.get(\"name\") == company), None)
            
            if company_data:
                patent_count = company_data.get(\"patent_count\", \"N/A\")
                focus = company_data.get(\"technology_focus\", \"various technologies\")
                growth = company_data.get(\"filing_growth\", \"stable\")
                
                company_insights += f\"**{company}** holds {patent_count} patents in this space, \"
                company_insights += f\"primarily focused on {focus}. \"
                company_insights += f\"Their patent activity has been {growth} over the {time_range} period.\
\
\"
            else:
                company_insights += f\"No specific patent data available for {company} in this technology area.\
\
\"
    
    # Assemble full response
    response = f\"# {title}\
\
\"
    response += f\"*{time_frame}*\
\
\"
    
    # Add executive summary
    response += \"## Executive Summary\
\"
    if landscape_data and \"summary\" in landscape_data:
        response += landscape_data[\"summary\"]
    else:
        if tech_domain:
            response += f\"The {tech_domain} patent landscape shows \"
        else:
            response += \"The biotech patent landscape shows \"
            
        # Add simple trend description
        if trend_data and \"yearly_filings\" in trend_data:
            years = sorted(trend_data[\"yearly_filings\"].keys())
            if len(years) >= 2:
                first_year = trend_data[\"yearly_filings\"][years[0]]
                last_year = trend_data[\"yearly_filings\"][years[-1]]
                
                if last_year > first_year * 1.1:
                    response += \"increasing innovation activity \"
                elif last_year < first_year * 0.9:
                    response += \"decreasing innovation activity \"
                else:
                    response += \"steady innovation activity \"
                    
            response += f\"over the {time_range} period. \"
        
        # Add key player insight
        if key_players and len(key_players) > 0:
            top_player = key_players[0][\"name\"]
            response += f\"{top_player} leads in patent filings, \"
            
            # Add technology focus if available
            if \"technology_focus\" in key_players[0]:
                response += f\"particularly in {key_players[0]['technology_focus']}.\"
            else:
                response += \"with a broad technology portfolio.\"
    
    # Add other sections
    response += filing_trends
    response += key_players_section
    
    # Add company insights if applicable
    if company_insights:
        response += company_insights
    
    # Add strategic implications
    response += \"\
## Strategic Implications\
\"
    if landscape_data and \"strategic_implications\" in landscape_data:
        response += landscape_data[\"strategic_implications\"]
    else:
        if tech_domain:
            response += f\"The {tech_domain} patent landscape suggests that organizations should:\
\
\"
        else:
            response += \"The current patent landscape suggests that organizations should:\
\
\"
            
        response += \"- Monitor key competitors' patent activity to identify technology direction\
\"
        response += \"- Consider strategic patenting in areas showing growth trends\
\"
        response += \"- Evaluate freedom-to-operate risks before entering this space\
\"
        response += \"- Explore potential licensing or partnership opportunities with major IP holders\
\"
    
    return response

def _format_freedom_to_operate(tech_domain: Optional[str],
                             target_markets: List[str],
                             molecule: Optional[str],
                             blocking_patents: List[Dict[str, Any]],
                             expiration_analysis: Dict[str, Any],
                             litigation_risk: Dict[str, Any],
                             **kwargs) -> str:
    \"\"\"Format freedom to operate analysis.\"\"\"
    # Create title
    if molecule:
        title = f\"Freedom to Operate Analysis: {molecule}\"
    elif tech_domain:
        title = f\"Freedom to Operate Analysis: {tech_domain.upper()} Technology\"
    else:
        title = \"Biotech Freedom to Operate Analysis\"
    
    # Format markets
    markets_str = \", \".join(target_markets)
    
    # Format blocking patents section
    blocking_patents_section = \"\
## Potential Blocking Patents\
\"
    if blocking_patents and len(blocking_patents) > 0:
        blocking_patents_section += f\"Identified {len(blocking_patents)} potentially blocking patents across {markets_str}:\
\
\"
        
        # Sort by risk level if available
        sorted_patents = sorted(blocking_patents, 
                               key=lambda x: x.get(\"risk_level\", 0), 
                               reverse=True)
        
        # List top risk patents
        for i, patent in enumerate(sorted_patents[:5]):
            patent_id = patent.get(\"id\", \"Unknown\")
            owner = patent.get(\"owner\", \"Unknown\")
            title = patent.get(\"title\", \"Unknown\")
            risk = patent.get(\"risk_level\", \"Unknown\")
            
            risk_str = \"High\" if risk > 7 else \"Medium\" if risk > 4 else \"Low\"
            
            blocking_patents_section += f\"- **{patent_id}** ({owner}): {title} - Risk: {risk_str}\
\"
        
        if len(sorted_patents) > 5:
            blocking_patents_section += f\"...and {len(sorted_patents) - 5} additional patents with lower risk profiles.\
\"
    else:
        blocking_patents_section += \"No specific blocking patents identified for this technology area and target markets.\"
    
    # Format expiration analysis
    expiration_section = \"\
## Patent Expiration Analysis\
\"
    if expiration_analysis:
        expiring_soon = expiration_analysis.get(\"expiring_soon\", [])
        if expiring_soon and len(expiring_soon) > 0:
            expiration_section += \"Key patents expiring within the next 3 years:\
\
\"
            
            for patent in expiring_soon[:3]:
                patent_id = patent.get(\"id\", \"Unknown\")
                owner = patent.get(\"owner\", \"Unknown\")
                expiry = patent.get(\"expiry_date\", \"Unknown\")
                
                expiration_section += f\"- **{patent_id}** ({owner}) expires on {expiry}\
\"
            
            if len(expiring_soon) > 3:
                expiration_section += f\"...and {len(expiring_soon) - 3} additional patents expiring soon.\
\"
        else:
            expiration_section += \"No significant patents identified as expiring in the next 3 years.\
\"
        
        # Add long-term outlook
        long_term = expiration_analysis.get(\"long_term_outlook\", \"\")
        if long_term:
            expiration_section += f\"\
{long_term}\
\"
    else:
        expiration_section += \"No specific expiration data available for analysis.\"
    
    # Format litigation risk
    litigation_section = \"\
## Litigation Risk Assessment\
\"
    if litigation_risk:
        overall_risk = litigation_risk.get(\"overall_risk\", \"Unknown\")
        litigation_section += f\"Overall litigation risk in this space is assessed as **{overall_risk}**.\
\
\"
        
        # Add active litigation
        active_litigation = litigation_risk.get(\"active_cases\", [])
        if active_litigation and len(active_litigation) > 0:
            litigation_section += f\"There are currently {len(active_litigation)} active litigation cases in this technology area, including:\
\
\"
            
            for case in active_litigation[:2]:
                plaintiff = case.get(\"plaintiff\", \"Unknown\")
                defendant = case.get(\"defendant\", \"Unknown\")
                issue = case.get(\"issue\", \"Unknown\")
                
                litigation_section += f\"- {plaintiff} vs. {defendant}: {issue}\
\"
                
            if len(active_litigation) > 2:
                litigation_section += f\"...and {len(active_litigation) - 2} additional active cases.\
\"
        else:
            litigation_section += \"No active litigation cases identified in this specific technology area.\
\"
        
        # Add litigation trends
        trends = litigation_risk.get(\"trends\", \"\")
        if trends:
            litigation_section += f\"\
{trends}\
\"
    else:
        litigation_section += \"No specific litigation risk data available for analysis.\"
    
    # Assemble full response
    response = f\"# {title}\
\
\"
    response += f\"*Target Markets: {markets_str}*\
\
\"
    
    # Add executive summary
    response += \"## Executive Summary\
\"
    if molecule:
        response += f\"This freedom-to-operate (FTO) analysis for {molecule} across {markets_str} markets \"
    elif tech_domain:
        response += f\"This freedom-to-operate (FTO) analysis for {tech_domain} technology across {markets_str} markets \"
    else:
        response += f\"This freedom-to-operate (FTO) analysis across {markets_str} markets \"
    
    # Add risk assessment
    if blocking_patents and len(blocking_patents) > 0:
        high_risk = sum(1 for p in blocking_patents if p.get(\"risk_level\", 0) > 7)
        medium_risk = sum(1 for p in blocking_patents if 4 < p.get(\"risk_level\", 0) <= 7)
        
        if high_risk > 0:
            response += f\"reveals **{high_risk} high-risk** and **{medium_risk} medium-risk** patents that could potentially block market entry. \"
        elif medium_risk > 0:
            response += f\"reveals **{medium_risk} medium-risk** patents that warrant attention, but no high-risk blocking patents. \"
        else:
            response += \"reveals no high or medium-risk blocking patents, suggesting favorable FTO conditions. \"
    else:
        response += \"reveals no significant patent barriers to market entry at this time. \"
    
    # Add litigation context
    if litigation_risk and litigation_risk.get(\"overall_risk\", \"\").lower() in [\"high\", \"elevated\"]:
        response += \"The current litigation environment in this space is active, suggesting caution. \"
    else:
        response += \"The current litigation environment appears relatively favorable. \"
    
    # Add other sections
    response += blocking_patents_section
    response += expiration_section
    response += litigation_section
    
    # Add recommendations
    response += \"\
## Strategic Recommendations\
\"
    
    # Generate recommendations based on results
    if blocking_patents and len(blocking_patents) > 0:
        high_risk = sum(1 for p in blocking_patents if p.get(\"risk_level\", 0) > 7)
        
        if high_risk > 0:
            response += \"Based on the high-risk patents identified, consider:\
\
\"
            response += \"- Detailed analysis of the high-risk patents to assess precise infringement risk\
\"
            response += \"- Potential design-around strategies to avoid key claims\
\"
            response += \"- Licensing opportunities with key patent holders\
\"
            response += \"- Market entry strategies that avoid the most problematic jurisdictions initially\
\"
        else:
            response += \"Based on the medium/low-risk patents identified, consider:\
\
\"
            response += \"- Monitoring the patent landscape for new filings\
\"
            response += \"- Strengthening your own IP position in this area\
\"
            response += \"- Targeted freedom-to-operate clearances before product launch\
\"
    else:
        response += \"Based on the favorable FTO conditions, consider:\
\
\"
        response += \"- Accelerating R&D and market entry plans\
\"
        response += \"- Building a strong patent portfolio to protect your innovations\
\"
        response += \"- Regular monitoring to maintain awareness of competitive activity\
\"
    
    # Add expiration opportunities if any
    if expiration_analysis and expiration_analysis.get(\"expiring_soon\", []):
        response += \"- Strategic timing to coincide with key patent expirations\
\"
    
    return response

def _format_ip_strategy(tech_domain: Optional[str],
                      company: Optional[str],
                      stage: str,
                      filing_strategy: Dict[str, Any],
                      competitive_position: Optional[Dict[str, Any]],
                      strategic_options: Dict[str, Any],
                      **kwargs) -> str:
    \"\"\"Format IP strategy recommendations.\"\"\"
    # Create title
    if company:
        title = f\"IP Strategy for {company}: {tech_domain or 'Biotech'} Focus\"
    elif tech_domain:
        title = f\"IP Strategy: {tech_domain.upper()} Technology\"
    else:
        title = \"Biotech IP Strategy Recommendations\"
    
    # Format company stage
    stage_name = stage.capitalize()
    
    # Format filing strategy
    filing_section = \"\
## Patent Filing Strategy\
\"
    if filing_strategy:
        key_areas = filing_strategy.get(\"key_areas\", [])
        if key_areas and len(key_areas) > 0:
            filing_section += \"Recommended focus areas for patent protection:\
\
\"
            
            for area in key_areas:
                name = area.get(\"name\", \"Unknown\")
                rationale = area.get(\"rationale\", \"Important technology area\")
                
                filing_section += f\"- **{name}**: {rationale}\
\"
        
        # Add filing approach
        approach = filing_strategy.get(\"approach\", \"\")
        if approach:
            filing_section += f\"\
{approach}\
\"
        
        # Add jurisdiction strategy
        jurisdictions = filing_strategy.get(\"jurisdictions\", [])
        if jurisdictions and len(jurisdictions) > 0:
            filing_section += \"\
Priority filing jurisdictions:\
\
\"
            
            for jur in jurisdictions[:5]:
                name = jur.get(\"name\", \"Unknown\")
                reason = jur.get(\"reason\", \"\")
                
                filing_section += f\"- **{name}**: {reason}\
\"
    else:
        filing_section += \"No specific filing strategy data available for analysis.\"
    
    # Format competitive position
    position_section = \"\"
    if competitive_position:
        position_section = \"\
## Competitive IP Position\
\"
        
        # Add overall assessment
        strength = competitive_position.get(\"strength\", \"Unknown\")
        position_section += f\"Current IP position relative to competitors: **{strength}**\
\
\"
        
        # Add key strengths
        strengths = competitive_position.get(\"strengths\", [])
        if strengths and len(strengths) > 0:
            position_section += \"Key IP strengths:\
\
\"
            
            for strength in strengths:
                position_section += f\"- {strength}\
\"
            
            position_section += \"\
\"
        
        # Add key gaps
        gaps = competitive_position.get(\"gaps\", [])
        if gaps and len(gaps) > 0:
            position_section += \"Critical IP gaps:\
\
\"
            
            for gap in gaps:
                position_section += f\"- {gap}\
\"
    
    # Format strategic options
    options_section = \"\
## Strategic Options\
\"
    if strategic_options:
        # Add organic strategy
        organic = strategic_options.get(\"organic\", [])
        if organic and len(organic) > 0:
            options_section += \"Internal R&D and patenting opportunities:\
\
\"
            
            for opt in organic:
                name = opt.get(\"name\", \"Unknown\")
                impact = opt.get(\"impact\", \"Medium\")
                
                options_section += f\"- **{name}**: Impact: {impact}\
\"
            
            options_section += \"\
\"
        
        # Add partnership options
        partnerships = strategic_options.get(\"partnerships\", [])
        if partnerships and len(partnerships) > 0:
            options_section += \"Potential strategic partnerships:\
\
\"
            
            for partner in partnerships:
                name = partner.get(\"name\", \"Unknown\")
                complementarity = partner.get(\"complementarity\", \"\")
                
                options_section += f\"- **{name}**: {complementarity}\
\"
            
            options_section += \"\
\"
        
        # Add acquisition targets
        acquisitions = strategic_options.get(\"acquisitions\", [])
        if acquisitions and len(acquisitions) > 0 and stage != \"early\":
            options_section += \"Potential IP acquisition targets:\
\
\"
            
            for target in acquisitions:
                name = target.get(\"name\", \"Unknown\")
                rationale = target.get(\"rationale\", \"\")
                
                options_section += f\"- **{name}**: {rationale}\
\"
    else:
        options_section += \"No specific strategic options data available for analysis.\"
    
    # Assemble full response
    response = f\"# {title}\
\
\"
    response += f\"*Company Stage: {stage_name}*\
\
\"
    
    # Add executive summary
    response += \"## Executive Summary\
\"
    if tech_domain:
        response += f\"This IP strategy assessment for the {tech_domain} space \"
    else:
        response += \"This biotech IP strategy assessment \"
    
    if company:
        response += f\"for {company} at its {stage} stage \"
    else:
        response += f\"for {stage}-stage companies \"
    
    # Add summary based on company stage
    if stage == \"early\":
        response += \"focuses on establishing foundational IP protection while conserving resources. \"
        response += \"The strategy emphasizes protecting core technology with carefully targeted patent filings \"
        response += \"and building a strategic IP foundation for future growth.\"
    elif stage == \"growth\":
        response += \"balances expanding IP protection with strategic partnerships. \"
        response += \"The strategy emphasizes broadening patent coverage to secure market position, \"
        response += \"while exploring collaborations that strengthen the overall IP portfolio.\"
    else:  # mature
        response += \"prioritizes defending market position and exploring new growth areas. \"
        response += \"The strategy emphasizes maintaining robust IP protection for commercial products, \"
        response += \"while identifying strategic acquisitions and licensing opportunities to drive continued innovation.\"
    
    # Add other sections
    response += filing_section
    
    if position_section:
        response += position_section
        
    response += options_section
    
    # Add implementation priorities
    response += \"\
## Implementation Priorities\
\"
    
    # Generate recommendations based on stage
    if stage == \"early\":
        response += \"For early-stage companies, prioritize:\
\
\"
        response += \"1. Protect core technology with provisional applications followed by strategic PCT filings\
\"
        response += \"2. Implement cost-effective IP monitoring to avoid unnecessary FTO issues\
\"
        response += \"3. Focus patenting resources on differentiating technology with commercial potential\
\"
        response += \"4. Consider strategic defensive publications for secondary innovations\
\"
        response += \"5. Develop clear IP ownership agreements with founders, employees, and collaborators\
\"
    elif stage == \"growth\":
        response += \"For growth-stage companies, prioritize:\
\
\"
        response += \"1. Expand patent portfolio breadth with continuation and divisional applications\
\"
        response += \"2. Conduct regular FTO analyses before entering new markets\
\"
        response += \"3. Develop a comprehensive global filing strategy aligned with commercial plans\
\"
        response += \"4. Secure IP rights from strategic partnerships and collaborations\
\"
        response += \"5. Consider targeted licensing to generate revenue from non-core assets\
\"
    else:  # mature
        response += \"For mature companies, prioritize:\
\
\"
        response += \"1. Maintain robust protection for commercial products through lifecycle management\
\"
        response += \"2. Strategically acquire complementary IP to consolidate market position\
\"
        response += \"3. Develop licensing programs to maximize return on IP investments\
\"
        response += \"4. Implement sophisticated IP analytics to inform R&D direction\
\"
        response += \"5. Align patent strategy with regulatory exclusivity opportunities\
\"
    
    return response

def _format_legal_developments(tech_domain: Optional[str],
                             region: str,
                             developments: List[Dict[str, Any]],
                             court_cases: List[Dict[str, Any]],
                             regulatory_changes: List[Dict[str, Any]],
                             **kwargs) -> str:
    \"\"\"Format legal developments analysis.\"\"\"
    # Create title
    if tech_domain:
        title = f\"IP Legal Developments: {tech_domain.upper()}\"
    else:
        title = \"Biotech IP Legal Developments\"
    
    # Format region
    region_name = region.upper() if len(region) <= 3 else region.capitalize()
    
    # Format developments section
    developments_section = \"\
## Recent Legal Developments\
\"
    if developments and len(developments) > 0:
        developments_section += f\"Key IP legal changes affecting the {region_name} market:\
\
\"
        
        # Sort by date if available
        sorted_devs = sorted(developments, 
                            key=lambda x: x.get(\"date\", \"\"), 
                            reverse=True)
        
        # List recent developments
        for dev in sorted_devs[:3]:
            date = dev.get(\"date\", \"Recent\")
            title = dev.get(\"title\", \"Unknown\")
            impact = dev.get(\"impact\", \"\")
            
            developments_section += f\"- **{date}**: {title} - {impact}\
\"
        
        if len(sorted_devs) > 3:
            developments_section += f\"...and {len(sorted_devs) - 3} additional legal developments.\
\"
    else:
        developments_section += f\"No significant legal developments identified for the {region_name} market recently.\"
    
    # Format court cases
    cases_section = \"\
## Significant Court Cases\
\"
    if court_cases and len(court_cases) > 0:
        cases_section += \"Recent court decisions with potential impact:\
\
\"
        
        # Sort by date if available
        sorted_cases = sorted(court_cases, 
                             key=lambda x: x.get(\"date\", \"\"), 
                             reverse=True)
        
        # List recent cases
        for case in sorted_cases[:3]:
            name = case.get(\"name\", \"Unknown\")
            court = case.get(\"court\", \"Unknown\")
            date = case.get(\"date\", \"Recent\")
            ruling = case.get(\"ruling\", \"\")
            impact = case.get(\"impact\", \"\")
            
            cases_section += f\"- **{name}** ({court}, {date}): {ruling}\
  *Impact*: {impact}\
\
\"
        
        if len(sorted_cases) > 3:
            cases_section += f\"...and {len(sorted_cases) - 3} additional significant cases.\
\"
    else:
        cases_section += \"No significant court cases identified recently.\"
    
    # Format regulatory changes
    regulatory_section = \"\
## Regulatory Changes\
\"
    if regulatory_changes and len(regulatory_changes) > 0:
        regulatory_section += \"Recent or upcoming regulatory changes:\
\
\"
        
        # Sort by date if available
        sorted_regs = sorted(regulatory_changes, 
                            key=lambda x: x.get(\"date\", \"\"), 
                            reverse=True)
        
        # List recent regulations
        for reg in sorted_regs[:3]:
            title = reg.get(\"title\", \"Unknown\")
            authority = reg.get(\"authority\", \"Unknown\")
            date = reg.get(\"date\", \"Recent\")
            status = reg.get(\"status\", \"\")
            impact = reg.get(\"impact\", \"\")
            
            regulatory_section += f\"- **{title}** ({authority}, {date}): {status}\
  *Impact*: {impact}\
\
\"
        
        if len(sorted_regs) > 3:
            regulatory_section += f\"...and {len(sorted_regs) - 3} additional regulatory changes.\
\"
    else:
        regulatory_section += \"No significant regulatory changes identified recently.\"
    
    # Assemble full response
    response = f\"# {title}\
\
\"
    response += f\"*Region: {region_name}*\
\
\"
    
    # Add executive summary
    response += \"## Executive Summary\
\"
    
    # Generate summary based on content
    if developments and len(developments) > 0:
        high_impact = any(dev.get(\"impact_level\", \"medium\").lower() == \"high\" for dev in developments)
        
        if high_impact:
            response += f\"Recent legal developments in the {region_name} region include **significant changes** that could substantially impact \"
        else:
            response += f\"Recent legal developments in the {region_name} region include incremental changes that may affect \"
    else:
        response += f\"The legal landscape in the {region_name} region has remained relatively stable, with few major changes that would affect \"
    
    if tech_domain:
        response += f\"{tech_domain} intellectual property strategies. \"
    else:
        response += \"biotech intellectual property strategies. \"
    
    # Add court case insight
    if court_cases and len(court_cases) > 0:
        precedent_setting = any(case.get(\"precedent_setting\", False) for case in court_cases)
        
        if precedent_setting:
            response += \"Several precedent-setting court decisions have emerged that may reshape IP enforcement approaches. \"
        else:
            response += \"Recent court decisions have generally maintained established IP doctrine without major shifts. \"
    
    # Add regulatory insight
    if regulatory_changes and len(regulatory_changes) > 0:
        major_changes = any(reg.get(\"impact_level\", \"medium\").lower() == \"high\" for reg in regulatory_changes)
        
        if major_changes:
            response += \"Significant regulatory reforms are underway that will require adaptation of IP strategies.\"
        else:
            response += \"Incremental regulatory adjustments suggest continued stability in the IP regulatory environment.\"
    
    # Add other sections
    response += developments_section
    response += cases_section
    response += regulatory_section
    
    # Add strategic implications
    response += \"\
## Strategic Implications\
\"
    
    # Generate implications based on content
    response += \"Based on these legal developments, consider the following strategic adjustments:\
\
\"
    
    if developments and court_cases and regulatory_changes:
        response += \"1. Update patent filing and prosecution strategies to align with recent legal changes\
\"
        response += \"2. Reassess enforcement strategies in light of recent court decisions\
\"
        response += \"3. Monitor ongoing regulatory developments that may impact IP rights\
\"
        
        # Add technology-specific recommendations
        if tech_domain == \"crispr\":
            response += \"4. Review CRISPR patent claims in light of recent scope interpretations\
\"
            response += \"5. Consider alternative patent strategies focusing on delivery or applications\
\"
        elif tech_domain == \"antibodies\":
            response += \"4. Adapt antibody patenting to address recent enablement decisions\
\"
            response += \"5. Consider epitope mapping and functional characterization to strengthen claims\
\"
        elif tech_domain == \"small_molecules\":
            response += \"4. Review formulation and polymorph protection strategies\
\"
            response += \"5. Consider secondary use patents in light of recent decisions\
\"
        else:
            response += \"4. Conduct a comprehensive IP portfolio review in light of these developments\
\"
            response += \"5. Consider engaging specialized IP counsel for this evolving legal landscape\
\"
    else:
        response += \"1. Maintain current patenting approaches given the stable legal environment\
\"
        response += \"2. Continue standard IP monitoring practices\
\"
        response += \"3. Focus on education about IP fundamentals rather than specialized strategies\
\"
    
    return response

def _format_general_overview(ip_overview: Dict[str, Any],
                           key_trends: List[Dict[str, Any]],
                           **kwargs) -> str:
    """Format general IP overview."""
    # Create title
    title = "Biotech Intellectual Property Overview"
    
    # Format trends section
    trends_section = "\n## Key IP Trends in Biotech\n"
    if key_trends and len(key_trends) > 0:
        trends_section += "Notable trends shaping the biotech IP landscape:\n\n"
        
        # List key trends
        for i, trend in enumerate(key_trends[:5]):
            name = trend.get("name", "Unknown")
            description = trend.get("description", "")
            impact = trend.get("impact", "")
            
            trends_section += f"- **{name}**: {description}\n"
            if impact:
                trends_section += f"  *Impact*: {impact}\n\n"
            else:
                trends_section += "\n"
            
        if len(key_trends) > 5:
            trends_section += f"...and {len(key_trends) - 5} additional emerging trends.\n"
    else:
        trends_section += "No specific trend data available for analysis."
    
    # Format overview sections from ip_overview data
    filing_section = "\n## Patent Filing Overview\n"
    if ip_overview and "filing_overview" in ip_overview:
        filing_section += ip_overview["filing_overview"]
    else:
        filing_section += "Biotech patent filings continue to grow globally, with particular concentration in therapeutic applications. "
        filing_section += "The USPTO, EPO, and CNIPA remain the dominant patent offices for biotech innovation, "
        filing_section += "with an increasing number of filings also seen in emerging markets.\n"
    
    enforcement_section = "\n## Enforcement Landscape\n"
    if ip_overview and "enforcement_landscape" in ip_overview:
        enforcement_section += ip_overview["enforcement_landscape"]
    else:
        enforcement_section += "The biotech IP enforcement landscape remains complex, with significant regional variations. "
        enforcement_section += "Patent litigation in the US continues to focus on biologics and biosimilars, "
        enforcement_section += "while European enforcement often centers on supplementary protection certificates (SPCs) "
        enforcement_section += "and regulatory data protection.\n"
    
    challenges_section = "\n## Key Challenges\n"
    if ip_overview and "key_challenges" in ip_overview:
        challenges_section += ip_overview["key_challenges"]
    else:
        challenges_section += "Biotech innovators face several persistent IP challenges:\n\n"
        challenges_section += "- Increasing scrutiny of patent subject matter eligibility\n"
        challenges_section += "- Growing complexity in global patent strategy coordination\n"
        challenges_section += "- Balancing open innovation with proprietary protection\n"
        challenges_section += "- Managing rising costs of global patent portfolios\n"
        challenges_section += "- Addressing disclosure requirements for bioinformatics and AI innovations\n"
    
    # Assemble full response
    response = f"# {title}\n\n"
    
    # Add executive summary
    response += "## Executive Summary\n"
    if ip_overview and "executive_summary" in ip_overview:
        response += ip_overview["executive_summary"]
    else:
        response += "The biotech intellectual property landscape continues to evolve through technological advancement, "
        response += "regulatory developments, and shifting business models. Key value continues to be created through "
        response += "strategic patent portfolios, though the approach to IP is increasingly nuanced with complementary "
        response += "strategies including regulatory exclusivities, trade secrets, and collaborative innovation models.\n"
    
    # Add other sections
    response += trends_section
    response += filing_section
    response += enforcement_section
    response += challenges_section
    
    # Add strategic considerations
    response += "\n## Strategic Considerations\n"
    if ip_overview and "strategic_considerations" in ip_overview:
        response += ip_overview["strategic_considerations"]
    else:
        response += "For biotech organizations navigating the current IP landscape, consider these key strategies:\n\n"
        response += "1. Implement adaptive IP strategies responsive to evolving legal doctrines\n"
        response += "2. Utilize complementary protection mechanisms beyond patents\n"
        response += "3. Develop territory-specific approaches for global IP portfolios\n"
        response += "4. Consider defensive publication for non-core innovations\n"
        response += "5. Explore collaborative IP models in pre-competitive research areas\n"
    
    return response

