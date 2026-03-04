"""BaseRepository re-export for jobs service repositories.

All repositories in this service inherit from the shared BaseRepository.
"""

from tp360_shared.db.base_repository import BaseRepository

__all__ = ["BaseRepository"]
