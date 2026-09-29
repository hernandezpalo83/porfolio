"""
Views for Documentation Hub.

Querysets are served from the versioned 'wiki' content cache, which is
invalidated whenever a category or document is saved (see apps.py).
"""

from django.db.models import Count, Q
from django.http import Http404
from django.views.generic import DetailView, ListView

from app.utils.content_cache import cached

from .models import Category, Document
from .utils import extract_toc


def _visible_category(slug: str) -> Category:
    category = cached(('wiki',), f'category:{slug}', lambda: (
        Category.objects.filter(slug=slug, is_visible=True).first()
    ))
    if category is None:
        raise Http404("Categoría no encontrada")
    return category


class CategoryListView(ListView):
    """List all visible categories"""
    model = Category
    template_name = 'documentum/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return cached(('wiki',), 'categories', lambda: list(
            Category.objects.filter(is_visible=True)
            .annotate(published_count=Count('documents', filter=Q(documents__status='published')))
            .order_by('order', 'name')
        ))


class DocumentListView(ListView):
    """List published documents in a specific category (paginated)"""
    model = Document
    template_name = 'documentum/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        self.category = _visible_category(self.kwargs['category_slug'])
        return cached(('wiki',), f'documents:{self.category.pk}', lambda: list(
            Document.published.filter(category=self.category)
            .select_related('category')  # get_absolute_url and reading_time need category + markdown
            .defer('content_html')
            .order_by('-updated_at')
        ))

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
        category_slug, slug = self.kwargs['category_slug'], self.kwargs['slug']
        document = cached(('wiki',), f'document:{category_slug}:{slug}', lambda: (
            Document.published.select_related('category')
            .filter(category__slug=category_slug, slug=slug).first()
        ))
        if document is None:
            raise Http404("Documento no encontrado")
        return document

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc = self.object
        context['toc'] = cached(('wiki',), f'toc:{doc.pk}', lambda: extract_toc(doc.content_markdown))
        context['related_documents'] = cached(('wiki',), f'related:{doc.pk}', lambda: list(
            Document.published.filter(category_id=doc.category_id).exclude(pk=doc.pk)
            .select_related('category')[:5]
        ))
        return context
