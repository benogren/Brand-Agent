"""
Tests for the Name Generator Agent.

This module tests the name generator's ability to create brand names
using multiple strategies and brand personality customization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.name_generator import (
    NameGeneratorAgent,
    NAME_GENERATOR_INSTRUCTION
)


class TestNameGeneratorAgent:
    """Test the NameGeneratorAgent class."""

    @patch('google.cloud.aiplatform.init')
    def test_agent_initialization(self, mock_init):
        """Test that agent initializes correctly."""
        agent = NameGeneratorAgent(
            project_id='test-project',
            location='us-central1'
        )

        assert agent.project_id == 'test-project'
        assert agent.location == 'us-central1'
        assert agent.model_name == 'gemini-2.5-pro'
        assert agent.agent is not None
        mock_init.assert_called_once_with(
            project='test-project',
            location='us-central1'
        )

    @patch('google.cloud.aiplatform.init')
    def test_custom_model_name(self, mock_init):
        """Test initialization with custom model name."""
        agent = NameGeneratorAgent(
            project_id='test-project',
            model_name='custom-model'
        )

        assert agent.model_name == 'custom-model'


class TestGenerateNames:
    """Test the generate_names method."""

    @patch('google.cloud.aiplatform.init')
    def test_generate_names_default_params(self, mock_init):
        """Test generating names with default parameters."""
        agent = NameGeneratorAgent(project_id='test-project')

        names = agent.generate_names(
            product_description='AI meal planning app for busy parents'
        )

        # Should generate 30 names by default
        assert len(names) == 30

        # Check structure of first name
        assert 'brand_name' in names[0]
        assert 'naming_strategy' in names[0]
        assert 'rationale' in names[0]
        assert 'tagline' in names[0]
        assert 'syllables' in names[0]
        assert 'memorable_score' in names[0]

    @patch('google.cloud.aiplatform.init')
    def test_generate_names_custom_count(self, mock_init):
        """Test generating custom number of names."""
        agent = NameGeneratorAgent(project_id='test-project')

        # Test minimum (20)
        names = agent.generate_names(
            product_description='Test product',
            num_names=20
        )
        assert len(names) == 20

        # Test maximum (50)
        names = agent.generate_names(
            product_description='Test product',
            num_names=50
        )
        assert len(names) == 50

        # Test clamping (below minimum)
        names = agent.generate_names(
            product_description='Test product',
            num_names=10
        )
        assert len(names) == 20  # Should clamp to minimum

        # Test clamping (above maximum)
        names = agent.generate_names(
            product_description='Test product',
            num_names=100
        )
        assert len(names) == 50  # Should clamp to maximum

    @patch('google.cloud.aiplatform.init')
    def test_brand_personality_validation(self, mock_init):
        """Test that invalid brand personalities default to professional."""
        agent = NameGeneratorAgent(project_id='test-project')

        # Valid personality
        names = agent.generate_names(
            product_description='Test product',
            brand_personality='playful'
        )
        assert len(names) > 0

        # Invalid personality (should default to 'professional')
        names = agent.generate_names(
            product_description='Test product',
            brand_personality='invalid_personality'
        )
        assert len(names) > 0

    @patch('google.cloud.aiplatform.init')
    def test_all_naming_strategies_used(self, mock_init):
        """Test that all naming strategies are represented."""
        agent = NameGeneratorAgent(project_id='test-project')

        names = agent.generate_names(
            product_description='Test product',
            num_names=40  # Enough to ensure all strategies
        )

        strategies = set(name['naming_strategy'] for name in names)

        # Should have all 4 strategies
        assert 'portmanteau' in strategies
        assert 'descriptive' in strategies
        assert 'invented' in strategies
        assert 'acronym' in strategies

    @patch('google.cloud.aiplatform.init')
    def test_healthcare_app_example(self, mock_init):
        """Test generating names for healthcare app."""
        agent = NameGeneratorAgent(project_id='test-project')

        names = agent.generate_names(
            product_description='AI-powered telemedicine app for remote consultations',
            target_audience='Patients aged 40-65',
            brand_personality='professional',
            industry='healthcare'
        )

        assert len(names) == 30
        assert all('brand_name' in name for name in names)
        assert all('rationale' in name for name in names)
        assert all('tagline' in name for name in names)

    @patch('google.cloud.aiplatform.init')
    def test_fintech_app_example(self, mock_init):
        """Test generating names for fintech app."""
        agent = NameGeneratorAgent(project_id='test-project')

        names = agent.generate_names(
            product_description='Peer-to-peer lending platform for small businesses',
            target_audience='Small business owners',
            brand_personality='innovative',
            industry='fintech'
        )

        assert len(names) == 30
        # Verify all names have required fields
        for name in names:
            assert isinstance(name['brand_name'], str)
            assert isinstance(name['naming_strategy'], str)
            assert isinstance(name['rationale'], str)
            assert isinstance(name['tagline'], str)
            assert isinstance(name['syllables'], int)
            assert isinstance(name['memorable_score'], int)

    @patch('google.cloud.aiplatform.init')
    def test_ecommerce_app_example(self, mock_init):
        """Test generating names for e-commerce app."""
        agent = NameGeneratorAgent(project_id='test-project')

        names = agent.generate_names(
            product_description='Sustainable fashion marketplace for eco-conscious shoppers',
            target_audience='Women aged 25-40',
            brand_personality='playful',
            industry='e_commerce'
        )

        assert len(names) == 30
        # Check that personality is reflected (placeholder implementation)
        assert all(name['brand_name'] for name in names)


class TestValidateNameQuality:
    """Test the validate_name_quality method."""

    @patch('google.cloud.aiplatform.init')
    def test_validate_good_name(self, mock_init):
        """Test validation of a good brand name."""
        agent = NameGeneratorAgent(project_id='test-project')

        result = agent.validate_name_quality('Spotify')

        assert result['length_ok'] is True
        assert result['syllable_count'] > 0
        assert result['pronounceable'] is True
        assert 'unique_score' in result

    @patch('google.cloud.aiplatform.init')
    def test_validate_short_name(self, mock_init):
        """Test validation of too-short name."""
        agent = NameGeneratorAgent(project_id='test-project')

        result = agent.validate_name_quality('X')

        assert result['length_ok'] is False  # Too short

    @patch('google.cloud.aiplatform.init')
    def test_validate_long_name(self, mock_init):
        """Test validation of too-long name."""
        agent = NameGeneratorAgent(project_id='test-project')

        result = agent.validate_name_quality('ThisIsAVeryLongBrandName')

        assert result['length_ok'] is False  # Too long


class TestSyllableEstimation:
    """Test the _estimate_syllables method."""

    @patch('google.cloud.aiplatform.init')
    def test_estimate_syllables_simple(self, mock_init):
        """Test syllable estimation for simple words."""
        agent = NameGeneratorAgent(project_id='test-project')

        assert agent._estimate_syllables('cat') == 1
        assert agent._estimate_syllables('table') == 2
        assert agent._estimate_syllables('beautiful') == 3

    @patch('google.cloud.aiplatform.init')
    def test_estimate_syllables_brand_names(self, mock_init):
        """Test syllable estimation for brand names."""
        agent = NameGeneratorAgent(project_id='test-project')

        assert agent._estimate_syllables('Spotify') >= 2
        assert agent._estimate_syllables('Google') >= 2
        assert agent._estimate_syllables('Amazon') >= 3

    @patch('google.cloud.aiplatform.init')
    def test_estimate_syllables_empty(self, mock_init):
        """Test syllable estimation for edge cases."""
        agent = NameGeneratorAgent(project_id='test-project')

        # Single letter should have 1 syllable
        assert agent._estimate_syllables('a') >= 1


class TestPronounceability:
    """Test the _check_pronounceability method."""

    @patch('google.cloud.aiplatform.init')
    def test_pronounceable_words(self, mock_init):
        """Test that common words are pronounceable."""
        agent = NameGeneratorAgent(project_id='test-project')

        assert agent._check_pronounceability('Spotify') is True
        assert agent._check_pronounceability('Amazon') is True
        assert agent._check_pronounceability('Google') is True

    @patch('google.cloud.aiplatform.init')
    def test_unpronounceable_words(self, mock_init):
        """Test that consonant-heavy words are not pronounceable."""
        agent = NameGeneratorAgent(project_id='test-project')

        # Words with too few vowels
        assert agent._check_pronounceability('xyzqrs') is False
        assert agent._check_pronounceability('bcdfg') is False

    @patch('google.cloud.aiplatform.init')
    def test_pronounceability_edge_cases(self, mock_init):
        """Test pronounceability edge cases."""
        agent = NameGeneratorAgent(project_id='test-project')

        # Too many vowels
        assert agent._check_pronounceability('aeiouy') is False


class TestFormatUserBrief:
    """Test the _format_user_brief method."""

    @patch('google.cloud.aiplatform.init')
    def test_format_brief_complete(self, mock_init):
        """Test formatting complete user brief."""
        agent = NameGeneratorAgent(project_id='test-project')

        brief = agent._format_user_brief(
            product_description='AI meal planning app',
            target_audience='Busy parents',
            brand_personality='warm',
            industry='food_tech',
            num_names=25
        )

        assert 'AI meal planning app' in brief
        assert 'Busy parents' in brief
        assert 'warm' in brief
        assert 'food_tech' in brief
        assert '25' in brief

    @patch('google.cloud.aiplatform.init')
    def test_format_brief_minimal(self, mock_init):
        """Test formatting minimal user brief."""
        agent = NameGeneratorAgent(project_id='test-project')

        brief = agent._format_user_brief(
            product_description='Test product',
            target_audience='',
            brand_personality='professional',
            industry='general',
            num_names=30
        )

        assert 'Test product' in brief
        assert 'General audience' in brief
        assert 'professional' in brief


class TestInstructionPrompt:
    """Test the NAME_GENERATOR_INSTRUCTION prompt."""

    def test_instruction_contains_strategies(self):
        """Test that instruction includes all naming strategies."""
        assert 'portmanteau' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'descriptive' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'invented' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'acronym' in NAME_GENERATOR_INSTRUCTION.lower()

    def test_instruction_contains_personalities(self):
        """Test that instruction includes brand personalities."""
        assert 'playful' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'professional' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'innovative' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'luxury' in NAME_GENERATOR_INSTRUCTION.lower()

    def test_instruction_contains_quality_criteria(self):
        """Test that instruction includes quality criteria."""
        assert 'memorable' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'pronounceable' in NAME_GENERATOR_INSTRUCTION.lower()
        assert 'syllable' in NAME_GENERATOR_INSTRUCTION.lower()

    def test_instruction_specifies_output_format(self):
        """Test that instruction specifies output format."""
        assert 'brand_name' in NAME_GENERATOR_INSTRUCTION
        assert 'naming_strategy' in NAME_GENERATOR_INSTRUCTION
        assert 'rationale' in NAME_GENERATOR_INSTRUCTION
        assert 'tagline' in NAME_GENERATOR_INSTRUCTION


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
