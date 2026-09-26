import logging
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg
from .models import PageView, SessionTracker, PostAnalytics, RelatedPostsCache
from app.blog.models import Post

logger = logging.getLogger(__name__)


@login_required
def analytics_dashboard(request):
    """Dashboard general de analítica."""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Métricas generales
    total_views_today = PageView.objects.filter(timestamp__date=today).count()
    total_views_7d = PageView.objects.filter(timestamp__date__gte=week_ago).count()
    total_views_30d = PageView.objects.filter(timestamp__date__gte=month_ago).count()

    unique_sessions_7d = SessionTracker.objects.filter(
        created_at__date__gte=week_ago
    ).count()

    bounce_rate_7d = SessionTracker.objects.filter(
        created_at__date__gte=week_ago
    ).filter(is_bounce=True).count() / max(unique_sessions_7d, 1) * 100

    avg_duration_7d = SessionTracker.objects.filter(
        created_at__date__gte=week_ago
    ).aggregate(Avg('total_duration'))['total_duration__avg'] or 0

    contexto = {
        'total_views_today': total_views_today,
        'total_views_7d': total_views_7d,
        'total_views_30d': total_views_30d,
        'unique_sessions_7d': unique_sessions_7d,
        'bounce_rate_7d': round(bounce_rate_7d, 1),
        'avg_duration_7d': int(avg_duration_7d),
    }

    return render(request, 'private/analytics_dashboard.html', contexto)


@login_required
@require_http_methods(['GET'])
def api_views_by_day(request):
    """API: Vistas diarias (últimos 30 días)."""
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    data = []
    for i in range(30):
        date = month_ago + timedelta(days=i)
        count = PageView.objects.filter(timestamp__date=date).count()
        data.append({
            'date': date.isoformat(),
            'views': count
        })

    return JsonResponse({'data': data})


@login_required
@require_http_methods(['GET'])
def api_devices_distribution(request):
    """API: Distribución por dispositivo (últimos 7 días)."""
    week_ago = timezone.now().date() - timedelta(days=7)

    distribution = PageView.objects.filter(
        timestamp__date__gte=week_ago
    ).values('device').annotate(count=Count('device')).order_by('-count')

    data = [
        {'device': item['device'], 'count': item['count']}
        for item in distribution
    ]

    return JsonResponse({'data': data})


@login_required
@require_http_methods(['GET'])
def api_countries_distribution(request):
    """API: Tráfico por país (últimos 30 días)."""
    month_ago = timezone.now().date() - timedelta(days=30)

    distribution = PageView.objects.filter(
        timestamp__date__gte=month_ago,
        country__isnull=False
    ).exclude(country='XX').values('country').annotate(count=Count('country')).order_by('-count')[:15]

    data = [
        {'country': item['country'], 'count': item['count']}
        for item in distribution
    ]

    return JsonResponse({'data': data})


@login_required
@require_http_methods(['GET'])
def api_top_pages(request):
    """API: Páginas más visitadas (últimos 30 días)."""
    month_ago = timezone.now().date() - timedelta(days=30)

    top_pages = PageView.objects.filter(
        timestamp__date__gte=month_ago
    ).values('path').annotate(count=Count('path')).order_by('-count')[:10]

    data = [
        {'path': item['path'], 'views': item['count']}
        for item in top_pages
    ]

    return JsonResponse({'data': data})


@login_required
@require_http_methods(['GET'])
def api_referrers(request):
    """API: Origen del tráfico (últimos 30 días)."""
    month_ago = timezone.now().date() - timedelta(days=30)

    referrers = PageView.objects.filter(
        timestamp__date__gte=month_ago,
        referrer__isnull=False
    ).exclude(referrer='').values('referrer').annotate(count=Count('referrer')).order_by('-count')[:10]

    data = [
        {'referrer': item['referrer'][:100], 'count': item['count']}
        for item in referrers
    ]

    return JsonResponse({'data': data})


@login_required
def blog_analytics_dashboard(request):
    """Dashboard de analítica de blog."""
    week_ago = timezone.now().date() - timedelta(days=7)

    # Posts trending (últimos 7 días)
    trending_posts = PostAnalytics.objects.filter(
        updated_at__date__gte=week_ago
    ).order_by('-views_7d')[:10]

    # Top posts all-time
    top_posts_all_time = PostAnalytics.objects.order_by('-views_all_time')[:10]

    contexto = {
        'trending_posts': trending_posts,
        'top_posts_all_time': top_posts_all_time,
    }

    return render(request, 'private/blog_analytics_dashboard.html', contexto)


@login_required
def post_detail_analytics(request, post_id):
    """Dashboard detallado de un post específico."""
    try:
        post = Post.objects.get(id=post_id)
        analytics = post.analytics
    except (Post.DoesNotExist, PostAnalytics.DoesNotExist):
        return render(request, 'private/analytics_not_found.html', status=404)

    # Posts relacionados (por tags compartidos)
    related_cache = RelatedPostsCache.objects.filter(post=post).first()
    related_posts = related_cache.related_posts.all() if related_cache else []

    # Últimas vistas del post
    recent_views = PageView.objects.filter(
        path=f'/blog/{post.slug}/'
    ).order_by('-timestamp')[:100]

    contexto = {
        'post': post,
        'analytics': analytics,
        'related_posts': related_posts,
        'recent_views': recent_views,
    }

    return render(request, 'private/post_detail_analytics.html', contexto)


@login_required
@require_http_methods(['GET'])
def api_post_views_by_day(request, post_id):
    """API: Vistas diarias de un post (últimos 30 días)."""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post no encontrado'}, status=404)

    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    data = []
    for i in range(30):
        date = month_ago + timedelta(days=i)
        count = PageView.objects.filter(
            path=f'/blog/{post.slug}/',
            timestamp__date=date
        ).count()
        data.append({
            'date': date.isoformat(),
            'views': count
        })

    return JsonResponse({'data': data})
