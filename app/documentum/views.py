"""
Views for Documentation Hub
"""

from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Category, Document


class CategoryListView(ListView):
    """List all visible categories"""
    model = Category
    template_name = 'documentum/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return (
            Category.objects.filter(is_visible=True)
            .order_by('order', 'name')
            .prefetch_related('documents')
        )


class DocumentListView(ListView):
    """List published documents in a specific category (paginated)"""
    model = Document
    template_name = 'documentum/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_visible=True
        )
        return (
            Document.published.filter(category=self.category)
            .only('title', 'slug', 'meta_description', 'updated_at', 'stack_version')
            .order_by('-updated_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class DocumentDetailView(DetailView):
    """Display a single document with TOC"""
    model = Document
    template_name = 'documentum/document_detail.html'
    context_object_name = 'document'
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            Document.published,
            category__slug=self.kwargs['category_slug'],
            slug=self.kwargs['slug']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .utils import extract_toc
        context['toc'] = extract_toc(self.object.content_markdown)
        # Get Related documents in same category
        context['related_documents'] = Document.published.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:5]
        return context
