from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
import logging

from app.analytics.models import PageView, SessionTracker, PostAnalytics, RelatedPostsCache
from app.analytics.utils import calculate_trending_score
from app.blog.models import Post

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualiza agregaciones de analítica (PostAnalytics, trending scores, posts relacionados)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Recalcular desde cero (puede ser lento)',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Actualizando analíticas...')

        # Actualizar PostAnalytics para cada post
        self.update_post_analytics(options.get('full', False))

        # Actualizar posts relacionados (co-ocurrencia de tags)
        self.update_related_posts()

        self.stdout.write(self.style.SUCCESS('✅ Analíticas actualizadas'))

    def update_post_analytics(self, full_recalc=False):
        """Actualizar agregaciones por post."""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        posts = Post.objects.all()

        for post in posts:
            post_path = f'/blog/{post.slug}/'

            views_today = PageView.objects.filter(
                path=post_path,
                timestamp__date=today
            ).count()

            views_7d = PageView.objects.filter(
                path=post_path,
                timestamp__date__gte=week_ago
            ).count()

            views_30d = PageView.objects.filter(
                path=post_path,
                timestamp__date__gte=month_ago
            ).count()

            views_all_time = PageView.objects.filter(path=post_path).count()

            # Bounce rate: sesiones que vieron solo este post
            bounce_sessions = SessionTracker.objects.filter(
                last_page=post_path,
                is_bounce=True
            )
            total_sessions_7d = SessionTracker.objects.filter(
                created_at__date__gte=week_ago,
                last_page=post_path
            ).count()

            bounce_rate = (bounce_sessions.count() / max(total_sessions_7d, 1)) * 100 if total_sessions_7d > 0 else 0

            # Scroll depth y tiempo promedio
            scroll_stats = PageView.objects.filter(path=post_path).aggregate(
                avg_scroll=Avg('scroll_depth'),
                avg_time=Avg('time_spent')
            )

            avg_scroll_depth = scroll_stats['avg_scroll'] or 0
            avg_time_spent = int(scroll_stats['avg_time'] or 0)

            # Visitantes únicos (sesiones únicas) en últimos 7 días
            unique_visitors_7d = SessionTracker.objects.filter(
                last_page=post_path,
                created_at__date__gte=week_ago
            ).values('session_id').distinct().count()

            # Calcular trending score
            trending_score = calculate_trending_score(views_7d, unique_visitors_7d, bounce_rate)

            # Crear o actualizar PostAnalytics
            analytics, created = PostAnalytics.objects.update_or_create(
                post=post,
                defaults={
                    'views_today': views_today,
                    'views_7d': views_7d,
                    'views_30d': views_30d,
                    'views_all_time': views_all_time,
                    'bounce_rate': bounce_rate,
                    'avg_scroll_depth': avg_scroll_depth,
                    'avg_time_spent': avg_time_spent,
                    'unique_visitors_7d': unique_visitors_7d,
                    'trending_score': trending_score,
                }
            )

            if created:
                self.stdout.write(f'  ✨ Nuevo: {post.title}')
            else:
                self.stdout.write(f'  📊 Actualizado: {post.title} ({views_7d} views 7d)')

    def update_related_posts(self):
        """Calcular y cachear posts relacionados basado en tags compartidos."""
        posts = Post.objects.prefetch_related('tags').all()

        for post in posts:
            post_tags = set(post.tags.values_list('id', flat=True))

            if not post_tags:
                continue

            # Encontrar posts que compartan al menos 2 tags
            related_posts = Post.objects.filter(
                tags__in=post_tags
            ).exclude(id=post.id).annotate(
                shared_tags=Count('tags', filter=Q(tags__in=post_tags))
            ).filter(shared_tags__gte=2).order_by('-shared_tags').distinct()[:5]

            # Actualizar o crear RelatedPostsCache
            cache, created = RelatedPostsCache.objects.update_or_create(
                post=post,
                defaults={}
            )

            cache.related_posts.set(related_posts)

            if created:
                self.stdout.write(f'  🔗 Relacionados para: {post.title}')
