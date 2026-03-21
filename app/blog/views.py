from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from .models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.http import HttpRequest, HttpResponse
from typing import Optional, List

def post_list(request: HttpRequest, category_slug: Optional[str] = None) -> HttpResponse:
    # Base de posts publicados
    posts_list = Post.objects.filter(status='published').select_related('category').order_by('-publish')
    
    # Filtro por búsqueda
    query: Optional[str] = request.GET.get('q')
    year: Optional[str] = request.GET.get('year')
    
    category: Optional[Category] = None
    categories: List[Category] = list(Category.objects.all())
    
    # Filtro por búsqueda
    if query:
        posts_list = posts_list.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
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