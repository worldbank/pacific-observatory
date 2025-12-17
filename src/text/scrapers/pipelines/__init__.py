"""
Pipelines package for data processing and storage.
"""

from .storage import CSVStorage
from .cleaning import apply_cleaning, CLEANING_FUNCTIONS

__all__ = ['CSVStorage', 'apply_cleaning', 'CLEANING_FUNCTIONS']
