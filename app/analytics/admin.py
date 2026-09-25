from django.contrib import admin
from .models import PageView, SessionTracker, PostAnalytics, RelatedPostsCache


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'country', 'device', 'scroll_depth', 'timestamp')
    list_filter = ('device', 'country', 'timestamp')
    search_fields = ('path', 'referrer')
    readonly_fields = ('timestamp', 'session_id', 'ip_address')

    fieldsets = (
        ('Request', {'fields': ('path', 'method', 'session_id')}),
        ('Ubicación', {'fields': ('country', 'ip_address')}),
        ('Dispositivo', {'fields': ('device', 'user_agent')}),
        ('Comportamiento', {'fields': ('scroll_depth', 'time_spent', 'referrer')}),
        ('Metadata', {'fields': ('timestamp',)}),
    )


@admin.register(SessionTracker)
class SessionTrackerAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'country', 'device', 'page_count', 'is_bounce', 'created_at')
    list_filter = ('device', 'country', 'is_bounce', 'created_at')
    search_fields = ('session_id', 'first_page', 'last_page')
    readonly_fields = ('session_id', 'created_at', 'updated_at')


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('post', 'views_7d', 'views_30d', 'bounce_rate', 'trending_score')
    list_filter = ('updated_at',)
    search_fields = ('post__title',)
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Post', {'fields': ('post',)}),
        ('Vistas', {'fields': ('views_today', 'views_7d', 'views_30d', 'views_all_time')}),
        ('Comportamiento', {'fields': ('bounce_rate', 'avg_scroll_depth', 'avg_time_spent')}),
        ('Trending', {'fields': ('unique_visitors_7d', 'trending_score')}),
        ('Metadata', {'fields': ('updated_at',)}),
    )


@admin.register(RelatedPostsCache)
class RelatedPostsCacheAdmin(admin.ModelAdmin):
    list_display = ('post', 'get_related_count', 'updated_at')
    readonly_fields = ('updated_at',)
    filter_horizontal = ('related_posts',)

    def get_related_count(self, obj):
        return obj.related_posts.count()
    get_related_count.short_description = 'Posts relacionados'
