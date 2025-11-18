"""
Tests for context compaction functionality.

Verifies that conversation history is correctly summarized while preserving
essential information in long brainstorming sessions.
"""

import pytest
from src.session.context_compaction import ContextCompactor, compact_if_needed


@pytest.fixture
def context_compactor():
    """Create a ContextCompactor instance for testing."""
    return ContextCompactor(project_id="test-project", model_name="gemini-2.0-flash-exp")


@pytest.fixture
def short_conversation():
    """Create a short conversation that doesn't need compaction."""
    return [
        {
            'turn': 1,
            'user_brief': {
                'product_description': 'AI meal planning app',
                'industry': 'food tech',
                'brand_personality': 'friendly'
            }
        },
        {
            'turn': 2,
            'generated_names': ['MealMind', 'FoodFlow', 'NutriPlan']
        },
        {
            'turn': 3,
            'approved_names': ['MealMind', 'FoodFlow']
        }
    ]


@pytest.fixture
def long_conversation():
    """Create a long conversation (20+ turns) that needs compaction."""
    conversation = [
        {
            'turn': 1,
            'user_brief': {
                'product_description': 'Healthcare appointment scheduling platform',
                'industry': 'healthcare',
                'brand_personality': 'professional',
                'target_audience': 'Medical practices'
            }
        }
    ]

    # Add 25 turns of back-and-forth
    for i in range(2, 27):
        if i % 3 == 0:
            # Generation turn
            conversation.append({
                'turn': i,
                'generated_names': [f'Brand{i}A', f'Brand{i}B', f'Brand{i}C']
            })
        elif i % 3 == 1:
            # Feedback turn
            conversation.append({
                'turn': i,
                'feedback': {
                    'liked_names': [f'Brand{i-1}A'],
                    'disliked_names': [f'Brand{i-1}C'],
                    'liked_patterns': ['short names'],
                    'disliked_patterns': ['numbers']
                }
            })
        else:
            # Decision turn
            conversation.append({
                'turn': i,
                'decision': f'Focus on {["medical", "tech", "care"][i % 3]} terminology'
            })

    # Add final approval
    conversation.append({
        'turn': 27,
        'approved_names': ['HealthSync', 'MediFlow', 'CareConnect']
    })

    return conversation


