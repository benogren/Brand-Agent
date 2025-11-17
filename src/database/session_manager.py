"""
Session Management for AI Brand Studio.

This module provides session management for tracking user interactions,
brand generation history, and project state. For Phase 2, uses file-based
storage. Production version (Phase 3) will integrate with Cloud SQL.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid

logger = logging.getLogger('brand_studio.session_manager')


class SessionManager:
    """
    Manages user sessions and brand generation history.

    For Phase 2, stores sessions in JSON files. In production, this would
    use Cloud SQL (PostgreSQL) for scalable, persistent storage.
    """

    def __init__(self, storage_dir: str = ".sessions"):
        """
        Initialize the session manager.

        Args:
            storage_dir: Directory to store session files (default: .sessions)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"SessionManager initialized with storage: {self.storage_dir}")

    def create_session(
        self,
        user_id: str = "default_user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session.

        Args:
            user_id: User identifier
            metadata: Optional session metadata

        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "events": [],
            "generated_brands": []
        }

        self._save_session(session_id, session_data)
        logger.info(f"Created new session: {session_id} for user: {user_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary or None if not found
        """
        session_file = self.storage_dir / f"{session_id}.json"
        if not session_file.exists():
            logger.warning(f"Session not found: {session_id}")
            return None

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            logger.debug(f"Retrieved session: {session_id}")
            return session_data
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None

    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False

        # Update fields
        for key, value in updates.items():
            if key not in ['session_id', 'created_at']:  # Protect immutable fields
                session_data[key] = value

        session_data['updated_at'] = datetime.utcnow().isoformat()

        self._save_session(session_id, session_data)
        logger.debug(f"Updated session: {session_id}")
        return True

    def add_event(
        self,
        session_id: str,
        event_type: str,
        content: str,
        author: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an event to the session.

        Args:
            session_id: Session identifier
            event_type: Type of event (e.g., 'message', 'tool_call', 'generation')
            content: Event content
            author: Event author ('user' or 'agent')
            metadata: Optional event metadata

        Returns:
            True if successful, False otherwise
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "author": author,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        session_data['events'].append(event)
        session_data['updated_at'] = datetime.utcnow().isoformat()

        self._save_session(session_id, session_data)
        logger.debug(f"Added {event_type} event to session: {session_id}")
        return True

    def add_generated_brand(
        self,
        session_id: str,
        brand_data: Dict[str, Any]
    ) -> bool:
        """
        Add a generated brand to the session history.

        Args:
            session_id: Session identifier
            brand_data: Brand data dictionary (from name generator)

        Returns:
            True if successful, False otherwise
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False

        # Add brand with timestamp
        brand_record = {
            "brand_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            **brand_data
        }

        session_data['generated_brands'].append(brand_record)
        session_data['updated_at'] = datetime.utcnow().isoformat()

        self._save_session(session_id, session_data)
        logger.info(
            f"Added brand '{brand_data.get('brand_name', 'Unknown')}' "
            f"to session: {session_id}"
        )
        return True

    def get_session_brands(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all brands generated in a session.

        Args:
            session_id: Session identifier

        Returns:
            List of brand dictionaries
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return []

        return session_data.get('generated_brands', [])

    def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List sessions, optionally filtered by user.

        Args:
            user_id: Optional user ID filter
            limit: Maximum number of sessions to return

        Returns:
            List of session summary dictionaries
        """
        sessions = []

        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)

                # Apply user filter
                if user_id and session_data.get('user_id') != user_id:
                    continue

                # Create summary
                summary = {
                    "session_id": session_data['session_id'],
                    "user_id": session_data['user_id'],
                    "created_at": session_data['created_at'],
                    "updated_at": session_data['updated_at'],
                    "event_count": len(session_data.get('events', [])),
                    "brand_count": len(session_data.get('generated_brands', []))
                }
                sessions.append(summary)

            except Exception as e:
                logger.error(f"Error reading session file {session_file}: {e}")
                continue

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)

        return sessions[:limit]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        session_file = self.storage_dir / f"{session_id}.json"
        if not session_file.exists():
            logger.warning(f"Session not found for deletion: {session_id}")
            return False

        try:
            session_file.unlink()
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

    def _save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Save session data to file."""
        session_file = self.storage_dir / f"{session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics about stored sessions.

        Returns:
            Statistics dictionary
        """
        total_sessions = len(list(self.storage_dir.glob("*.json")))
        total_brands = 0
        total_events = 0
        unique_users = set()

        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                total_brands += len(session_data.get('generated_brands', []))
                total_events += len(session_data.get('events', []))
                unique_users.add(session_data.get('user_id'))
            except Exception:
                continue

        return {
            "total_sessions": total_sessions,
            "total_brands_generated": total_brands,
            "total_events": total_events,
            "unique_users": len(unique_users),
            "storage_location": str(self.storage_dir.absolute())
        }


# Singleton instance for global use
_session_manager_instance: Optional[SessionManager] = None


def get_session_manager(storage_dir: str = ".sessions") -> SessionManager:
    """
    Get or create the global SessionManager instance.

    Args:
        storage_dir: Directory for session storage

    Returns:
        SessionManager singleton instance
    """
    global _session_manager_instance

    if _session_manager_instance is None:
        _session_manager_instance = SessionManager(storage_dir)

    return _session_manager_instance
