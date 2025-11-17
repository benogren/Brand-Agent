"""
Workflow pattern implementations for multi-agent orchestration.

This module contains:
- Parallel: Execute agents in parallel (research + name generation)
- Sequential: Execute agents in sequence (generation → validation → SEO → story)
- Loop: Loop refinement with max iterations (regenerate if validation fails)
"""
