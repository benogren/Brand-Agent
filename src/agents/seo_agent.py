"""
SEO Optimizer Agent for AI Brand Studio.

This agent optimizes brand names and generates SEO-friendly content including
meta titles, descriptions, and keyword strategies.
"""

import logging
import os
from typing import Dict, Any
from google.cloud import aiplatform

try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

logger = logging.getLogger('brand_studio.seo_agent')


SEO_AGENT_INSTRUCTION = """
You are an SEO optimization specialist for AI Brand Studio. Your role is to
optimize brand names and create SEO-friendly content for maximum discoverability.

## YOUR RESPONSIBILITIES

1. **Analyze Brand Name SEO Potential:**
   - Assess keyword relevance and search intent
   - Evaluate brandability vs. keyword optimization
   - Identify semantic associations

2. **Generate Meta Title:**
   - 50-60 characters optimal
   - Include primary keyword
   - Compelling and click-worthy
   - Brand name integration

3. **Generate Meta Description:**
   - 150-160 characters optimal
   - Include secondary keywords
   - Clear value proposition
   - Call-to-action when appropriate

4. **Calculate SEO Score (0-100):**
   - Keyword relevance: 30 points
   - Brandability: 25 points
   - Search volume potential: 20 points
   - Memorability: 15 points
   - Domain availability: 10 points

5. **Provide Keyword Recommendations:**
   - Primary target keywords
   - Secondary/long-tail keywords
   - Related search terms
   - Content marketing opportunities

## OUTPUT FORMAT

```
{
  "seo_score": 85,
  "meta_title": "BrandName - Primary Benefit | Category",
  "meta_description": "Compelling description with keywords and value prop",
  "primary_keywords": ["keyword1", "keyword2"],
  "secondary_keywords": ["long-tail1", "long-tail2"],
  "content_opportunities": ["blog topic 1", "blog topic 2"],
  "optimization_tips": ["tip1", "tip2"]
}
```
"""


class SEOAgent:
    """SEO Optimizer Agent for brand name content."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash"
    ):
        """Initialize the SEO agent."""
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        logger.info("Initializing SEOAgent")

        try:
            aiplatform.init(project=project_id, location=location)
        except Exception as e:
            logger.warning(f"Vertex AI init issue: {e}")

        self.agent = LlmAgent(
            name="seo_optimizer",
            model=model_name,
            description="Optimizes brand names for search engines",
            instruction=SEO_AGENT_INSTRUCTION
        )
        logger.info("SEO LlmAgent initialized")

    def optimize_brand_seo(
        self,
        brand_name: str,
        product_description: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        Generate SEO optimization for a brand name.

        Args:
            brand_name: The brand name to optimize
            product_description: Product/service description
            industry: Target industry

        Returns:
            SEO optimization dictionary
        """
        logger.info(f"Optimizing SEO for brand: {brand_name}")

        # For Phase 2, generate structured SEO content
        seo_result = {
            "brand_name": brand_name,
            "seo_score": self._calculate_seo_score(brand_name, product_description),
            "meta_title": self._generate_meta_title(brand_name, product_description),
            "meta_description": self._generate_meta_description(brand_name, product_description),
            "primary_keywords": self._extract_primary_keywords(product_description, industry),
            "secondary_keywords": self._generate_secondary_keywords(brand_name, industry),
            "content_opportunities": self._suggest_content_topics(brand_name, industry),
            "optimization_tips": self._generate_optimization_tips(brand_name)
        }

        logger.info(f"SEO optimization complete: score={seo_result['seo_score']}")
        return seo_result

    def _calculate_seo_score(self, brand_name: str, product_description: str) -> int:
        """Calculate SEO score (0-100)."""
        score = 50  # Base score

        # Length optimization (shorter is often better for memorability)
        if 4 <= len(brand_name) <= 12:
            score += 15

        # Keyword presence
        desc_words = set(product_description.lower().split())
        name_words = set(brand_name.lower().split())
        if name_words.intersection(desc_words):
            score += 20

        # Pronounceability (vowel ratio)
        vowels = sum(1 for c in brand_name.lower() if c in 'aeiou')
        vowel_ratio = vowels / max(len(brand_name), 1)
        if 0.3 <= vowel_ratio <= 0.5:
            score += 15

        return min(100, score)

    def _generate_meta_title(self, brand_name: str, description: str) -> str:
        """Generate SEO-optimized meta title."""
        # Extract main benefit/action
        words = description.split()
        key_benefit = " ".join(words[:3]) if len(words) >= 3 else description[:20]

        title = f"{brand_name} - {key_benefit}"
        # Truncate to 60 chars
        return title[:60] if len(title) > 60 else title

    def _generate_meta_description(self, brand_name: str, description: str) -> str:
        """Generate SEO-optimized meta description."""
        # Create compelling description
        desc = f"{brand_name}: {description}"
        if len(desc) < 150:
            desc += " Discover the future of innovation."

        # Truncate to 160 chars
        return desc[:160] if len(desc) > 160 else desc

    def _extract_primary_keywords(self, description: str, industry: str) -> list:
        """Extract primary keywords."""
        words = description.lower().split()
        # Filter meaningful words
        keywords = [w for w in words if len(w) > 4][:3]
        keywords.append(industry.lower())
        return list(set(keywords))

    def _generate_secondary_keywords(self, brand_name: str, industry: str) -> list:
        """Generate secondary/long-tail keywords."""
        return [
            f"{brand_name.lower()} {industry}",
            f"best {industry} solution",
            f"{industry} platform"
        ]

    def _suggest_content_topics(self, brand_name: str, industry: str) -> list:
        """Suggest content marketing topics."""
        return [
            f"How {brand_name} transforms {industry}",
            f"Top {industry} trends for 2025",
            f"{brand_name} vs competitors: A comparison"
        ]

    def _generate_optimization_tips(self, brand_name: str) -> list:
        """Generate SEO optimization tips."""
        tips = ["Use brand name consistently across all platforms"]

        if len(brand_name) > 15:
            tips.append("Consider shortening brand name for better SEO")

        tips.append("Create high-quality backlinks from industry sites")
        tips.append("Optimize page load speed for better rankings")

        return tips
