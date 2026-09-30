from django.contrib import admin
from django.utils.html import format_html

from .models import Channel, Event, NetworkLabel, PageView, PostAnalytics, RelatedPostsCache, SessionTracker


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'link', 'notes', 'visits')
    search_fields = ('name', 'code')
    readonly_fields = ('link', 'created_at')

    @admin.display(description="Enlace para copiar")
    def link(self, obj):
        return format_html('<code>{}</code>', obj.url) if obj.pk else "(guarda primero)"

    @admin.display(description="Visitas")
    def visits(self, obj):
        return obj.pageviews.count()


@admin.register(NetworkLabel)
class NetworkLabelAdmin(admin.ModelAdmin):
    list_display = ('asn', 'name', 'network_type', 'notes', 'updated_at')
    list_filter = ('network_type',)
    search_fields = ('name', 'asn', 'notes')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'kind', 'label', 'organization', 'network_type', 'channel', 'path')
    list_filter = ('kind', 'network_type', 'channel', 'timestamp')
    search_fields = ('label', 'organization', 'path')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'path', 'organization', 'network_type', 'source', 'channel', 'time_spent',
                    'scroll_depth', 'country', 'device')
    list_filter = ('network_type', 'source', 'channel', 'device', 'country', 'timestamp')
    search_fields = ('path', 'organization', 'referrer_domain', 'utm_campaign')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SessionTracker)
class SessionTrackerAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'organization', 'network_type', 'source', 'channel', 'page_count', 'is_bounce',
                    'country', 'device')
    list_filter = ('network_type', 'source', 'channel', 'device', 'country', 'is_bounce', 'created_at')
    search_fields = ('organization', 'first_page', 'last_page')
    readonly_fields = ('session_id', 'visitor_id', 'created_at', 'updated_at')


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
