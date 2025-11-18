"""
Context Compaction for AI Brand Studio.

Manages conversation history summarization to prevent context window overflow
in long brainstorming sessions (20+ turns).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os

logger = logging.getLogger('brand_studio.context_compaction')

# Try to import Vertex AI for summarization
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False
    logger.warning("Vertex AI not available. Context compaction will use simple truncation.")


class ContextCompactor:
    """
    Manages context compaction for long brainstorming sessions.

    Automatically summarizes conversation history when token limits are
    approached, preserving essential information while reducing context size.

    Essential information preserved:
    - User brief (product description, target audience, brand personality, industry)
    - Selected/approved brand names
    - Key feedback themes (liked patterns, disliked elements)
    - Critical decisions and constraints
    """

    # Approximate token limits (conservative estimates)
    TOKEN_LIMIT_GEMINI_FLASH = 32000  # Gemini 2.5 Flash context window
    TOKEN_LIMIT_GEMINI_PRO = 128000   # Gemini 2.5 Pro context window
    COMPACTION_THRESHOLD = 0.75       # Compact when 75% of limit reached

    # Approximate tokens per character (English text)
    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash-exp",
        token_limit: Optional[int] = None
    ):
        """
        Initialize context compactor.

        Args:
            project_id: Google Cloud project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            location: Google Cloud region
            model_name: Gemini model for summarization
            token_limit: Custom token limit (defaults based on model)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        self.model_name = model_name

        # Set token limit based on model
        if token_limit:
            self.token_limit = token_limit
        elif 'flash' in model_name.lower():
            self.token_limit = self.TOKEN_LIMIT_GEMINI_FLASH
        else:
            self.token_limit = self.TOKEN_LIMIT_GEMINI_PRO

        self.compaction_threshold_tokens = int(self.token_limit * self.COMPACTION_THRESHOLD)

        logger.info(
            f"ContextCompactor initialized: model={model_name}, "
            f"token_limit={self.token_limit}, "
            f"compaction_threshold={self.compaction_threshold_tokens}"
        )

        # Initialize Vertex AI if available
        if VERTEXAI_AVAILABLE and self.project_id:
            try:
                vertexai.init(project=self.project_id, location=self.location)
                self.model = GenerativeModel(model_name)
                logger.info("Vertex AI initialized for context compaction")
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI: {e}. Using simple compaction.")
                self.model = None
        else:
            self.model = None

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses a simple heuristic: ~4 characters per token for English text.
        This is conservative to ensure we don't exceed limits.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // self.CHARS_PER_TOKEN

    def should_compact(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """
        Determine if conversation history should be compacted.

        Args:
            conversation_history: List of conversation turn dictionaries

        Returns:
            True if compaction is needed
        """
        # Serialize conversation to estimate size
        import json
        history_text = json.dumps(conversation_history)
        estimated_tokens = self.estimate_tokens(history_text)

        should_compact = estimated_tokens >= self.compaction_threshold_tokens

        if should_compact:
            logger.info(
                f"Context compaction needed: {estimated_tokens} tokens "
                f">= {self.compaction_threshold_tokens} threshold"
            )

        return should_compact

    def compact_context(
        self,
        conversation_history: List[Dict[str, Any]],
        essential_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compact conversation history while preserving essential information.

        Args:
            conversation_history: List of conversation turns
            essential_info: Essential information to preserve (user brief, key decisions)

        Returns:
            Dictionary with:
            - summary: Summarized conversation
            - essential_info: Preserved essential information
            - compacted_at: Timestamp of compaction
            - original_turns: Number of original turns
            - compaction_ratio: Reduction in size (0.0-1.0)
        """
        logger.info(f"Compacting conversation with {len(conversation_history)} turns")

        # Extract essential information if not provided
        if essential_info is None:
            essential_info = self._extract_essential_info(conversation_history)

        # Generate summary
        if self.model:
            summary = self._summarize_with_gemini(conversation_history, essential_info)
        else:
            summary = self._summarize_simple(conversation_history, essential_info)

        # Calculate compaction ratio
        import json
        original_size = len(json.dumps(conversation_history))
        compacted_size = len(json.dumps(summary))
        compaction_ratio = 1.0 - (compacted_size / original_size) if original_size > 0 else 0.0

        logger.info(
            f"Context compacted: {len(conversation_history)} turns → summary. "
            f"Reduction: {compaction_ratio * 100:.1f}%"
        )

        return {
            'summary': summary,
            'essential_info': essential_info,
            'compacted_at': datetime.now(timezone.utc).isoformat(),
            'original_turns': len(conversation_history),
            'compaction_ratio': compaction_ratio
        }

    def _extract_essential_info(
        self,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract essential information from conversation history.

        Preserves:
        - Initial user brief
        - All approved/selected brand names
        - Key feedback patterns
        - Important decisions
        """
        essential = {
            'user_brief': {},
            'approved_names': [],
            'feedback_themes': {
                'liked': [],
                'disliked': []
            },
            'key_decisions': []
        }

        for turn in conversation_history:
            # Extract user brief from first turn
            if 'user_brief' in turn and not essential['user_brief']:
                essential['user_brief'] = turn['user_brief']

            # Extract approved names
            if 'approved_names' in turn:
                essential['approved_names'].extend(turn['approved_names'])

            # Extract feedback
            if 'feedback' in turn:
                feedback = turn['feedback']
                if 'liked_names' in feedback:
                    essential['feedback_themes']['liked'].extend(feedback['liked_names'])
                if 'disliked_names' in feedback:
                    essential['feedback_themes']['disliked'].extend(feedback['disliked_names'])

            # Extract key decisions
            if 'decision' in turn or 'constraint' in turn:
                essential['key_decisions'].append({
                    'type': turn.get('type', 'unknown'),
                    'content': turn.get('decision') or turn.get('constraint')
                })

        # Deduplicate
        essential['approved_names'] = list(set(essential['approved_names']))
        essential['feedback_themes']['liked'] = list(set(essential['feedback_themes']['liked']))
        essential['feedback_themes']['disliked'] = list(set(essential['feedback_themes']['disliked']))

        return essential

    def _summarize_with_gemini(
        self,
        conversation_history: List[Dict[str, Any]],
        essential_info: Dict[str, Any]
    ) -> str:
        """
        Summarize conversation using Gemini model.

        Args:
            conversation_history: Full conversation history
            essential_info: Essential information to preserve

        Returns:
            Summarized conversation text
        """
        import json

        # Prepare prompt for summarization
        history_text = json.dumps(conversation_history, indent=2)
        essential_text = json.dumps(essential_info, indent=2)

        prompt = f"""
You are summarizing a brand naming brainstorming session to reduce context size while preserving essential information.

CONVERSATION HISTORY:
{history_text}

ESSENTIAL INFORMATION (MUST BE PRESERVED):
{essential_text}

Please create a concise summary that:
1. Captures the main flow of the conversation
2. Preserves all essential information (user brief, approved names, feedback themes)
3. Highlights key decision points and iterations
4. Removes redundant or non-essential details
5. Is structured and easy to parse

Keep the summary under 500 words but ensure NO essential information is lost.

SUMMARY:
"""

        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            logger.info("Successfully generated summary using Gemini")
            return summary
        except Exception as e:
            logger.error(f"Gemini summarization failed: {e}. Using simple summarization.")
            return self._summarize_simple(conversation_history, essential_info)

    def _summarize_simple(
        self,
        conversation_history: List[Dict[str, Any]],
        essential_info: Dict[str, Any]
    ) -> str:
        """
        Simple rule-based summarization fallback.

        Args:
            conversation_history: Full conversation history
            essential_info: Essential information

        Returns:
            Simple text summary
        """
        summary_parts = []

        # Add user brief
        if essential_info.get('user_brief'):
            brief = essential_info['user_brief']
            summary_parts.append(
                f"User Brief: {brief.get('product_description', 'N/A')} | "
                f"Industry: {brief.get('industry', 'N/A')} | "
                f"Personality: {brief.get('brand_personality', 'N/A')}"
            )

        # Add conversation stats
        summary_parts.append(f"Total conversation turns: {len(conversation_history)}")

        # Add approved names
        if essential_info.get('approved_names'):
            names = ', '.join(essential_info['approved_names'])
            summary_parts.append(f"Approved names: {names}")

        # Add feedback themes
        feedback = essential_info.get('feedback_themes', {})
        if feedback.get('liked'):
            summary_parts.append(f"Liked patterns: {', '.join(feedback['liked'][:5])}")
        if feedback.get('disliked'):
            summary_parts.append(f"Disliked patterns: {', '.join(feedback['disliked'][:5])}")

        # Add key decisions
        if essential_info.get('key_decisions'):
            decisions = [d.get('content', 'N/A') for d in essential_info['key_decisions']]
            summary_parts.append(f"Key decisions: {'; '.join(decisions[:3])}")

        summary = "\n".join(summary_parts)
        logger.info("Generated simple rule-based summary")
        return summary


# Convenience function
def compact_if_needed(
    conversation_history: List[Dict[str, Any]],
    essential_info: Optional[Dict[str, Any]] = None,
    project_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Compact conversation history if needed.

    Args:
        conversation_history: Conversation turns
        essential_info: Essential information to preserve
        project_id: Google Cloud project ID

    Returns:
        Compaction result dictionary if compaction was performed, None otherwise
    """
    compactor = ContextCompactor(project_id=project_id)

    if compactor.should_compact(conversation_history):
        return compactor.compact_context(conversation_history, essential_info)

    return None
