from django.shortcuts import render, get_object_or_404
from .models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.http import HttpRequest, HttpResponse
from typing import Optional, Dict, Any, List

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
        
    return render(request, 'blog/post_list.html', {
        'category': category,
        'categories': categories,
        'posts': posts,
        'query': query,
        'archive_years': archive_years,
        'current_year': year
    })

def post_detail(request: HttpRequest, post: str) -> HttpResponse:
    post_obj: Post = get_object_or_404(Post, slug=post, status='published')
    
    # Lógica de Artículos Relacionados: misma categoría, excluir el actual, últimos 3
    related_posts = Post.objects.filter(
        category=post_obj.category, 
        status='published'
    ).exclude(id=post_obj.id).order_by('-publish')[:3]
    
    return render(request, 'blog/post_detail.html', {
        'post': post_obj,
        'related_posts': related_posts
    })