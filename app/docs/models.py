"""
Documentation Hub Models
========================

Models for managing technical documentation with Markdown support,
versioning, and SEO optimization.
"""

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from .managers import PublishedDocumentsManager

 
class Category(models.Model):
    """Documentation categories (e.g., Infrastructure, Backend, Product Strategy)"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Infrastructure')"
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        help_text="URL-friendly version (auto-generated)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of this category"
    )
    icon = models.CharField(
        max_length=50,
        default='fa-book',
        help_text="FontAwesome icon class (e.g., 'fa-server')"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower = first)"
    )
    is_visible = models.BooleanField(
        default=True,
        help_text="Show in public category list"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'docs'
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('docs:category_detail', kwargs={'slug': self.slug})

    @property
    def document_count(self):
        """Count of published documents in this category"""
        return self.documents.filter(status='published').count()


class Document(models.Model):
    """Technical documentation articles"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
        ('deprecated', 'Deprecated'),
    ]
    
    # Core fields
    title = models.CharField(
        max_length=200,
        help_text="Document title"
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        help_text="URL-friendly version (auto-generated)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Documentation category"
    )
    
    # Content
    content_markdown = models.TextField(
        help_text="Markdown source (editable)"
    )
    content_html = models.TextField(
        editable=False,
        blank=True,
        help_text="Rendered HTML (auto-generated)"
    )
    
    # Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Publication status"
    )
    last_revision = models.DateTimeField(
        auto_now=True,
        help_text="Last modification date"
    )
    stack_version = models.CharField(
        max_length=100,
        blank=True,
        help_text="Tech stack version (e.g., 'Django 5.1, Python 3.12')"
    )
    
    # SEO
    meta_description = models.CharField(
        max_length=160,
        help_text="SEO meta description (max 160 chars)"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords for SEO"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Managers
    objects = models.Manager()
    published = PublishedDocumentsManager()

    class Meta:
        app_label = 'docs'
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status', '-updated_at']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Render Markdown to HTML
        from .utils import render_markdown
        self.content_html = render_markdown(self.content_markdown)
        
        super().save(*args, **kwargs)
        
        # Create version history
        if self.pk:
            DocumentVersion.objects.create(
                document=self,
                content_markdown=self.content_markdown,
                changed_by='admin',  # TODO: Use request.user
                change_summary=f'Updated {self.title}'
            )

    def get_absolute_url(self):
        return reverse('docs:document_detail', kwargs={
            'category_slug': self.category.slug,
            'slug': self.slug
        })

    @property
    def reading_time(self):
        """Estimated reading time in minutes"""
        words = len(self.content_markdown.split())
        return max(1, round(words / 200))  # 200 words per minute

    @property
    def is_published(self):
        return self.status == 'published'


class DocumentVersion(models.Model):
    """Version history for documents"""
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text="Parent document"
    )
    content_markdown = models.TextField(
        help_text="Markdown content at this version"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Version creation timestamp"
    )
    changed_by = models.CharField(
        max_length=100,
        help_text="User who made the change"
    )
    change_summary = models.TextField(
        blank=True,
        help_text="Summary of changes made"
    )

    class Meta:
        app_label = 'docs'
        verbose_name = "Document Version"
        verbose_name_plural = "Document Versions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', '-created_at']),
        ]

    def __str__(self):
        return f"{self.document.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
