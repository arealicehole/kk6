#!/usr/bin/env python3
"""
Category-Specific Professional Extraction Prompts
Each prompt is written from the perspective of a domain expert reviewing KK6 planning transcripts.
"""

from typing import Dict, List

class CategoryPrompts:
    """Professional extraction prompts for each planning category."""
    
    @staticmethod
    def get_category_prompt(category_name: str, transcript_chunks: List[str]) -> str:
        """Get specialized extraction prompt for a category."""
        
        # Combine relevant transcript chunks
        relevant_content = "\n\n".join(transcript_chunks)
        
        # Get the specialist prompt for this category
        specialist_prompts = {
            "venue_management": CategoryPrompts._venue_management_prompt,
            "food_catering": CategoryPrompts._food_catering_prompt,
            "cannabis_supply": CategoryPrompts._cannabis_supply_prompt,
            "budget_finance": CategoryPrompts._budget_finance_prompt,
            "staffing_volunteers": CategoryPrompts._staffing_volunteers_prompt,
            "legal_compliance": CategoryPrompts._legal_compliance_prompt,
            "marketing_promotion": CategoryPrompts._marketing_promotion_prompt,
            "security_safety": CategoryPrompts._security_safety_prompt,
            "attendee_management": CategoryPrompts._attendee_management_prompt,
            "logistics_coordination": CategoryPrompts._logistics_coordination_prompt,
            "equipment_supplies": CategoryPrompts._equipment_supplies_prompt,
            "entertainment_activities": CategoryPrompts._entertainment_activities_prompt,
            "transportation_parking": CategoryPrompts._transportation_parking_prompt,
            "risk_management": CategoryPrompts._risk_management_prompt,
            "partnerships_sponsors": CategoryPrompts._partnerships_sponsors_prompt,
            "charity_component": CategoryPrompts._charity_component_prompt,
            "communication_coordination": CategoryPrompts._communication_coordination_prompt,
            "date_scheduling": CategoryPrompts._date_scheduling_prompt,
            "capacity_attendance": CategoryPrompts._capacity_attendance_prompt,
            "technology_av": CategoryPrompts._technology_av_prompt,
            "permits_licensing": CategoryPrompts._permits_licensing_prompt,
            "waste_management": CategoryPrompts._waste_management_prompt,
            "weather_contingency": CategoryPrompts._weather_contingency_prompt,
            "photography_media": CategoryPrompts._photography_media_prompt,
            "registration_ticketing": CategoryPrompts._registration_ticketing_prompt,
            "accessibility_accommodation": CategoryPrompts._accessibility_accommodation_prompt,
            "vendor_management": CategoryPrompts._vendor_management_prompt,
            "quality_control": CategoryPrompts._quality_control_prompt,
            "post_event_analysis": CategoryPrompts._post_event_analysis_prompt,
            "emergency_procedures": CategoryPrompts._emergency_procedures_prompt,
            "miscellaneous": CategoryPrompts._miscellaneous_prompt
        }
        
        prompt_function = specialist_prompts.get(category_name)
        if not prompt_function:
            return CategoryPrompts._generic_prompt(category_name, relevant_content)
            
        return prompt_function(relevant_content)
    
    @staticmethod
    def _venue_management_prompt(content: str) -> str:
        return f"""Extract venue-related planning information from this KK6 transcript.

TRANSCRIPT:
{content}

Find ANY mentions of:
- Venue names, restaurant locations
- Space capacity, room size, seating
- Layout, patio, indoor/outdoor areas
- Venue policies, hours, restrictions

Return JSON:
{{
  "extracted_items": [
    {{
      "category_name": "venue_management",
      "title": "Brief descriptive title",
      "description": "Detailed explanation and key context from transcript",
      "confidence_level": 1-10,
      "tags": ["venue", "location"]
    }}
  ]
}}"""

    @staticmethod
    def _food_catering_prompt(content: str) -> str:
        return f"""You are a professional CATERING MANAGER reviewing this Kanna Kickback 6 planning discussion. Your expertise is in food service, beverage planning, and event dining logistics.

RELEVANT TRANSCRIPT SECTIONS:
{content}

CATERING MANAGER ANALYSIS:
As a catering specialist, scan this content for ANY information related to:

**FOOD SERVICE & MENU:**
- Food types, menu items, cuisine preferences
- Sushi mentions, appetizers, main courses, desserts
- Dietary restrictions, special requirements (vegan, gluten-free, etc.)
- Food preparation methods, cooking requirements
- Portion planning, serving sizes, quantities needed

**BEVERAGE SERVICE:**
- Alcoholic beverages, beer, wine, cocktails, happy hour pricing
- Non-alcoholic options, soft drinks, water service
- Bar setup, bartending requirements
- Beverage quantities, cost considerations

**SERVICE LOGISTICS:**
- Serving methods (buffet, plated service, food stations)
- Serving equipment needs (plates, cups, bowls, utensils, napkins)
- Food presentation, display requirements
- Service staff needs, food runners, servers
- Kitchen access, food preparation areas

**VENDOR & COST CONSIDERATIONS:**
- Restaurant partnerships, catering vendor discussions
- Food cost negotiations, pricing structures
- Revenue sharing agreements for food sales
- Food sourcing, supply chain considerations
- Food safety, health regulations

**TIMING & COORDINATION:**
- Meal timing, service windows
- Food preparation schedules
- Coordination with other activities

EXTRACT EVERYTHING food/beverage-related, including vendor negotiations and cost discussions.

Return valid JSON format:
{{
  "extracted_items": [
    {{
      "category_name": "food_catering",
      "item_key": "menu_planning_discussion",
      "title": "Clear, specific title about food/catering aspect",
      "description": "Full context and details from transcript",
      "value_text": "specific food item or detail",
      "value_numeric": cost_or_quantity_if_mentioned,
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["food", "catering", "menu", "beverages", etc.]
    }}
  ]
}}"""

    @staticmethod
    def _cannabis_supply_prompt(content: str) -> str:
        return f"""Extract cannabis-related planning information from this KK6 transcript.

TRANSCRIPT:
{content}

Find ANY mentions of:
- Cannabis products (flower, edibles, sushi)
- Weed quantities, supply needs
- Dispensary partnerships, vendors
- Cannabis consumption areas
- Legal/regulation concerns

Return JSON:
{{
  "extracted_items": [
    {{
      "category_name": "cannabis_supply",
      "title": "Brief descriptive title",
      "description": "Detailed explanation and key context from transcript",
      "confidence_level": 1-10,
      "tags": ["cannabis", "supply"]
    }}
  ]
}}"""

    @staticmethod
    def _budget_finance_prompt(content: str) -> str:
        return f"""You are a professional FINANCIAL PLANNER reviewing this Kanna Kickback 6 planning discussion. Your expertise is in event budgeting, revenue planning, and cost management.

RELEVANT TRANSCRIPT SECTIONS:
{content}

FINANCIAL PLANNER ANALYSIS:
As a finance specialist, scan this content for ANY information related to:

**REVENUE PLANNING:**
- Revenue sharing agreements, percentage splits
- Ticket pricing, admission fees, registration costs
- Food sales revenue, bar sales income
- Vendor revenue sharing, commission structures
- Profit projections, income estimates

**COST STRUCTURE:**
- Venue rental costs, facility fees
- Food and beverage costs, catering expenses
- Staff wages, contractor payments
- Equipment rental costs, supply expenses
- Marketing and promotional costs

**FINANCIAL NEGOTIATIONS:**
- Vendor contract negotiations, pricing discussions
- Payment terms, cost splitting arrangements
- Discount negotiations, bulk pricing deals
- Cost-saving strategies, budget optimization
- Financial risk discussions

**PAYMENT & PROCESSING:**
- Payment methods, transaction processing
- Cash handling procedures, payment logistics
- Refund policies, financial guarantees
- Invoice management, billing arrangements
- Financial tracking, accounting procedures

**BUDGET PLANNING:**
- Overall budget discussions, financial limits
- Cost allocation across categories
- Financial milestones, payment schedules
- ROI calculations, profitability analysis
- Financial contingency planning

EXTRACT EVERYTHING financial, including specific numbers, percentages, and cost estimates.

Return valid JSON format:
{{
  "extracted_items": [
    {{
      "category_name": "budget_finance",
      "item_key": "revenue_sharing_discussion",
      "title": "Clear, specific title about financial aspect",
      "description": "Full context and details from transcript",
      "value_text": "financial detail or agreement",
      "value_numeric": dollar_amount_or_percentage_if_mentioned,
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["budget", "revenue", "costs", "finance", etc.]
    }}
  ]
}}"""

    @staticmethod
    def _staffing_volunteers_prompt(content: str) -> str:
        return f"""You are a professional HR COORDINATOR reviewing this Kanna Kickback 6 planning discussion. Your expertise is in staffing, volunteer management, and human resources planning.

RELEVANT TRANSCRIPT SECTIONS:
{content}

HR COORDINATOR ANALYSIS:
As a staffing specialist, scan this content for ANY information related to:

**STAFFING REQUIREMENTS:**
- Staff roles needed (servers, bartenders, security, coordinators)
- Food runners, kitchen staff, service personnel
- Volunteer positions, volunteer coordination needs
- Management roles, supervisory requirements
- Specialized roles (cannabis handlers, entertainment staff)

**PERSONNEL LOGISTICS:**
- Staff scheduling, shift planning, work hours
- Staff-to-guest ratios, coverage requirements
- Break schedules, staff meal planning
- Staff coordination, communication needs
- Staff training requirements, skill needs

**COMPENSATION & AGREEMENTS:**
- Staff wages, hourly rates, payment structures
- Volunteer incentives, volunteer benefits
- Staff contracts, work agreements
- Payment schedules, compensation discussions
- Tips, gratuities, revenue sharing with staff

**TEAM COORDINATION:**
- Team assignments, role responsibilities
- Staff hierarchy, reporting structures
- Staff communication methods, coordination tools
- Staff meetings, briefing requirements
- Performance expectations, quality standards

**HUMAN RESOURCES:**
- Staff recruitment, hiring discussions
- Background checks, staff vetting
- Staff availability, scheduling conflicts
- Staff experience requirements, qualifications
- Staff management challenges, HR issues

EXTRACT EVERYTHING staffing-related, including volunteer management and compensation discussions.

Return valid JSON format:
{{
  "extracted_items": [
    {{
      "category_name": "staffing_volunteers",
      "item_key": "staff_roles_discussion",
      "title": "Clear, specific title about staffing aspect",
      "description": "Full context and details from transcript",
      "value_text": "specific role or staffing detail",
      "value_numeric": staff_count_or_wage_if_mentioned,
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["staff", "volunteers", "roles", "scheduling", etc.]
    }}
  ]
}}"""

    @staticmethod
    def _legal_compliance_prompt(content: str) -> str:
        return f"""You are a professional LEGAL ADVISOR reviewing this Kanna Kickback 6 planning discussion. Your expertise is in event law, regulatory compliance, and risk mitigation.

RELEVANT TRANSCRIPT SECTIONS:
{content}

LEGAL ADVISOR ANALYSIS:
As a legal specialist, scan this content for ANY information related to:

**REGULATORY COMPLIANCE:**
- Cannabis regulations, legal cannabis requirements
- Alcohol licensing, liquor law compliance
- Event permits, licensing requirements
- Health department regulations, food safety laws
- Fire safety codes, occupancy regulations

**LIABILITY & RISK:**
- Insurance requirements, liability coverage
- Risk assessments, legal risk factors
- Indemnification agreements, liability waivers
- Legal responsibility assignments
- Accident prevention, safety protocols

**CONTRACTS & AGREEMENTS:**
- Vendor contracts, service agreements
- Venue rental agreements, facility contracts
- Staff contracts, employment agreements
- Partnership agreements, collaboration terms
- Revenue sharing agreements, financial contracts

**LEGAL BOUNDARIES:**
- Age restrictions, ID verification requirements
- Consumption limitations, legal boundaries
- Legal vs. illegal activities, compliance gaps
- Law enforcement considerations, police relations
- Legal precedents, regulatory guidelines

**DOCUMENTATION & COMPLIANCE:**
- Required documentation, permit applications
- Legal filings, compliance reporting
- Record keeping requirements, documentation standards
- Legal review needs, attorney consultations
- Compliance monitoring, legal oversight

EXTRACT EVERYTHING with legal implications, including regulatory discussions and compliance concerns.

Return valid JSON format:
{{
  "extracted_items": [
    {{
      "category_name": "legal_compliance",
      "item_key": "regulatory_compliance_discussion",
      "title": "Clear, specific title about legal aspect",
      "description": "Full context and details from transcript",
      "value_text": "specific legal requirement or concern",
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["legal", "compliance", "regulations", "permits", etc.]
    }}
  ]
}}"""

    # Continuing with more specialized prompts...
    @staticmethod
    def _security_safety_prompt(content: str) -> str:
        return f"""You are a professional SECURITY MANAGER reviewing this Kanna Kickback 6 planning discussion. Your expertise is in crowd control, safety protocols, and security planning.

RELEVANT TRANSCRIPT SECTIONS:
{content}

SECURITY MANAGER ANALYSIS:
As a security specialist, scan this content for ANY information related to:

**CROWD CONTROL:**
- Attendance numbers, crowd size expectations
- Entry/exit control, access management
- Line management, queue control strategies
- Crowd flow planning, bottleneck prevention
- Overcrowding prevention, capacity management

**SECURITY PERSONNEL:**
- Security staff requirements, guard assignments
- Security contractor needs, professional security services
- Volunteer security roles, staff security responsibilities
- Security training needs, protocol briefings
- Security coordination, communication systems

**ACCESS CONTROL:**
- Guest list management, invitation verification
- ID checking procedures, age verification
- VIP access, special permissions
- Restricted area management, off-limits zones
- Entry screening, security checks

**SAFETY PROTOCOLS:**
- Emergency procedures, evacuation plans
- First aid requirements, medical emergency response
- Fire safety, safety equipment needs
- Incident response protocols, crisis management
- Safety training, staff safety briefings

**RISK ASSESSMENT:**
- Security threats, risk factors identification
- Cannabis-related security considerations
- Alcohol-related safety concerns
- Conflict prevention, de-escalation strategies
- Security vulnerabilities, weak points

EXTRACT EVERYTHING security and safety-related, including crowd management and emergency planning.

Return valid JSON format:
{{
  "extracted_items": [
    {{
      "category_name": "security_safety",
      "item_key": "crowd_control_discussion",
      "title": "Clear, specific title about security aspect",
      "description": "Full context and details from transcript",
      "value_text": "specific security measure or concern",
      "value_numeric": staff_count_or_capacity_if_mentioned,
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["security", "safety", "crowd_control", "emergency", etc.]
    }}
  ]
}}"""

    # Adding the remaining category prompts with abbreviated versions for space
    @staticmethod
    def _attendee_management_prompt(content: str) -> str:
        return f"""You are an ATTENDEE SERVICES COORDINATOR reviewing this Kanna Kickback 6 planning discussion.

RELEVANT TRANSCRIPT SECTIONS:
{content}

ATTENDEE COORDINATOR ANALYSIS:
Scan for guest list management, registration processes, attendee communication, check-in procedures, guest services, attendee experience planning, and customer service considerations.

Return valid JSON with category_name: "attendee_management"."""

    @staticmethod
    def _logistics_coordination_prompt(content: str) -> str:
        return f"""You are a LOGISTICS COORDINATOR reviewing this Kanna Kickback 6 planning discussion.

RELEVANT TRANSCRIPT SECTIONS:
{content}

LOGISTICS COORDINATOR ANALYSIS:
Scan for timeline coordination, task sequencing, team coordination, resource allocation, scheduling dependencies, and overall event logistics planning.

Return valid JSON with category_name: "logistics_coordination"."""

    @staticmethod
    def _equipment_supplies_prompt(content: str) -> str:
        return f"""You are an EQUIPMENT MANAGER reviewing this Kanna Kickback 6 planning discussion.

RELEVANT TRANSCRIPT SECTIONS:
{content}

EQUIPMENT MANAGER ANALYSIS:
Scan for equipment rentals, supply needs, setup requirements, technical equipment, furniture needs, tableware, and material procurement discussions.

Return valid JSON with category_name: "equipment_supplies"."""

    # Continue with abbreviated versions for remaining categories...
    @staticmethod
    def _marketing_promotion_prompt(content: str) -> str:
        return f"""You are a professional MARKETING DIRECTOR reviewing this Kanna Kickback 6 planning discussion.

RELEVANT TRANSCRIPT SECTIONS:
{content}

MARKETING DIRECTOR ANALYSIS:
Scan for promotional strategies, social media plans, advertising approaches, audience targeting, brand messaging, and marketing channel discussions.

Return valid JSON with category_name: "marketing_promotion"."""

    @staticmethod
    def _generic_prompt(category_name: str, content: str) -> str:
        return f"""You are a specialist reviewing this Kanna Kickback 6 planning discussion for {category_name.replace('_', ' ')} information.

RELEVANT TRANSCRIPT SECTIONS:
{content}

SPECIALIST ANALYSIS:
Extract any information relevant to {category_name.replace('_', ' ')} planning and management.

Return valid JSON format:
{{
  "extracted_items": [
    {{
      "category_name": "{category_name}",
      "item_key": "general_discussion",
      "title": "Clear, specific title",
      "description": "Full context and details from transcript",
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["{category_name.split('_')[0]}", "planning"]
    }}
  ]
}}"""

    # Add remaining category prompts...
    @staticmethod
    def _entertainment_activities_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("entertainment_activities", content)
    
    @staticmethod
    def _transportation_parking_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("transportation_parking", content)
    
    @staticmethod
    def _risk_management_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("risk_management", content)
    
    @staticmethod
    def _partnerships_sponsors_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("partnerships_sponsors", content)
    
    @staticmethod
    def _charity_component_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("charity_component", content)
    
    @staticmethod
    def _communication_coordination_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("communication_coordination", content)
    
    @staticmethod
    def _date_scheduling_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("date_scheduling", content)
    
    @staticmethod
    def _capacity_attendance_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("capacity_attendance", content)
    
    @staticmethod
    def _technology_av_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("technology_av", content)
    
    @staticmethod
    def _permits_licensing_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("permits_licensing", content)
    
    @staticmethod
    def _waste_management_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("waste_management", content)
    
    @staticmethod
    def _weather_contingency_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("weather_contingency", content)
    
    @staticmethod
    def _photography_media_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("photography_media", content)
    
    @staticmethod
    def _registration_ticketing_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("registration_ticketing", content)
    
    @staticmethod
    def _accessibility_accommodation_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("accessibility_accommodation", content)
    
    @staticmethod
    def _vendor_management_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("vendor_management", content)
    
    @staticmethod
    def _quality_control_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("quality_control", content)
    
    @staticmethod
    def _post_event_analysis_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("post_event_analysis", content)
    
    @staticmethod
    def _emergency_procedures_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("emergency_procedures", content)
    
    @staticmethod
    def _miscellaneous_prompt(content: str) -> str:
        return CategoryPrompts._generic_prompt("miscellaneous", content)

# Test the category prompts
if __name__ == "__main__":
    # Test with sample content
    test_content = ["We need to figure out the restaurant deal and get 200 people fed with sushi and drinks."]
    
    # Test venue management prompt
    venue_prompt = CategoryPrompts.get_category_prompt("venue_management", test_content)
    print("VENUE MANAGEMENT PROMPT:")
    print(venue_prompt[:500] + "...")
    
    # Test food catering prompt  
    food_prompt = CategoryPrompts.get_category_prompt("food_catering", test_content)
    print("\nFOOD CATERING PROMPT:")
    print(food_prompt[:500] + "...")