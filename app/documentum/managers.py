"""
Custom Managers for Documentation Models
"""

from django.db import models


class PublishedDocumentsManager(models.Manager):
    """Manager to filter only published documents"""
    
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
    
    def by_category(self, category_slug):
        """Get published documents in a specific category"""
        return self.get_queryset().filter(category__slug=category_slug)
    
    def recent(self, limit=5):
        """Get most recently updated published documents"""
        return self.get_queryset().order_by('-updated_at')[:limit]
