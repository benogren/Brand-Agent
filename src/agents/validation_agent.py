"""
Validation Agent for AI Brand Studio.

This agent validates brand names for availability across multiple channels:
domain availability, trademark conflicts, and overall risk assessment.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from google.cloud import aiplatform

# Import validation tools
from src.tools.domain_checker import check_domain_availability
from src.tools.trademark_checker import search_trademarks_uspto

# Try to import real ADK, fall back to mock
try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

logger = logging.getLogger('brand_studio.validation_agent')


# Validation agent instruction prompt
VALIDATION_AGENT_INSTRUCTION = """
You are a brand validation specialist for AI Brand Studio. Your role is to assess
the viability of brand name candidates by checking availability and risk factors.

## YOUR RESPONSIBILITIES

1. **Domain Availability:**
   - Check .com, .ai, .io domain availability
   - Assess alternative domain options
   - Flag names with no available domains

2. **Trademark Risk Assessment:**
   - Search USPTO trademark database
   - Identify exact matches and similar marks
   - Assess conflict risk (low/medium/high/critical)
   - Flag names with active trademark conflicts

3. **Overall Risk Scoring:**
   - Combine domain and trademark findings
   - Provide clear recommendations
   - Categorize names as: Clear, Caution, or Blocked

4. **Recommendation Format:**
   For each validated name, provide:
   - Domain status summary
   - Trademark risk level
   - Overall recommendation
   - Specific concerns or flags
   - Alternative suggestions if blocked

## OUTPUT STRUCTURE

```
{
  "brand_name": "ExampleBrand",
  "validation_status": "clear|caution|blocked",
  "domain_check": {
    "com_available": true|false,
    "ai_available": true|false,
    "io_available": true|false,
    "best_available": ".com|.ai|.io|none"
  },
  "trademark_check": {
    "risk_level": "low|medium|high|critical",
    "conflicts_found": 0,
    "exact_matches": [],
    "similar_marks": []
  },
  "recommendation": "Clear to use|Use with caution|Blocked - high risk",
  "concerns": ["concern1", "concern2", ...],
  "overall_score": 85  // 0-100, higher is better
}
```

## VALIDATION LOGIC

**Clear (Score 80-100):**
- .com domain available
- No exact trademark matches
- Low/medium trademark risk
- Recommendation: Proceed with confidence

**Caution (Score 50-79):**
- .com taken but .ai or .io available
- Some similar trademarks but no exact matches
- Medium trademark risk
- Recommendation: Proceed with legal review