class TestContextCompactor:
    """Test ContextCompactor functionality."""

    def test_estimate_tokens(self, context_compactor):
        """Test token estimation."""
        short_text = "Hello world"
        long_text = "This is a longer piece of text " * 100

        short_tokens = context_compactor.estimate_tokens(short_text)
        long_tokens = context_compactor.estimate_tokens(long_text)

        assert short_tokens > 0
        assert long_tokens > short_tokens
        assert short_tokens < 10  # "Hello world" should be ~3 tokens

    def test_should_compact_short_conversation(self, context_compactor, short_conversation):
        """Test that short conversations don't trigger compaction."""
        should_compact = context_compactor.should_compact(short_conversation)
        assert should_compact is False

    def test_extract_essential_info(self, context_compactor, long_conversation):
        """Test essential information extraction."""
        essential = context_compactor._extract_essential_info(long_conversation)

        # Check user brief is preserved
        assert 'user_brief' in essential
        assert essential['user_brief']['product_description'] == 'Healthcare appointment scheduling platform'
        assert essential['user_brief']['industry'] == 'healthcare'

        # Check approved names are preserved
        assert 'approved_names' in essential
        assert 'HealthSync' in essential['approved_names']
        assert 'MediFlow' in essential['approved_names']
        assert 'CareConnect' in essential['approved_names']

        # Check feedback themes are captured
        assert 'feedback_themes' in essential
        assert len(essential['feedback_themes']['liked']) > 0
        assert len(essential['feedback_themes']['disliked']) > 0

    def test_compact_context_simple(self, context_compactor, long_conversation):
        """Test context compaction with simple summarization."""
        # Force simple summarization by removing model
        context_compactor.model = None

        result = context_compactor.compact_context(long_conversation)

        # Verify result structure
        assert 'summary' in result
        assert 'essential_info' in result
        assert 'compacted_at' in result
        assert 'original_turns' in result
        assert 'compaction_ratio' in result

        # Verify metrics
        assert result['original_turns'] == len(long_conversation)
        assert result['compaction_ratio'] > 0  # Should reduce size
        assert result['compaction_ratio'] <= 1.0

        # Verify essential info is preserved
        essential = result['essential_info']
        assert essential['user_brief']['industry'] == 'healthcare'
        assert len(essential['approved_names']) == 3

    def test_compact_context_preserves_approved_names(self, context_compactor, long_conversation):
        """Test that approved names are always preserved."""
        context_compactor.model = None
        result = context_compactor.compact_context(long_conversation)

        essential = result['essential_info']
        approved = essential['approved_names']

        assert 'HealthSync' in approved
        assert 'MediFlow' in approved
        assert 'CareConnect' in approved

    def test_compact_context_preserves_user_brief(self, context_compactor, long_conversation):
        """Test that user brief is always preserved."""
        context_compactor.model = None
        result = context_compactor.compact_context(long_conversation)

        essential = result['essential_info']
        brief = essential['user_brief']

        assert brief['product_description'] == 'Healthcare appointment scheduling platform'
        assert brief['industry'] == 'healthcare'
        assert brief['brand_personality'] == 'professional'

    def test_compaction_ratio_calculation(self, context_compactor, long_conversation):
        """Test that compaction ratio is calculated correctly."""
        context_compactor.model = None
        result = context_compactor.compact_context(long_conversation)

        # Compaction should significantly reduce size for long conversations
        assert result['compaction_ratio'] > 0.3  # At least 30% reduction
        assert result['compaction_ratio'] < 1.0  # Not 100% reduction

    def test_custom_essential_info(self, context_compactor, short_conversation):
        """Test compaction with custom essential info."""
        custom_essential = {
            'user_brief': {'custom': 'brief'},
            'approved_names': ['CustomName'],
            'feedback_themes': {'liked': ['custom theme'], 'disliked': []}
        }

        context_compactor.model = None
        result = context_compactor.compact_context(
            short_conversation,
            essential_info=custom_essential
        )

        assert result['essential_info'] == custom_essential


class TestCompactIfNeeded:
    """Test convenience function."""

    def test_compact_if_needed_short(self, short_conversation):
        """Test that short conversations return None."""
        result = compact_if_needed(short_conversation, project_id="test-project")
        assert result is None

    def test_compact_if_needed_with_override(self, short_conversation):
        """Test forcing compaction with manual threshold."""
        compactor = ContextCompactor(
            project_id="test-project",
            token_limit=10  # Very low limit to force compaction
        )

        if compactor.should_compact(short_conversation):
            result = compactor.compact_context(short_conversation)
            assert result is not None
            assert 'summary' in result


class TestContextCompactionIntegration:
    """Integration tests for context compaction."""

    def test_multiple_compactions(self, context_compactor):
        """Test multiple rounds of compaction."""
        # Start with a long conversation
        conversation = [{'turn': i, 'content': f'Turn {i}'} for i in range(30)]

        # First compaction
        result1 = context_compactor.compact_context(conversation)
        assert result1['original_turns'] == 30

        # Simulate adding more turns after compaction
        new_turns = [{'turn': i, 'content': f'New turn {i}'} for i in range(30, 60)]

        # Second compaction (would include summary + new turns)
        result2 = context_compactor.compact_context(new_turns)
        assert result2['original_turns'] == 30

    def test_deduplication(self, context_compactor):
        """Test that duplicate names/feedback are deduplicated."""
        conversation = [
            {'turn': 1, 'approved_names': ['Name1', 'Name2']},
            {'turn': 2, 'approved_names': ['Name1', 'Name3']},  # Name1 duplicate
            {'turn': 3, 'feedback': {'liked_names': ['Name1', 'Name1']}}  # Duplicates
        ]

        essential = context_compactor._extract_essential_info(conversation)

        # Check deduplication
        assert essential['approved_names'].count('Name1') == 1
        assert len(essential['approved_names']) == 3  # Name1, Name2, Name3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
