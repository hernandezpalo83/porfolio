import logging

from django.conf import settings as django_settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Post, Category, Subscriber
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.http import HttpRequest, HttpResponse
from typing import Optional, List

logger = logging.getLogger('app.blog')


def _search_posts(queryset, query: str):
    """
    NEW-004: Búsqueda full-text.
    - PostgreSQL: usa SearchVector + SearchQuery (ranking incluido).
    - SQLite: fallback con icontains en title + excerpt.
    """
    db_engine = django_settings.DATABASES['default']['ENGINE']
    if 'postgresql' in db_engine or 'postgis' in db_engine:
        try:
            from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
            from django.db.models import F
            vector = SearchVector('title', weight='A') + SearchVector('excerpt', weight='B')
            search_query = SearchQuery(query, config='spanish')
            return (
                queryset
                .annotate(search=vector, rank=SearchRank(vector, search_query))
                .filter(search=search_query)
                .order_by('-rank')
            )
        except Exception:
            pass
    # Fallback SQLite / error
    return queryset.filter(
        Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query)
    )

def post_list(request: HttpRequest, category_slug: Optional[str] = None) -> HttpResponse:
    # Base de posts publicados
    posts_list = Post.objects.filter(status='published').select_related('category').order_by('-publish')
    
    # Filtro por búsqueda
    query: Optional[str] = request.GET.get('q')
    year: Optional[str] = request.GET.get('year')
    
    category: Optional[Category] = None
    categories: List[Category] = list(Category.objects.all())
    
    # Filtro por búsqueda (full-text en Postgres, icontains en SQLite)
    if query:
        posts_list = _search_posts(posts_list, query)
    
    # Filtro por categoría
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts_list = posts_list.filter(category=category)

    # Filtro por año
    if year:
        posts_list = posts_list.filter(publish__year=year)

    # Obtener lista de años únicos para el sidebar
    archive_years = Post.objects.filter(status='published').annotate(
        year_val=ExtractYear('publish')
    ).values_list('year_val', flat=True).distinct().order_by('-year_val')
    
    # Paginación (5 posts)
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
        
    # SEO: meta description dinámica según contexto del filtro
    if query:
        meta_description = f'Resultados de búsqueda para "{query}" en el blog de Javier Hernández Martin.'
    elif category:
        meta_description = f'Artículos de {category.name} — Blog de Javier Hernández Martin, Technical Product Manager.'
    elif year:
        meta_description = f'Artículos del año {year} — Blog de Javier Hernández Martin, Technical Product Manager.'
    else:
        meta_description = 'Blog de Javier Hernández Martin: reflexiones sobre Product Management, ingeniería y liderazgo técnico.'

    return render(request, 'blog/post_list.html', {
        'category': category,
        'categories': categories,
        'posts': posts,
        'query': query,
        'archive_years': archive_years,
        'current_year': year,
        'meta_description': meta_description,
    })

def post_detail(request: HttpRequest, post: str) -> HttpResponse:
    post_obj: Post = get_object_or_404(
        Post.objects.select_related('category', 'author'),
        slug=post,
        status='published',
    )

    # Posts relacionados cacheados 15 min por categoría
    cache_key = f'related_posts_{post_obj.category_id}'
    related_posts = cache.get(cache_key)
    if related_posts is None:
        related_posts = list(
            Post.objects.filter(category=post_obj.category, status='published')
            .exclude(pk=post_obj.pk)
            .only('title', 'slug', 'excerpt', 'publish', 'category_id')
            .order_by('-publish')[:3]
        )
        cache.set(cache_key, related_posts, 60 * 15)

    return render(request, 'blog/post_detail.html', {
        'post': post_obj,
        'related_posts': related_posts,
    })


# ── NEW-003: Newsletter ───────────────────────────────────────────────────────

@require_POST
def subscribe(request: HttpRequest) -> HttpResponse:
    """Registra un email y muestra la página de confirmación pendiente."""
    email = request.POST.get('email', '').strip().lower()
    if not email:
        return redirect('blog:post_list')

    subscriber, created = Subscriber.objects.get_or_create(email=email)

    if created:
        logger.info("Nuevo suscriptor: %s — token %s", email, subscriber.token)
        # TODO: enviar email con subscriber.get_confirm_url() via SendGrid/SMTP
        # Cuando se configure un email backend en settings, descomentar:
        # from django.core.mail import send_mail
        # send_mail(
        #     subject='Confirma tu suscripción al blog',
        #     message=f'Confirma en: {request.build_absolute_uri(subscriber.get_confirm_url())}',
        #     from_email='noreply@hernandezpalo.es',
        #     recipient_list=[email],
        # )

    return render(request, 'blog/subscribe_pending.html', {
        'email': email,
        'already_subscribed': not created and subscriber.confirmed,
    })


def confirm_subscription(request: HttpRequest, token: str) -> HttpResponse:
    """Confirma la suscripción mediante el token del email."""
    subscriber = get_object_or_404(Subscriber, token=token)

    if not subscriber.confirmed:
        subscriber.confirmed = True
        subscriber.confirmed_at = timezone.now()
        subscriber.save(update_fields=['confirmed', 'confirmed_at'])
        logger.info("Suscripción confirmada: %s", subscriber.email)

    return render(request, 'blog/subscribe_confirmed.html', {
        'email': subscriber.email,
        'already_confirmed': subscriber.confirmed_at and subscriber.confirmed,
    })