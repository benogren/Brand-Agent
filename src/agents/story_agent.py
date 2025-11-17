"""
Brand Story Generator Agent for AI Brand Studio.

This agent creates compelling brand narratives, taglines, and marketing copy
that brings brand names to life.
"""

import logging
import os
from typing import Dict, Any, List
from google.cloud import aiplatform
from google import genai
from google.genai import types

try:
    from google_genai.adk import LlmAgent
except ImportError:
    from src.utils.mock_adk import LlmAgent

logger = logging.getLogger('brand_studio.story_agent')


STORY_AGENT_INSTRUCTION = """
You are a brand storytelling expert for AI Brand Studio. Your role is to create
compelling narratives that bring brand names to life and connect with audiences.

## YOUR RESPONSIBILITIES

1. **Generate Taglines (5 options):**
   - 5-8 words each
   - Memorable and action-oriented
   - Match brand personality
   - Communicate core value

2. **Craft Brand Story (200-300 words):**
   - Origin and purpose
   - Unique value proposition
   - Target audience connection
   - Differentiation from competitors
   - Emotional resonance

3. **Create Landing Page Hero Copy (50-100 words):**
   - Attention-grabbing headline
   - Clear value proposition
   - Call-to-action
   - Conversion-focused

4. **Write Value Proposition (20-30 words):**
   - Clear and compelling
   - Benefit-focused
   - Unique and memorable

## OUTPUT FORMAT

```
{
  "taglines": [
    "Tagline option 1",
    "Tagline option 2",
    "Tagline option 3",
    "Tagline option 4",
    "Tagline option 5"
  ],
  "brand_story": "Full narrative...",
  "hero_copy": "Landing page hero section...",
  "value_proposition": "Clear value prop statement"
}
```
"""


class StoryAgent:
    """Brand Story Generator Agent."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-pro"
    ):
        """Initialize the story agent."""
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        logger.info("Initializing StoryAgent")

        try:
            aiplatform.init(project=project_id, location=location)
        except Exception as e:
            logger.warning(f"Vertex AI init issue: {e}")

        self.agent = LlmAgent(
            name="story_generator",
            model=model_name,
            description="Generates brand stories and marketing copy",
            instruction=STORY_AGENT_INSTRUCTION
        )
        logger.info("Story LlmAgent initialized")

    def generate_brand_story(
        self,
        brand_name: str,
        product_description: str,
        brand_personality: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive brand story and marketing copy.

        Args:
            brand_name: The brand name
            product_description: What the product does
            brand_personality: Tone (playful, professional, innovative, luxury)
            target_audience: Who it's for

        Returns:
            Dictionary with taglines, story, hero copy, and value prop
        """
        logger.info(f"Generating brand story for: {brand_name}")

        # For Phase 2, use real LLM if available
        try:
            story_content = self._generate_with_llm(
                brand_name=brand_name,
                product_description=product_description,
                brand_personality=brand_personality,
                target_audience=target_audience
            )
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, using templates")
            story_content = self._generate_with_templates(
                brand_name=brand_name,
                product_description=product_description,
                brand_personality=brand_personality
            )

        logger.info(f"Brand story generated for {brand_name}")
        return story_content

    def _generate_with_llm(
        self,
        brand_name: str,
        product_description: str,
        brand_personality: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """Generate story using real LLM (Google AI API)."""
        # Clear GCP env vars to use Google AI API
        saved_project = os.environ.get('GOOGLE_CLOUD_PROJECT')
        saved_location = os.environ.get('GOOGLE_CLOUD_LOCATION')
        saved_vertexai = os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')

        try:
            os.environ.pop('GOOGLE_CLOUD_PROJECT', None)
            os.environ.pop('GOOGLE_CLOUD_LOCATION', None)
            os.environ.pop('GOOGLE_GENAI_USE_VERTEXAI', None)

            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise Exception("GOOGLE_API_KEY not available")

            client = genai.Client(api_key=api_key)

            prompt = f"""
Create a compelling brand identity for "{brand_name}".

Product: {product_description}
Personality: {brand_personality}
Target Audience: {target_audience}

Generate:
1. Five tagline options (5-8 words each)
2. Brand story (200-300 words)
3. Hero section copy (50-100 words)
4. Value proposition (20-30 words)

Return as JSON with keys: taglines (array), brand_story (string), hero_copy (string), value_proposition (string)
"""

            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.9, top_p=0.95)
            )

            # Parse response
            import json
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            return json.loads(response_text)

        finally:
            if saved_project:
                os.environ['GOOGLE_CLOUD_PROJECT'] = saved_project
            if saved_location:
                os.environ['GOOGLE_CLOUD_LOCATION'] = saved_location
            if saved_vertexai:
                os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = saved_vertexai

    def _generate_with_templates(
        self,
        brand_name: str,
        product_description: str,
        brand_personality: str
    ) -> Dict[str, Any]:
        """Generate story using templates (fallback)."""
        personality_adjectives = {
            'playful': 'fun, creative, innovative',
            'professional': 'reliable, efficient, trustworthy',
            'innovative': 'cutting-edge, transformative, forward-thinking',
            'luxury': 'premium, exclusive, sophisticated'
        }

        adjectives = personality_adjectives.get(brand_personality, 'innovative, reliable')

        return {
            "taglines": [
                f"{brand_name}: Where innovation meets simplicity",
                f"Elevate your experience with {brand_name}",
                f"{brand_name} - The future is here",
                f"Transform your world with {brand_name}",
                f"{brand_name}: Built for tomorrow"
            ],
            "brand_story": f"{brand_name} was born from a simple idea: {product_description} should be accessible, {adjectives}, and transformative. We believe that great experiences come from understanding what people truly need. Our mission is to deliver solutions that not only meet expectations but exceed them. With {brand_name}, you're not just using a product—you're joining a community of forward-thinkers who refuse to settle for the status quo.",
            "hero_copy": f"Welcome to {brand_name}. We're revolutionizing {product_description} with a {brand_personality} approach that puts you first. Experience the difference that thoughtful design and cutting-edge technology can make.",
            "value_proposition": f"{brand_name} delivers {product_description} that's {adjectives}, designed for modern needs."
        }
