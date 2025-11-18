"""
Session and memory management for AI Brand Studio.

This module contains:
- Database: Cloud SQL PostgreSQL connection and session service
- Models: Database schema models (sessions, events, generated_brands)
- Memory Bank: Vertex AI Memory Bank integration for long-term memory
"""

from src.session.memory_bank import MemoryBankClient, get_memory_bank_client

__all__ = ['MemoryBankClient', 'get_memory_bank_client']