**Blocked (Score 0-49):**
- No domains available
- Exact trademark matches
- High/critical trademark risk
- Recommendation: Avoid, choose alternative
"""


class ValidationAgent:
    """
    Validation Agent that checks brand name availability and risks.

    Integrates domain checking and trademark search to provide comprehensive
    validation of brand name candidates.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize the validation agent.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region
            model_name: Gemini model to use
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        logger.info(
            "Initializing ValidationAgent",
            extra={'project_id': project_id, 'model': model_name}
        )

        # Initialize Vertex AI
        try:
            aiplatform.init(project=project_id, location=location)
            logger.info("Vertex AI initialized for ValidationAgent")
        except Exception as e:
            logger.warning(f"Vertex AI initialization issue: {e}")

        # Initialize the LLM agent
        self.agent = LlmAgent(
            name="validation_agent",
            model=model_name,
            description="Validates brand names for availability and risk",
            instruction=VALIDATION_AGENT_INSTRUCTION
        )
        logger.info("Validation LlmAgent initialized")

    def validate_brand_name(
        self,
        brand_name: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a single brand name.

        Args:
            brand_name: Brand name to validate
            category: Optional trademark category (Nice classification)

        Returns:
            Validation results dictionary

        Example:
            >>> agent = ValidationAgent(project_id="my-project")
            >>> result = agent.validate_brand_name("TechFlow")
            >>> print(result['validation_status'])
            'clear'
        """
        logger.info(f"Validating brand name: {brand_name}")

        # Check domain availability
        domain_results = check_domain_availability(brand_name)
        logger.debug(f"Domain check complete for {brand_name}")

        # Check trademark conflicts
        trademark_results = search_trademarks_uspto(brand_name, category=category)
        logger.debug(f"Trademark check complete for {brand_name}")

        # Combine results and calculate score
        validation_result = self._compile_validation_results(
            brand_name=brand_name,
            domain_results=domain_results,
            trademark_results=trademark_results
        )

        logger.info(
            f"Validation complete for '{brand_name}': "
            f"status={validation_result['validation_status']}, "
            f"score={validation_result['overall_score']}"
        )

        return validation_result

    def validate_brand_names_batch(
        self,
        brand_names: List[str],
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple brand names.

        Args:
            brand_names: List of brand names to validate
            category: Optional trademark category

        Returns:
            List of validation results
        """
        logger.info(f"Starting batch validation for {len(brand_names)} brands")

        results = []
        for brand_name in brand_names:
            result = self.validate_brand_name(brand_name, category=category)
            results.append(result)

        # Sort by overall score (best first)
        results.sort(key=lambda x: x['overall_score'], reverse=True)

        logger.info(f"Batch validation complete for {len(brand_names)} brands")
        return results

    def _compile_validation_results(
        self,
        brand_name: str,
        domain_results: Dict[str, bool],
        trademark_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compile validation results from domain and trademark checks.

        Args:
            brand_name: Brand name being validated
            domain_results: Domain availability results
            trademark_results: Trademark search results

        Returns:
            Compiled validation result dictionary
        """
        # Extract domain availability
        com_available = domain_results.get(f"{brand_name.lower().replace(' ', '')}.com", False)
        ai_available = domain_results.get(f"{brand_name.lower().replace(' ', '')}.ai", False)
        io_available = domain_results.get(f"{brand_name.lower().replace(' ', '')}.io", False)

        # Determine best available domain
        if com_available:
            best_available = ".com"
        elif ai_available:
            best_available = ".ai"
        elif io_available:
            best_available = ".io"
        else:
            best_available = "none"

        # Extract trademark info
        trademark_risk = trademark_results.get('risk_level', 'unknown')
        conflicts_found = trademark_results.get('conflicts_found', 0)
        exact_matches = trademark_results.get('exact_matches', [])
        similar_marks = trademark_results.get('similar_marks', [])

        # Calculate overall score
        score = self._calculate_validation_score(
            com_available=com_available,
            ai_available=ai_available,
            io_available=io_available,
            trademark_risk=trademark_risk,
            exact_matches_count=len(exact_matches)
        )

        # Determine validation status
        if score >= 80:
            status = "clear"
        elif score >= 50:
            status = "caution"
        else:
            status = "blocked"

        # Generate recommendation
        recommendation = self._generate_recommendation(
            status=status,
            best_available=best_available,
            trademark_risk=trademark_risk
        )

        # Identify concerns
        concerns = self._identify_concerns(
            best_available=best_available,
            trademark_risk=trademark_risk,
            exact_matches=exact_matches
        )

        return {
            "brand_name": brand_name,
            "validation_status": status,
            "domain_check": {
                "com_available": com_available,
                "ai_available": ai_available,
                "io_available": io_available,
                "best_available": best_available
            },
            "trademark_check": {
                "risk_level": trademark_risk,
                "conflicts_found": conflicts_found,
                "exact_matches": [m.get('mark', '') for m in exact_matches],
                "similar_marks": [m.get('mark', '') for m in similar_marks]
            },
            "recommendation": recommendation,
            "concerns": concerns,
            "overall_score": score
        }

    def _calculate_validation_score(
        self,
        com_available: bool,
        ai_available: bool,
        io_available: bool,
        trademark_risk: str,
        exact_matches_count: int
    ) -> int:
        """Calculate overall validation score (0-100)."""
        score = 100

        # Domain availability scoring
        if not com_available:
            score -= 20
        if not ai_available and not io_available:
            score -= 10

        # Trademark risk scoring
        risk_penalties = {
            'critical': 60,
            'high': 40,
            'medium': 20,
            'low': 5,
            'unknown': 10
        }
        score -= risk_penalties.get(trademark_risk, 10)

        # Exact trademark matches are very serious
        if exact_matches_count > 0:
            score -= 30

        return max(0, min(100, score))

    def _generate_recommendation(
        self,
        status: str,
        best_available: str,
        trademark_risk: str
    ) -> str:
        """Generate human-readable recommendation."""
        if status == "clear":
            return f"Clear to use - {best_available} domain available with low trademark risk"
        elif status == "caution":
            if best_available == "none":
                return "Use with caution - no ideal domain available"
            else:
                return f"Use with caution - {best_available} available but trademark concerns exist"
        else:
            return "Blocked - high risk due to trademark conflicts or domain unavailability"

    def _identify_concerns(
        self,
        best_available: str,
        trademark_risk: str,
        exact_matches: List[Dict]
    ) -> List[str]:
        """Identify specific concerns."""
        concerns = []

        if best_available == "none":
            concerns.append("No premium domains (.com, .ai, .io) available")
        elif best_available != ".com":
            concerns.append(".com domain not available")

        if trademark_risk in ['critical', 'high']:
            concerns.append(f"High trademark risk ({trademark_risk})")

        if exact_matches:
            concerns.append(f"Exact trademark match found: {exact_matches[0].get('mark', 'Unknown')}")

        return concerns
