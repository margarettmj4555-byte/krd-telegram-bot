"""
Init file for handlers package
"""

from .main import router as main_router
from .admin import router as admin_router

__all__ = ['main_router', 'admin_router']
