"""
Test suite for Brand Collision Detection Agent.

Tests the collision detection agent's ability to identify brand conflicts
through web search analysis.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.collision_agent import BrandCollisionAgent


class TestBrandCollisionAgent(unittest.TestCase):
    """Test cases for BrandCollisionAgent."""

    def setUp(self):
        """Set up test fixtures."""
        # Get project ID from environment
        self.project_id = os.getenv('GCP_PROJECT_ID', 'test-project')
        self.location = 'us-central1'

    def test_collision_agent_initialization(self):
        """Test that collision agent initializes correctly."""
        agent = BrandCollisionAgent(
            project_id=self.project_id,
            location=self.location
        )

        self.assertIsNotNone(agent)
        self.assertEqual(agent.project_id, self.project_id)
        self.assertEqual(agent.location, self.location)

    @unittest.skipIf(
        not os.getenv('RUN_INTEGRATION_TESTS'),
        "Skipping integration test (set RUN_INTEGRATION_TESTS=1 to run)"
    )
    def test_collision_analysis_high_risk(self):
        """
        Test collision analysis for a name with high collision risk.

        Uses 'Apple' which should have high collision risk due to Apple Inc.
        """
        agent = BrandCollisionAgent(
            project_id=self.project_id,
            location=self.location
        )

        result = agent.analyze_brand_collision(
            brand_name="Apple",
            industry="technology",
            product_description="A new tech product"
        )

        # Verify structure
        self.assertIn('brand_name', result)
        self.assertIn('collision_risk_level', result)
        self.assertIn('risk_summary', result)

        # For 'Apple', expect high collision risk
        self.assertEqual(result['brand_name'], 'Apple')
        # Note: actual risk level depends on search results
        # but Apple should generally be high risk
        self.assertIn(
            result['collision_risk_level'],
            ['high', 'medium']  # Could be medium if search is specific to tech
        )

    @unittest.skipIf(
        not os.getenv('RUN_INTEGRATION_TESTS'),
        "Skipping integration test (set RUN_INTEGRATION_TESTS=1 to run)"
    )
    def test_collision_analysis_low_risk(self):
        """
        Test collision analysis for a unique invented name.

        Uses a random invented name that should have low/no collision risk.
        """
        agent = BrandCollisionAgent(
            project_id=self.project_id,
            location=self.location
        )

        # Use a very unique invented name
        unique_name = "Zynthiqor"  # Very unlikely to collide

        result = agent.analyze_brand_collision(
            brand_name=unique_name,
            industry="technology",
            product_description="A new tech product"
        )

        # Verify structure
        self.assertIn('brand_name', result)
        self.assertIn('collision_risk_level', result)
        self.assertIn('risk_summary', result)

        self.assertEqual(result['brand_name'], unique_name)
        # Expect low or no collision risk for invented name
        self.assertIn(
            result['collision_risk_level'],
            ['low', 'none', 'unknown']
        )

    @unittest.skipIf(
        not os.getenv('RUN_INTEGRATION_TESTS'),
        "Skipping integration test (set RUN_INTEGRATION_TESTS=1 to run)"
    )
    def test_collision_analysis_error_handling(self):
        """Test that collision agent handles errors gracefully."""
        agent = BrandCollisionAgent(
            project_id=self.project_id,
            location=self.location
        )

        # Test with empty brand name
        result = agent.analyze_brand_collision(
            brand_name="",
            industry="technology",
            product_description=""
        )

        # Should return error but not crash
        self.assertIn('brand_name', result)
        # May have unknown risk or error
        self.assertIsNotNone(result.get('collision_risk_level'))

    def test_collision_result_structure(self):
        """Test that collision results have expected structure."""
        # Mock the model to avoid actual API calls in unit test
        with patch('src.agents.collision_agent.GenerativeModel') as mock_model:
            # Create mock response
            mock_response = MagicMock()
            mock_response.text = '''
            {
                "brand_name": "TestBrand",
                "collision_risk_level": "medium",
                "risk_summary": "Similar to existing brand in related industry",
                "top_results_analysis": {
                    "dominant_entity": "TestBrand Inc.",
                    "industry": "technology",
                    "result_types": ["company_website", "social_media"]
                },
                "collision_details": [
                    {
                        "entity_name": "TestBrand Inc.",
                        "entity_type": "company",
                        "industry": "technology",
                        "risk_explanation": "Existing tech company with same name"
                    }
                ],
                "differentiation_challenges": [
                    "SEO competition from established brand"
                ],
                "recommendation": "caution",
                "recommendation_details": "Can proceed with careful differentiation",
                "mitigations": [
                    "Add qualifier to brand name",
                    "Focus on niche market differentiation"
                ]
            }
            '''

            mock_model_instance = MagicMock()
            mock_model_instance.generate_content.return_value = mock_response
            mock_model.return_value = mock_model_instance

            agent = BrandCollisionAgent(
                project_id=self.project_id,
                location=self.location
            )

            result = agent.analyze_brand_collision(
                brand_name="TestBrand",
                industry="technology"
            )

            # Verify all expected fields are present
            expected_fields = [
                'brand_name',
                'collision_risk_level',
                'risk_summary',
                'top_results_analysis',
                'collision_details',
                'differentiation_challenges',
                'recommendation',
                'recommendation_details',
                'mitigations'
            ]

            for field in expected_fields:
                self.assertIn(field, result, f"Missing field: {field}")


if __name__ == '__main__':
    unittest.main()
