from django.shortcuts import render, get_object_or_404
from .models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import ExtractYear

def post_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    query = request.GET.get('q')
    year = request.GET.get('year')
    
    # Base de posts publicados
    posts_list = Post.objects.filter(status='published').select_related('category').order_by('-publish')
    
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

def post_detail(request, post):
    post = get_object_or_404(Post, slug=post, status='published')
    
    # Lógica de Artículos Relacionados: misma categoría, excluir el actual, últimos 3
    related_posts = Post.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id).order_by('-publish')[:3]
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related_posts
    })